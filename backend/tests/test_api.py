import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_get_agents():
    with TestClient(app) as client:
        response = client.get("/api/agents")
        assert response.status_code == 200
        assert "driver_behavior" in response.json()
        assert "vehicle_dynamics" in response.json()
        assert "prediction" in response.json()
        assert "intervention" in response.json()
