"""
FloraCare AI – Image Preprocessor
Handles image validation, plant detection heuristic, and tensor preparation.
"""
from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image, UnidentifiedImageError
#import torch
#import torchvision.transforms as T

from ml_model.config import IMAGE_SIZE, IMAGENET_MEAN, IMAGENET_STD

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Supported MIME types → file extensions
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_FILE_SIZE_MB = 10

# ── Transforms ─────────────────────────────────────────────────────────────────
#_val_transform = T.Compose([
 #   T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
  #  T.ToTensor(),
   # T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
#])


def validate_image_format(file_bytes: bytes, filename: str = "") -> None:
    """
    Validate that file_bytes represent a supported image format.
    Raises ValueError with a user-friendly message on failure.
    """
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(
            f"Image file is too large ({len(file_bytes) / 1024 / 1024:.1f} MB). "
            f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
        )
    try:
        img = Image.open(io.BytesIO(file_bytes))
        fmt = (img.format or "").upper()
        if fmt not in ALLOWED_FORMATS:
            raise ValueError(
                f"Unsupported image format '{fmt}'. "
                f"Please upload a JPEG, PNG, or WEBP image."
            )
    except UnidentifiedImageError:
        raise ValueError(
            "The uploaded file could not be identified as a valid image. "
            "Please upload a JPEG, PNG, or WEBP image."
        )


def load_image_from_bytes(file_bytes: bytes) -> Image.Image:
    """
    Open image bytes and convert to RGB PIL Image.
    Raises ValueError if the image cannot be opened.
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
        return img.convert("RGB")
    except Exception as exc:
        raise ValueError(f"Could not open image: {exc}") from exc

def is_plant_image(pil_image: Image.Image) -> dict:
    """
    Lightweight validation for plant/flower images.

    This intentionally avoids rejecting pale or white flowers.
    The trained flower classifier performs the actual identification.
    """
    w, h = pil_image.size

    if w < 64 or h < 64:
        return {
            "is_plant": False,
            "confidence": 0.0,
            "green_fraction": 0.0,
            "vivid_fraction": 0.0,
            "reason": "Image resolution is too low (less than 64×64 pixels).",
        }

    small = pil_image.resize((128, 128))
    arr = np.array(small, dtype=np.float32) / 255.0

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # Green foliage
    green_mask = (
        (g > r * 1.05) &
        (g > b * 1.05) &
        (g > 0.15)
    )
    green_fraction = float(green_mask.mean())

    # Saturated flower colours
    max_c = np.maximum(r, np.maximum(g, b))
    min_c = np.minimum(r, np.minimum(g, b))
    sat = np.where(
        max_c > 0.05,
        (max_c - min_c) / (max_c + 1e-6),
        0.0,
    )

    vivid_mask = (
        (sat > 0.25) &
        (max_c > 0.20)
    )
    vivid_fraction = float(vivid_mask.mean())

    # Bright/light petals — important for white and pale flowers
    bright_mask = (
        (r > 0.75) &
        (g > 0.75) &
        (b > 0.75)
    )
    bright_fraction = float(bright_mask.mean())

    # Be permissive here. The ML classifier performs identification.
    score = min(
        1.0,
        green_fraction * 2.5
        + vivid_fraction * 1.8
        + bright_fraction * 0.5
    )

    is_plant = (
        green_fraction >= 0.03
        or vivid_fraction >= 0.05
        or bright_fraction >= 0.20
    )

    if green_fraction >= 0.03:
        reason = f"Detected green plant content ({green_fraction:.0%})."
    elif vivid_fraction >= 0.05:
        reason = f"Detected coloured flower regions ({vivid_fraction:.0%})."
    elif bright_fraction >= 0.20:
        reason = f"Detected bright/pale flower regions ({bright_fraction:.0%})."
    else:
        reason = "Image passed basic resolution checks."

    return {
        "is_plant": bool(is_plant),
        "confidence": round(score, 3),
        "green_fraction": round(green_fraction, 3),
        "vivid_fraction": round(vivid_fraction, 3),
        "reason": reason,
    }


def preprocess_image(pil_image: Image.Image):
    """
    Prepare an image for ONNX Runtime.

    Returns:
        numpy.ndarray with shape (1, 3, 224, 224), float32.
    """
    image = pil_image.convert("RGB")
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))

    arr = np.array(image, dtype=np.float32) / 255.0

    # HWC -> CHW
    arr = np.transpose(arr, (2, 0, 1))

    mean = np.array(IMAGENET_MEAN, dtype=np.float32).reshape(3, 1, 1)
    std = np.array(IMAGENET_STD, dtype=np.float32).reshape(3, 1, 1)

    arr = (arr - mean) / std

    # Add batch dimension: (3,224,224) → (1,3,224,224)
    return np.expand_dims(arr, axis=0).astype(np.float32)


def get_image_visual_features(pil_image: Image.Image) -> dict:
    """
    Extract simple visual descriptors from an image.
    Used for the explainability module.

    Returns:
        dict: {
            "dominant_colors": list[str],   # e.g. ["pink", "green", "white"]
            "avg_brightness": float,         # 0-100
            "color_diversity": float,        # 0-1
            "green_fraction": float,
            "vivid_fraction": float
        }
    """
    small = pil_image.resize((64, 64))
    arr = np.array(small, dtype=np.float32) / 255.0

    r, g, b = arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean()
    avg_brightness = float((r + g + b) / 3 * 100)

    # Dominant colour heuristic
    dominant_colors: list[str] = []
    if g > 0.25 and g > r and g > b:
        dominant_colors.append("green")
    if r > 0.35 and r > g * 1.1:
        dominant_colors.append("red/pink")
    if b > 0.30 and b > r:
        dominant_colors.append("blue/purple")
    if r > 0.45 and g > 0.35 and b < 0.25:
        dominant_colors.append("yellow/orange")
    if r > 0.55 and g > 0.55 and b > 0.55:
        dominant_colors.append("white")
    if not dominant_colors:
        dominant_colors.append("mixed")

    # Colour diversity: std across all pixel values
    color_diversity = float(np.std(arr))

    plant_info = is_plant_image(pil_image)

    return {
        "dominant_colors": dominant_colors,
        "avg_brightness": round(avg_brightness, 1),
        "color_diversity": round(color_diversity, 3),
        "green_fraction": plant_info["green_fraction"],
        "vivid_fraction": plant_info["vivid_fraction"],
    }
