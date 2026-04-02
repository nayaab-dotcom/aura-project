import random
import time

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
