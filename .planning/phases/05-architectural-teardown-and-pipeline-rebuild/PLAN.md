---
status: "planned"
---

# Phase 05: Architectural Teardown and Pipeline Rebuild

## Phase Goal
Transition the AURA backend from a UI-simulation to a fully functional, end-to-end disaster response pipeline. The system must process sensor data, classify hazards, maintain a real map, detect survivors, and calculate precise pathfinding before exposing data via a strict REST API.

## Requirements
- BACKEND-01: Modular architecture (data, detection, mapping, database, planning, utils).
- BACKEND-02: Drones act as physical entities emitting sensor data.
- BACKEND-03: Real-time background simulation loop (1 second tick).
- BACKEND-04: Full REST API layer for frontend consumption.
- FRONTEND-01: Remove all mock data paths and connect components to real endpoints.

## Execution Plans

### Plan 1: Foundation and Modules
- Create backend directory structure (`data`, `detection`, `mapping`, `database`, `planning`, `utils`, `drone`).
- Implement `utils/helpers.py`.
- Implement `mapping/grid_map.py` (50x50 state array).
- Implement `database/victim_db.py` (in-memory survivor list).
- Implement `detection/hazard.py` (risk classification rules).
- Implement `detection/survivor.py` and `detection/duplicate.py` (probability logic and filtering).

### Plan 2: Drones and Pathfinding
- Implement `drone/drone.py` (Drone state machine and movement processing).
- Port over `planning/pathfinding.py` and modify to use the new `grid_map` structure.
- Add `data/simulator.py` to trigger sensor generation based on drone movements.

### Plan 3: The Core Pipeline and API Layer
- Rewrite `app.py` to establish the central Flask API (`/data`, `/grid`, `/survivors`, `/logs`, `/drones`, `/action/scan`, `/action/recall`).
- Setup the background loop that executes the strict Pipeline: Drone moves → Sensor data → Hazard classification → Grid update → Survivor detection → Filtering → Store → Repath.

### Plan 4: Frontend Re-Wiring
- Open `frontend/src/App.jsx`.
- Replace `Socket.IO` references with standard `fetch` APIs inside a `setInterval` (1-2s polling loop).
- Update MapView, DroneCards, and LogsPanel to consume the new REST endpoint logic.
- Verify end-to-end functionality visually.
