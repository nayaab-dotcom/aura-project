# AURA — Autonomous Unified Rescue and Assessment System

## What This Is

AURA is a drone-based disaster response simulation system built as a college project. It simulates how a team of 4 autonomous drones can detect environmental hazards (fires, floods, earthquakes), identify survivors, and generate safe evacuation paths using A* pathfinding. The system includes a Python/Flask backend processing engine and a React dashboard for real-time monitoring and control.

## Core Value

**Demonstrate a working end-to-end disaster response simulation** — drones collect sensor data, the system detects hazards and survivors, builds a dynamic risk map, and computes safe evacuation paths, all visible through a real-time dashboard.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Simulate drone sensor data (temperature, gas levels, location, timestamp)
- [ ] Classify environmental risk zones (HIGH/MEDIUM/SAFE) based on sensor thresholds
- [ ] Detect survivors using probability-based logic tied to risk levels
- [ ] Prevent duplicate survivor detection using Euclidean distance + time proximity
- [ ] Store detected survivors in a central in-memory database
- [ ] Maintain a dynamic 50×50 grid map with risk levels per cell
- [ ] Implement A* pathfinding to generate safest evacuation paths avoiding HIGH-risk zones
- [ ] Simulate 4 drones with positions, statuses (Idle/Scanning/Returning), and movement
- [ ] Expose REST API endpoints for frontend integration (drones, grid, survivors, logs, actions)
- [ ] Build a real-time React dashboard with drone grid, risk heatmap, event logs, and analytics
- [ ] Provide Scan/Recall controls for each drone with immediate UI feedback
- [ ] Display risk-colored heatmap with drone positions, survivor markers, and path overlay
- [ ] Show scrollable event log panel with latest events
- [ ] Include analytics page with survivor counts, risk distribution charts, scan totals

### Out of Scope

- Real hardware/drone integration — all data is simulated
- Machine Learning for hazard/survivor detection — rule-based logic only
- Real video feeds — simulated with placeholder images
- User authentication — no login system needed
- Database persistence (SQL/NoSQL) — in-memory storage is sufficient
- Mobile app — web dashboard only
- Deployment to cloud — runs locally for demo

## Context

- **College project** — needs to work as a convincing demo, clean code, good presentation value
- **No real hardware** — all sensor data, drone movement, and video feeds are simulated
- **Full-stack** — Python Flask backend + React/Vite frontend with Tailwind CSS
- **Existing workspace** — lives inside `erp/AURA/` subfolder alongside an existing ERP project
- **Previous work** — a React frontend with some components (DroneCard, Dashboard, StatsBar, MapView, LogsPanel) was started but needs the full backend and proper integration

## Constraints

- **Backend**: Python + Flask — no other frameworks
- **Frontend**: React + Vite + Tailwind CSS + vanilla HTML/CSS
- **Language**: JavaScript for frontend (no TypeScript)
- **Grid Size**: 50×50 environment grid
- **Drone Count**: Exactly 4 drones
- **Data**: All simulated, no external APIs or hardware
- **Simplicity**: Rule-based logic, no ML/AI libraries

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python Flask for backend | Simple, lightweight, easy to demo | — Pending |
| React + Vite for frontend | Modern, fast dev server, good for college project | — Pending |
| In-memory storage over database | Simpler setup, no DB dependencies for demo | — Pending |
| A* for pathfinding | Classic algorithm, well-documented, good for college explanation | — Pending |
| Rule-based hazard detection | Simple thresholds (temp/gas > 70 = HIGH), easy to explain | — Pending |
| Polling over WebSockets | Simpler to implement, 1-2 second interval sufficient for demo | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-01 after initialization*
