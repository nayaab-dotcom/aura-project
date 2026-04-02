# Roadmap: AURA — Autonomous Unified Rescue and Assessment System

## Overview

AURA will be built in four logical phases, moving from the core simulation engine to advanced autonomous pathfinding, and finally to a high-performance real-time dashboard. This allows us to verify the "brains" of the drones before focusing on the visual "wow" factor needed for the college demo.

## Phases

- [ ] **Phase 1: Simulation Engine & Backend Foundation** - Core grid and drone state management.
- [ ] **Phase 2: Autonomous Intelligence** - Risk-aware A* pathfinding and safety logic.
- [ ] **Phase 3: Real-Time Visualization** - High-performance React dashboard and mapping.
- [ ] **Phase 4: Advanced Features & Final Integration** - Swarm mission logic and final demo polish.

## Phase Details

### Phase 1: Simulation Engine & Backend Foundation
**Goal**: Establish the base 50x50 grid simulation, hazard generation, and basic drone state machine.
**Depends on**: Nothing
**Requirements**: SIM-01, SIM-02, SIM-03, SIM-04, DRON-01, DRON-02, DRON-03
**Success Criteria**:
  1. Backend can generate a 50x50 grid with random hazards.
  2. Four drones exist in memory with IDLE/SCANNING states.
  3. Drones lose battery proportionally to "time" in simulation.
**Plans**: 2 plans

Plans:
- [ ] 01-01: Grid and Hazard generation logic.
- [ ] 01-02: Drone state machine and battery simulation.

### Phase 2: Autonomous Intelligence
**Goal**: Implement the A* pathfinding algorithm that accounts for risk zones.
**Depends on**: Phase 1
**Requirements**: PATH-01, PATH-02, PATH-03, PATH-04
**Success Criteria**:
  1. System can calculate a path avoiding "Red" (High Risk) cells.
  2. Drones automatically recalculate paths when a new hazard is detected.
  3. Safe evacuation paths are generated for "ground units".
**Plans**: 2 plans

Plans:
- [ ] 02-01: Risk-weighted A* implementation.
- [ ] 02-02: Mission-based pathfinding (Go to Target, Return-to-Base).

### Phase 3: Real-Time Visualization
**Goal**: Build the React dashboard with high-performance mapping and controls.
**Depends on**: Phase 2
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, MAP-01, MAP-02, MAP-03, MAP-04
**Success Criteria**:
  1. Map displays 50x50 grid with colors for risk levels.
  2. Drone markers move smoothly on the map in real-time.
  3. Control cards allow "Scan" and "Recall" actions with feedback.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Dashboard Shell and Grid Component.
- [ ] 03-02: Drone and Survivor Map Layers.
- [ ] 03-03: Event Logs and Control Cards.

### Phase 4: Advanced Features & Final Integration
**Goal**: Final polish, WebSocket integration, and analytics for the demo.
**Depends on**: Phase 3
**Requirements**: API-01, API-02, API-03, DRON-04
**Success Criteria**:
  1. Dashboard updates via WebSockets (sub-second latency).
  2. Analytics page shows graphs of survivors vs time.
  3. "Swarm" mission logic prevents drones from searching the same area twice.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Socket.IO integration for real-time telemetry.
- [ ] 04-02: Analytics and Swarm mission logic.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/2 | Not started | - |
| 2. Intelligence | 0/2 | Not started | - |
| 3. Visualization | 0/3 | Not started | - |
| 4. Integration | 0/2 | Not started | - |

### Phase 5: Vanilla HTML/CSS Frontend Rebuild

**Goal:** Remove React/Tailwind/NPM dependencies and rewrite frontend in vanilla web technologies.
**Requirements**: TBD
**Depends on:** Phase 4
**Plans:** 1 plans

Plans:
- [x] 05-01: Remove React/NPM and implement vanilla HTML/CSS/JS dashboard.

### Phase 6: Human-in-the-Loop Control Architecture

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 5
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 6 to break down)

### Phase 7: Mission Lifecycle, Control Integrity, and Reporting Fix

**Goal:** [To be planned]
**Requirements**: TBD
**Depends on:** Phase 6
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 7 to break down)

---
*Roadmap defined: 2026-03-31*
*Last updated: 2026-03-31 after initialization*
