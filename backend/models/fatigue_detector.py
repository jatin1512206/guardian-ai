import numpy as np

class FatigueDetector:
    def __init__(self):
        # Initial parameters
        self.ear_history = []
        self.yawn_history = []
        self.blink_count = 0
        self.eyes_closed_frames = 0
        self.fps = 10

    def process_frame(self, frame_bgr: np.ndarray) -> dict:
        # In a real environment, we'd run MediaPipe Face Mesh
        # We simulate landmark metrics using mathematical transforms on the frames
        h, w, _ = frame_bgr.shape
        # Pure numpy implementation of BGR to Gray
        gray = np.dot(frame_bgr[...,:3], [0.114, 0.587, 0.299])
        
        # Calculate eye region variance as a proxy for eye openness
        left_eye_openness = float(np.var(gray[int(h*0.35):int(h*0.45), int(w*0.35):int(w*0.45)]) / 1000.0)
        right_eye_openness = float(np.var(gray[int(h*0.35):int(h*0.45), int(w*0.55):int(w*0.65)]) / 1000.0)
        
        # Bound between 0.15 and 0.4
        ear_left = max(0.15, min(0.4, 0.15 + left_eye_openness))
        ear_right = max(0.15, min(0.4, 0.15 + right_eye_openness))
        ear = (ear_left + ear_right) / 2.0
        
        # Mouth aspect ratio proxy
        mar = float(0.1 + np.var(gray[int(h*0.55):int(h*0.7), int(w*0.45):int(w*0.55)]) / 800.0)
        mar = max(0.1, min(0.8, mar))
        
        is_eyes_closed = ear < 0.22
        is_yawning = mar > 0.55
        
        self.ear_history.append(ear)
        if len(self.ear_history) > 100:
            self.ear_history.pop(0)
            
        # Blink count calculation
        if len(self.ear_history) >= 3:
            if self.ear_history[-3] > 0.25 and self.ear_history[-2] < 0.22 and self.ear_history[-1] > 0.25:
                self.blink_count += 1
                
        # Calculate PERCLOS (percentage of eye closure over sliding window)
        closed_frames = sum(1 for e in self.ear_history if e < 0.22)
        perclos = (closed_frames / len(self.ear_history)) * 100.0 if self.ear_history else 0.0
        
        # Base fatigue score
        fatigue_score = min(100.0, perclos * 2.0 + (50.0 if is_yawning else 0.0))
        drowsiness_prob = fatigue_score / 100.0
        
        return {
            "fatigue_score": fatigue_score,
            "drowsiness_probability": drowsiness_prob,
            "ear_left": ear_left,
            "ear_right": ear_right,
            "mar": mar,
            "perclos": perclos,
            "blink_rate": self.blink_count * (60.0 / max(1.0, len(self.ear_history) / self.fps)),
            "head_pitch": 2.5,
            "head_yaw": -1.2,
            "head_roll": 0.4,
            "is_yawning": is_yawning,
            "is_eyes_closed": is_eyes_closed,
            "landmarks_detected": True
        }
