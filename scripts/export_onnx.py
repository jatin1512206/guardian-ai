import torch
import os
from backend.models.driver_monitor import DriverMonitorModel
from backend.models.vehicle_behavior import VehicleBehaviorModel

def export_models():
    os.makedirs("./checkpoints", exist_ok=True)
    
    # 1. Export driver CNN
    driver = DriverMonitorModel()
    dummy_img = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        driver, dummy_img, "./checkpoints/driver_monitor.onnx",
        export_params=True, opset_version=12,
        input_names=["input"], output_names=["output"]
    )
    print("Exported driver_monitor.onnx successfully.")

    # 2. Export vehicle sequence model
    vehicle = VehicleBehaviorModel()
    dummy_seq = torch.randn(1, 50, 10)
    torch.onnx.export(
        vehicle, dummy_seq, "./checkpoints/vehicle_behavior.onnx",
        export_params=True, opset_version=12,
        input_names=["input"], output_names=["output"]
    )
    print("Exported vehicle_behavior.onnx successfully.")

if __name__ == "__main__":
    export_models()
