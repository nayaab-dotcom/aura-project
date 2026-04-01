# Research: Pitfalls dimension for AURA

## Common Disaster Simulation Failures

### 1. Blocking UI on Calculation
Pathfinding (A*) on a 50x50 grid with 4 drones can consume CPU if run too frequently on the main thread.
- **Prevention**: Use asynchronous processing or limit replanning to only when Hazards change.

### 2. High-Frequency Telemetry Jitter
Updating drone positions as fast as the backend generates them might cause "jitter" in React.
- **Prevention**: Interpolate positions on the frontend or throttle state updates (30 FPS is smoother than raw data).

### 3. Hazard/Survivor Desync
If the grid updates but the drones are still moving to "old" target positions.
- **Prevention**: Automatic replanning (Triggering A* on change) or local collision avoidance.

### 4. Overcomplicating "Swarm"
Coordinated swarms are difficult. For a college project, stick to independent drones with a shared "Mission Region" allocator.
- **Prevention**: Define search zones (A, B, C, D) so drones don't overlap missions unless recalled.

## When should we address these?

-   **Pitfall 1 & 3**: During Phase 2 (Backend Core).
-   **Pitfall 2 & 4**: During Phase 3 (Frontend Dashboard).

## Confidence Level: High
These pitfalls are common in college-level simulation projects where real-time visualization is the goal.
