from fastapi import APIRouter
from backend.services.event_bus import event_bus, EventType

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.get("/current")
def get_current_risk():
    history = event_bus.get_history(100)
    for evt in reversed(history):
        if evt.type == EventType.RISK_UPDATE:
            return evt.data
    return {"risk_score": 0, "risk_level": "low", "accident_probability": 0.0, "confidence": 1.0}
