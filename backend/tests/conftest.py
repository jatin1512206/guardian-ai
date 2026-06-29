import pytest
import asyncio
from backend.services.event_bus import EventBus

@pytest.fixture
def event_bus():
    return EventBus()

@pytest.fixture
def sample_driver_state():
    return {
        "attention_score": 92.5,
        "fatigue_level": 12.0,
        "distraction_probability": 0.05,
        "emotion": "neutral",
        "is_phone": False,
        "is_drowsy": False,
        "blink_rate": 14.5,
        "head_yaw": 1.2,
        "head_pitch": -0.5
    }

@pytest.fixture
def sample_vehicle_telemetry():
    return {
        "speed": 62.4,
        "rpm": 2100.0,
        "steering_angle": 1.2,
        "acceleration": 0.1,
        "brake_pressure": 0.0,
        "lane_position": 0.02,
        "stability_score": 98.0,
        "road_risk": 10.0,
        "gps_lat": 28.6139,
        "gps_lon": 77.2090
    }
