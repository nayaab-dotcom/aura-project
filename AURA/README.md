# AURA - Autonomous Unified Rescue and Assessment System

A Python-based drone disaster response simulation system that detects environmental hazards, identifies survivors, and generates safe evacuation paths.

## Features

- **Drone Simulation**: 4 autonomous drones with battery management and path following
- **Sensor Data**: Simulated temperature and gas readings based on fire hotspots
- **Hazard Detection**: Classifies areas as HIGH (danger), MEDIUM (caution), or SAFE
- **Survivor Detection**: Probability-based survivor detection with duplicate filtering
- **A* Pathfinding**: Safe route calculation avoiding high-risk zones
- **Real-time Dashboard**: Web-based visualization with live updates

## Project Structure

```
AURA/
├── main.py                    # System orchestrator (CLI version)
├── config/
│   └── settings.py           # Central configuration
├── utils/
│   └── helpers.py            # Distance calculations
├── data/
│   └── simulator.py          # Sensor simulation
├── detection/
│   ├── hazard.py             # Risk classification
│   ├── survivor.py            # Survivor detection
│   └── duplicate.py           # Duplicate filtering
├── database/
│   └── victim_db.py          # In-memory survivor storage
├── mapping/
│   └── grid_map.py           # 50x50 risk grid
├── planning/
│   └── pathfinding.py        # A* algorithm
└── dashboard/
    └── app.py                # Flask web dashboard
```

## Installation

```bash
cd AURA
pip install flask
```

## Running the System

### Option 1: Dashboard (Recommended)

```bash
python dashboard/app.py
```
Open http://localhost:8501 in your browser.

### Option 2: CLI Version

```bash
python main.py
```

### Option 3: Module Tests

```bash
python test_system.py
```

## How It Works

1. **Simulation Loop**: Runs every 1 second
2. **Drone Movement**: Drones move along assigned paths or stay idle
3. **Sensor Reading**: Each drone reads temperature and gas levels
4. **Hazard Classification**: Based on thresholds (temp > 70 or gas > 70 = HIGH)
5. **Grid Update**: Risk levels stored in 50x50 grid
6. **Survivor Detection**: Probability-based detection (SAFE=5%, MEDIUM=2%, HIGH=0.5%)
7. **Duplicate Filtering**: Prevents counting same survivor twice
8. **Pathfinding**: A* calculates safe routes avoiding HIGH-risk cells

## Configuration

Edit `config/settings.py` to modify:

- `GRID_WIDTH`, `GRID_HEIGHT`: Grid dimensions (default: 50x50)
- `RISK_TEMP_HIGH`, `RISK_GAS_HIGH`: Risk thresholds
- `FIRE_HOTSPOT_RADIUS`: Detection radius for fire effects
- `PROB_SAFE`, `PROB_MEDIUM`, `PROB_HIGH`: Survivor detection probabilities
- `DRONE_COUNT`: Number of drones (default: 4)

## API Endpoints (Dashboard)

- `GET /api/state` - Get complete system state
- `POST /api/reset` - Reset mission
- `POST /api/scan/<id>` - Send drone to scan
- `POST /api/recall/<id>` - Recall drone to base

## Risk Levels

| Level | Color | Conditions | Pathfinding Cost |
|-------|-------|------------|------------------|
| SAFE | Green | temp <= 40, gas <= 40 | 1 |
| MEDIUM | Yellow | temp > 40 OR gas > 40 | 20 |
| HIGH | Red | temp > 70 OR gas > 70 | 1000 (blocked) |

## License

MIT License
