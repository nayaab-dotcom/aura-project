# Requirements: AURA — Autonomous Unified Rescue and Assessment System

**Defined:** 2026-03-31
**Core Value:** Demonstrate a working end-to-end disaster response simulation where drones detect hazards/survivors and compute safe paths in real-time.

## v1 Requirements

Requirements for the initial college project demo.

### Simulation Engine (SIM)

- [ ] **SIM-01**: System generates random environmental hazards (Fires, Floods) on a 50x50 grid.
- [ ] **SIM-02**: System generates potential survivors based on hazard proximity and risk levels.
- [ ] **SIM-03**: Simulation runs at a configurable interval (default 1s) to update environmental state.
- [ ] **SIM-04**: Hazards can expand or diminish over time based on simple rule-based logic.

### Drone Management (DRON)

- [ ] **DRON-01**: Simulate exactly 4 drones with unique IDs, positions, and battery levels.
- [ ] **DRON-02**: Drones have 3 states: `IDLE`, `SCANNING`, `RETURNING`.
- [ ] **DRON-03**: Drones lose battery during flight and automatically return to base when below 10%.
- [ ] **DRON-04**: Drones detect survivors when within a 3-cell radius of their current position.

### Pathfinding (PATH)

- [ ] **PATH-01**: Implement A* algorithm to calculate paths between any two points on the 50x50 grid.
- [ ] **PATH-02**: Pathfinding must account for `HIGH` risk zones and avoid them by assigning large cost weights.
- [ ] **PATH-03**: Drones automatically recalculate paths if a new hazard appears on their current trajectory.
- [ ] **PATH-04**: Generate "Safe Evacuation Paths" for ground units (simulated as path overlays on the map).

### Mapping & GIS (MAP)

- [ ] **MAP-01**: Interactive 50x50 grid map showing cell-based risk levels (Green/Yellow/Red).
- [ ] **MAP-02**: Real-time markers for drone positions with orientation/status indicators.
- [ ] **MAP-03**: Markers for detected survivors with "Verified" vs "Unverified" status.
- [ ] **MAP-04**: Visual overlay of planned drone paths and evacuation routes.

### Dashboard & UI (DASH)

- [ ] **DASH-01**: Real-time status bar showing global stats (Total Survivors, High Risk Area %, Drones Active).
- [ ] **DASH-02**: Drone Control Cards for each of the 4 drones (Scan/Recall buttons, Battery/Status).
- [ ] **DASH-03**: Event Log panel showing the latest 20 system events (e.g., "Drone 2 found survivor at [12,45]").
- [ ] **DASH-04**: Analytics page with charts for survivor detection trends and risk level distribution.

### Connectivity (API)

- [ ] **API-01**: REST API endpoints for fetching grid state, drone positions, and event logs.
- [ ] **API-02**: WebSocket integration (Socket.IO) for real-time telemetry pushes from backend.
- [ ] **API-03**: Command endpoints to trigger drone actions (Scan, Return, Recall).

## v2 Requirements (Deferred)

- **AI-01**: Computer vision simulation (using images instead of rule-based coordinates).
- **SW-01**: Advanced swarm behavior (drones dividing search areas automatically).
- **MOB-01**: Mobile-responsive dashboard for field use.
- **AUD-02**: Voice alerts for critical events (e.g., "High risk detected in Zone B").

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real Drone Hardware | Out of project scope (simulated only). |
| User Authentication | Not required for a local college demo. |
| Persistent Database | In-memory storage is sufficient for a 15-min demo. |
| Real-time Video | Complexity of media servers; simulated with placeholders. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SIM-01..04 | Phase 1 | Pending |
| DRON-01..04 | Phase 1 | Pending |
| PATH-01..04 | Phase 2 | Pending |
| DASH-01..04 | Phase 3 | Pending |
| MAP-01..04 | Phase 3 | Pending |
| API-01..03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-31*
*Last updated: 2026-03-31 after initialization*
