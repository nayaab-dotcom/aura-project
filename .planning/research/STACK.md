# Research: Stack dimension for AURA

## Standard 2025 Stack for Disaster Response Simulation

| Layer | Recommendation | Rationale |
|-------|----------------|-----------|
| **Backend** | **Flask + Gevent/Eventlet** | Lightweight, easy to deploy, handles asynchronous tasks for simulation logic effectively. |
| **Real-time** | **WebSockets (Flask-SocketIO)** | Critical for low-latency drone telemetry and live map updates. Avoids polling overhead. |
| **Frontend** | **React + Vite** | Fast development, excellent ecosystem (Hook-based state management is ideal for drone status). |
| **Mapping** | **MapLibre GL JS / Deck.gl** | WebGL performance for high-frequency coordinate updates and risk heatmaps. |

## Why these choices?

- **Flask-SocketIO**: In disaster simulations, 1-2 second latency can be excessive. WebSockets provide the sub-second response needed for a "command" feel.
- **Deck.gl**: Specifically designed for large-scale data visualization. Layering drone paths on top of a risk heatmap is efficient here.

## What NOT to use and why

- **Next.js**: Overkill for a local simulation dashboard. Flask is more direct for the processing engine.
- **Base64 for video**: For simulated video feeds, use placeholder assets or a proper stream (RTSP/WebRTC) if real-time feeds are added later.

## Confidence Level: High
These choices align with modern standards for real-time visualization systems as of 2025.
