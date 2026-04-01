from planning.pathfinding import a_star
import random

_drones = []

def register_drone(drone):
    _drones.append(drone)

def get_all_drones():
    return _drones

class PhysicalDrone:
    def __init__(self, drone_id, start_x=0, start_y=0):
        self.drone_id = drone_id
        self.x = start_x
        self.y = start_y
        self.battery = 100.0
        self.state = 'IDLE' # IDLE, SCANNING, RETURNING
        self.mode = 'AUTO' # AUTO, ASSISTED, MANUAL
        self.manual_target = None
        self.assigned_zone = None # (x1, y1, x2, y2)
        self.path = []
        register_drone(self)
        
    def move(self):
        """Basic movement logic - move randomly by 1 step in x or y, stay within grid bounds (0-49)."""
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        
        self.x = max(0, min(49, self.x + dx))
        self.y = max(0, min(49, self.y + dy))
        
    def act(self, weight_grid):
        """Advances the drone 1 tick along its assigned path or manual target."""
        # 1. Manual Override takes absolute priority
        if self.mode == 'MANUAL' and self.manual_target:
            self._move_manual()
        
        # 2. Returning handles simple base-directed movement
        elif self.state == 'RETURNING':
            tx, ty = 0, 0
            dx = 1 if tx > self.x else -1 if tx < self.x else 0
            dy = 1 if ty > self.y else -1 if ty < self.y else 0
            self.x += dx
            self.y += dy
            if self.x == tx and self.y == ty:
                self.state = 'IDLE'
                self.path = []
        
        # 3. Scanning handles path-based movement
        elif self.state == 'SCANNING':
            if self.path and len(self.path) > 1:
                # Dynamic replan if the next cell just became hazardous
                next_pos = self.path[1]
                if weight_grid[next_pos[1]][next_pos[0]] >= 1000:
                    self.path = [] # Force replan next tick
                    return
                
                self.path.pop(0)
                if self.path:
                    target = self.path[0]
                    self.x, self.y = target[0], target[1]
            else:
                self._handle_path_completion()
        
        # 3. Always consume battery and check safety
        self._update_battery()
        self._check_safety(weight_grid)

    def _move_manual(self):
        """Moves the drone 1 step toward its manual target."""
        tx, ty = self.manual_target
        dx = 1 if tx > self.x else -1 if tx < self.x else 0
        dy = 1 if ty > self.y else -1 if ty < self.y else 0
        
        self.x += dx
        self.y += dy
        
        if self.x == tx and self.y == ty:
            self.manual_target = None # Arrived

    def _handle_path_completion(self):
        if self.state == 'RETURNING':
            self.state = 'IDLE'
            self.path = []
        elif self.state == 'SCANNING' and self.path:
            target = self.path[0]
            self.x, self.y = target[0], target[1]
            self.path = []

    def _update_battery(self):
        self.battery -= 0.5 # Drain per tick
        if self.battery < 0: self.battery = 0

    def _check_safety(self, weight_grid):
        """Hard safety recall if battery critically low."""
        if self.battery <= 20 and self.state != 'RETURNING':
            self.state = 'RETURNING'
            self.mode = 'AUTO' # Safety forces override of Manual if critical
            path = a_star(weight_grid, (self.x, self.y), (0, 0))
            if path:
                self.path = path

    def get_state(self):
        """Returns physical state for API."""
        return {
            'id': self.drone_id,
            'x': self.x,
            'y': self.y,
            'battery': round(self.battery, 1),
            'state': self.state,
            'mode': self.mode,
            'assigned_zone': self.assigned_zone,
            'path_length': len(self.path)
        }
