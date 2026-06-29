import asyncio
import numpy as np
from datetime import datetime, timedelta
from backend.agents.base_agent import BaseAgent
from backend.services.event_bus import event_bus, EventType
from backend.data.synthetic_generator import generator

class DriverBehaviorAgent(BaseAgent):
    def __init__(self):
        super().__init__("driver_behavior")
        # Initialize sub-models
        try:
            from backend.models.driver_monitor import DriverMonitorModel
            from backend.models.fatigue_detector import FatigueDetector
            from backend.models.distraction_classifier import DistractionClassifier
            self.driver_model = DriverMonitorModel()
            
            # Load checkpoints
            import os
            if os.path.exists("checkpoints/driver_monitor.pt"):
                self.driver_model.load("checkpoints/driver_monitor.pt")
                
            self.fatigue_model = FatigueDetector()
            self.distraction_model = DistractionClassifier()
            self.models_loaded = True
        except Exception as e:
            self.logger.warning(f"ML models could not be loaded directly: {e}. Running in simulation/synthetic mode.")
            self.models_loaded = False

    async def process(self):
        # 1. Check if we have active WebRTC camera updates flowing from the browser
        history = event_bus.get_history(30)
        has_live_cam = False
        
        for evt in history:
            if evt.source == "browser_webrtc_cam":
                try:
                    # If we got a live camera frame within the last 2 seconds, pause simulation
                    evt_time = datetime.fromisoformat(evt.timestamp)
                    if (datetime.utcnow() - evt_time).total_seconds() < 2.0:
                        has_live_cam = True
                        break
                except Exception:
                    pass

        if has_live_cam:
            # Live webcam is active, let the browser frames drive the event loop
            return

        # 2. Otherwise, fall back to the synthetic/simulated driver state generator
        step_data = generator.next_step()
        raw_driver = step_data["driver_state"]
        
        if self.models_loaded:
            # Simulated image processing pipeline
            mock_frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            pred_monitor = self.driver_model.predict(mock_frame)
            pred_fatigue = self.fatigue_model.process_frame(mock_frame)
            pred_distraction = self.distraction_model.predict(mock_frame)
            
            driver_state = {
                "attention_score": float(pred_monitor["attention_score"]),
                "fatigue_level": float(pred_fatigue["fatigue_score"]),
                "distraction_probability": float(pred_distraction["distraction_probability"]),
                "emotion": str(pred_monitor["class_name"]),
                "is_phone": bool(pred_distraction["is_distracted"]),
                "is_drowsy": bool(pred_fatigue["is_eyes_closed"]),
                "blink_rate": float(pred_fatigue["blink_rate"]),
                "head_yaw": float(pred_fatigue["head_yaw"]),
                "head_pitch": float(pred_fatigue["head_pitch"])
            }
        else:
            driver_state = raw_driver
            
        await self.publish_event(EventType.DRIVER_STATE_UPDATE, driver_state, confidence=0.95)
