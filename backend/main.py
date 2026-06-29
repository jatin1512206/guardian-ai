import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import create_tables
from backend.agents.agent_registry import registry
from backend.agents.driver_behavior_agent import DriverBehaviorAgent
from backend.agents.vehicle_dynamics_agent import VehicleDynamicsAgent
from backend.agents.prediction_agent import PredictionAgent
from backend.agents.intervention_agent import InterventionAgent
from backend.api import routes_agents, routes_predictions, routes_driver, routes_vehicle, routes_emergency, websocket

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    await create_tables()
    
    # Initialize agents
    registry.register(DriverBehaviorAgent())
    registry.register(VehicleDynamicsAgent())
    registry.register(PredictionAgent())
    registry.register(InterventionAgent())
    
    # Start agents
    await registry.start_all()
    
    yield
    # Shutdown tasks
    await registry.stop_all()

app = FastAPI(
    title=settings.APP_NAME,
    description="Behavioral Prediction System for Accident Prevention",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(routes_agents.router)
app.include_router(routes_predictions.router)
app.include_router(routes_driver.router)
app.include_router(routes_vehicle.router)
app.include_router(routes_emergency.router)
app.include_router(websocket.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
