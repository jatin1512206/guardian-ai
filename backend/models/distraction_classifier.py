import torch
import torch.nn as nn
import numpy as np

class DistractionClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1)
        )
        self.fc = nn.Linear(32, 5)
        self.classes = ["phone_usage", "eating", "smoking", "no_seatbelt", "hands_off_wheel"]

    def forward(self, x):
        features = self.conv(x)
        features = features.view(features.size(0), -1)
        return self.fc(features)

    def predict(self, frame_numpy: np.ndarray) -> dict:
        # Mock features extraction based on spatial brightness variances
        var_h = np.var(np.mean(frame_numpy, axis=1))
        
        prob = 0.02
        distractions = []
        
        if var_h > 1500: # Simulated high activity in frame
            prob = 0.72
            distractions.append("phone_usage")
            distractions.append("hands_off_wheel")
            
        return {
            "distractions": distractions,
            "distraction_probability": prob,
            "is_distracted": len(distractions) > 0,
            "confidence": 0.88 if len(distractions) > 0 else 0.95
        }

    def save(self, path: str):
        torch.save(self.state_dict(), path)

    def load(self, path: str):
        try:
            self.load_state_dict(torch.load(path, map_location='cpu'))
        except Exception:
            pass
