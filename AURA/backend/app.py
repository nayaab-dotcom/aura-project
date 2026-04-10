import threading
import time
import random
import os
import sys

# Ensure project root is on sys.path so sibling modules (bridge, mapping, etc.) resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, jsonify, request
from flask_cors import CORS

from data.simulator import SensorSimulator
from detection.hazard import classify_risk
from mapping.grid_map import GridMap
from detection.survivor import detect_survivor
from detection.duplicate import is_duplicate
from database.victim_db import VictimDB
from planning.pathfinding import a_star
from drone.drone import PhysicalDrone, _drones
from mission.controller import MissionController, SimulationController
from reporting.mission_report import generate_mission_report
from simulation.engine import SimulationEngine, DroneAutonomy
from logs.logger import get_logger
from bridge.aur_control import send_command as send_serial_command

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# --- CORE SYSTEM STATE ---
mission_ctrl = MissionController()
sim_controller = SimulationController()
simulator = SensorSimulator()
grid_map = GridMap()
victim_db = VictimDB()

# Create drones with quadrant assignments
drones = [PhysicalDrone(i+1, 0, 0) for i in range(4)]

system_logs = []

def log_event(msg):
    """Callback for engine logs."""
    system_logs.append({
        'timestamp': time.time(),
        'message': msg
    })
    if len(system_logs) > 50:
        system_logs.pop(0)

# Initialize simulation engine
engine = SimulationEngine(drones, grid_map, victim_db, simulator, log_event)
logger = get_logger()

for i, drone in enumerate(drones):
    drone.state = 'SCANNING'  # Start in scanning mode
    DroneAutonomy.assign_new_target(drone, grid_map)

# Start the autonomous engine
engine.start()

# --- MISSION & REPORTING ---

@app.route('/mission/reset', methods=['POST'])
@app.route('/api/reset', methods=['POST'])
def mission_reset():
    global drones
    mission_ctrl.reset_mission()
    grid_map.reset()
    victim_db.reset()
    system_logs.clear()
    
    # Reset drones to origin and reassign targets
    drones = [PhysicalDrone(i+1, 0, 0) for i in range(4)]
    for i, drone in enumerate(drones):
        drone.state = 'SCANNING'
        DroneAutonomy.assign_new_target(drone, grid_map)
    
    # Reset and restart engine
    engine.reset()
    engine.drones = drones
    engine.start()
    
    log_event(f"SYSTEM RESET: New Mission ID {mission_ctrl.get_mission_id()} Initialized")
    return jsonify({
        'status': 'reset',
        'mission_id': mission_ctrl.get_mission_id()
    })

@app.route('/report', methods=['GET'])
def get_report():
    report = generate_mission_report(mission_ctrl.current_mission, grid_map, victim_db)
    return jsonify(report)

# --- FLASK API ENDPOINTS ---

@app.route('/api/state', methods=['GET'])
def get_state():
    """Aggregate state endpoint for the dashboard frontend."""
    return jsonify({
        'grid': grid_map.get_grid_state(),
        'drones': [d.get_state() for d in drones],
        'survivors': victim_db.get_all(),
        'logs': system_logs[-20:],
        'stats': {
            'survivors_found': victim_db.get_count(),
            'coverage_percent': round(grid_map.get_coverage_percent(), 2),
            'high_risk_cells': grid_map.get_high_risk_count(),
            'medium_risk_cells': grid_map.get_medium_risk_count(),
            'safe_cells': grid_map.get_safe_count(),
            'total_cells': grid_map.width * grid_map.height
        }
    })

@app.route('/grid', methods=['GET'])
def get_grid():
    return jsonify({'grid': grid_map.get_grid_state()})

@app.route('/drones', methods=['GET'])
def get_drones():
    return jsonify({'drones': [d.get_state() for d in drones]})

@app.route('/survivors', methods=['GET'])
def get_survivors():
    return jsonify({'survivors': victim_db.get_all()})

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify({'logs': system_logs})

@app.route('/drone/<int:id>/frame', methods=['GET'])
def get_drone_frame(id):
    """Simulates a live video feed frame by returning a seeded dynamic image URL."""
    return jsonify({
        "frame": f"https://picsum.photos/seed/{id}_{int(time.time())}/600/400"
    })

@app.route('/action/scan', methods=['POST'])
@app.route('/api/scan/<int:drone_id>', methods=['POST'])
def action_scan(drone_id=None):
    if drone_id is None:
        data = request.json or {}
        drone_id = data.get('id')
    drone = next((d for d in drones if d.drone_id == drone_id), None)
    if drone:
        drone.state = 'SCANNING'
        drone.mode = 'AUTO'
        goal = (random.randint(0, 49), random.randint(0, 49))
        weight_grid = grid_map.get_weight_grid()
        path = a_star(weight_grid, (drone.x, drone.y), goal)
        if path:
            drone.path = path
            log_event(f"COMMAND: AURA-{drone_id} scanning vector -> {goal}")
            return jsonify({'status': 'success', 'goal': goal})
        return jsonify({'status': 'error', 'message': 'Path blocked'})
    return jsonify({'status': 'error', 'message': 'Drone not found'})

@app.route('/action/swarm', methods=['POST'])
@app.route('/api/swarm', methods=['POST'])
def action_swarm():
    """Assigns each drone to a specific 25x25 quadrant."""
    quadrants = [
        (12, 12), # Q1 (Top Left)
        (37, 12), # Q2 (Top Right)
        (12, 37), # Q3 (Bottom Left)
        (37, 37)  # Q4 (Bottom Right)
    ]
    weight_grid = grid_map.get_weight_grid()
    for i, drone in enumerate(drones):
        drone.state = 'SCANNING'
        drone.mode = 'AUTO'
        goal = quadrants[i % 4]
        path = a_star(weight_grid, (drone.x, drone.y), goal)
        if path:
            drone.path = path
    
    log_event("STRATEGY: Quad-Sector Swarm Pattern Engaged")
    return jsonify({'status': 'swarm_engaged'})

@app.route('/action/recall', methods=['POST'])
@app.route('/api/recall/<int:drone_id>', methods=['POST'])
def action_recall(drone_id=None):
    if drone_id is None:
        data = request.json or {}
        drone_id = data.get('id')
    drone = next((d for d in drones if d.drone_id == drone_id), None)
    if drone:
        drone.state = 'RETURNING'
        drone.mode = 'AUTO'
        weight_grid = grid_map.get_weight_grid()
        path = a_star(weight_grid, (drone.x, drone.y), (0, 0))
        if path:
            drone.path = path
            log_event(f"COMMAND: AURA-{drone_id} recalling to base (0,0)")
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Path blocked'})
    return jsonify({'status': 'error', 'message': 'Drone not found'})

# --- HITL CONTROL ENDPOINTS ---

@app.route('/control/mode', methods=['POST'])
def control_mode():
    data = request.json
    drone_id = data.get('id')
    mode = data.get('mode') # AUTO, ASSISTED, MANUAL
    drone = next((d for d in drones if d.drone_id == drone_id), None)
    if drone and mode in ['AUTO', 'ASSISTED', 'MANUAL']:
        drone.mode = mode
        log_event(f"OVERRIDE: AURA-{drone_id} mode changed to {mode}")
        return jsonify({'status': 'success', 'mode': mode})
    return jsonify({'status': 'error', 'message': 'Invalid drone or mode'})

@app.route('/control/move', methods=['POST'])
def control_move():
    data = request.json
    drone_id = data.get('id')
    x, y = data.get('x'), data.get('y')
    drone = next((d for d in drones if d.drone_id == drone_id), None)
    if drone and x is not None and y is not None:
        drone.mode = 'MANUAL'
        drone.manual_target = (x, y)
        drone.path = [] # Clear any auto path
        log_event(f"OVERRIDE: AURA-{drone_id} manual target set to [{x}, {y}]")
        return jsonify({'status': 'success', 'target': [x, y]})
    return jsonify({'status': 'error', 'message': 'Invalid coordinate or drone'})

@app.route('/control/pause', methods=['POST'])
def control_pause():
    data = request.json
    drone_id = data.get('id')
    drone = next((d for d in drones if d.drone_id == drone_id), None)
    if drone:
        drone.mode = 'MANUAL'
        drone.manual_target = (drone.x, drone.y) # Freeze in place
        drone.path = []
        log_event(f"OVERRIDE: AURA-{drone_id} Halted (PAUSED)")
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Drone not found'})

@app.route('/data', methods=['POST'])
def manual_data_ingest():
    """
    Manual data ingest API for bypassing internal simulator if needed.
    Accepts either:
      { "temp": 45, "gas": 30, "x": 10, "y": 10 }
    or bridge-friendly:
      { "drone_id":1, "temperature":45, "gas_level":30, "location":[10,10] }
    """
    data = request.json or {}
    print("[DATA] RECEIVED:", data, flush=True)

    # normalize payload
    if 'temp' in data or 'gas' in data:
        temp = data.get('temp')
        gas = data.get('gas')
        x = data.get('x')
        y = data.get('y')
    else:
        temp = data.get('temperature')
        gas = data.get('gas_level')
        loc = data.get('location') or []
        x = loc[0] if len(loc) > 0 else None
        y = loc[1] if len(loc) > 1 else None

    # basic validation
    if temp is None or gas is None or x is None or y is None:
        return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400

    try:
        temp = float(temp)
        gas = float(gas)
        x = int(x)
        y = int(y)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Non-numeric fields'}), 400

    risk = classify_risk(temp, gas)
    grid_map.update_cell(x, y, risk)

    return jsonify({
        'status': 'processed',
        'source': 'manual_data_ingest_v2',
        'classification': risk,
        'ingest': {'temp': temp, 'gas': gas, 'x': x, 'y': y}
    })

@app.route('/whoami', methods=['GET'])
def whoami():
    return jsonify({'app': 'backend/app.py', 'status': 'ok'})

# Explicit SPA entry points to avoid static-handler 404s
@app.route('/analysis')
@app.route('/report')
@app.route('/login')
def spa_named_routes():
    return app.send_static_file('index.html')

# --- SPA Fallback (serve React build for client-side routes) ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def spa(path):
    """
    Serve the Vite-built frontend for any non-API route so deep links like
    /drone/1 work when refreshed.
    """
    static_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_path):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

@app.route('/command', methods=['POST'])
def send_command():
    """
    Forward validated commands to ESP32 over serial.
    Expected JSON:
      { "drone_id": 1, "action": "move", "target": [x, y] }
    """
    data = request.json or {}
    drone_id = data.get('drone_id')
    action = data.get('action')
    target = data.get('target')

    # Basic validation
    if drone_id is None or action is None or target is None:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
    try:
        drone_id = int(drone_id)
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'drone_id must be int'}), 400

    if not isinstance(target, (list, tuple)) or len(target) != 2:
        return jsonify({'status': 'error', 'message': 'target must be [x, y]'}), 400
    try:
        tx = int(target[0])
        ty = int(target[1])
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'target coords must be numeric'}), 400

    payload = {
        "drone_id": drone_id,
        "action": action,
        "target": [tx, ty]
    }

    ok = send_serial_command(payload)
    if not ok:
        return jsonify({'status': 'error', 'message': 'serial send failed'}), 500

    return jsonify({'status': 'sent', 'payload': payload})

if __name__ == '__main__':
    # Engine is already started above
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port)
