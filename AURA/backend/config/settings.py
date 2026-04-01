"""
AURA Configuration Settings

Central configuration file for all system parameters.
Import this module to access all configurable values.
"""

# Grid Configuration
GRID_WIDTH = 50
GRID_HEIGHT = 50

# Base Environmental Values
BASE_TEMP = 20.0
BASE_GAS = 5.0
TEMP_VARIANCE = 2.0
GAS_VARIANCE = 1.0

# Risk Classification Thresholds
RISK_TEMP_HIGH = 70.0
RISK_TEMP_MEDIUM = 40.0
RISK_GAS_HIGH = 70.0
RISK_GAS_MEDIUM = 40.0

# Pathfinding Costs (for A* algorithm)
COST_SAFE = 1
COST_MEDIUM = 20
COST_HIGH = 1000

# Survivor Detection Probabilities
PROB_SAFE = 0.05
PROB_MEDIUM = 0.02
PROB_HIGH = 0.005

# Duplicate Detection Thresholds
SURVIVOR_DIST_THRESHOLD = 3.0
SURVIVOR_TIME_THRESHOLD = 60.0

# Simulation Settings
FIRE_HOTSPOT_RADIUS = 8
FIRE_SPREAD_PROBABILITY = 0.1
SIMULATION_INTERVAL = 1.0

# Drone Configuration
DRONE_COUNT = 4
INITIAL_BATTERY = 100.0
BATTERY_DRAIN_RATE = 0.5
LOW_BATTERY_THRESHOLD = 20.0
CRITICAL_BATTERY_THRESHOLD = 10.0

# Initial Fire Hotspots (x, y, intensity)
INITIAL_HOTSPOTS = [
    {'x': 25, 'y': 25, 'intensity': 100},
    {'x': 10, 'y': 40, 'intensity': 80},
    {'x': 40, 'y': 10, 'intensity': 90}
]

# Base Station Position
BASE_STATION_X = 0
BASE_STATION_Y = 0
