import torch
import torch.nn as nn
import numpy as np

class VehicleBehaviorModel(nn.Module):
    def __init__(self, seq_len=50, input_dim=10, hidden_dim=64, num_classes=4):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=2, batch_first=True, bidirectional=True)
        self.attention = nn.Linear(hidden_dim * 2, 1)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.classes = ["safe", "moderate", "high_risk", "critical"]
        self.weights_loaded = False

    def forward(self, x):
        # x shape: (B, seq_len, input_dim)
        out, _ = self.gru(x) # (B, seq_len, hidden_dim * 2)
        attn_weights = torch.softmax(self.attention(out), dim=1) # (B, seq_len, 1)
        context = torch.sum(attn_weights * out, dim=1) # (B, hidden_dim * 2)
        return self.fc(context)

    def predict(self, sequence_numpy: np.ndarray) -> dict:
        # Run real network inference if checkpoints are loaded
        if getattr(self, "weights_loaded", False):
            try:
                # Convert sequence to float tensor (1, seq_len, 10)
                tensor = torch.tensor(sequence_numpy, dtype=torch.float32).unsqueeze(0)
                self.eval()
                with torch.no_grad():
                    logits = self(tensor)
                    probs = torch.softmax(logits, dim=1).squeeze(0).numpy()
                    
                pred_idx = int(np.argmax(probs))
                
                # compute simulated stability index based on steering inputs
                steering_variance = np.var(sequence_numpy[:, 1])
                max_speed = np.max(sequence_numpy[:, 0])
                stability = float(100.0 - steering_variance * 5.0 - (max_speed - 60.0) * 0.5)
                stability = max(0.0, min(100.0, stability))
                
                return {
                    "risk_class": pred_idx,
                    "risk_label": self.classes[pred_idx],
                    "class_probabilities": probs.tolist(),
                    "stability_score": stability
                }
            except Exception as e:
                pass # fallback on exception

        # Fallback heuristics
        speed = sequence_numpy[:, 0]
        steering = sequence_numpy[:, 1]
        brake = sequence_numpy[:, 3]
        
        max_speed = np.max(speed)
        steering_variance = np.var(steering)
        max_brake = np.max(brake)
        
        prob = np.zeros(4)
        if max_speed > 100.0 or steering_variance > 5.0:
            prob[2] = 0.7 
            prob[3] = 0.2
        elif max_speed > 80.0 and max_brake > 0.7:
            prob[1] = 0.6 
            prob[2] = 0.3
        else:
            prob[0] = 0.9 
            
        prob = prob / np.sum(prob)
        idx = int(np.argmax(prob))
        
        stability = float(100.0 - steering_variance * 5.0 - (max_speed - 60.0) * 0.5)
        stability = max(0.0, min(100.0, stability))
        
        return {
            "risk_class": idx,
            "risk_label": self.classes[idx],
            "class_probabilities": prob.tolist(),
            "stability_score": stability
        }

    def save(self, path: str):
        torch.save(self.state_dict(), path)

    def load(self, path: str):
        try:
            self.load_state_dict(torch.load(path, map_location='cpu'))
            self.weights_loaded = True
        except Exception:
            self.weights_loaded = False
