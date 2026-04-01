"""
Utilities Module

Helper functions used across the AURA system.
"""

import math
from typing import Tuple


def calculate_distance(loc1: Tuple[int, int], loc2: Tuple[int, int]) -> float:
    """
    Calculate Euclidean distance between two coordinates.
    
    Args:
        loc1: First coordinate (x, y)
        loc2: Second coordinate (x, y)
    
    Returns:
        Euclidean distance as float.
    """
    return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)


def manhattan_distance(loc1: Tuple[int, int], loc2: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two coordinates.
    Useful for 4-directional pathfinding.
    
    Args:
        loc1: First coordinate (x, y)
        loc2: Second coordinate (x, y)
    
    Returns:
        Manhattan distance as integer.
    """
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
    
    Returns:
        Clamped value.
    """
    return max(min_val, min(max_val, value))


def is_within_bounds(x: int, y: int, width: int, height: int) -> bool:
    """
    Check if coordinates are within grid bounds.
    
    Args:
        x: X coordinate
        y: Y coordinate
        width: Grid width
        height: Grid height
    
    Returns:
        True if coordinates are valid.
    """
    return 0 <= x < width and 0 <= y < height
