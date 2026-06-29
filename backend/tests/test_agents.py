import pytest
import asyncio
from backend.agents.driver_behavior_agent import DriverBehaviorAgent
from backend.agents.vehicle_dynamics_agent import VehicleDynamicsAgent
from backend.agents.agent_registry import registry

@pytest.mark.asyncio
async def test_agent_lifecycle():
    agent = DriverBehaviorAgent()
    assert agent.status == "idle"
    await agent.start()
    assert agent.status == "running"
    await agent.stop()
    assert agent.status == "idle"

@pytest.mark.asyncio
async def test_agent_registry():
    agent = VehicleDynamicsAgent()
    registry.register(agent)
    assert registry.get_agent("vehicle_dynamics") == agent
    statuses = registry.get_status()
    assert "vehicle_dynamics" in statuses
