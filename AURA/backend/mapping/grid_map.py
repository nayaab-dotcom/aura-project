"""
Grid Map Module

Represents the disaster environment as a 50x50 grid.
Each cell stores risk level and tracks drone coverage.
"""

from typing import List, Tuple, Optional, Set

from config.settings import GRID_WIDTH, GRID_HEIGHT, COST_SAFE, COST_MEDIUM, COST_HIGH


class GridMap:
    """
    2D grid map with risk levels and coverage tracking.
    
    Cell values:
    - 0: SAFE
    - 1: MEDIUM risk
    - 2: HIGH risk
    """
    
    CELL_SAFE = 0
    CELL_MEDIUM = 1
    CELL_HIGH = 2
    
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        """
        Initialize grid map with dimensions.
        
        Args:
            width: Grid width (default from config)
            height: Grid height (default from config)
        """
        self.width = width
        self.height = height
        self.grid = [[self.CELL_SAFE for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]
        self.visit_count = [[0 for _ in range(width)] for _ in range(height)]
        self._frontier_cache = []
        self._frontier_dirty = True
    
    def update_cell(self, x: int, y: int, risk_level: str) -> None:
        """
        Update cell risk level and mark as visited.
        
        Args:
            x: X coordinate
            y: Y coordinate
            risk_level: Risk classification ('SAFE', 'MEDIUM', 'HIGH')
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        self.visited[y][x] = True
        self.visit_count[y][x] += 1
        self._frontier_dirty = True
        
        if risk_level == 'HIGH':
            self.grid[y][x] = self.CELL_HIGH
        elif risk_level == 'MEDIUM':
            self.grid[y][x] = max(self.grid[y][x], self.CELL_MEDIUM)
    
    def get_cell(self, x: int, y: int) -> int:
        """
        Get cell risk level at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Cell value (0=SAFE, 1=MEDIUM, 2=HIGH)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return self.CELL_HIGH
    
    def get_risk_at(self, x: int, y: int) -> str:
        """
        Get risk level as string at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Risk level string.
        """
        cell = self.get_cell(x, y)
        return self._cell_to_risk(cell)
    
    def _cell_to_risk(self, cell_value: int) -> str:
        """Convert cell integer to risk string."""
        mapping = {
            self.CELL_SAFE: 'SAFE',
            self.CELL_MEDIUM: 'MEDIUM',
            self.CELL_HIGH: 'HIGH'
        }
        return mapping.get(cell_value, 'SAFE')
    
    def get_weight_grid(self) -> List[List[int]]:
        """
        Convert grid to A* pathfinding cost grid.
        
        Returns:
            2D array of costs for each cell.
        """
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
    
    def get_weight_grid_with_visited_penalty(self, visit_penalty: int = 5) -> List[List[int]]:
        """
        Get weight grid with penalty for visited cells to encourage exploration.
        
        Args:
            visit_penalty: Additional cost per visit (higher = more exploration)
        
        Returns:
            2D array of costs with visited penalties.
        """
        weight_grid = self.get_weight_grid()
        for y in range(self.height):
            for x in range(self.width):
                if self.visited[y][x]:
                    visits = self.visit_count[y][x]
                    weight_grid[y][x] += visit_penalty * visits
        return weight_grid
    
    def get_grid_state(self) -> List[List[int]]:
        """
        Return raw grid state for API serialization.
        
        Returns:
            2D array of cell values.
        """
        return self.grid
    
    def is_visited(self, x: int, y: int) -> bool:
        """Check if cell has been visited by a drone."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.visited[y][x]
        return False
    
    def get_visited_count(self) -> int:
        """Count total visited cells."""
        return sum(sum(row) for row in self.visited)
    
    def get_coverage_percent(self) -> float:
        """Get percentage of grid covered by drones."""
        total_cells = self.width * self.height
        visited = self.get_visited_count()
        return (visited / total_cells) * 100 if total_cells > 0 else 0
    
    def get_risk_counts(self) -> dict:
        """Get count of cells in each risk category."""
        counts = {'SAFE': 0, 'MEDIUM': 0, 'HIGH': 0}
        for row in self.grid:
            for cell in row:
                risk = self._cell_to_risk(cell)
                counts[risk] += 1
        return counts
    
    def get_high_risk_count(self) -> int:
        """Count HIGH risk cells."""
        return sum(row.count(self.CELL_HIGH) for row in self.grid)
    
    def get_medium_risk_count(self) -> int:
        """Count MEDIUM risk cells."""
        return sum(row.count(self.CELL_MEDIUM) for row in self.grid)
    
    def get_safe_count(self) -> int:
        """Count SAFE cells."""
        return sum(row.count(self.CELL_SAFE) for row in self.grid)
    
    def get_unvisited_cells(self) -> List[Tuple[int, int]]:
        """Get list of all unvisited cell coordinates."""
        unvisited = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.visited[y][x]:
                    unvisited.append((x, y))
        return unvisited
    
    def get_frontiers(self, limit: int = 0) -> List[Tuple[int, int]]:
        """
        Get frontier cells - visited cells adjacent to unvisited cells.
        
        Args:
            limit: If > 0, return only closest 'limit' frontiers sorted by distance from origin.
                   If 0, return all frontiers.
        
        Returns:
            List of frontier coordinates.
        """
        if not self._frontier_dirty:
            return self._frontier_cache
        
        frontiers = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for y in range(self.height):
            for x in range(self.width):
                if not self.visited[y][x]:
                    continue
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if not self.visited[ny][nx]:
                            if (x, y) not in frontiers:
                                frontiers.append((x, y))
                            break
        
        self._frontier_cache = frontiers
        self._frontier_dirty = False
        
        # If limit is set, return closest 'limit' frontiers
        if limit > 0 and len(frontiers) > limit:
            import math
            # Sort by distance from center of map for variety
            center_x, center_y = self.width / 2, self.height / 2
            frontiers = sorted(
                frontiers,
                key=lambda f: math.sqrt((f[0] - center_x)**2 + (f[1] - center_y)**2)
            )[:limit]
        
        return frontiers
    
    def get_visit_count(self, x: int, y: int) -> int:
        """Get number of times a cell has been visited."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.visit_count[y][x]
        return 0
    
    def reset(self) -> None:
        """Clear grid and visited data for new mission."""
        self.grid = [[self.CELL_SAFE for _ in range(self.width)] for _ in range(self.height)]
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.visit_count = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self._frontier_dirty = True
