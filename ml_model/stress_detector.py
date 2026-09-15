"""
FloraCare AI – Plant Stress Detector
Visual analysis of uploaded plant images for possible stress indicators.

IMPORTANT DISCLAIMER:
This module uses image colour analysis heuristics (OpenCV/NumPy).
Results are approximations only. All output is labelled as 'Possible'
stress indicators. This is NOT a medical or scientific diagnosis.
Always verify with physical plant inspection.
"""
from __future__ import annotations

import logging

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ── Colour thresholds (HSV space, OpenCV convention: H 0-179, S 0-255, V 0-255) ─
# Yellowing leaves: yellow-green hue range
YELLOW_H_MIN, YELLOW_H_MAX = 20, 40
YELLOW_S_MIN, YELLOW_V_MIN = 60, 80

# Brown spots: brownish hue
BROWN_H_MIN, BROWN_H_MAX = 8, 22
BROWN_S_MIN, BROWN_S_MAX = 40, 200
BROWN_V_MIN, BROWN_V_MAX = 40, 160

# Healthy green: reference to distinguish from yellowing
GREEN_H_MIN, GREEN_H_MAX = 35, 85
GREEN_S_MIN, GREEN_V_MIN = 50, 50

# Threshold fractions for detection
YELLOWING_THRESHOLD  = 0.08   # 8% of pixels
BROWN_SPOT_THRESHOLD = 0.04   # 4% of pixels


def _pil_to_bgr(pil_image: Image.Image) -> np.ndarray:
    """Convert PIL RGB image to OpenCV BGR array."""
    arr = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _detect_yellowing(bgr: np.ndarray, hsv: np.ndarray) -> dict | None:
    """Detect yellowing leaves via yellow-green HSV range."""
    mask = cv2.inRange(
        hsv,
        np.array([YELLOW_H_MIN, YELLOW_S_MIN, YELLOW_V_MIN]),
        np.array([YELLOW_H_MAX, 255, 255]),
    )
    fraction = float(mask.sum() / 255) / (bgr.shape[0] * bgr.shape[1])

    if fraction >= YELLOWING_THRESHOLD:
        confidence = (
            "high"     if fraction > 0.20
            else "moderate"  if fraction > 0.12
            else "low"
        )
        return {
            "type": "yellowing",
            "label": "Possible Yellowing",
            "confidence": confidence,
            "fraction": round(fraction, 3),
            "description": (
                f"Approximately {fraction:.0%} of the image shows yellow-green tones, "
                f"which may indicate leaf yellowing (chlorosis)."
            ),
            "possible_causes": ["overwatering", "underwatering", "nitrogen deficiency", "natural ageing"],
            "recommended_action": "Check soil moisture and watering frequency. Inspect roots for rot.",
            "disclaimer": "Possible stress detected — manual inspection recommended.",
        }
    return None


def _detect_brown_spots(bgr: np.ndarray, hsv: np.ndarray) -> dict | None:
    """Detect brown spots or leaf scorch via brownish HSV range."""
    mask = cv2.inRange(
        hsv,
        np.array([BROWN_H_MIN, BROWN_S_MIN, BROWN_V_MIN]),
        np.array([BROWN_H_MAX, BROWN_S_MAX, BROWN_V_MAX]),
    )
    fraction = float(mask.sum() / 255) / (bgr.shape[0] * bgr.shape[1])

    if fraction >= BROWN_SPOT_THRESHOLD:
        confidence = (
            "high"    if fraction > 0.12
            else "moderate" if fraction > 0.06
            else "low"
        )
        return {
            "type": "brown_spots",
            "label": "Possible Brown Spots / Leaf Scorch",
            "confidence": confidence,
            "fraction": round(fraction, 3),
            "description": (
                f"Approximately {fraction:.0%} of the image contains brownish tones, "
                f"which may indicate brown spots, leaf scorch, or fungal lesions."
            ),
            "possible_causes": ["fungal disease", "sunburn", "underwatering", "fertiliser burn", "bacterial infection"],
            "recommended_action": "Inspect leaves closely. Check watering, sunlight intensity, and fertiliser application.",
            "disclaimer": "Possible stress detected — manual inspection recommended.",
        }
    return None


def _detect_wilting(bgr: np.ndarray, hsv: np.ndarray) -> dict | None:
    """
    Heuristic wilting detection: analyse texture variance and
    overall brightness uniformity. Low texture + low saturation can
    indicate wilted/flaccid tissue.
    """
    # Convert to grayscale for texture analysis
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Laplacian variance as a sharpness / texture measure
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Low-saturation regions (potential wilted tissue)
    low_sat_mask = hsv[:, :, 1] < 40
    low_sat_fraction = float(low_sat_mask.mean())

    # Only flag if texture is VERY low AND lots of low-saturation area
    if lap_var < 50 and low_sat_fraction > 0.35:
        return {
            "type": "wilting",
            "label": "Possible Wilting / Low Vigour",
            "confidence": "low",
            "fraction": round(low_sat_fraction, 3),
            "description": (
                f"The image shows low texture contrast and high low-saturation areas ({low_sat_fraction:.0%}), "
                f"which may be consistent with wilting or plant stress."
            ),
            "possible_causes": ["underwatering", "overwatering (root rot)", "heat stress", "transplant shock"],
            "recommended_action": "Check soil moisture. Ensure plant is not in direct midday sun if heat-sensitive.",
            "disclaimer": "Possible stress detected — manual inspection recommended.",
        }
    return None


def detect_stress(pil_image: Image.Image) -> dict:
    """
    Analyse a PIL image for visible plant stress indicators.

    All findings are heuristic approximations using colour analysis.
    Results are clearly labelled as 'Possible' and include disclaimers.

    Args:
        pil_image: RGB PIL Image of the plant.

    Returns:
        dict: {
            "stress_detected": bool,
            "possible_issues": list[dict],
            "overall_stress_level": "none" | "low" | "moderate" | "high",
            "analysis_note": str,
        }
    """
    try:
        bgr = _pil_to_bgr(pil_image)
        # Resize for consistent analysis
        bgr = cv2.resize(bgr, (256, 256))
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        issues: list[dict] = []

        yellow = _detect_yellowing(bgr, hsv)
        if yellow:
            issues.append(yellow)

        brown = _detect_brown_spots(bgr, hsv)
        if brown:
            issues.append(brown)

        wilt = _detect_wilting(bgr, hsv)
        if wilt:
            issues.append(wilt)

        # Overall stress level
        if not issues:
            level = "none"
        elif any(i["confidence"] == "high" for i in issues) or len(issues) >= 2:
            level = "high"
        elif any(i["confidence"] == "moderate" for i in issues):
            level = "moderate"
        else:
            level = "low"

        return {
            "stress_detected": bool(issues),
            "possible_issues": issues,
            "overall_stress_level": level,
            "analysis_note": (
                "This is an AI-generated visual colour analysis — NOT a scientific diagnosis. "
                "Results should always be verified with physical inspection of the plant. "
                "Image quality, lighting and shadows significantly affect analysis accuracy."
            ),
        }

    except Exception as exc:
        logger.warning("Stress detection failed: %s", exc)
        return {
            "stress_detected": False,
            "possible_issues": [],
            "overall_stress_level": "none",
            "analysis_note": (
                "Stress analysis could not be completed for this image. "
                "Please inspect the plant manually."
            ),
        }
