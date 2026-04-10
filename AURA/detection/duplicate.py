"""Duplicate detection based on spatial and temporal proximity."""

from typing import Iterable, Optional

from config import SURVIVOR_DIST_THRESHOLD, SURVIVOR_TIME_THRESHOLD
from utils.helpers import ValidationError, calculate_distance


def _iter_survivors(victim_db_or_list) -> Iterable[dict]:
    """Return an iterable of survivor dicts given either a DB or a raw list."""
    if hasattr(victim_db_or_list, "get_all"):
        return victim_db_or_list.get_all()
    if isinstance(victim_db_or_list, list):
        return victim_db_or_list
    raise ValidationError("victim_db must expose get_all() or be a list of survivors")


def is_duplicate(
    new_survivor: dict,
    victim_db_or_list,
    distance_threshold: Optional[float] = None,
    time_threshold: Optional[float] = None,
) -> bool:
    """
    Check if a newly detected survivor matches an existing one.

    Conditions (both must be true):
    1. Euclidean distance <= distance_threshold
    2. |timestamp difference| <= time_threshold
    """
    dist_thresh = distance_threshold or SURVIVOR_DIST_THRESHOLD
    time_thresh = time_threshold or SURVIVOR_TIME_THRESHOLD

    try:
        new_location = (new_survivor["x"], new_survivor["y"])
        new_time = float(new_survivor["timestamp"])
    except KeyError as exc:
        raise ValidationError(f"new_survivor missing key: {exc}") from exc

    for survivor in _iter_survivors(victim_db_or_list):
        try:
            existing_location = (survivor["x"], survivor["y"])
            existing_time = float(survivor["timestamp"])
        except KeyError:
            # Skip malformed survivor records but do not fail the pipeline
            continue

        distance = calculate_distance(new_location, existing_location)
        time_diff = abs(existing_time - new_time)

        if distance <= dist_thresh and time_diff <= time_thresh:
            return True

    return False
