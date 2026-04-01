"""
Pathfinding Module

Implements A* algorithm for safe path calculation.
Avoids HIGH-risk zones, prefers SAFE paths through the grid.
"""

import heapq
import math
from typing import List, Tuple, Optional

from config.settings import COST_HIGH


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """
    Calculate Euclidean distance heuristic.
    Used for 8-directional movement estimation.
    
    Args:
        a: Starting coordinates (x, y)
        b: Goal coordinates (x, y)
    
    Returns:
        Estimated distance to goal.
    """
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def a_star(
    grid_state: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding with 8-directional movement.
    
    Finds the optimal path from start to goal while avoiding
    HIGH-risk cells (cost >= 1000).
    
    Args:
        grid_state: 2D cost grid from GridMap.get_weight_grid()
        start: Starting coordinates (x, y)
        goal: Target coordinates (x, y)
    
    Returns:
        List of coordinates from start to goal, or None if no path exists.
    """
    rows = len(grid_state)
    cols = len(grid_state[0]) if rows > 0 else 0
    
    if not _is_valid_coord(start, rows, cols) or not _is_valid_coord(goal, rows, cols):
        return None
    
    if start == goal:
        return [start]
    
    directions = [
        (0, 1, 1), (0, -1, 1), (1, 0, 1), (-1, 0, 1),
        (1, 1, 1.41), (1, -1, 1.41), (-1, 1, 1.41), (-1, -1, 1.41)
    ]
    
    open_list = [(0.0, start)]
    g_score = {start: 0.0}
    parent = {start: None}
    
    while open_list:
        _, current = heapq.heappop(open_list)
        
        if current == goal:
            return _reconstruct_path(parent, current)
        
        for dx, dy, move_cost in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if not _is_valid_coord(neighbor, rows, cols):
                continue
            
            cost = grid_state[neighbor[1]][neighbor[0]]
            
            if cost >= COST_HIGH:
                continue
            
            tentative_g = g_score[current] + (move_cost * cost)
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                parent[neighbor] = current
                heapq.heappush(open_list, (f_score, neighbor))
    
    return None


def _is_valid_coord(coord: Tuple[int, int], rows: int, cols: int) -> bool:
    """Check if coordinates are within grid bounds."""
    x, y = coord
    return 0 <= x < cols and 0 <= y < rows


def _reconstruct_path(parent: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Reconstruct path from parent map."""
    path = []
    while current is not None:
        path.append(current)
        current = parent[current]
    return path[::-1]


def find_path_length(path: Optional[List[Tuple[int, int]]]) -> int:
    """
    Calculate the length of a path.
    
    Args:
        path: List of coordinates
    
    Returns:
        Number of steps in path, or 0 if no path.
    """
    return len(path) if path else 0


def simplify_path(path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Simplify path by removing unnecessary waypoints.
    Keeps only turn points in the path.
    
    Args:
        path: Full path from A*
    
    Returns:
        Simplified path with only essential waypoints.
    """
    if len(path) <= 2:
        return path
    
    simplified = [path[0]]
    
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        curr = path[i]
        next_pt = path[i + 1]
        
        dx1 = curr[0] - prev[0]
        dy1 = curr[1] - prev[1]
        dx2 = next_pt[0] - curr[0]
        dy2 = next_pt[1] - curr[1]
        
        if dx1 != dx2 or dy1 != dy2:
            simplified.append(curr)
    
    simplified.append(path[-1])
    return simplified
