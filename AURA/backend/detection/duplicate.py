"""
Duplicate Detection Module

Prevents counting the same survivor multiple times.
Uses spatial (distance) and temporal (time) proximity checks
to determine if a newly detected survivor matches an existing record.
"""

import time
from typing import Optional, Tuple

from utils.helpers import calculate_distance
from config.settings import SURVIVOR_DIST_THRESHOLD, SURVIVOR_TIME_THRESHOLD


def is_duplicate(
    new_survivor: dict,
    victim_db,
    distance_threshold: Optional[float] = None,
    time_threshold: Optional[float] = None
) -> bool:
    """
    Check if a newly detected survivor is a duplicate of an existing entry.
    
    A survivor is considered a duplicate if:
    1. They are within the distance threshold of an existing survivor
    2. AND the detection occurred within the time threshold
    
    Args:
        new_survivor: Newly detected survivor dictionary
        victim_db: VictimDB instance with get_all() method
        distance_threshold: Max Euclidean distance (default from config)
        time_threshold: Max time difference in seconds (default from config)
    
    Returns:
        True if duplicate, False otherwise.
    """
    dist_thresh = distance_threshold or SURVIVOR_DIST_THRESHOLD
    time_thresh = time_threshold or SURVIVOR_TIME_THRESHOLD
    current_time = time.time()
    
    new_location = (new_survivor['x'], new_survivor['y'])
    
    for survivor in victim_db.get_all():
        existing_location = (survivor['x'], survivor['y'])
        distance = calculate_distance(new_location, existing_location)
        
        if distance < dist_thresh:
            time_diff = current_time - survivor['timestamp']
            if time_diff < time_thresh:
                return True
    
    return False


def find_nearby_survivors(
    x: int,
    y: int,
    victim_db,
    distance_threshold: Optional[float] = None
) -> list:
    """
    Find all survivors within a given distance of coordinates.
    
    Args:
        x: X coordinate to search from
        y: Y coordinate to search from
        victim_db: VictimDB instance
        distance_threshold: Search radius (default from config)
    
    Returns:
        List of nearby survivor dictionaries.
    """
    dist_thresh = distance_threshold or SURVIVOR_DIST_THRESHOLD
    location = (x, y)
    nearby = []
    
    for survivor in victim_db.get_all():
        survivor_loc = (survivor['x'], survivor['y'])
        distance = calculate_distance(location, survivor_loc)
        
        if distance < dist_thresh:
            nearby.append(survivor)
    
    return nearby


def merge_survivor_records(existing: dict, new: dict) -> dict:
    """
    Merge two survivor records, keeping the most complete data.
    
    Args:
        existing: Existing survivor record
        new: New survivor record
    
    Returns:
        Merged survivor dictionary.
    """
    merged = existing.copy()
    
    # Keep earliest timestamp
    if new.get('timestamp', float('inf')) < existing.get('timestamp', float('inf')):
        merged['timestamp'] = new['timestamp']
    
    # Combine any additional fields
    for key, value in new.items():
        if key not in merged:
            merged[key] = value
    
    return merged
