from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import PredictionFeedback, TrainingExample, User
from backend.schemas import PredictionFeedbackCreate, TrainingExampleCreate

router = APIRouter(prefix="/api", tags=["Model Experience & Feedback"])


@router.post("/feedback")
async def add_feedback(
    payload: PredictionFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.actual_species or not payload.predicted_species:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prediction and actual species are required")

    feedback = PredictionFeedback(
        user_id=current_user.id,
        photo_id=payload.photo_id,
        predicted_species=payload.predicted_species,
        actual_species=payload.actual_species,
        confidence=payload.confidence,
        notes=payload.notes,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"success": True, "feedback_id": feedback.id}


@router.post("/training-example")
async def add_training_example(
    payload: TrainingExampleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    example = TrainingExample(
        user_id=current_user.id,
        photo_path=payload.photo_path,
        predicted_species=payload.predicted_species,
        actual_species=payload.actual_species,
        confidence=payload.confidence,
        metadata=payload.metadata,
    )
    db.add(example)
    db.commit()
    db.refresh(example)
    return {"success": True, "training_example_id": example.id}
