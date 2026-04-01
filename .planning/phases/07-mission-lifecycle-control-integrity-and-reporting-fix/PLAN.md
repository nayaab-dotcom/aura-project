---
status: "planned"
---

# Phase 07: Mission Lifecycle, Control Integrity, and Reporting Fix

## Phase Goal
Implement a functional mission lifecycle and real reporting system, ensuring all UI actions map to backend state changes with a robust mission reset mechanism.

## Requirements
- BACKEND-01: Mission controller tracking `mission_id`, `start_time`, and `status`.
- BACKEND-02: `POST /mission/reset` to clear grid, survivors, drones, and logs.
- BACKEND-03: Real reporting module (`reporting/mission_report.py`) with coverage and risk metrics.
- BACKEND-04: Functional swarm logic (4-quadrant assignment).
- FRONTEND-01: Auto-reset mission on page load/refresh.
- FRONTEND-02: Export real mission report JSON.

## Execution Plans

### Plan 1: Mission Controller & State Management
- `[ ]` Create `backend/mission/controller.py`.
- `[ ]` Implement `MissionController` class to manage simulation state resets.

### Plan 2: Enhanced Mapping & Real Reporting
- `[ ]` Modify `GridMap` to track `visited_cells` for coverage analytics.
- `[ ]` Create `backend/reporting/mission_report.py` for real-time mission metrics.
- `[ ]` Expose `GET /report` endpoint in `app.py`.

### Plan 3: Reset API & Command Integrity
- `[ ]` Implement `POST /mission/reset` in `app.py`.
- `[ ]` Implement `POST /action/swarm` with sector assignment logic.
- `[ ]` Ensure mission reset clears drones, survivors, and logs.

### Plan 4: Frontend State Authority & Mission Reset
- `[ ]` Update `App.jsx` to call `/mission/reset` via `useEffect` (Simulation Mode).
- `[ ]` Connect UI "Export" to the `/report` JSON download.
- `[ ]` Final verification of button commands vs backend logs.
