"""Utility helpers shared across the AURA backend stack.

This module intentionally stays dependency-light so it can be safely used by
both the simulation engine and the Flask API layer. Keep anything that
performs I/O or heavy lifting out of here.
"""

import math
import time
from typing import Any, Dict, Sequence, Tuple

from config import GRID_WIDTH, GRID_HEIGHT


class ValidationError(ValueError):
    """Raised when an inbound payload fails strict validation."""


def calculate_distance(loc1: Tuple[int, int], loc2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two coordinates."""
    return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)


def manhattan_distance(loc1: Tuple[int, int], loc2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two coordinates."""
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max bounds."""
    return max(min_val, min(max_val, value))


def is_within_bounds(x: int, y: int, width: int, height: int) -> bool:
    """Check if coordinates are within grid bounds."""
    return 0 <= x < width and 0 <= y < height


def normalize_location(location: Sequence[Any]) -> Tuple[int, int]:
    """Validate and coerce a location-like sequence to an ``(x, y)`` tuple."""
    if not isinstance(location, (list, tuple)) or len(location) != 2:
        raise ValidationError("location must be a 2-element list/tuple")
    try:
        x = int(location[0])
        y = int(location[1])
    except (TypeError, ValueError):
        raise ValidationError("location elements must be numeric") from None
    if not is_within_bounds(x, y, GRID_WIDTH, GRID_HEIGHT):
        raise ValidationError(
            f"location out of bounds: ({x}, {y}) not within 0-{GRID_WIDTH-1}, 0-{GRID_HEIGHT-1}"
        )
    return x, y


def normalize_sensor_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure inbound sensor data conforms to the required schema.

    Expected format (strict):
    {
        "drone_id": int,
        "temperature": float,
        "gas_level": float,
        "location": (x, y),
        "timestamp": float
    }
    """
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a JSON object")

    required_fields = ["drone_id", "temperature", "gas_level", "location", "timestamp"]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        raise ValidationError(f"missing required fields: {', '.join(missing)}")

    try:
        drone_id = int(payload["drone_id"])
    except (TypeError, ValueError):
        raise ValidationError("drone_id must be an integer") from None

    try:
        temperature = float(payload["temperature"])
        gas_level = float(payload["gas_level"])
    except (TypeError, ValueError):
        raise ValidationError("temperature and gas_level must be numeric") from None

    x, y = normalize_location(payload["location"])

    try:
        timestamp = float(payload["timestamp"])
    except (TypeError, ValueError):
        raise ValidationError("timestamp must be a unix epoch float") from None

    return {
        "drone_id": drone_id,
        "temperature": temperature,
        "gas_level": gas_level,
        "location": (x, y),
        "timestamp": timestamp,
    }


def utc_timestamp() -> float:
    """Return a monotonic-friendly timestamp (seconds since epoch)."""
    return time.time()
