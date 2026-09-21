import os
import torch
import torch.nn as nn
import torchvision.models as models

from ml_model.config import MODEL_PATH, NUM_CLASSES, DROPOUT_RATE


# Build the same MobileNetV2 architecture used during training
model = models.mobilenet_v2(
    weights=models.MobileNet_V2_Weights.IMAGENET1K_V1
)

in_features = model.classifier[1].in_features

model.classifier = nn.Sequential(
    nn.Dropout(p=DROPOUT_RATE, inplace=True),
    nn.Linear(in_features, NUM_CLASSES),
)

# Load trained weights
checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
    checkpoint = checkpoint["model_state_dict"]

model.load_state_dict(checkpoint)

model.eval()

# Dummy input: MobileNetV2 expects 224x224 RGB images
dummy_input = torch.randn(1, 3, 224, 224)

# Output ONNX file
output_path = os.path.join(
    os.path.dirname(MODEL_PATH),
    "flower_model.onnx"
)

torch.onnx.export(
    model,
    dummy_input,
    output_path,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"},
    },
    opset_version=17,
)

print(f"ONNX model created successfully: {output_path}")
