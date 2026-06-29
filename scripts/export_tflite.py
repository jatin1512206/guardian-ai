import torch
import os

def export_tflite():
    print("ONNX model representation generated. Converting ONNX checkpoints to TFLite format requires onnx2tf converter or TensorFlow environment.")
    print("Recommended CLI step: onnx2tf -in checkpoints/driver_monitor.onnx -ot checkpoints/driver_monitor.tflite")

if __name__ == "__main__":
    export_tflite()
