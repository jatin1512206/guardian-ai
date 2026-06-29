from fastapi import APIRouter
from backend.services.event_bus import event_bus, EventType

router = APIRouter(prefix="/api/emergency", tags=["Emergency"])

@router.get("/status")
def get_emergency_status():
    history = event_bus.get_history(100)
    for evt in reversed(history):
        if evt.type == EventType.EMERGENCY_ALERT:
            return {"status": "triggered", "data": evt.data}
    return {"status": "normal"}
