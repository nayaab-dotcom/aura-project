# Research Summary: AURA — Disaster Response Simulation

The domain research for AURA is complete. We've investigated the best tools for real-time visualization, mission features for disaster response, A* pathfinding constraints, and pitfalls to avoid.

## Key Findings

- **Real-Time Stack**: Flask-SocketIO (WebSockets) is the benchmark for low-latency command dashboards in 2025. It beats polling for "control" feel.
- **Dynamic Risk Mapping**: A* pathfinding with risk-weighted costs is essential. We should implement safety buffers around hazards.
- **Frontend Visualization**: `Deck.gl` or `MapLibre GL JS` provide the best performance for drone telemetry on top of a 50x50 dynamic grid.
- **Survivor Detection**: Algorithms can use sensor data (Temp > 37°C) for probability detection, but we must handle sensor noise and false positives.

## Decision Markers

| Topic | Best Practice | Recommended for AURA? |
|-------|---------------|-------------------------|
| Communication | WebSockets | Yes (Upgrade from Polling) |
| Mapping | GIS-based (MapLibre) | Yes (Premium visualization) |
| Pathfinding | D* Lite / Risk-weighted A* | Yes (Standard A* first, upgrade second) |
| Data | Protobuf | No (JSON is simpler for demo) |

## Next Steps

1.  **Refine REQUIREMENTS.md**: Extracting requirements from this research and `PROJECT.md`.
2.  **Define ROADMAP.md**: Phased execution starting with the Backend processing engine.
3.  **Initialize STATE.md**: Setting up the project context tracker.

---

### Research Complete
Verified against 2025 domain benchmarks.
