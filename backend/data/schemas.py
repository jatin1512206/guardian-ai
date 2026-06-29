from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DriverState(BaseModel):
    attention_score: float = Field(..., ge=0, le=100)
    fatigue_level: float = Field(..., ge=0, le=100)
    distraction_probability: float = Field(..., ge=0, le=1.0)
    emotion: str = "neutral"
    is_phone: bool = False
    is_drowsy: bool = False
    blink_rate: float = 15.0
    head_yaw: float = 0.0
    head_pitch: float = 0.0

class VehicleTelemetry(BaseModel):
    speed: float
    rpm: float
    steering_angle: float
    acceleration: float
    brake_pressure: float
    lane_position: float
    gps_lat: float
    gps_lon: float

class RiskAssessment(BaseModel):
    risk_score: int
    risk_level: str
    accident_probability: float
    time_to_collision: Optional[float] = None
    confidence: float
    contributing_factors: List[str]
    recommended_intervention: str
