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
import torch
import torchvision.transforms as T

from ml_model.config import IMAGE_SIZE, IMAGENET_MEAN, IMAGENET_STD

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Supported MIME types → file extensions
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_FILE_SIZE_MB = 10

# ── Transforms ─────────────────────────────────────────────────────────────────
_val_transform = T.Compose([
    T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])


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
    Heuristic check: does this image likely contain a plant or flower?

    Strategy:
    - Convert to HSV colour space (using numpy approximation)
    - Check fraction of pixels that are green (plant foliage)
    - Check fraction of pixels that are vivid / saturated (flower petals)
    - Minimum resolution check (very small images are likely icons)

    Returns:
        dict: {
            "is_plant": bool,
            "confidence": float,   # 0.0–1.0
            "green_fraction": float,
            "vivid_fraction": float,
            "reason": str
        }
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

    # Resize to 128×128 for fast analysis
    small = pil_image.resize((128, 128))
    arr = np.array(small, dtype=np.float32) / 255.0  # shape (128,128,3) RGB

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # ── Green detection (foliage) ──────────────────────────────────────────────
    # A pixel is "green" if G is dominant, not too dark, not too grey
    green_mask = (
        (g > r * 1.05) &     # green channel dominant
        (g > b * 1.05) &     # green brighter than blue
        (g > 0.15)           # not too dark
    )
    green_fraction = float(green_mask.mean())

    # ── Vivid / saturated colour detection (flower petals) ───────────────────
    # Compute a rough saturation estimate: (max - min) / max
    max_c = np.maximum(r, np.maximum(g, b))
    min_c = np.minimum(r, np.minimum(g, b))
    sat = np.where(max_c > 0.05, (max_c - min_c) / (max_c + 1e-6), 0.0)

    # Vivid = high saturation AND not too dark AND not nearly white
    vivid_mask = (sat > 0.35) & (max_c > 0.20) & (max_c < 0.97)
    vivid_fraction = float(vivid_mask.mean())

    # ── Decision ──────────────────────────────────────────────────────────────
    # Score = weighted combination; either green (foliage) or vivid (petals)
    score = min(1.0, green_fraction * 2.5 + vivid_fraction * 1.8)
    is_plant = score >= 0.30

    if green_fraction > 0.08:
        reason = f"Detected significant green (plant) content ({green_fraction:.0%} of pixels)."
    elif vivid_fraction > 0.12:
        reason = f"Detected vivid coloured regions ({vivid_fraction:.0%} of pixels) typical of flower petals."
    else:
        reason = (
            f"The image has limited green ({green_fraction:.0%}) and low colour saturation "
            f"({vivid_fraction:.0%}). It may not be a flower or plant image."
        )

    return {
        "is_plant": is_plant,
        "confidence": round(score, 3),
        "green_fraction": round(green_fraction, 3),
        "vivid_fraction": round(vivid_fraction, 3),
        "reason": reason,
    }


def preprocess_image(pil_image: Image.Image) -> torch.Tensor:
    """
    Apply ImageNet normalisation and resize to 224×224.

    Args:
        pil_image: RGB PIL Image of any size.

    Returns:
        torch.Tensor: shape (1, 3, 224, 224), float32, ImageNet-normalised.
    """
    tensor = _val_transform(pil_image)   # (3, 224, 224)
    return tensor.unsqueeze(0)           # (1, 3, 224, 224)


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
