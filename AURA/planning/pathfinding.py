"""
Pathfinding Module - Implements A* algorithm for safe path calculation.
"""

import heapq
import math
from typing import List, Tuple, Optional
from config import COST_HIGH


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Calculate Euclidean distance heuristic."""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def a_star(
    grid_state: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    A* pathfinding with 8-directional movement.
    Avoids HIGH-risk cells (cost >= 1000).
    """
    rows = len(grid_state)
    cols = len(grid_state[0]) if rows > 0 else 0
    
    if not _is_valid_coord(start, rows, cols) or not _is_valid_coord(goal, rows, cols):
        return None
    
    # Reject pathfinding from or to HIGH-risk cells
    if grid_state[start[1]][start[0]] >= COST_HIGH:
        return None
    if grid_state[goal[1]][goal[0]] >= COST_HIGH:
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
