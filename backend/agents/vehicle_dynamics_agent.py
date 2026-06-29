import asyncio
import numpy as np
from datetime import datetime, timedelta
from backend.agents.base_agent import BaseAgent
from backend.services.event_bus import event_bus, EventType
from backend.data.synthetic_generator import generator

class VehicleDynamicsAgent(BaseAgent):
    def __init__(self):
        super().__init__("vehicle_dynamics")
        try:
            from backend.models.vehicle_behavior import VehicleBehaviorModel
            self.vehicle_model = VehicleBehaviorModel()
            
            # Load checkpoints
            import os
            if os.path.exists("checkpoints/vehicle_behavior.pt"):
                self.vehicle_model.load("checkpoints/vehicle_behavior.pt")
                
            self.models_loaded = True
        except Exception as e:
            self.logger.warning(f"Vehicle model could not be loaded: {e}. Running in simulation/synthetic mode.")
            self.models_loaded = False
            
        self.telemetry_history = []

    async def process(self):
        # 1. Check if we have manual UI slider overrides flowing from the browser
        history = event_bus.get_history(30)
        has_manual_override = False
        manual_data = {}
        
        for evt in history:
            if evt.source == "browser_telemetry_override":
                try:
                    evt_time = datetime.fromisoformat(evt.timestamp)
                    if (datetime.utcnow() - evt_time).total_seconds() < 2.0:
                        has_manual_override = True
                        manual_data = evt.data
                        break
                except Exception:
                    pass

        if has_manual_override:
            # Manual control is active: consume client steering/speed values directly
            speed = manual_data.get("speed", 60.0)
            steering_angle = manual_data.get("steering_angle", 0.0)
            lane_position = manual_data.get("lane_position", 0.0)
            acceleration = 0.5 if speed > 60 else -0.1
            brake_pressure = 0.8 if speed == 0 else 0.0
            
            stability = max(0.0, 100.0 - abs(steering_angle) * 5.0 - (speed - 60.0) * 0.2)
            stability = min(100.0, stability)
            road_risk = 10.0 if speed < 80 else 45.0
            
            vehicle_state = {
                "speed": float(speed),
                "rpm": float(speed * 35),
                "steering_angle": float(steering_angle),
                "acceleration": float(acceleration),
                "brake_pressure": float(brake_pressure),
                "lane_position": float(lane_position),
                "stability_score": float(stability),
                "road_risk": float(road_risk),
                "gps_lat": 28.6139,
                "gps_lon": 77.2090
            }
            await self.publish_event(EventType.VEHICLE_UPDATE, vehicle_state, confidence=1.0)
            return

        # 2. Otherwise, fall back to the synthetic generator loop
        step_data = generator.next_step()
        raw_telemetry = step_data["vehicle_telemetry"]
        
        # Keep sliding sequence window of 50
        feat_vector = [
            raw_telemetry["speed"], raw_telemetry["steering_angle"],
            raw_telemetry["acceleration"], raw_telemetry["brake_pressure"],
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]
        self.telemetry_history.append(feat_vector)
        if len(self.telemetry_history) > 50:
            self.telemetry_history.pop(0)
            
        if self.models_loaded and len(self.telemetry_history) == 50:
            seq = np.array(self.telemetry_history)
            pred = self.vehicle_model.predict(seq)
            stability = pred["stability_score"]
            road_risk = pred["risk_class"] * 25.0
        else:
            steering_var = np.var([x[1] for x in self.telemetry_history]) if self.telemetry_history else 0.0
            stability = max(0.0, 100.0 - steering_var * 10.0 - (raw_telemetry["speed"] - 60.0) * 0.2)
            stability = min(100.0, stability)
            road_risk = 10.0 if raw_telemetry["speed"] < 80 else 40.0
            
        vehicle_state = {
            "speed": raw_telemetry["speed"],
            "rpm": raw_telemetry["rpm"],
            "steering_angle": raw_telemetry["steering_angle"],
            "acceleration": raw_telemetry["acceleration"],
            "brake_pressure": raw_telemetry["brake_pressure"],
            "lane_position": raw_telemetry["lane_position"],
            "stability_score": stability,
            "road_risk": road_risk,
            "gps_lat": raw_telemetry["gps_lat"],
            "gps_lon": raw_telemetry["gps_lon"]
        }
        
        await self.publish_event(EventType.VEHICLE_UPDATE, vehicle_state, confidence=0.92)
