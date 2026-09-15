from __future__ import annotations
import logging
import io
import os
import json
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from PIL import Image

from ml_model.predict import predict
from ml_model.stress_detector import detect_stress
from ml_model.preprocessor import validate_image_format, is_plant_image, load_image_from_bytes
from ml_model.model import get_model_info, ModelNotAvailableError
from ml_model.config import EVALUATION_REPORT_PATH
from backend.utils.validators import validate_image_upload
from backend.utils.data_loader import get_flower_by_id
from backend.services.scoring import compute_health_score, compute_sustainability_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Prediction & Model"])

@router.get("/model/status")
async def model_status():
    """Return model readiness and weight availability."""
    info = get_model_info()
    return {
        "status": "ready" if info.get("available") else "unavailable",
        "available": info.get("available", False),
        "model_path": info.get("path"),
        "size_mb": info.get("size_mb"),
        "architecture": "MobileNetV2 (Transfer Learning, Oxford 102 Flowers)",
        "num_classes": 102,
        "message": info.get("message")
    }

@router.get("/model/evaluation")
async def model_evaluation():
    """Return real evaluation metrics if model has been evaluated."""
    if not os.path.isfile(EVALUATION_REPORT_PATH):
        return {
            "available": False,
            "message": "Required model/data is unavailable. Please add the trained model and dataset before using this feature.",
            "instructions": "Run: python ml_model/evaluation.py to evaluate the trained model on Oxford 102 test set."
        }
    try:
        with open(EVALUATION_REPORT_PATH, "r", encoding="utf-8") as f:
            report = json.load(f)
        return {"available": True, "report": report}
    except Exception as e:
        return {"available": False, "error": str(e)}

@router.post("/predict")
async def predict_flower(file: UploadFile = File(...)):
    """
    Core flower identification endpoint:
    1. Validates file format and size
    2. Validates that image is actually a plant/flower
    3. Runs MobileNetV2 prediction if model is trained
    4. Runs computer-vision stress detection (yellowing, brown spots, wilting)
    5. Attaches species-specific care profile
    """
    image_bytes = await validate_image_upload(file)

    # Validate image format via PIL
    try:
        pil_img = load_image_from_bytes(image_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_image", "message": f"Could not decode image: {e}"}
        )

    # Heuristic plant validation check
    plant_check = is_plant_image(pil_img)
    if not plant_check.get("is_plant", False):
        return {
            "success": False,
            "is_plant": False,
            "error": "not_a_plant",
            "message": (
                "The uploaded image does not appear to contain a flower or plant. "
                f"Reason: {plant_check.get('reason', 'Low vegetation or petal saturation detected.')} "
                "Please upload a clear photo of a flowering plant."
            ),
            "details": plant_check
        }

    # Run species classification
    try:
        pred_res = predict(image_bytes, filename=file.filename or "flower.jpg")
    except ModelNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "model_unavailable",
                "message": (
                    "Required model/data is unavailable. Please add the trained model and dataset before using this feature."
                ),
                "instructions": (
                    "Please run: python ml_model/train.py to train MobileNetV2 on the Oxford 102 Flowers dataset."
                )
            }
        )
    except Exception as e:
        logger.exception("Prediction failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "prediction_failed", "message": str(e)}
        )

    # Run computer vision stress detection
    stress_res = detect_stress(pil_img)

    # Lookup flower profile
    flower_id = pred_res.get("flower_id")
    flower_data = get_flower_by_id(flower_id) if flower_id else None

    # Compute baseline health and sustainability score
    default_env = {
        "temperature": 22.0,
        "humidity": 60.0,
        "sunlight_hours": 6.0,
        "soil_ph": 6.5,
        "soil_type": flower_data.get("soil", {}).get("type", "loamy") if flower_data else "loamy",
        "watering_frequency": "2-3 times per week"
    }
    health_assessment = compute_health_score(flower_data or {}, default_env, stress_res) if flower_data else None
    sustainability_assessment = compute_sustainability_score(flower_data or {}, default_env) if flower_data else None

    return {
        "success": True,
        "is_plant": True,
        "prediction": pred_res,
        "stress_detection": stress_res,
        "flower_profile": flower_data,
        "initial_health": health_assessment,
        "initial_sustainability": sustainability_assessment
    }
