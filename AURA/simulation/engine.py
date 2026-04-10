"""
Simulation Engine - Central autonomous execution loop.
Runs continuously every 1 second, executing the full pipeline for each drone.
"""

import threading
import time
from typing import List
from detection.hazard import classify_risk
from detection.survivor import detect_survivor
from detection.duplicate import is_duplicate
from mapping.grid_map import GridMap
from database.victim_db import VictimDB
from data.simulator import SensorSimulator
from planning.pathfinding import a_star
from simulation.drone import PhysicalDrone


class SimulationEngine:
    """
    Core autonomous simulation engine.
    Runs the complete pipeline every tick:
    1. Move each drone
    2. Generate sensor data
    3. Classify hazard
    4. Update grid
    5. Detect survivor
    6. Filter duplicates
    7. Store survivor
    8. Update logs
    """
    
    def __init__(
        self,
        drones: List[PhysicalDrone],
        grid_map: GridMap,
        victim_db: VictimDB,
        simulator: SensorSimulator,
        log_callback=None
    ):
        self.drones = drones
        self.grid_map = grid_map
        self.victim_db = victim_db
        self.simulator = simulator
        self.log_callback = log_callback
        self.running = False
        self.thread = None
        self.tick_count = 0
    
    def start(self):
        """Start the autonomous simulation loop."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self._log("ENGINE: Simulation started")
    
    def stop(self):
        """Stop the simulation loop."""
        self.running = False
        self._log("ENGINE: Simulation stopped")
    
    def _run_loop(self):
        """Main loop running every 1 second."""
        while self.running:
            try:
                self.run_tick()
            except Exception as e:
                print(f"[ENGINE] Tick error: {e}")
            time.sleep(1.0)
    
    def run_tick(self):
        """Execute one full simulation tick."""
        self.tick_count += 1
        weight_grid = self.grid_map.get_weight_grid()
        
        for drone in self.drones:
            self._process_drone(drone, weight_grid)
    
    def _process_drone(self, drone: PhysicalDrone, weight_grid: List[List[int]]):
        """Process a single drone through the full pipeline."""
        old_pos = (drone.x, drone.y)
        
        if drone.state == 'SCANNING' and not drone.path:
            drone.scan(weight_grid)
        
        drone.act(weight_grid)
        new_pos = (drone.x, drone.y)
        
        if old_pos != new_pos:
            self._log(f"DRONE-{drone.drone_id}: {old_pos} -> {new_pos} [{drone.state}]")
        
        sensor_data = self.simulator.read_sensor_data(drone)
        risk_level = classify_risk(sensor_data['temp'], sensor_data['gas'])
        self.grid_map.update_cell(sensor_data['x'], sensor_data['y'], risk_level, sensor_data['timestamp'])
        
        if risk_level != 'SAFE':
            self._log(f"DRONE-{drone.drone_id}: Hazard at {new_pos} [{risk_level}]")
        
        potential_survivor = detect_survivor(sensor_data['x'], sensor_data['y'], risk_level)
        
        if potential_survivor:
            if not is_duplicate(potential_survivor, self.victim_db):
                self.victim_db.add_survivor(potential_survivor)
                self._log(f"DRONE-{drone.drone_id}: SURVIVOR FOUND at {new_pos} [{potential_survivor['id']}]")
    
    def _log(self, message: str):
        """Log message to callback."""
        if self.log_callback:
            self.log_callback(message)
    
    def reset(self):
        """Reset engine state."""
        self.tick_count = 0
        self._log("ENGINE: Reset complete")
