import random
import time
from typing import List, Dict
from config import (
    GRID_WIDTH, GRID_HEIGHT,
    BASE_TEMP, BASE_GAS,
    TEMP_VARIANCE, GAS_VARIANCE,
    FIRE_HOTSPOT_RADIUS,
    FIRE_SPREAD_PROBABILITY,
    INITIAL_HOTSPOTS
)


class SensorSimulator:
    """Simulates drone sensor readings with environmental factors."""
    
    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.hotspots: List[Dict] = [
            {'x': h['x'], 'y': h['y'], 'intensity': h['intensity']}
            for h in INITIAL_HOTSPOTS
        ]
    
    def read_sensor_data(self, drone) -> Dict:
        x, y = drone.x, drone.y
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        temp = BASE_TEMP + random.uniform(-TEMP_VARIANCE, TEMP_VARIANCE)
        gas = BASE_GAS + random.uniform(-GAS_VARIANCE, GAS_VARIANCE)
        
        temp, gas = self._apply_hotspot_influence(x, y, temp, gas)
        
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
    
    def _apply_hotspot_influence(self, x: int, y: int, base_temp: float, base_gas: float) -> tuple:
        for spot in self.hotspots:
            distance = max(((x - spot['x'])**2 + (y - spot['y'])**2)**0.5, 1)
            if distance < FIRE_HOTSPOT_RADIUS:
                multiplier = (FIRE_HOTSPOT_RADIUS - distance) / FIRE_HOTSPOT_RADIUS
                base_temp += (spot['intensity'] - BASE_TEMP) * multiplier * random.uniform(0.8, 1.2)
                base_gas += (spot['intensity'] - BASE_GAS) * multiplier * random.uniform(0.8, 1.2)
        return base_temp, base_gas
    
    def _spread_fire(self) -> None:
        for spot in self.hotspots:
            spot['x'] += random.choice([-1, 0, 1])
            spot['y'] += random.choice([-1, 0, 1])
            spot['x'] = max(0, min(self.width - 1, spot['x']))
            spot['y'] = max(0, min(self.height - 1, spot['y']))
    
    def reset_hotspots(self) -> None:
        self.hotspots = [
            {'x': h['x'], 'y': h['y'], 'intensity': h['intensity']}
            for h in INITIAL_HOTSPOTS
        ]


def _generate_location() -> list[int]:
    """Generates a random location strictly within a 50x50 grid."""
    x = random.randint(0, 49)
    y = random.randint(0, 49)
    return [x, y]

def _generate_temperature() -> float:
    """Generates a simulated temperature reading in Celsius with a chance for spikes."""
    temp = random.uniform(20.0, 45.0)
    # 20% chance to add a spike (+30 to +60)
    if random.random() < 0.20:
        temp += random.uniform(30.0, 60.0)
    return round(temp, 2)

def _generate_gas_level() -> float:
    """Generates a simulated gas level reading with a chance for spikes."""
    gas = random.uniform(10.0, 40.0)
    # 15% chance to add a spike (+30 to +70)
    if random.random() < 0.15:
        gas += random.uniform(30.0, 70.0)
    return round(gas, 2)

def generate_sensor_data(drone_id: int) -> dict:
    """
    Generates realistic simulated drone sensor data.
    
    Args:
        drone_id (int): The unique identifier for the drone.
        
    Returns:
        dict: A dictionary containing the drone's id, location, temperature,
              gas level, and a unix timestamp.
    """
    return {
        "drone_id": drone_id,
        "temperature": _generate_temperature(),
        "gas_level": _generate_gas_level(),
        "location": _generate_location(),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    print("--- 5 Sample Drone Sensor Readings ---")
    for i in range(1, 6):
        sample_data = generate_sensor_data(drone_id=i)
        print(sample_data)
