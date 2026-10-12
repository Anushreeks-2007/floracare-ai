from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.deps import get_current_user
from backend.database import get_db
from backend.models import PhotoUpload, PredictionLog, UserFeedback, User
from backend.schemas import FeedbackCreate

router = APIRouter(prefix="/api", tags=["User History"])


@router.get("/history/photos")
async def get_user_photo_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    photos = (
        db.query(PhotoUpload)
        .filter(PhotoUpload.user_id == user.id)
        .order_by(PhotoUpload.created_at.desc())
        .all()
    )
    return [
        {
            "id": photo.id,
            "filename": photo.filename,
            "original_name": photo.original_name,
            "file_url": photo.file_url,
            "prediction_label": photo.prediction_label,
            "confidence": photo.confidence,
            "status": photo.status,
            "created_at": photo.created_at.isoformat(),
        }
        for photo in photos
    ]


@router.get("/history/predictions")
async def get_user_prediction_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logs = (
        db.query(PredictionLog)
        .filter(PredictionLog.user_id == user.id)
        .order_by(PredictionLog.created_at.desc())
        .all()
    )
    return [
        {
            "id": log.id,
            "predicted_label": log.predicted_label,
            "confidence": log.confidence,
            "actual_label": log.actual_label,
            "model_version": log.model_version,
            "result_json": log.result_json,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get("/history/feedback")
async def get_user_feedback_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entries = (
        db.query(UserFeedback)
        .filter(UserFeedback.user_id == user.id)
        .order_by(UserFeedback.created_at.desc())
        .all()
    )
    return [
        {
            "id": entry.id,
            "photo_id": entry.photo_id,
            "predicted_label": entry.predicted_label,
            "corrected_label": entry.corrected_label,
            "notes": entry.notes,
            "created_at": entry.created_at.isoformat(),
        }
        for entry in entries
    ]


@router.post("/history/feedback")
async def create_user_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    feedback = UserFeedback(
        user_id=user.id,
        photo_id=payload.photo_id,
        predicted_label=payload.predicted_label,
        corrected_label=payload.corrected_label,
        notes=payload.notes,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return {
        "success": True,
        "message": "Feedback saved for model improvement.",
        "feedback_id": feedback.id,
    }
