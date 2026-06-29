import asyncio
import logging
from typing import Dict, Any, List
from backend.services.event_bus import event_bus, Event, EventType

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.status = "idle"
        self.health = "healthy"
        self.stats = {"events_processed": 0, "errors": 0}
        self.state_history: List[Dict[str, Any]] = []
        self._task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"Agent.{name}")
        self.inference_interval = 0.1 # 100ms

    async def start(self):
        if self.status == "running":
            return
        self.status = "running"
        self._task = asyncio.create_task(self.run_loop())
        self.logger.info(f"Agent {self.name} started successfully.")

    async def stop(self):
        if self.status != "running":
            return
        self.status = "idle"
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info(f"Agent {self.name} stopped.")

    async def run_loop(self):
        while self.status == "running":
            try:
                await self.process()
                self.stats["events_processed"] += 1
            except Exception as e:
                self.stats["errors"] += 1
                self.health = "degraded"
                self.logger.error(f"Error in process loop: {e}", exc_info=True)
            await asyncio.sleep(self.inference_interval)

    async def process(self):
        raise NotImplementedError("Agents must implement process()")

    def get_state(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "health": self.health,
            "stats": self.stats
        }

    async def publish_event(self, event_type: EventType, data: dict, confidence: float = 1.0):
        evt = Event(type=event_type, data=data, source=self.name, confidence=confidence)
        await event_bus.publish(evt)
