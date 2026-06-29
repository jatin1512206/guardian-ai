import asyncio
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any
import uuid
from datetime import datetime

class EventType(Enum):
    DRIVER_STATE_UPDATE = "DRIVER_STATE_UPDATE"
    VEHICLE_UPDATE = "VEHICLE_UPDATE"
    RISK_UPDATE = "RISK_UPDATE"
    INTERVENTION_COMMAND = "INTERVENTION_COMMAND"
    AGENT_HEALTH = "AGENT_HEALTH"
    EMERGENCY_ALERT = "EMERGENCY_ALERT"

@dataclass
class Event:
    type: EventType
    data: Dict[str, Any]
    source: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 1.0
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[asyncio.Queue]] = {t: [] for t in EventType}
        self._history: List[Event] = []
        self._max_history = 1000
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: EventType) -> asyncio.Queue:
        async with self._lock:
            q = asyncio.Queue()
            self._subscribers[event_type].append(q)
            return q

    async def unsubscribe(self, event_type: EventType, queue: asyncio.Queue):
        async with self._lock:
            if queue in self._subscribers[event_type]:
                self._subscribers[event_type].remove(queue)

    async def publish(self, event: Event):
        async with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)
            
            for q in self._subscribers[event.type]:
                await q.put(event)

    def get_history(self, limit: int = 100) -> List[Event]:
        return self._history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_events_published": len(self._history),
            "active_subscribers": {t.name: len(self._subscribers[t]) for t in EventType}
        }

event_bus = EventBus()
