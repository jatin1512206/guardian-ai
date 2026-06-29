from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime
from backend.services.event_bus import event_bus, Event, EventType
from backend.agents.agent_registry import registry

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Task to handle incoming messages from the client (webcam telemetry)
    async def receive_loop():
        try:
            while True:
                data_str = await websocket.receive_text()
                try:
                    payload = json.loads(data_str)
                    if payload.get("action") == "update_driver_state":
                        driver_data = payload.get("data", {})
                        # Publish directly to event bus so the Prediction Agent can fuse it
                        evt = Event(
                            type=EventType.DRIVER_STATE_UPDATE,
                            data=driver_data,
                            source="browser_webrtc_cam",
                            confidence=0.98
                        )
                        await event_bus.publish(evt)
                    elif payload.get("action") == "update_vehicle_telemetry":
                        vehicle_data = payload.get("data", {})
                        evt = Event(
                            type=EventType.VEHICLE_UPDATE,
                            data=vehicle_data,
                            source="browser_telemetry_override",
                            confidence=1.0
                        )
                        await event_bus.publish(evt)
                except Exception as e:
                    print(f"Error parsing client socket payload: {e}")
        except WebSocketDisconnect:
            pass

    # Task to stream active agent states back to the client
    async def send_loop():
        try:
            while True:
                history = event_bus.get_history(100)
                
                driver = {}
                vehicle = {}
                risk = {}
                interventions = []
                
                # Walk backward to find latest updates
                for evt in reversed(history):
                    if not driver and evt.type == EventType.DRIVER_STATE_UPDATE:
                        driver = evt.data
                    elif not vehicle and evt.type == EventType.VEHICLE_UPDATE:
                        vehicle = evt.data
                    elif not risk and evt.type == EventType.RISK_UPDATE:
                        risk = evt.data
                    elif evt.type == EventType.INTERVENTION_COMMAND:
                        interventions.append(evt.data)
                        
                agent_status = registry.get_status()
                
                payload = {
                    "driver_state": driver,
                    "vehicle_telemetry": vehicle,
                    "risk_assessment": risk,
                    "interventions": interventions[:5],
                    "agents": agent_status,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_text(json.dumps(payload))
                await asyncio.sleep(0.1) # 10Hz stream
        except WebSocketDisconnect:
            pass

    # Run both loops concurrently. If either task raises an exception/disconnect, cancel the other.
    try:
        await asyncio.gather(receive_loop(), send_loop())
    finally:
        manager.disconnect(websocket)
