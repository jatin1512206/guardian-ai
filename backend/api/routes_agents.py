from fastapi import APIRouter, HTTPException
from backend.agents.agent_registry import registry

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("")
def list_agents():
    return registry.get_status()

@router.post("/{name}/start")
async def start_agent(name: str):
    agent = registry.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent.start()
    return {"status": "started", "agent": name}

@router.post("/{name}/stop")
async def stop_agent(name: str):
    agent = registry.get_agent(name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent.stop()
    return {"status": "stopped", "agent": name}
