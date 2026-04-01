"""
AI Scoring Module

Provides intelligent frontier scoring for target selection.
Uses multiple factors to evaluate and rank exploration targets.
"""

import math
from typing import Tuple, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """Configurable weights for scoring factors."""
    gain: float = 5.0       # Exploration gain weight
    distance: float = 1.0   # Distance weight
    risk: float = 10.0       # Risk penalty weight
    congestion: float = 3.0 # Congestion penalty weight
    revisit: float = 2.0     # Revisit penalty weight
    region_value: float = 6.0  # Region value (lookahead) weight


# Default weights
DEFAULT_WEIGHTS = ScoringWeights()


def score_frontier(
    drone_pos: Tuple[int, int],
    frontier_pos: Tuple[int, int],
    grid_map: Any,
    other_drone_positions: List[Tuple[int, int]],
    weights: ScoringWeights = DEFAULT_WEIGHTS
) -> float:
    """
    Calculate a score for a frontier cell based on multiple factors.
    
    Higher score = better target for exploration.
    
    Args:
        drone_pos: Current position of the drone (x, y)
        frontier_pos: Position of the frontier cell (x, y)
        grid_map: GridMap instance with visited/risk data
        other_drone_positions: List of (x, y) tuples for other drones
        weights: ScoringWeights for tuning factor importance
    
    Returns:
        Float score (higher = better target)
    """
    # 1. Distance score (closer = better, so negative distance)
    dist = math.sqrt((frontier_pos[0] - drone_pos[0])**2 + (frontier_pos[1] - drone_pos[1])**2)
    distance_score = -weights.distance * dist
    
    # 2. Exploration gain (more unvisited neighbors = better)
    gain_score = weights.gain * _calculate_exploration_gain(frontier_pos, grid_map)
    
    # 3. Risk penalty (HIGH risk = large penalty)
    risk_penalty = weights.risk * _calculate_risk_penalty(frontier_pos, grid_map)
    
    # 4. Congestion penalty (penalize if other drones are nearby)
    congestion_penalty = weights.congestion * _calculate_congestion(frontier_pos, other_drone_positions)
    
    # 5. Revisit penalty (penalize cells that have been visited multiple times)
    revisit_penalty = weights.revisit * _calculate_revisit_penalty(frontier_pos, grid_map)
    
    # 6. Region value (estimate of future exploration potential)
    region_value = weights.region_value * calculate_region_value(frontier_pos, grid_map)
    
    # Final score: sum of all factors
    total_score = gain_score + distance_score - risk_penalty - congestion_penalty - revisit_penalty + region_value
    
    return total_score


def _calculate_exploration_gain(frontier_pos: Tuple[int, int], grid_map: Any) -> float:
    """Calculate how much new territory this frontier opens up."""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    unvisited_count = 0
    
    for dx, dy in directions:
        nx, ny = frontier_pos[0] + dx, frontier_pos[1] + dy
        if 0 <= nx < grid_map.width and 0 <= ny < grid_map.height:
            if not grid_map.visited[ny][nx]:
                unvisited_count += 1
    
    return float(unvisited_count)


def _calculate_risk_penalty(frontier_pos: Tuple[int, int], grid_map: Any) -> float:
    """Calculate risk penalty for a frontier cell."""
    risk_level = grid_map.get_risk_at(frontier_pos[0], frontier_pos[1])
    
    risk_penalties = {
        'HIGH': 1.0,
        'MEDIUM': 0.5,
        'SAFE': 0.0
    }
    
    return risk_penalties.get(risk_level, 0.0)


def _calculate_congestion(frontier_pos: Tuple[int, int], other_drone_positions: List[Tuple[int, int]], radius: int = 5) -> float:
    """Calculate congestion penalty based on nearby drones."""
    if not other_drone_positions:
        return 0.0
    
    congestion_count = 0
    for other_pos in other_drone_positions:
        dist = math.sqrt((frontier_pos[0] - other_pos[0])**2 + (frontier_pos[1] - other_pos[1])**2)
        if dist <= radius:
            congestion_count += 1
    
    return float(congestion_count)


def _calculate_revisit_penalty(frontier_pos: Tuple[int, int], grid_map: Any) -> float:
    """Calculate revisit penalty based on visit count."""
    visit_count = grid_map.get_visit_count(frontier_pos[0], frontier_pos[1])
    return float(max(0, visit_count - 1))


def calculate_region_value(frontier_pos: Tuple[int, int], grid_map: Any, depth: int = 8) -> float:
    """
    Estimate the value of a region using bounded flood-fill.
    
    Args:
        frontier_pos: Starting position for exploration
        grid_map: GridMap instance
        depth: Maximum search depth for flood-fill
    
    Returns:
        Estimated value (number of reachable unvisited cells)
    """
    visited = grid_map.visited
    width = grid_map.width
    height = grid_map.height
    
    frontier_cells = set([frontier_pos])
    reachable_unvisited = set()
    queue = [frontier_pos]
    seen = set([frontier_pos])
    
    while queue and len(seen) < depth * 10:
        current = queue.pop(0)
        
        if not visited[current[1]][current[0]]:
            reachable_unvisited.add(current)
        
        if len(reachable_unvisited) >= 20:
            break
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in seen:
                    cell_risk = grid_map.get_cell(nx, ny)
                    if cell_risk < 2:
                        seen.add((nx, ny))
                        queue.append((nx, ny))
    
    return float(len(reachable_unvisited))


def score_all_frontiers(
    drone_pos: Tuple[int, int],
    frontiers: List[Tuple[int, int]],
    grid_map: Any,
    other_drone_positions: List[Tuple[int, int]],
    assigned_targets: set,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
    limit: int = 30
) -> List[Tuple[Tuple[int, int], float, Dict]]:
    """
    Score all frontiers and return sorted list of (frontier, score, details).
    
    Args:
        drone_pos: Current drone position
        frontiers: List of frontier positions
        grid_map: GridMap instance
        other_drone_positions: Positions of other drones
        assigned_targets: Set of already claimed targets
        weights: Scoring weights
        limit: Maximum frontiers to consider
    
    Returns:
        List of (frontier, score, details_dict) sorted by score descending
    """
    scored_frontiers = []
    
    # Filter out already assigned targets
    available_frontiers = [f for f in frontiers if f not in assigned_targets]
    
    # Limit to prevent computation overload
    if len(available_frontiers) > limit:
        # Sort by distance and take closest 'limit' to reduce noise
        available_frontiers = sorted(
            available_frontiers,
            key=lambda f: math.sqrt((f[0] - drone_pos[0])**2 + (f[1] - drone_pos[1])**2)
        )[:limit]
    
    for frontier in available_frontiers:
        score = score_frontier(drone_pos, frontier, grid_map, other_drone_positions, weights)
        
        # Build details dict for logging
        details = {
            'gain': _calculate_exploration_gain(frontier, grid_map),
            'distance': math.sqrt((frontier[0] - drone_pos[0])**2 + (frontier[1] - drone_pos[1])**2),
            'risk': grid_map.get_risk_at(frontier[0], frontier[1]),
            'congestion': _calculate_congestion(frontier, other_drone_positions),
            'visits': grid_map.get_visit_count(frontier[0], frontier[1]),
            'region_value': calculate_region_value(frontier, grid_map)
        }
        
        scored_frontiers.append((frontier, score, details))
    
    # Sort by score descending (highest first)
    scored_frontiers.sort(key=lambda x: x[1], reverse=True)
    
    return scored_frontiers