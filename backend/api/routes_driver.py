from fastapi import APIRouter
from backend.services.event_bus import event_bus, EventType
from backend.services.driver_profile import driver_profile_service

router = APIRouter(prefix="/api/driver", tags=["Driver"])

@router.get("/state")
def get_driver_state():
    history = event_bus.get_history(100)
    for evt in reversed(history):
        if evt.type == EventType.DRIVER_STATE_UPDATE:
            return evt.data
    return {}

@router.get("/profile")
async def get_driver_profile():
    return await driver_profile_service.get_profile()
