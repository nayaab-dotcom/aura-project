"""Survivor detection logic with probabilistic outcomes driven by risk level."""

import random
import time
import uuid
from typing import Dict, Optional

from config import PROB_HIGH, PROB_MEDIUM, PROB_SAFE
from utils.helpers import ValidationError, normalize_location


def _resolve_inputs(*args):
    """Support both legacy (x, y, risk) and new (risk_level, location) calling styles."""
    if len(args) >= 3:
        # Legacy signature: (x, y, risk_level)
        x, y, risk_level = args[0], args[1], args[2]
    elif len(args) >= 2 and isinstance(args[0], str):
        # New signature: (risk_level, location)
        risk_level = args[0]
        x, y = normalize_location(args[1])
    else:
        raise ValidationError(
            "detect_survivor expects (x, y, risk_level) or (risk_level, location)"
        )
    return int(x), int(y), str(risk_level)


def _probability_lookup(
    risk_level: str, override: Optional[Dict[str, float]] = None
) -> float:
    mapping = override or {
        "SAFE": PROB_SAFE,
        "MEDIUM": PROB_MEDIUM,
        "HIGH": PROB_HIGH,
    }
    # Guarantee ordering SAFE > MEDIUM > HIGH even if misconfigured
    safe = mapping.get("SAFE", 0.0)
    medium = min(mapping.get("MEDIUM", 0.0), safe)
    high = min(mapping.get("HIGH", 0.0), medium)
    ordered = {"SAFE": safe, "MEDIUM": medium, "HIGH": high}
    return ordered.get(risk_level, 0.0)


def detect_survivor(
    *args,
    timestamp: Optional[float] = None,
    probabilities: Optional[Dict[str, float]] = None,
) -> Optional[Dict]:
    """
    Attempt to detect a survivor at the specified location.

    Probability is risk-weighted:
    - SAFE   -> highest chance
    - MEDIUM -> moderate chance
    - HIGH   -> lowest chance
    """
    x, y, risk_level = _resolve_inputs(*args)
    prob = _probability_lookup(risk_level, probabilities)

    if random.random() >= prob:
        return None

    survivor_id = f"VICTIM-{uuid.uuid4().hex[:6].upper()}"
    detected_at = timestamp if timestamp is not None else time.time()

    return {
        "id": survivor_id,
        "x": x,
        "y": y,
        "location": (x, y),
        "timestamp": detected_at,
        "status": "VERIFIED",
        "risk_level_at_detection": risk_level,
        "confidence": round(prob, 4),
    }
