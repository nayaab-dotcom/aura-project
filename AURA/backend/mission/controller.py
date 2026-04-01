import uuid
import time
import threading
import logging

from drone.drone import get_all_drones
from data.simulator import SensorSimulator

logging.basicConfig(level=logging.INFO)

class Mission:
    def __init__(self):
        self.id = str(uuid.uuid4())[:8].upper()
        self.start_time = time.time()
        self.status = 'ACTIVE' # ACTIVE, COMPLETED

class SimulationController:
    """Autonomous simulation loop controller - runs continuously every 1 second."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.sensor_simulator = SensorSimulator()
        self.latest_sensor_data = []
    
    def start(self):
        """Start the simulation loop."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the simulation loop."""
        self.running = False
    
    def run_loop(self):
        """Main loop running every 1 second."""
        print("[SIM] Simulation loop started")
        while self.running:
            self.tick()
            time.sleep(1.0)
    
    def tick(self):
        """Single simulation tick - moves drones, generates sensor data, and logs heartbeat."""
        print("[SIM] Tick")
        
        drones = get_all_drones()
        sensor_data_batch = []
        
        for drone in drones:
            old_pos = (drone.x, drone.y)
            drone.move()
            logging.info(f"[DRONE {drone.drone_id}] moved to ({drone.x}, {drone.y})")
            
            data = self.sensor_simulator.read_sensor_data(drone)
            sensor_data_batch.append(data)
            logging.info(
                f"[SENSOR] Drone {data['drone_id']} | "
                f"TEMP={data['temp']:.2f} | "
                f"GAS={data['gas']:.2f} | "
                f"LOC=({data['x']}, {data['y']})"
            )
        
        self.latest_sensor_data = sensor_data_batch

class MissionController:
    def __init__(self):
        self.current_mission = Mission()
        
    def reset_mission(self):
        """Generates a new mission ID and resets the clock."""
        self.current_mission = Mission()
        return self.current_mission

    def get_mission_id(self):
        return self.current_mission.id

    def get_start_time(self):
        return self.current_mission.start_time

    def get_status(self):
        return self.current_mission.status

    def get_duration(self):
        return time.time() - self.current_mission.start_time
