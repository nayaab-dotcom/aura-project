"""
Drone Module - Represents autonomous drones in the AURA system.
"""

import random
from typing import List, Tuple, Optional
from planning.pathfinding import a_star
from config import BASE_STATION_X, BASE_STATION_Y, COST_HIGH


class PhysicalDrone:
    """Represents a single drone in the system."""
    
    def __init__(self, drone_id: int, start_x: int = 0, start_y: int = 0):
        self.drone_id = drone_id
        self.x = start_x
        self.y = start_y
        self.battery = 100.0
        self.state = 'IDLE'
        self.mode = 'AUTO'
        self.manual_target: Optional[Tuple[int, int]] = None
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
    
    def move_toward(self, target_x: int, target_y: int) -> None:
        """Move one step toward target coordinates."""
        dx = 1 if target_x > self.x else -1 if target_x < self.x else 0
        dy = 1 if target_y > self.y else -1 if target_y < self.y else 0
        self.x += dx
        self.y += dy
    
    def follow_path(self) -> bool:
        """Follow assigned path, return True if reached end."""
        if not self.path or self.path_index >= len(self.path):
            return True
        
        target = self.path[self.path_index]
        self.move_toward(target[0], target[1])
        
        if self.x == target[0] and self.y == target[1]:
            self.path_index += 1
        
        return self.path_index >= len(self.path)
    
    def act(self, weight_grid: List[List[int]]) -> None:
        """Process one tick of drone behavior."""
        if self.mode == 'MANUAL' and self.manual_target:
            self._move_manual()
        elif self.state == 'RETURNING':
            self._handle_returning(weight_grid)
        elif self.state == 'SCANNING':
            self._handle_scanning(weight_grid)
        
        self._update_battery()
        self._check_safety(weight_grid)
    
    def _move_manual(self) -> None:
        """Moves drone one step toward manual target."""
        if not self.manual_target:
            return
        tx, ty = self.manual_target
        self.move_toward(tx, ty)
        if self.x == tx and self.y == ty:
            self.manual_target = None
    
    def _handle_returning(self, weight_grid: List[List[int]]) -> None:
        """Handle RETURNING state."""
        if self.follow_path():
            if self.x == BASE_STATION_X and self.y == BASE_STATION_Y:
                self.state = 'IDLE'
                self.battery = 100.0
                self.path = []
                self.path_index = 0
    
    def _handle_scanning(self, weight_grid: List[List[int]]) -> None:
        """Handle SCANNING state."""
        if self.follow_path():
            self.path = []
            self.path_index = 0
            self._assign_new_target(weight_grid)
    
    def _assign_new_target(self, weight_grid: List[List[int]]) -> None:
        """Assign a new random target for scanning."""
        goal = (random.randint(0, 49), random.randint(0, 49))
        path = a_star(weight_grid, (self.x, self.y), goal)
        if path:
            self.path = path
            self.path_index = 0
            self.state = 'SCANNING'
    
    def _update_battery(self) -> None:
        """Drain battery."""
        self.battery = max(0, self.battery - 0.5)
    
    def _check_safety(self, weight_grid: List[List[int]]) -> None:
        """Hard safety recall if battery critically low."""
        if self.battery <= 20 and self.state != 'RETURNING':
            self.state = 'RETURNING'
            self.mode = 'AUTO'
            path = a_star(weight_grid, (self.x, self.y), (BASE_STATION_X, BASE_STATION_Y))
            if path:
                self.path = path
                self.path_index = 0
    
    def recall(self, weight_grid: List[List[int]]) -> bool:
        """Recall drone to base station."""
        path = a_star(weight_grid, (self.x, self.y), (BASE_STATION_X, BASE_STATION_Y))
        if path:
            self.path = path
            self.path_index = 0
            self.state = 'RETURNING'
            return True
        return False
    
    def scan(self, weight_grid: List[List[int]]) -> bool:
        """Send drone to scan random location."""
        goal = (random.randint(0, 49), random.randint(0, 49))
        path = a_star(weight_grid, (self.x, self.y), goal)
        if path:
            self.path = path
            self.path_index = 0
            self.state = 'SCANNING'
            return True
        return False
    
    def get_state(self) -> dict:
        """Returns physical state for API."""
        return {
            'id': self.drone_id,
            'x': self.x,
            'y': self.y,
            'battery': round(self.battery, 1),
            'state': self.state,
            'mode': self.mode,
            'path_length': len(self.path) - self.path_index if self.path else 0
        }
