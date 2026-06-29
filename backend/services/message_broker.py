import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime

@dataclass
class AgentMessage:
    sender: str
    recipient: str
    content: Any
    priority: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class MessageBroker:
    def __init__(self):
        self._queues: Dict[str, asyncio.PriorityQueue] = {}
        self._lock = asyncio.Lock()

    async def register_agent(self, agent_name: str):
        async with self._lock:
            if agent_name not in self._queues:
                self._queues[agent_name] = asyncio.PriorityQueue()

    async def send(self, msg: AgentMessage):
        async with self._lock:
            if msg.recipient not in self._queues:
                self._queues[msg.recipient] = asyncio.PriorityQueue()
            # PriorityQueue sorts ascending. Lower priority value = higher priority.
            # Using tuple (-priority, msg) to make higher priority parameter processed first.
            await self._queues[msg.recipient].put((-msg.priority, msg))

    async def receive(self, agent_name: str) -> AgentMessage:
        if agent_name not in self._queues:
            await self.register_agent(agent_name)
        _, msg = await self._queues[agent_name].get()
        return msg

message_broker = MessageBroker()
