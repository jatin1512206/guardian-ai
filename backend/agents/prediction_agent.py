import asyncio
import numpy as np
from backend.agents.base_agent import BaseAgent
from backend.services.event_bus import event_bus, EventType
from backend.models.risk_scorer import RiskScorer

class PredictionAgent(BaseAgent):
    def __init__(self):
        super().__init__("prediction")
        self.risk_scorer = RiskScorer()
        try:
            import torch
            from backend.models.sensor_fusion import SensorFusionModel
            from backend.models.accident_predictor import AccidentPredictor
            self.fusion_model = SensorFusionModel()
            self.predictor_model = AccidentPredictor()
            # Load checkpoints
            import os
            if os.path.exists("checkpoints/sensor_fusion.pt"):
                self.fusion_model.load_state_dict(torch.load("checkpoints/sensor_fusion.pt", map_location="cpu"))
            if os.path.exists("checkpoints/accident_predictor.pt"):
                self.predictor_model.load("checkpoints/accident_predictor.pt")
            self.models_loaded = True
        except Exception as e:
            self.logger.warning(f"Prediction models could not be loaded: {e}. Using rules engine fallback.")
            self.models_loaded = False
            
        self.fused_history = []
        self.latest_driver = {}
        self.latest_vehicle = {}
        
        # Subscribe queue references
        self.driver_q = None
        self.vehicle_q = None

    async def start(self):
        await super().start()
        self.driver_q = await event_bus.subscribe(EventType.DRIVER_STATE_UPDATE)
        self.vehicle_q = await event_bus.subscribe(EventType.VEHICLE_UPDATE)

    async def process(self):
        # Empty queues asynchronously
        while not self.driver_q.empty():
            evt = await self.driver_q.get()
            self.latest_driver = evt.data
            
        while not self.vehicle_q.empty():
            evt = await self.vehicle_q.get()
            self.latest_vehicle = evt.data
            
        if not self.latest_driver or not self.latest_vehicle:
            return
            
        # Run fusion and predictor
        if self.models_loaded:
            fused_vector = self.fusion_model.fuse(self.latest_driver, self.latest_vehicle).numpy()
            self.fused_history.append(fused_vector[0])
            if len(self.fused_history) > 30:
                self.fused_history.pop(0)
                
            if len(self.fused_history) == 30:
                seq = np.array(self.fused_history)
                pred = self.predictor_model.predict(seq)
            else:
                pred = {"accident_probability": 0.05, "time_to_collision": None, "collision_type": "none", "confidence": 0.9}
        else:
            # Rule engine fallback
            accident_prob = 0.02
            collision_type = "none"
            ttc = None
            
            if self.latest_driver["attention_score"] < 40 and self.latest_vehicle["speed"] > 80:
                accident_prob = 0.85
                collision_type = "rear_end"
                ttc = 2.1
            elif self.latest_vehicle["stability_score"] < 50:
                accident_prob = 0.60
                collision_type = "loss_of_control"
                ttc = 3.5
                
            pred = {
                "accident_probability": accident_prob,
                "time_to_collision": ttc,
                "collision_type": collision_type,
                "confidence": 0.90
            }
            
        # Bayesian scoring
        risk = self.risk_scorer.compute(self.latest_driver, self.latest_vehicle, pred)
        
        prediction_payload = {
            "accident_probability": pred["accident_probability"],
            "time_to_collision": pred["time_to_collision"],
            "collision_type": pred["collision_type"],
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "confidence": risk["confidence"],
            "contributing_factors": risk["contributing_factors"],
            "recommended_intervention": risk["recommended_intervention"]
        }
        
        await self.publish_event(EventType.RISK_UPDATE, prediction_payload, confidence=risk["confidence"])
