# Research: Architecture dimension for AURA

## Core Architectural Components

### High-Frequency State (Drone Telemetry)
The drone telemetry (position, battery, sensors) should be managed as an **Atomic State** on the backend.
- **Backend**: Use a central `DroneManager` object in-memory.
- **Frontend**: Use a dedicated Hook (e.g., `useTelemetry`) to bridge the state with React’s view.

### Risk-Aware A* Pathfinding
Modified A* that treats every cell in the 50x50 grid as a node with a **cost weight**:
- **Calculation**: $f(n) = g(n) + h(n) + R(n)$, where $R(n)$ is the risk penalty.
- **Safety Buffers**: High-risk cells have a penalty large enough to make the drone bypass them even if the distance is significantly longer.

### Data Flow Pattern
1.  **Simulation Engine**: Randomly generates hazards/survivors within the 50x50 grid.
2.  **Drone Processor**: Updates drone locations based on their current missions (Scanning/Returning/Recall).
3.  **API Handler**: Serializes the `DroneManager` and `GridMap` to JSON for the frontend.
4.  **Dashboard Controller**: Renders the state and triggers commands (Scan/Recall) back to the `DroneProcessor`.

## Suggested Build Order

1.  **Backend Sim**: Hazard and grid generation logic.
2.  **Drone Engine**: State machine for Idle/Scanning/Returning.
3.  **Pathfinding Module**: A* implementation with risk weightings.
4.  **Frontend Map**: Grid visualization (risks + drones + survivors).
5.  **Integration**: Command handling and real-time updates.

## Confidence Level: Medium-High
Standard simulation patterns work well here. The primary challenge is balancing frequency with UI smoothness.
