import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np

# Import models
from backend.models.driver_monitor import DriverMonitorModel
from backend.models.vehicle_behavior import VehicleBehaviorModel
from backend.models.sensor_fusion import SensorFusionModel
from backend.models.accident_predictor import AccidentPredictor

# Ensure checkpoints folder exists
os.makedirs("checkpoints", exist_ok=True)

def train_driver_monitor():
    print("\n--- Training DriverMonitorModel ---")
    model = DriverMonitorModel(num_classes=10)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    # Generate mock image tensors (B, 3, 224, 224) and labels
    x_train = torch.randn(64, 3, 224, 224)
    y_train = torch.randint(0, 10, (64,))
    
    dataset = TensorDataset(x_train, y_train)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    model.train()
    for epoch in range(3):
        total_loss = 0.0
        for x_batch, y_batch in loader:
            optimizer.zero_grad()
            out = model(x_batch)
            loss = criterion(out, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/3 - Loss: {total_loss/len(loader):.4f}")
        
    model.save("checkpoints/driver_monitor.pt")
    print("Saved driver_monitor.pt")

def train_vehicle_behavior():
    print("\n--- Training VehicleBehaviorModel ---")
    model = VehicleBehaviorModel(seq_len=50, input_dim=10, num_classes=4)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    # Generate mock sequence tensors (B, 50, 10) and labels (0-3)
    x_train = torch.randn(128, 50, 10)
    y_train = torch.randint(0, 4, (128,))
    
    dataset = TensorDataset(x_train, y_train)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model.train()
    for epoch in range(3):
        total_loss = 0.0
        for x_batch, y_batch in loader:
            optimizer.zero_grad()
            out = model(x_batch)
            loss = criterion(out, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/3 - Loss: {total_loss/len(loader):.4f}")
        
    model.save("checkpoints/vehicle_behavior.pt")
    print("Saved vehicle_behavior.pt")

def train_sensor_fusion():
    print("\n--- Training SensorFusionModel ---")
    model = SensorFusionModel(d_driver=32, d_vehicle=32, d_context=16, d_model=64)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    
    # Generate mock features: driver (B, 32), vehicle (B, 32), context (B, 16)
    d_feat = torch.randn(128, 32)
    v_feat = torch.randn(128, 32)
    c_feat = torch.randn(128, 16)
    # Output target representation (B, 128)
    y_target = torch.randn(128, 128)
    
    dataset = TensorDataset(d_feat, v_feat, c_feat, y_target)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model.train()
    for epoch in range(3):
        total_loss = 0.0
        for d_b, v_b, c_b, y_b in loader:
            optimizer.zero_grad()
            out = model(d_b, v_b, c_b)
            loss = criterion(out, y_b)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/3 - Loss: {total_loss/len(loader):.4f}")
        
    torch.save(model.state_dict(), "checkpoints/sensor_fusion.pt")
    print("Saved sensor_fusion.pt")

def train_accident_predictor():
    print("\n--- Training AccidentPredictor ---")
    model = AccidentPredictor(input_dim=128, hidden_dim=64, seq_len=30)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Loss functions
    bce = nn.BCELoss()
    mse = nn.MSELoss()
    cel = nn.CrossEntropyLoss()
    
    # Mock input: (B, 30, 128)
    x_train = torch.randn(128, 30, 128)
    # Mock targets: prob (B, 1), ttc (B, 1), type (B,)
    y_prob = torch.rand(128, 1)
    y_ttc = torch.rand(128, 1) * 10.0
    y_type = torch.randint(0, 6, (128,))
    
    dataset = TensorDataset(x_train, y_prob, y_ttc, y_type)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model.train()
    for epoch in range(3):
        total_loss = 0.0
        for x_b, yp_b, yt_b, yty_b in loader:
            optimizer.zero_grad()
            prob, ttc, type_logits = model(x_b)
            
            loss_prob = bce(prob, yp_b)
            loss_ttc = mse(ttc, yt_b)
            loss_type = cel(type_logits, yty_b)
            
            loss = loss_prob + loss_ttc * 0.1 + loss_type * 0.5
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/3 - Loss: {total_loss/len(loader):.4f}")
        
    torch.save(model.state_dict(), "checkpoints/accident_predictor.pt")
    print("Saved accident_predictor.pt")

if __name__ == "__main__":
    train_driver_monitor()
    train_vehicle_behavior()
    train_sensor_fusion()
    train_accident_predictor()
    print("\n🎉 All models trained and checkpoints saved successfully!")
