"""
Simulation Engine Module

Central autonomous execution loop that orchestrates the entire system.
Runs continuously every 1 second, executing the full pipeline for each drone.
"""

import threading
import time
import logging
import math
from typing import List, Tuple, Set, Optional

from drone.drone import PhysicalDrone
from data.simulator import SensorSimulator
from detection.hazard import classify_risk
from mapping.grid_map import GridMap
from mapping.frontier_cluster import cluster_frontiers, get_cluster_info
from detection.survivor import detect_survivor
from detection.duplicate import is_duplicate
from database.victim_db import VictimDB
from planning.pathfinding import a_star
from config.settings import GRID_WIDTH, GRID_HEIGHT
from ai.scoring import score_all_frontiers, ScoringWeights, DEFAULT_WEIGHTS
from reporting.performance import MetricsCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Core autonomous simulation engine.
    
    Runs the complete pipeline every tick:
    1. Move each drone based on autonomy logic
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
        self.metrics = MetricsCollector()
        
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
        self._log("ENGINE: Simulation engine started")
    
    def stop(self):
        """Stop the simulation loop."""
        self.running = False
        self._log("ENGINE: Simulation engine stopped")
    
    def _run_loop(self):
        """Main loop running every 1 second."""
        logger.info("[ENGINE] Simulation loop started")
        while self.running:
            try:
                self.run_tick()
            except Exception as e:
                logger.error(f"[ENGINE] Tick error: {e}")
            time.sleep(1.0)
    
    def run_tick(self):
        """Execute one full simulation tick - the complete pipeline."""
        self.tick_count += 1
        
        # Get positions of all drones for collision avoidance
        drone_positions = {(d.x, d.y): d.drone_id for d in self.drones}
        
        weight_grid = self.grid_map.get_weight_grid_with_visited_penalty(visit_penalty=3)
        
        for drone in self.drones:
            self._process_drone(drone, weight_grid, drone_positions)
        
        # Update performance metrics once per tick
        visited = self.grid_map.get_visited_count()
        total = self.grid_map.width * self.grid_map.height
        avg_path = sum(len(d.path) for d in self.drones if d.path) / max(1, len([d for d in self.drones if d.path]))
        self.metrics.update(visited, total, int(avg_path))
        
        logger.info(f"[ENGINE] Tick {self.tick_count} complete")
    
    def _process_drone(self, drone: PhysicalDrone, weight_grid: List[List[int]], drone_positions: dict):
        """Process a single drone through the full pipeline."""
        
        # Track if drone had a target before movement
        old_target = None
        if drone.path and len(drone.path) > 1:
            old_target = drone.path[-1]
        
        # Ensure drone has valid target if in SCANNING state
        if drone.state == 'SCANNING' and not drone.path:
            DroneAutonomy.assign_new_target(drone, self.grid_map, other_drones=self.drones)
        
        # 1. Move drone (autonomous logic handles state)
        old_pos = (drone.x, drone.y)
        
        # Check for collision - if next position is occupied, try to adjust
        proposed_pos = self._get_proposed_position(drone, weight_grid, drone_positions)
        if proposed_pos:
            drone.x, drone.y = proposed_pos
        
        new_pos = (drone.x, drone.y)
        
        # Update drone positions for collision detection
        if old_pos != new_pos and old_pos in drone_positions:
            del drone_positions[old_pos]
        if new_pos not in drone_positions:
            drone_positions[new_pos] = drone.drone_id
        
        # Log movement
        if old_pos != new_pos:
            self._log(f"DRONE-{drone.drone_id}: Moved {old_pos} -> {new_pos} [{drone.state}]")
        
        # If drone arrived at target, assign new one and release old target
        if drone.state == 'SCANNING' and not drone.path:
            if old_target:
                DroneAutonomy.release_target(old_target)
            DroneAutonomy.assign_new_target(drone, self.grid_map, other_drones=self.drones)
        
        # 2. Generate sensor data
        sensor_data = self.simulator.read_sensor_data(drone)
        
        # 3. Classify hazard
        risk_level = classify_risk(sensor_data['temp'], sensor_data['gas'])
        
        # 4. Update grid with risk level and mark as visited
        self.grid_map.update_cell(sensor_data['x'], sensor_data['y'], risk_level)
        
        if risk_level != 'SAFE':
            self._log(f"DRONE-{drone.drone_id}: Hazard detected at {new_pos} [{risk_level}]")
        
        # 5. Detect survivor
        potential_survivor = detect_survivor(sensor_data['x'], sensor_data['y'], risk_level)
        
        # 6. Filter duplicates
        if potential_survivor:
            if not is_duplicate(potential_survivor, self.victim_db):
                # 7. Store survivor
                self.victim_db.add_survivor(potential_survivor)
                self._log(f"DRONE-{drone.drone_id}: SURVIVOR FOUND at {new_pos} [ID: {potential_survivor['id']}]")
            else:
                self._log(f"DRONE-{drone.drone_id}: Duplicate survivor at {new_pos} - filtered")
    
    def _get_proposed_position(self, drone: PhysicalDrone, weight_grid: List[List[int]], drone_positions: dict) -> Tuple[int, int]:
        """Get the next position for a drone, checking for collisions."""
        
        # Save old position
        old_x, old_y = drone.x, drone.y
        
        # Let drone decide move via act()
        drone.act(weight_grid)
        
        new_x, new_y = drone.x, drone.y
        new_pos = (new_x, new_y)
        
        # Check if new position collides with another drone
        if new_pos in drone_positions and drone_positions[new_pos] != drone.drone_id:
            # Collision detected - restore old position and find alternate
            drone.x, drone.y = old_x, old_y
            new_pos = None
            
            # Try alternate moves (in order of preference)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                alt_pos = (max(0, min(49, old_x + dx)), max(0, min(49, old_y + dy)))
                if alt_pos not in drone_positions:
                    # Check if this position is safe (not HIGH risk)
                    if weight_grid[alt_pos[1]][alt_pos[0]] < 1000:
                        drone.x, drone.y = alt_pos
                        return alt_pos
            
            # No safe alternate - stay in place
            return old_x, old_y
        
        return new_pos
    
    def _log(self, message: str):
        """Log message to logger and optional callback."""
        logger.info(message)
        if self.log_callback:
            self.log_callback(message)
    
    def reset(self):
        """Reset engine state for new mission."""
        self.tick_count = 0
        DroneAutonomy.reset()
        self._log("ENGINE: Engine reset for new mission")


class DroneAutonomy:
    """
    Handles autonomous drone behavior - movement strategy and target assignment.
    Uses frontier-based exploration with multi-drone coordination.
    """
    
    # Shared state for multi-drone coordination
    _assigned_targets = set()
    _lock = None
    
    @staticmethod
    def initialize():
        """Initialize shared coordination state."""
        DroneAutonomy._assigned_targets = set()
    
    @staticmethod
    def reset():
        """Reset coordination state."""
        DroneAutonomy._assigned_targets = set()
    
    @staticmethod
    def claim_target(target: Tuple[int, int]) -> bool:
        """
        Try to claim a target. Returns True if successful.
        
        Args:
            target: (x, y) coordinate
            
        Returns:
            True if target was claimed, False if already taken
        """
        if target in DroneAutonomy._assigned_targets:
            return False
        DroneAutonomy._assigned_targets.add(target)
        return True
    
    @staticmethod
    def release_target(target: Tuple[int, int]):
        """Release a target when drone is done."""
        if target in DroneAutonomy._assigned_targets:
            DroneAutonomy._assigned_targets.discard(target)
    
    @staticmethod
    def assign_new_target(drone: PhysicalDrone, grid_map: GridMap, exclude_taken: bool = True, other_drones = None):
        """
        Assign a new target using AI-style scoring system with clustering.
        Evaluates clustered frontiers and selects the highest-scored one.
        
        Args:
            drone: The drone to assign target to
            grid_map: GridMap for frontier information
            exclude_taken: If True, exclude already claimed targets
            other_drones: List of other drone objects for congestion calculation
        """
        # First check: if drone already has a valid path, don't reassign
        if drone.path and len(drone.path) > 1:
            return
        
        # Get more raw frontiers and then cluster them
        raw_frontiers = grid_map.get_frontiers(limit=100)
        
        # Cluster frontiers to reduce decision space (radius=5, max=15 clusters)
        if len(raw_frontiers) > 15:
            targets = cluster_frontiers(raw_frontiers, radius=5, max_clusters=15)
        else:
            targets = raw_frontiers
        
        # If no frontiers yet (early exploration), use different initial targets per drone
        if not targets:
            target = DroneAutonomy._get_initial_target(drone.drone_id, grid_map, exclude_taken)
        else:
            # Get positions of other drones for congestion calculation
            other_positions = []
            if other_drones:
                for other in other_drones:
                    if other.drone_id != drone.drone_id:
                        other_positions.append((other.x, other.y))
            
            # Score clustered frontiers and select the best one
            scored = score_all_frontiers(
                drone_pos=(drone.x, drone.y),
                frontiers=targets,
                grid_map=grid_map,
                other_drone_positions=other_positions,
                assigned_targets=DroneAutonomy._assigned_targets if exclude_taken else set(),
                weights=DEFAULT_WEIGHTS,
                limit=15
            )
            
            if scored:
                target = scored[0][0]  # Get highest scored cluster
                
                # Log top 3 for debugging
                top3 = scored[:3]
                logger.info(f"DRONE-{drone.drone_id}: Top scores: {[(f[0], round(f[1],1)) for f in top3]}")
                
                if exclude_taken:
                    DroneAutonomy.claim_target(target)
            else:
                # Fallback if no available targets
                target = DroneAutonomy._get_initial_target(drone.drone_id, grid_map, exclude_taken)
        
        # Calculate path to target
        weight_grid = grid_map.get_weight_grid_with_visited_penalty(visit_penalty=3)
        path = a_star(weight_grid, (drone.x, drone.y), target)
        
        if path:
            drone.path = path
            logger.info(f"DRONE-{drone.drone_id}: Assigned target {target}, path length {len(path)}")
        else:
            logger.warning(f"DRONE-{drone.drone_id}: No path found to {target}")
    
    @staticmethod
    def _get_initial_target(drone_id: int, grid_map: GridMap, exclude_taken: bool) -> Tuple[int, int]:
        """Get initial target for early exploration when no frontiers exist."""
        targets = {
            1: (10, 10),
            2: (40, 10),
            3: (10, 40),
            4: (40, 40)
        }
        target = targets.get(drone_id, (25, 25))
        
        if exclude_taken and target in DroneAutonomy._assigned_targets:
            unvisited = grid_map.get_unvisited_cells()
            if unvisited:
                import math
                target = min(
                    unvisited,
                    key=lambda c: math.sqrt((c[0] - 25)**2 + (c[1] - 25)**2)
                )
        
        return target
    
    @staticmethod
    def _log(message: str):
        logger.info(message)