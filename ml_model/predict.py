"""
FloraCare AI – Prediction Pipeline
Runs flower identification on an uploaded image using the trained MobileNetV2 model.

Usage:
    from ml_model.predict import predict
    result = predict(image_bytes)
"""
from __future__ import annotations

import logging

import torch
import torch.nn.functional as F

from ml_model.config import (
    OXFORD_FLOWER_LABELS,
    CONFIDENCE_THRESHOLD,
    get_flower_emoji,
    label_to_db_id,
)
from ml_model.model import load_model, ModelNotAvailableError
from ml_model.preprocessor import (
    validate_image_format,
    load_image_from_bytes,
    is_plant_image,
    preprocess_image,
    get_image_visual_features,
)

logger = logging.getLogger(__name__)

# Module-level model cache — loaded once, reused across requests
_MODEL_CACHE: torch.nn.Module | None = None


def _get_model() -> torch.nn.Module:
    """Return cached model, loading it on first call."""
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = load_model()
    return _MODEL_CACHE


def _build_ai_explanation(
    predicted_label: str,
    confidence: float,
    visual_features: dict,
    top3: list[dict],
) -> str:
    """
    Generate a beginner-friendly plain-English explanation of the prediction.
    This is an interpretive text based on visual features — not a scientific analysis.
    """
    dom_colors = ", ".join(visual_features.get("dominant_colors", ["mixed"]))
    brightness = visual_features.get("avg_brightness", 50)
    green_pct  = int(visual_features.get("green_fraction", 0) * 100)
    vivid_pct  = int(visual_features.get("vivid_fraction", 0) * 100)

    brightness_desc = (
        "a bright, well-lit"  if brightness > 60
        else "a moderately lit"  if brightness > 35
        else "a darker-toned"
    )

    confidence_desc = (
        "with high confidence"   if confidence > 0.75
        else "with moderate confidence"  if confidence > 0.50
        else "as the most probable match (low confidence — consider the top alternatives below)"
    )

    second_guess = f" The second possibility was '{top3[1]['name'].title()}' ({top3[1]['confidence']:.0%})." if len(top3) > 1 else ""

    explanation = (
        f"The AI identified this as a **{predicted_label.title()}** {confidence_desc}. "
        f"The image showed {brightness_desc} scene with dominant colours: {dom_colors}. "
        f"Approximately {green_pct}% of the image contained green plant material (foliage/stems), "
        f"and {vivid_pct}% featured vivid, saturated tones consistent with flower petals. "
        f"The model compared these visual patterns against its training on 102 flower species "
        f"from the Oxford Flowers102 dataset.{second_guess}"
    )
    return explanation


def predict(image_bytes: bytes, filename: str = "upload.jpg") -> dict:
    """
    Full prediction pipeline: validate → check plant → preprocess → infer → explain.

    Args:
        image_bytes: Raw image file bytes.
        filename:    Original filename (used for format detection hint).

    Returns:
        dict: {
            "success": True,
            "flower_id": int,       # 1-based Oxford class ID
            "flower_label": str,    # raw label e.g. "pink primrose"
            "flower_name": str,     # title-cased display name
            "emoji": str,
            "confidence": float,    # 0.0–1.0
            "top3": [               # top-3 predictions
                {"flower_id": int, "name": str, "label": str, "confidence": float}
            ],
            "visual_features": dict,
            "ai_explanation": str,
            "low_confidence_warning": bool,
        }

    Raises:
        ModelNotAvailableError: Model weights not found.
        ValueError:             Not a plant image or invalid image format.
    """
    # ── 1. Format validation ────────────────────────────────────────────────────
    validate_image_format(image_bytes, filename)

    # ── 2. Load PIL image ───────────────────────────────────────────────────────
    pil_image = load_image_from_bytes(image_bytes)

    # ── 3. Plant detection heuristic ────────────────────────────────────────────
    plant_check = is_plant_image(pil_image)
    if not plant_check["is_plant"]:
        raise ValueError(
            f"The uploaded image does not appear to be a flower or plant photo. "
            f"{plant_check['reason']} "
            f"Please upload a clear photo of a flower or plant."
        )

    # ── 4. Extract visual features (for explainability) ─────────────────────────
    visual_features = get_image_visual_features(pil_image)

    # ── 5. Preprocess for model ─────────────────────────────────────────────────
    input_tensor = preprocess_image(pil_image)

    # ── 6. Model inference ──────────────────────────────────────────────────────
    model = _get_model()
    device = next(model.parameters()).device
    input_tensor = input_tensor.to(device)

    with torch.no_grad():
        logits = model(input_tensor)           # (1, 102)
        probs  = F.softmax(logits, dim=1)[0]   # (102,)

    # ── 7. Extract top-3 predictions ────────────────────────────────────────────
    top_probs, top_idxs = torch.topk(probs, k=3)
    top3 = []
    for prob, idx in zip(top_probs.tolist(), top_idxs.tolist()):
        label = OXFORD_FLOWER_LABELS[idx]
        top3.append({
            "flower_id": idx + 1,       # 1-based Oxford class ID
            "label": label,
            "name": label.title(),
            "confidence": round(prob, 4),
            "emoji": get_flower_emoji(label),
        })

    # ── 8. Primary prediction ────────────────────────────────────────────────────
    best = top3[0]
    confidence = best["confidence"]
    low_conf = confidence < CONFIDENCE_THRESHOLD

    # ── 9. Build explanation ─────────────────────────────────────────────────────
    ai_explanation = _build_ai_explanation(
        predicted_label=best["label"],
        confidence=confidence,
        visual_features=visual_features,
        top3=top3,
    )

    logger.info(
        "Prediction: %s (%.1f%%) | top3: %s",
        best["name"], confidence * 100,
        [f"{t['name']} {t['confidence']:.0%}" for t in top3],
    )

    return {
        "success": True,
        "flower_id": best["flower_id"],
        "flower_label": best["label"],
        "flower_name": best["name"],
        "emoji": best["emoji"],
        "confidence": confidence,
        "top3": top3,
        "visual_features": visual_features,
        "ai_explanation": ai_explanation,
        "low_confidence_warning": low_conf,
        "plant_check": plant_check,
    }


def clear_model_cache() -> None:
    """Force the model to be reloaded on the next prediction call."""
    global _MODEL_CACHE
    _MODEL_CACHE = None
