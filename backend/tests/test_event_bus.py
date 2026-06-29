import pytest
import asyncio
from backend.services.event_bus import EventBus, Event, EventType

@pytest.mark.asyncio
async def test_publish_subscribe():
    bus = EventBus()
    q = await bus.subscribe(EventType.DRIVER_STATE_UPDATE)
    
    evt = Event(type=EventType.DRIVER_STATE_UPDATE, data={"test": "val"}, source="test_source")
    await bus.publish(evt)
    
    received = await q.get()
    assert received.data["test"] == "val"
    assert received.source == "test_source"

@pytest.mark.asyncio
async def test_history_limit():
    bus = EventBus()
    for i in range(1005):
        evt = Event(type=EventType.DRIVER_STATE_UPDATE, data={"id": i}, source="test")
        await bus.publish(evt)
        
    history = bus.get_history(2000)
    assert len(history) == 1000
    assert history[0].data["id"] == 5
