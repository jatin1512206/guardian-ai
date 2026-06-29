# API Documentation

## REST Endpoints
- `GET /health`: Server health check status.
- `GET /api/agents`: Returns list of all active agents with system heartbeats.
- `POST /api/agents/{name}/start`: Starts target agent instance.
- `GET /api/predictions/current`: Returns the latest risk score evaluation.

## WebSockets
- `WS /ws/live`: Streams telemetry feeds at 10Hz.
