from fastapi import APIRouter
from backend.services.event_bus import event_bus, EventType

router = APIRouter(prefix="/api/vehicle", tags=["Vehicle"])

@router.get("/telemetry")
def get_vehicle_telemetry():
    history = event_bus.get_history(100)
    for evt in reversed(history):
        if evt.type == EventType.VEHICLE_UPDATE:
            return evt.data
    return {}
