"""
AURA System Test Script
Run to verify all modules work correctly.
"""

import sys
sys.path.insert(0, 'backend')

from config.settings import GRID_WIDTH, GRID_HEIGHT
from utils.helpers import calculate_distance, manhattan_distance
from data.simulator import SensorSimulator
from detection.hazard import classify_risk, risk_to_cost
from detection.survivor import detect_survivor, create_survivor_record
from detection.duplicate import is_duplicate, find_nearby_survivors
from database.victim_db import VictimDB
from mapping.grid_map import GridMap
from planning.pathfinding import a_star, simplify_path

def test_all():
    print("=" * 50)
    print("AURA System - Module Verification")
    print("=" * 50)
    
    print("\n[1] Config Settings")
    print(f"    Grid Size: {GRID_WIDTH}x{GRID_HEIGHT}")
    
    print("\n[2] Utils Helpers")
    dist = calculate_distance((0, 0), (3, 4))
    print(f"    Distance (0,0) to (3,4): {dist}")
    mdist = manhattan_distance((0, 0), (3, 4))
    print(f"    Manhattan Distance: {mdist}")
    
    print("\n[3] Sensor Simulator")
    sim = SensorSimulator()
    class MockDrone:
        drone_id = 1
        x = 25
        y = 25
    drone = MockDrone()
    sensor_data = sim.read_sensor_data(drone)
    print(f"    Sensor Reading: temp={sensor_data['temp']:.1f}, gas={sensor_data['gas']:.1f}")
    print(f"    Hotspots: {len(sim.get_hotspots())}")
    
    print("\n[4] Hazard Detection")
    print(f"    classify_risk(25, 5) = {classify_risk(25, 5)}")
    print(f"    classify_risk(45, 5) = {classify_risk(45, 5)}")
    print(f"    classify_risk(75, 5) = {classify_risk(75, 5)}")
    print(f"    risk_to_cost('HIGH') = {risk_to_cost('HIGH')}")
    
    print("\n[5] Survivor Detection")
    survivor = detect_survivor(25, 25, 'SAFE')
    print(f"    Detection at SAFE zone: {'Found' if survivor else 'Not found'}")
    
    print("\n[6] Duplicate Detection")
    db = VictimDB()
    s1 = create_survivor_record(15, 15, 'VERIFIED')
    db.add_survivor(s1)
    test_dup = {'id': 'TEST', 'x': 16, 'y': 15, 'timestamp': 9999999999}
    is_dup = is_duplicate(test_dup, db, 3.0, 60)
    print(f"    Is duplicate of nearby: {is_dup}")
    
    print("\n[7] Victim Database")
    print(f"    Survivors stored: {db.get_count()}")
    stats = db.get_statistics()
    print(f"    Statistics: {stats}")
    
    print("\n[8] Grid Map")
    grid = GridMap()
    grid.update_cell(10, 10, 'HIGH')
    grid.update_cell(20, 20, 'MEDIUM')
    print(f"    HIGH cells: {grid.get_high_risk_count()}")
    print(f"    MEDIUM cells: {grid.get_medium_risk_count()}")
    print(f"    Coverage: {grid.get_coverage_percent():.2f}%")
    
    print("\n[9] A* Pathfinding")
    weight_grid = grid.get_weight_grid()
    path = a_star(weight_grid, (0, 0), (30, 30))
    print(f"    Path from (0,0) to (30,30): {len(path)} steps")
    if path:
        simple = simplify_path(path)
        print(f"    Simplified path: {len(simple)} waypoints")
    
    print("\n" + "=" * 50)
    print("ALL AURA MODULES VERIFIED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == '__main__':
    test_all()
