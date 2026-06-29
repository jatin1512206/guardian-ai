import torch
import torch.nn as nn

class SensorFusionModel(nn.Module):
    def __init__(self, d_driver=32, d_vehicle=32, d_context=16, d_model=64):
        super().__init__()
        self.proj_driver = nn.Linear(d_driver, d_model)
        self.proj_vehicle = nn.Linear(d_vehicle, d_model)
        self.proj_context = nn.Linear(d_context, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=4, dim_feedforward=128, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        self.out_proj = nn.Linear(d_model * 3, 128)

    def forward(self, driver_feat, vehicle_feat, context_feat):
        d = self.proj_driver(driver_feat).unsqueeze(1) # (B, 1, d_model)
        v = self.proj_vehicle(vehicle_feat).unsqueeze(1) # (B, 1, d_model)
        c = self.proj_context(context_feat).unsqueeze(1) # (B, 1, d_model)
        
        tokens = torch.cat([d, v, c], dim=1) # (B, 3, d_model)
        fused = self.transformer(tokens) # (B, 3, d_model)
        
        fused_flat = fused.view(fused.size(0), -1) # (B, 3 * d_model)
        return self.out_proj(fused_flat) # (B, 128)

    def fuse(self, driver_dict: dict, vehicle_dict: dict) -> torch.Tensor:
        # Utility to generate fused tensor representation for real-time inference
        t = torch.zeros(1, 128)
        # Simulating projection features
        t[0, 0] = driver_dict.get("attention_score", 100.0) / 100.0
        t[0, 1] = driver_dict.get("fatigue_score", 0.0) / 100.0
        t[0, 2] = vehicle_dict.get("speed", 0.0) / 120.0
        t[0, 3] = vehicle_dict.get("steering_angle", 0.0) / 45.0
        return t
