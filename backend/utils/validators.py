"""
FloraCare AI – Input Validators
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB


async def validate_image_upload(file: UploadFile) -> bytes:
    """
    Validate and read an uploaded image file.
    Returns file bytes.
    Raises HTTPException 400 on invalid input.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_format",
                "message": (
                    f"Unsupported file type '{file.content_type}'. "
                    f"Please upload a JPEG, PNG, or WEBP image."
                ),
            },
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "empty_file", "message": "The uploaded file is empty."},
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        size_mb = len(content) / 1024 / 1024
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "file_too_large",
                "message": (
                    f"Image is too large ({size_mb:.1f} MB). "
                    f"Maximum allowed size is 10 MB."
                ),
            },
        )

    return content


def validate_flower_id(flower_id: int) -> None:
    """Raise HTTPException if flower_id is outside valid range 1–102."""
    if not (1 <= flower_id <= 102):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_flower_id",
                "message": f"Flower ID must be between 1 and 102. Got: {flower_id}",
            },
        )


def validate_environment_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    """
    Clamp and validate environmental input values.
    Returns the validated (and clamped) dict.
    """
    validated: dict[str, Any] = {}
    errors: list[str] = []

    # Temperature: -30 to 50 °C
    temp = inputs.get("temperature")
    if temp is not None:
        try:
            t = float(temp)
            if not (-30 <= t <= 50):
                errors.append(f"Temperature must be between -30 and 50 °C. Got: {t}")
            else:
                validated["temperature"] = round(t, 1)
        except (TypeError, ValueError):
            errors.append("Temperature must be a number.")
    else:
        validated["temperature"] = None

    # Humidity: 0–100 %
    humidity = inputs.get("humidity")
    if humidity is not None:
        try:
            h = float(humidity)
            if not (0 <= h <= 100):
                errors.append(f"Humidity must be between 0 and 100 %. Got: {h}")
            else:
                validated["humidity"] = round(h, 1)
        except (TypeError, ValueError):
            errors.append("Humidity must be a number.")
    else:
        validated["humidity"] = None

    # Sunlight hours: 0–24
    sunlight = inputs.get("sunlight_hours")
    if sunlight is not None:
        try:
            s = float(sunlight)
            if not (0 <= s <= 24):
                errors.append(f"Sunlight hours must be between 0 and 24. Got: {s}")
            else:
                validated["sunlight_hours"] = round(s, 1)
        except (TypeError, ValueError):
            errors.append("Sunlight hours must be a number.")
    else:
        validated["sunlight_hours"] = None

    # Soil pH: 3.0–9.0
    ph = inputs.get("soil_ph")
    if ph is not None:
        try:
            p = float(ph)
            if not (3.0 <= p <= 9.0):
                errors.append(f"Soil pH must be between 3.0 and 9.0. Got: {p}")
            else:
                validated["soil_ph"] = round(p, 1)
        except (TypeError, ValueError):
            errors.append("Soil pH must be a number.")
    else:
        validated["soil_ph"] = None

    # Soil type: string
    soil_type = inputs.get("soil_type")
    valid_soils = {"sandy", "loamy", "clay", "silty", "peaty", "chalky", "orchid_bark", "laterite", "other"}
    if soil_type:
        st = str(soil_type).lower().strip()
        if st not in valid_soils:
            st = "other"
        validated["soil_type"] = st
    else:
        validated["soil_type"] = None

    # Watering frequency: string
    watering = inputs.get("watering_frequency")
    valid_watering = {"daily", "twice_a_week", "once_a_week", "twice_a_month", "rarely", "other"}
    if watering:
        w = str(watering).lower().strip().replace(" ", "_")
        if w not in valid_watering:
            w = "other"
        validated["watering_frequency"] = w
    else:
        validated["watering_frequency"] = None

    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "invalid_environment_inputs",
                "message": "One or more environment values are invalid.",
                "validation_errors": errors,
            },
        )

    return validated
