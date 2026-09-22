from __future__ import annotations

import io
import logging

import numpy as np
import onnxruntime as ort
from PIL import Image, UnidentifiedImageError

from ml_model.config import (
    OXFORD_FLOWER_LABELS,
    CONFIDENCE_THRESHOLD,
    get_flower_emoji,
    label_to_db_id,
)
from ml_model.preprocessor import (
    validate_image_format,
    load_image_from_bytes,
    is_plant_image,
    preprocess_image,
    get_image_visual_features,
)

logger = logging.getLogger(__name__)

_SESSION = None


def _get_session():
    global _SESSION

    if _SESSION is None:
        import os
        from ml_model.config import MODEL_PATH

        model_path = os.path.join(
            os.path.dirname(MODEL_PATH),
            "flower_model.onnx"
        )

        if not os.path.isfile(model_path):
            raise RuntimeError(
                "ONNX flower model not found. "
                "Expected: ml_model/flower_model.onnx"
            )

        _SESSION = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )

        logger.info("ONNX flower model loaded successfully.")

    return _SESSION


def predict(image_bytes: bytes, filename: str = "upload.jpg") -> dict:
    """
    Predict flower species using the ONNX model.
    """

    # Validate file
    validate_image_format(image_bytes,filename)

    # Load image
    try:
        pil_image = load_image_from_bytes(image_bytes)
    except (UnidentifiedImageError, ValueError) as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc

    # Basic plant-image validation
    try:
        if not is_plant_image(pil_image):
            raise ValueError(
                "The uploaded image does not appear to contain a suitable plant or flower."
            )
    except Exception:
        # If the existing heuristic fails unexpectedly, continue to model prediction.
        logger.warning("Plant-image validation could not be completed.")

    # Preprocess
    input_array = preprocess_image(pil_image)

    # ONNX inference
    session = _get_session()

    input_name = session.get_inputs()[0].name

    outputs = session.run(
        None,
        {input_name: input_array},
    )

    logits = np.asarray(outputs[0])[0]

    # Softmax
    logits = logits - np.max(logits)
    probabilities = np.exp(logits)
    probabilities = probabilities / np.sum(probabilities)
    # Top 3 predictions
    top_indices = np.argsort(probabilities)[::-1][:3]

    predictions = []

    for index in top_indices:
        confidence = float(probabilities[index])

        if index < len(OXFORD_FLOWER_LABELS):
            label = OXFORD_FLOWER_LABELS[index]
        else:
            label = f"Class {index}"

        predictions.append(
            {
                "label": label,
                "confidence": round(confidence, 4),
                "confidence_percent": round(confidence * 100, 2),
                "flower_id": label_to_db_id(label),
                "emoji": get_flower_emoji(label),
            }
        )

    best = predictions[0]

    return {
        "success": True,
        "filename": filename,
        "prediction": best,
        "top_predictions": predictions,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "model": "MobileNetV2-Oxford102-ONNX",
        "visual_features": get_image_visual_features(pil_image),
    }