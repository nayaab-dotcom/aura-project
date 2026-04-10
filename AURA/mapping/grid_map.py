"""
Grid Map Module - 50x50 grid representing disaster environment.
Each cell stores risk level and tracks drone coverage.
"""

from typing import List, Tuple
from config import GRID_WIDTH, GRID_HEIGHT, COST_SAFE, COST_MEDIUM, COST_HIGH


class GridMap:
    """
    2D grid map with risk levels and coverage tracking.
    Cell values: 0=SAFE, 1=MEDIUM, 2=HIGH
    """
    
    CELL_SAFE = 0
    CELL_MEDIUM = 1
    CELL_HIGH = 2
    
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.grid = [[self.CELL_SAFE for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]
        self.visit_count = [[0 for _ in range(width)] for _ in range(height)]
        self.timestamps = [[0.0 for _ in range(width)] for _ in range(height)]
    
    def update_cell(self, x: int, y: int, risk_level: str, timestamp: float = 0) -> None:
        """Update cell risk level and mark as visited."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        self.visited[y][x] = True
        self.visit_count[y][x] += 1
        if timestamp:
            self.timestamps[y][x] = timestamp
        
        if risk_level == 'HIGH':
            self.grid[y][x] = self.CELL_HIGH
        elif risk_level == 'MEDIUM':
            self.grid[y][x] = max(self.grid[y][x], self.CELL_MEDIUM)
    
    def get_cell(self, x: int, y: int) -> int:
        """Get cell risk level at coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return self.CELL_HIGH
    
    def get_risk_at(self, x: int, y: int) -> str:
        """Get risk level as string at coordinates."""
        cell = self.get_cell(x, y)
        mapping = {self.CELL_SAFE: 'SAFE', self.CELL_MEDIUM: 'MEDIUM', self.CELL_HIGH: 'HIGH'}
        return mapping.get(cell, 'SAFE')
    
    def get_weight_grid(self) -> List[List[int]]:
        """Convert grid to A* pathfinding cost grid."""
        weight_grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell == self.CELL_HIGH:
                    cost = COST_HIGH
                elif cell == self.CELL_MEDIUM:
                    cost = COST_MEDIUM
                else:
                    cost = COST_SAFE
                row.append(cost)
            weight_grid.append(row)
        return weight_grid
    
    def get_grid_state(self) -> List[List[int]]:
        """Return raw grid state for API serialization."""
        return self.grid
    
    def get_grid_full(self) -> dict:
        """Return full grid state with metadata."""
        cells = []
        for y in range(self.height):
            for x in range(self.width):
                cells.append({
                    'x': x,
                    'y': y,
                    'risk': self._cell_to_risk(self.grid[y][x]),
                    'visited': self.visited[y][x],
                    'timestamp': self.timestamps[y][x]
                })
        return {'cells': cells, 'width': self.width, 'height': self.height}
    
    def _cell_to_risk(self, cell_value: int) -> str:
        mapping = {self.CELL_SAFE: 'SAFE', self.CELL_MEDIUM: 'MEDIUM', self.CELL_HIGH: 'HIGH'}
        return mapping.get(cell_value, 'SAFE')
    
    def is_visited(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.visited[y][x]
        return False
    
    def get_visited_count(self) -> int:
        return sum(sum(row) for row in self.visited)
    
    def get_coverage_percent(self) -> float:
        total = self.width * self.height
        visited = self.get_visited_count()
        return (visited / total) * 100 if total > 0 else 0
    
    def get_high_risk_count(self) -> int:
        return sum(row.count(self.CELL_HIGH) for row in self.grid)
    
    def get_medium_risk_count(self) -> int:
        return sum(row.count(self.CELL_MEDIUM) for row in self.grid)
    
    def get_safe_count(self) -> int:
        return sum(row.count(self.CELL_SAFE) for row in self.grid)
    
    def get_unvisited_cells(self) -> List[Tuple[int, int]]:
        unvisited = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.visited[y][x]:
                    unvisited.append((x, y))
        return unvisited
    
    def reset(self) -> None:
        self.grid = [[self.CELL_SAFE for _ in range(self.width)] for _ in range(self.height)]
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.visit_count = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.timestamps = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
