import pytest
import numpy as np
import torch
from backend.models.driver_monitor import DriverMonitorModel
from backend.models.vehicle_behavior import VehicleBehaviorModel
from backend.models.risk_scorer import RiskScorer

def test_driver_monitor_shape():
    model = DriverMonitorModel()
    dummy = torch.randn(1, 3, 224, 224)
    out = model(dummy)
    assert out.shape == (1, 10)

def test_driver_predict():
    model = DriverMonitorModel()
    dummy_frame = np.zeros((224, 224, 3), dtype=np.uint8)
    pred = model.predict(dummy_frame)
    assert "attention_score" in pred
    assert "class_name" in pred

def test_vehicle_predict():
    model = VehicleBehaviorModel()
    seq = np.zeros((50, 10))
    pred = model.predict(seq)
    assert "stability_score" in pred
    assert "risk_label" in pred

def test_risk_scorer():
    scorer = RiskScorer()
    driver = {"attention_score": 90.0, "fatigue_score": 10.0, "distraction_probability": 0.05}
    vehicle = {"stability_score": 95.0, "speed": 60.0}
    pred = {"accident_probability": 0.05, "confidence": 0.9}
    
    risk = scorer.compute(driver, vehicle, pred)
    assert risk["risk_score"] < 25
    assert risk["risk_level"] == "low"
