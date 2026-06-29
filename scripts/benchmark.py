import time
import torch
import numpy as np
from backend.models.driver_monitor import DriverMonitorModel
from backend.models.vehicle_behavior import VehicleBehaviorModel

def run_benchmarks():
    print("==================================================")
    print("            GUARDIANAI MODEL BENCHMARKS           ")
    print("==================================================")
    
    # Driver model
    driver = DriverMonitorModel()
    driver.eval()
    times = []
    
    for _ in range(50):
        t0 = time.time()
        with torch.no_grad():
            img = torch.randn(1, 3, 224, 224)
            _ = driver(img)
        times.append(time.time() - t0)
        
    print(f"Driver CNN Inference (CPU): Mean={np.mean(times)*1000:.2f}ms, P95={np.percentile(times, 95)*1000:.2f}ms")

    # Vehicle sequence GRU
    vehicle = VehicleBehaviorModel()
    vehicle.eval()
    times_v = []
    
    for _ in range(50):
        t0 = time.time()
        with torch.no_grad():
            seq = torch.randn(1, 50, 10)
            _ = vehicle(seq)
        times_v.append(time.time() - t0)
        
    print(f"Vehicle GRU Inference (CPU): Mean={np.mean(times_v)*1000:.2f}ms, P95={np.percentile(times_v, 95)*1000:.2f}ms")
    print("==================================================")

if __name__ == "__main__":
    run_benchmarks()
