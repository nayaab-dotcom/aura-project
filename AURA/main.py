"""
AURA - Autonomous Unified Rescue and Assessment System

Main orchestrator that connects all modules and runs the simulation loop.
"""

import sys
import os
import time
import threading
from typing import List, Dict, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config.settings import (
    SIMULATION_INTERVAL, DRONE_COUNT,
    BASE_STATION_X, BASE_STATION_Y
)
from data.simulator import SensorSimulator
from detection.hazard import classify_risk
from detection.survivor import detect_survivor
from detection.duplicate import is_duplicate
from database.victim_db import VictimDB
from mapping.grid_map import GridMap
from planning.pathfinding import a_star


class PhysicalDrone:
    """Represents a single drone in the system."""
    
    def __init__(self, drone_id: int, x: int = 0, y: int = 0):
        self.drone_id = drone_id
        self.x = x
        self.y = y
        self.battery = 100.0
        self.state = 'IDLE'
        self.path: List[tuple] = []
        self.target: Optional[tuple] = None
    
    def move_toward(self, target_x: int, target_y: int) -> None:
        """Move one step toward target coordinates."""
        dx = 1 if target_x > self.x else -1 if target_x < self.x else 0
        dy = 1 if target_y > self.y else -1 if target_y < self.y else 0
        self.x += dx
        self.y += dy
    
    def follow_path(self) -> bool:
        """Follow assigned path, return True if reached end."""
        if not self.path:
            return True
        
        self.move_toward(self.path[0][0], self.path[0][1])
        
        if self.x == self.path[0][0] and self.y == self.path[0][1]:
            self.path.pop(0)
        
        return len(self.path) == 0
    
    def get_state(self) -> Dict:
        """Get drone state for API."""
        return {
            'id': self.drone_id,
            'x': self.x,
            'y': self.y,
            'battery': round(self.battery, 1),
            'state': self.state,
            'path_length': len(self.path)
        }


class AURASystem:
    """
    Main AURA system orchestrator.
    
    Manages drones, sensors, hazard detection, survivor tracking,
    and pathfinding for autonomous disaster response.
    """
    
    def __init__(self):
        """Initialize the AURA system."""
        self.simulator = SensorSimulator()
        self.grid_map = GridMap()
        self.victim_db = VictimDB()
        
        self.drones: List[PhysicalDrone] = [
            PhysicalDrone(i + 1, BASE_STATION_X, BASE_STATION_Y)
            for i in range(DRONE_COUNT)
        ]
        
        self.system_logs: List[Dict] = []
        self.running = False
        self.mission_start_time = time.time()
        self.tick_count = 0
    
    def start(self) -> None:
        """Start the AURA system."""
        self.running = True
        self.mission_start_time = time.time()
        self._log("SYSTEM ONLINE: AURA Mission Started")
        
        while self.running:
            self._simulation_tick()
            time.sleep(SIMULATION_INTERVAL)
    
    def stop(self) -> None:
        """Stop the AURA system."""
        self.running = False
        self._log("SYSTEM OFFLINE: AURA Mission Ended")
    
    def _simulation_tick(self) -> None:
        """Execute one simulation tick for all drones."""
        self.tick_count += 1
        
        weight_grid = self.grid_map.get_weight_grid()
        
        for drone in self.drones:
            self._process_drone(drone, weight_grid)
    
    def _process_drone(self, drone: PhysicalDrone, weight_grid: List[List[int]]) -> None:
        """Process sensor data and detection for one drone."""
        sensor_data = self.simulator.read_sensor_data(drone)
        
        risk_level = classify_risk(sensor_data['temp'], sensor_data['gas'])
        
        self.grid_map.update_cell(drone.x, drone.y, risk_level)
        
        potential_survivor = detect_survivor(drone.x, drone.y, risk_level)
        
        if potential_survivor and not is_duplicate(potential_survivor, self.victim_db):
            self.victim_db.add_survivor(potential_survivor)
            self._log(f"AURA-{drone.drone_id}: Survivor Detected at [{drone.x}, {drone.y}]")
        
        drone.battery = max(0, drone.battery - 0.5)
        
        if drone.battery <= 10 and drone.state != 'RETURNING':
            drone.state = 'RETURNING'
            self._recall_drone(drone, weight_grid)
    
    def _recall_drone(self, drone: PhysicalDrone, weight_grid: List[List[int]]) -> None:
        """Recall drone to base station."""
        path = a_star(weight_grid, (drone.x, drone.y), (BASE_STATION_X, BASE_STATION_Y))
        if path:
            drone.path = path
            drone.state = 'RETURNING'
            self._log(f"COMMAND: AURA-{drone.drone_id} recalled to base (low battery)")
    
    def scan_drone(self, drone_id: int) -> bool:
        """Send drone to scan random location."""
        import random
        drone = self._get_drone(drone_id)
        if not drone:
            return False
        
        goal = (random.randint(0, 49), random.randint(0, 49))
        weight_grid = self.grid_map.get_weight_grid()
        path = a_star(weight_grid, (drone.x, drone.y), goal)
        
        if path:
            drone.path = path
            drone.state = 'SCANNING'
            self._log(f"COMMAND: AURA-{drone_id} scanning toward {goal}")
            return True
        return False
    
    def recall_drone(self, drone_id: int) -> bool:
        """Recall specific drone to base."""
        drone = self._get_drone(drone_id)
        if not drone:
            return False
        
        weight_grid = self.grid_map.get_weight_grid()
        path = a_star(weight_grid, (drone.x, drone.y), (BASE_STATION_X, BASE_STATION_Y))
        
        if path:
            drone.path = path
            drone.state = 'RETURNING'
            self._log(f"COMMAND: AURA-{drone_id} recalled to base")
            return True
        return False
    
    def _get_drone(self, drone_id: int) -> Optional[PhysicalDrone]:
        """Get drone by ID."""
        for drone in self.drones:
            if drone.drone_id == drone_id:
                return drone
        return None
    
    def _log(self, message: str) -> None:
        """Add log entry."""
        self.system_logs.append({
            'timestamp': time.time(),
            'message': message
        })
        if len(self.system_logs) > 100:
            self.system_logs.pop(0)
    
    def get_state(self) -> Dict:
        """Get complete system state for dashboard."""
        return {
            'mission_id': f"MISSION-{self.tick_count:06d}",
            'duration': time.time() - self.mission_start_time,
            'tick': self.tick_count,
            'grid': self.grid_map.get_grid_state(),
            'drones': [d.get_state() for d in self.drones],
            'survivors': self.victim_db.get_all(),
            'logs': self.system_logs[-20:],
            'stats': {
                'survivors_found': self.victim_db.get_count(),
                'coverage_percent': round(self.grid_map.get_coverage_percent(), 2),
                'high_risk_cells': self.grid_map.get_high_risk_count(),
                'medium_risk_cells': self.grid_map.get_medium_risk_count(),
                'safe_cells': self.grid_map.get_safe_count(),
                'total_cells': self.grid_map.width * self.grid_map.height
            }
        }
    
    def reset(self) -> None:
        """Reset system for new mission."""
        self.grid_map.reset()
        self.victim_db.reset()
        self.simulator.reset_hotspots()
        
        self.drones = [
            PhysicalDrone(i + 1, BASE_STATION_X, BASE_STATION_Y)
            for i in range(DRONE_COUNT)
        ]
        
        self.system_logs = []
        self.mission_start_time = time.time()
        self.tick_count = 0
        
        self._log("SYSTEM RESET: New mission initialized")


def main():
    """Main entry point."""
    print("=" * 50)
    print("AURA - Autonomous Unified Rescue System")
    print("=" * 50)
    
    system = AURASystem()
    
    try:
        print("\nStarting simulation...")
        print("Press Ctrl+C to stop\n")
        system.start()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        system.stop()
        print("System stopped.")


if __name__ == '__main__':
    main()
