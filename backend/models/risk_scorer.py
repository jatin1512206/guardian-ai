import numpy as np

class RiskScorer:
    def __init__(self, config=None):
        self.weights = {
            "attention": 0.25,
            "fatigue": 0.15,
            "distraction": 0.15,
            "stability": 0.15,
            "prediction": 0.30
        }

    def compute(self, driver_state: dict, vehicle_state: dict, prediction_state: dict) -> dict:
        # Base indicators
        attention = driver_state.get("attention_score", 100.0) # 0 to 100
        fatigue = driver_state.get("fatigue_score", 0.0) # 0 to 100
        distraction = driver_state.get("distraction_probability", 0.0) * 100.0 # 0 to 100
        stability = vehicle_state.get("stability_score", 100.0) # 0 to 100
        accident_prob = prediction_state.get("accident_probability", 0.0) * 100.0 # 0 to 100
        
        # Risk formulas (higher score means higher risk)
        attn_risk = 100.0 - attention
        fatigue_risk = fatigue
        distraction_risk = distraction
        stability_risk = 100.0 - stability
        pred_risk = accident_prob
        
        # Weighted ensemble
        risk_score = (
            attn_risk * self.weights["attention"] +
            fatigue_risk * self.weights["fatigue"] +
            distraction_risk * self.weights["distraction"] +
            stability_risk * self.weights["stability"] +
            pred_risk * self.weights["prediction"]
        )
        
        risk_score = max(0.0, min(100.0, risk_score))
        
        # Risk level categorization
        if risk_score < 25.0:
            level = "low"
            intervention = "Dashboard monitoring active"
        elif risk_score < 50.0:
            level = "moderate"
            intervention = "Loud cabin audio notification triggered"
        elif risk_score < 75.0:
            level = "high"
            intervention = "Haptic seat feedback + Auto throttling active"
        else:
            level = "critical"
            intervention = "Emergency hazard dispatching initiated"
            
        factors = []
        if attn_risk > 40: factors.append("Driver Distracted")
        if fatigue_risk > 40: factors.append("Driver Fatigue Detected")
        if stability_risk > 30: factors.append("Unstable Vehicle Steering")
        if pred_risk > 50: factors.append("High Pre-Collision Risk")
        
        return {
            "risk_score": int(risk_score),
            "risk_level": level,
            "confidence": float(prediction_state.get("confidence", 0.90)),
            "contributing_factors": factors,
            "recommended_intervention": intervention
        }
