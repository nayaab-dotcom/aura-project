"""Flask API exposing the full AURA backend processing pipeline."""

import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import BASE_STATION_X, BASE_STATION_Y, COST_HIGH, GRID_HEIGHT, GRID_WIDTH
from data.simulator import generate_sensor_data
from database.victim_db import VictimDB
from detection.duplicate import is_duplicate
from detection.hazard import classify_risk
from detection.survivor import detect_survivor
from mapping.grid_map import GridMap
from planning.pathfinding import a_star
from utils.helpers import ValidationError, normalize_location, normalize_sensor_payload

logger = logging.getLogger("aura.server")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class AuraBackend:
    """Central coordinator that holds mission state and runs the processing pipeline."""

    def __init__(self):
        self.grid_map = GridMap()
        self.victim_db = VictimDB()
        self._lock = threading.RLock()
        self.last_path = None
        self.last_goal: Optional[Tuple[int, int]] = None
        self.last_result: Optional[Dict[str, Any]] = None

    def process_sensor_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """Run the mandatory pipeline for a single sensor packet."""
        normalized = normalize_sensor_payload(packet)
        x, y = normalized["location"]
        risk = classify_risk(normalized["temperature"], normalized["gas_level"])

        with self._lock:
            # 2. Update grid
            self.grid_map.update_cell(x, y, risk, normalized["timestamp"])

            # 3. Detect survivor (probability-based)
            detected = detect_survivor(x, y, risk, timestamp=normalized["timestamp"])

            # 4. Duplicate filtering
            duplicate = False
            stored_survivor = None
            if detected:
                duplicate = is_duplicate(detected, self.victim_db)
                if not duplicate:
                    stored_survivor = self.victim_db.add_survivor(detected)

            # 5. Pathfinding (safest path base -> observation)
            path = self._compute_path((BASE_STATION_X, BASE_STATION_Y), (x, y))

            self.last_goal = (x, y)
            self.last_path = path

            self.last_result = {
                "sensor": normalized,
                "risk": risk,
                "survivor_detected": bool(detected),
                "duplicate": duplicate,
                "stored_survivor": stored_survivor,
                "path": path,
            }
            return self.last_result

    def _compute_path(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """Compute a path with A* avoiding HIGH risk cells."""
        if not self._is_within_grid(goal):
            return None

        weight_grid = self.grid_map.get_weight_grid()
        if weight_grid[goal[1]][goal[0]] >= COST_HIGH:
            return None  # Cannot terminate on a high-risk cell

        return a_star(weight_grid, start, goal)

    def compute_path(
        self, goal: Tuple[int, int], start: Optional[Tuple[int, int]] = None
    ) -> Optional[List[Tuple[int, int]]]:
        """Public helper for path recalculation without running the full pipeline."""
        with self._lock:
            start_point = start or (BASE_STATION_X, BASE_STATION_Y)
            return self._compute_path(start_point, goal)

    def get_state(self) -> Dict[str, Any]:
        """Return a consistent snapshot of the mission state."""
        with self._lock:
            return {
                "grid": self.grid_map.get_grid_state(),
                "survivors": self.victim_db.get_all(),
                "last_goal": self.last_goal,
                "last_path": self.last_path,
            }

    @staticmethod
    def _is_within_grid(coord: Tuple[int, int]) -> bool:
        x, y = coord
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT


backend = AuraBackend()

app = Flask(__name__)
CORS(app)


@app.route("/data", methods=["POST"])
def ingest_data():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid or missing JSON payload"}), 400
    try:
        result = backend.process_sensor_packet(payload)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception("pipeline failure")
        return jsonify({"error": "internal server error", "detail": str(exc)}), 500

    return jsonify(
        {
            "status": "processed",
            "risk": result["risk"],
            "survivor_detected": result["survivor_detected"],
            "duplicate": result["duplicate"],
            "stored_survivor": result["stored_survivor"],
            "path": _serialize_path(result["path"]),
            "grid_cell": {
                "x": result["sensor"]["location"][0],
                "y": result["sensor"]["location"][1],
            },
        }
    )


@app.route("/grid", methods=["GET"])
def get_grid():
    state = backend.get_state()
    return jsonify({"grid": state["grid"]})


@app.route("/survivors", methods=["GET"])
def get_survivors():
    state = backend.get_state()
    return jsonify({"survivors": state["survivors"], "count": len(state["survivors"])})


@app.route("/path", methods=["GET"])
def get_path():
    goal = _parse_goal()
    if goal is None:
        latest = backend.victim_db.get_latest()
        if latest:
            goal = (latest["x"], latest["y"])
        elif backend.last_goal:
            goal = backend.last_goal
        else:
            return jsonify({"error": "no target provided and no known goal"}), 400

    start = _parse_start() or (BASE_STATION_X, BASE_STATION_Y)
    path = backend.compute_path(goal, start)
    return jsonify({"path": _serialize_path(path), "start": start, "goal": goal})


@app.route("/state", methods=["GET"])
def full_state():
    """Convenience endpoint for dashboards to fetch everything at once."""
    state = backend.get_state()
    return jsonify(
        {
            "grid": state["grid"],
            "survivors": state["survivors"],
            "last_goal": state["last_goal"],
            "last_path": _serialize_path(state["last_path"]),
        }
    )


@app.route("/simulate", methods=["GET"])
def simulate_once():
    """Utility endpoint: generate one simulator reading and run the pipeline."""
    drone_id = int(request.args.get("drone_id", 1))
    packet = generate_sensor_data(drone_id=drone_id)
    result = backend.process_sensor_packet(packet)
    return jsonify(
        {
            "generated": packet,
            "risk": result["risk"],
            "survivor_detected": result["survivor_detected"],
            "duplicate": result["duplicate"],
            "path": _serialize_path(result["path"]),
        }
    )


def _parse_goal() -> Optional[Tuple[int, int]]:
    if "x" in request.args and "y" in request.args:
        return normalize_location((request.args["x"], request.args["y"]))
    if "target" in request.args:
        target = request.args.get("target", "")
        parts = target.split(",")
        if len(parts) == 2:
            return normalize_location(parts)
    return None


def _parse_start() -> Optional[Tuple[int, int]]:
    if "start_x" in request.args and "start_y" in request.args:
        return normalize_location((request.args["start_x"], request.args["start_y"]))
    return None


def _serialize_path(path):
    if path is None:
        return None
    return [(int(x), int(y)) for x, y in path]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
