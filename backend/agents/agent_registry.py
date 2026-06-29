import logging
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentRegistry")

    def register(self, agent: BaseAgent):
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    def get_agent(self, name: str) -> BaseAgent:
        return self.agents.get(name)

    async def start_all(self):
        for agent in self.agents.values():
            await agent.start()

    async def stop_all(self):
        for agent in self.agents.values():
            await agent.stop()

    def get_status(self) -> Dict[str, dict]:
        return {name: agent.get_state() for name, agent in self.agents.items()}

registry = AgentRegistry()
