"""
Model Export Script

This script is used for exporting a trained segmentation model to ONNX format and optionally quantizing the model.

The script takes a YAML configuration file as input, which specifies the paths to the trained model checkpoint,
input tensor shape, and other configuration parameters.

Usage:
    python <model>_export.py <config_path>

Args:
    config_path (str): Path to the YAML configuration file containing model export parameters.
"""

import sys

import torch
import segmentation_models_pytorch as smp

from src.models.deeplab.model import DeepLab
from src.models.inference import export_model_onnx, quantize_onnx
from src.models.utils.config import read_yaml_config

if __name__ == "__main__":
    config_path = sys.argv[1]
    config_handler = read_yaml_config(config_path)

    model_checkpoint_path = config_handler.read("checkpoint_path")
    net = smp.DeepLabV3Plus(encoder_name="resnet34")

    model = DeepLab(net=net)
    model.load_state_dict(torch.load(model_checkpoint_path))

    input_tensor_shape = config_handler.read('input_tensor_shape')

    export_model_onnx(
        model,
        config_handler=config_handler
    )

    if config_handler.read('acceleration', 'quantization'):
        quantize_onnx(config_handler)
