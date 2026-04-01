"""
Sensor Simulator Module

Generates realistic synthetic sensor data for drone simulation.
Simulates temperature and gas readings based on proximity to fire hotspots.
"""

import random
import time
from typing import List, Dict
from config.settings import (
    GRID_WIDTH, GRID_HEIGHT,
    BASE_TEMP, BASE_GAS,
    TEMP_VARIANCE, GAS_VARIANCE,
    FIRE_HOTSPOT_RADIUS,
    FIRE_SPREAD_PROBABILITY,
    INITIAL_HOTSPOTS
)


class SensorSimulator:
    """
    Simulates drone sensor readings with environmental factors.
    
    Reads temperature and gas levels based on drone position
    relative to hidden fire hotspots. Fire can spread organically
    over time to create dynamic hazard zones.
    """
    
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        """
        Initialize the sensor simulator.
        
        Args:
            width: Grid width (default from config)
            height: Grid height (default from config)
        """
        self.width = width
        self.height = height
        
        # Initialize fire hotspots from config
        self.hotspots: List[Dict] = [
            {'x': h['x'], 'y': h['y'], 'intensity': h['intensity']}
            for h in INITIAL_HOTSPOTS
        ]
    
    def read_sensor_data(self, drone) -> Dict:
        """
        Generate sensor reading based on drone's current position.
        
        Args:
            drone: PhysicalDrone object with x, y, drone_id attributes
        
        Returns:
            Dictionary containing sensor readings and metadata.
        """
        x, y = drone.x, drone.y
        
        # Validate and clamp coordinates
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        # Generate base environmental noise
        temp = BASE_TEMP + random.uniform(-TEMP_VARIANCE, TEMP_VARIANCE)
        gas = BASE_GAS + random.uniform(-GAS_VARIANCE, GAS_VARIANCE)
        
        # Apply hotspot influence based on proximity
        temp, gas = self._apply_hotspot_influence(x, y, temp, gas)
        
        # Spread fire organically (configurable probability)
        if random.random() < FIRE_SPREAD_PROBABILITY:
            self._spread_fire()
        
        return {
            'drone_id': drone.drone_id,
            'x': x,
            'y': y,
            'temp': round(temp, 1),
            'gas': round(gas, 1),
            'timestamp': time.time()
        }
    
    def _apply_hotspot_influence(
        self, x: int, y: int, base_temp: float, base_gas: float
    ) -> tuple:
        """
        Calculate temperature and gas readings based on hotspot proximity.
        
        Args:
            x: Drone x coordinate
            y: Drone y coordinate
            base_temp: Base temperature before hotspot influence
            base_gas: Base gas level before hotspot influence
        
        Returns:
            Tuple of (adjusted_temp, adjusted_gas)
        """
        for spot in self.hotspots:
            distance = max(
                ((x - spot['x'])**2 + (y - spot['y'])**2)**0.5, 
                1
            )
            
            if distance < FIRE_HOTSPOT_RADIUS:
                # Calculate influence multiplier (stronger when closer)
                multiplier = (FIRE_HOTSPOT_RADIUS - distance) / FIRE_HOTSPOT_RADIUS
                
                # Apply intensity with random variance
                temp_increase = (spot['intensity'] - BASE_TEMP) * multiplier
                gas_increase = (spot['intensity'] - BASE_GAS) * multiplier
                
                base_temp += temp_increase * random.uniform(0.8, 1.2)
                base_gas += gas_increase * random.uniform(0.8, 1.2)
        
        return base_temp, base_gas
    
    def _spread_fire(self) -> None:
        """
        Spread fire hotspots organically across the grid.
        Each hotspot has a chance to move one cell in any direction.
        """
        for spot in self.hotspots:
            spot['x'] += random.choice([-1, 0, 1])
            spot['y'] += random.choice([-1, 0, 1])
            
            # Keep within grid bounds
            spot['x'] = max(0, min(self.width - 1, spot['x']))
            spot['y'] = max(0, min(self.height - 1, spot['y']))
    
    def get_hotspots(self) -> List[Dict]:
        """
        Get current hotspot positions and intensities.
        
        Returns:
            List of hotspot dictionaries.
        """
        return self.hotspots.copy()
    
    def reset_hotspots(self) -> None:
        """
        Reset hotspots to initial configuration.
        """
        self.hotspots = [
            {'x': h['x'], 'y': h['y'], 'intensity': h['intensity']}
            for h in INITIAL_HOTSPOTS
        ]
