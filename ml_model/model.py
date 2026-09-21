"""
FloraCare AI – MobileNetV2 Model Definition & Loader
"""
from __future__ import annotations

import logging
import os

#import torch
#import torch.nn as nn
#import torchvision.models as models

from ml_model.config import MODEL_PATH, NUM_CLASSES, DROPOUT_RATE

logger = logging.getLogger(__name__)


class ModelNotAvailableError(RuntimeError):
    """Raised when the trained model weights are not found."""

    MESSAGE = (
        "The trained flower identification model is not available. "
        "Please run: python ml_model/train.py  — this will download the Oxford 102 "
        "Flowers dataset and fine-tune MobileNetV2. Training takes 30–120 minutes "
        "depending on your hardware. Once complete, restart the backend server."
    )

    def __init__(self, custom_message: str | None = None) -> None:
        super().__init__(custom_message or self.MESSAGE)


def build_model(num_classes: int = NUM_CLASSES) -> nn.Module:
    """
    Build MobileNetV2 with a custom classification head.

    Architecture:
        MobileNetV2 feature extractor (pretrained on ImageNet)
        └─► AdaptiveAvgPool2d → Flatten → Dropout(0.2) → Linear(1280, num_classes)

    Returns:
        nn.Module (not loaded with trained weights yet)
    """
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

    # Replace classifier head
    in_features = model.classifier[1].in_features  # 1280 for MobileNetV2
    model.classifier = nn.Sequential(
        nn.Dropout(p=DROPOUT_RATE, inplace=True),
        nn.Linear(in_features, num_classes),
    )

    return model


def freeze_base(model: nn.Module) -> nn.Module:
    """Freeze all feature layers; leave classifier trainable (phase 1)."""
    for param in model.features.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True
    return model


def unfreeze_top_layers(model: nn.Module, num_blocks: int = 4) -> nn.Module:
    """
    Unfreeze the last `num_blocks` feature blocks for fine-tuning (phase 2).
    MobileNetV2 has 19 feature sub-modules (features[0..18]).
    """
    # First freeze everything
    for param in model.features.parameters():
        param.requires_grad = False
    # Then unfreeze the last N blocks
    for block in list(model.features)[-num_blocks:]:
        for param in block.parameters():
            param.requires_grad = True
    for param in model.classifier.parameters():
        param.requires_grad = True
    return model


def load_model(path: str | None = None) -> nn.Module:
    """
    Load trained MobileNetV2 weights and return the model in eval mode.

    Args:
        path: Path to the .pth checkpoint. Defaults to MODEL_PATH from config.

    Returns:
        nn.Module in eval mode, on CPU (or CUDA if available).

    Raises:
        ModelNotAvailableError: If the weight file does not exist.
    """
    weights_path = path or MODEL_PATH

    if not os.path.isfile(weights_path):
        raise ModelNotAvailableError()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_model()

    try:
        state_dict = torch.load(weights_path, map_location=device)
        # Support checkpoints saved as {"model_state_dict": ...}
        if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
            state_dict = state_dict["model_state_dict"]
        model.load_state_dict(state_dict)
    except Exception as exc:
        raise ModelNotAvailableError(
            f"Found model file at '{weights_path}' but failed to load weights: {exc}. "
            "The file may be corrupted. Please re-train the model."
        ) from exc

    model.to(device)
    model.eval()
    logger.info("✅ Model loaded from '%s' on %s", weights_path, device)
    return model


def get_model_info() -> dict:
    """
    Return availability status and metadata about the trained model.

    Returns:
        dict: {
            "available": bool,
            "path": str,
            "size_mb": float | None,
            "message": str
        }
    """
    path = MODEL_PATH
    if os.path.isfile(path):
        size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)
        return {
            "available": True,
            "path": path,
            "size_mb": size_mb,
            "message": f"Trained model found ({size_mb} MB). Ready for predictions.",
        }
    return {
        "available": False,
        "path": path,
        "size_mb": None,
        "message": ModelNotAvailableError.MESSAGE,
    }
