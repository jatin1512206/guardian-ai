import numpy as np
import time
from datetime import datetime

class SyntheticDataGenerator:
    def __init__(self):
        self.step = 0
        self.scenario = "normal"
        self.scenario_timer = 0

    def set_scenario(self, scenario: str):
        self.scenario = scenario
        self.scenario_timer = 30 # Scenario lasts 30 steps

    def next_step(self) -> dict:
        self.step += 1
        
        # Automatically rotate scenarios if not fixed
        if self.scenario_timer > 0:
            self.scenario_timer -= 1
        else:
            scenarios = ["normal", "drowsy", "distracted", "aggressive", "recovery"]
            self.scenario = scenarios[(self.step // 100) % len(scenarios)]
            
        timestamp = datetime.utcnow().isoformat()
        
        # Telemetry modeling based on scenario states
        if self.scenario == "normal":
            speed = 60.0 + np.sin(self.step * 0.1) * 2.0
            rpm = 2000.0 + np.sin(self.step * 0.1) * 100.0
            steering = 0.0 + np.random.normal(0, 0.5)
            accel = 0.1
            brake = 0.0
            lane = 0.0 + np.random.normal(0, 0.05)
            
            attn = 95.0 - np.random.normal(0, 1.0)
            fatigue = 10.0 + np.random.normal(0, 0.5)
            distract = 0.05
            is_phone = False
            is_drowsy = False
            
        elif self.scenario == "drowsy":
            speed = 55.0 - (self.step % 20) * 0.5
            rpm = 1800.0 - (self.step % 20) * 15.0
            # Drifting steering
            steering = np.sin(self.step * 0.05) * 4.0
            accel = 0.0
            brake = 0.0
            lane = np.sin(self.step * 0.05) * 0.4 # lane drift
            
            # Heavy drowsiness
            attn = max(40.0, 80.0 - (self.step % 50) * 1.2)
            fatigue = min(95.0, 20.0 + (self.step % 50) * 1.5)
            distract = 0.1
            is_phone = False
            is_drowsy = fatigue > 60.0
            
        elif self.scenario == "distracted":
            speed = 65.0 + np.random.normal(0, 2.0)
            rpm = 2200.0
            steering = 0.0 + np.random.normal(0, 0.8)
            accel = 0.2
            brake = 0.0
            lane = np.random.normal(0, 0.15)
            
            # Driver looking down/using phone
            attn = max(20.0, 50.0 - np.random.normal(0, 5.0))
            fatigue = 12.0
            distract = 0.85
            is_phone = True
            is_drowsy = False
            
        elif self.scenario == "aggressive":
            speed = 95.0 + np.sin(self.step * 0.2) * 10.0
            rpm = 3800.0 + np.sin(self.step * 0.2) * 400.0
            steering = np.sin(self.step * 0.2) * 8.0 # Sharp turns
            accel = 0.8 if np.sin(self.step * 0.2) > 0 else 0.0
            brake = 0.9 if np.sin(self.step * 0.2) <= 0 else 0.0
            lane = np.sin(self.step * 0.2) * 0.3
            
            attn = 85.0
            fatigue = 15.0
            distract = 0.15
            is_phone = False
            is_drowsy = False
            
        else: # recovery
            speed = 50.0 - np.random.normal(0, 0.5)
            rpm = 1500.0
            steering = 0.0
            accel = 0.0
            brake = 0.1
            lane = 0.0
            
            attn = 98.0
            fatigue = 5.0
            distract = 0.01
            is_phone = False
            is_drowsy = False

        # Add physical properties to dict representation
        return {
            "driver_state": {
                "attention_score": float(attn),
                "fatigue_level": float(fatigue),
                "distraction_probability": float(distract),
                "emotion": "neutral" if attn > 60 else "stressed",
                "is_phone": is_phone,
                "is_drowsy": is_drowsy,
                "blink_rate": 12.0 + (fatigue * 0.2),
                "head_yaw": float(steering * 0.2),
                "head_pitch": -5.0 if is_phone else 0.0
            },
            "vehicle_telemetry": {
                "speed": float(speed),
                "rpm": float(rpm),
                "steering_angle": float(steering),
                "acceleration": float(accel),
                "brake_pressure": float(brake),
                "lane_position": float(lane),
                "gps_lat": 28.6139 + (self.step * 0.0001),
                "gps_lon": 77.2090 + (self.step * 0.0001)
            },
            "timestamp": timestamp,
            "scenario": self.scenario
        }

generator = SyntheticDataGenerator()
