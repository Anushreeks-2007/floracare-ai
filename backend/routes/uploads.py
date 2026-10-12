from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import PhotoUpload, User
from backend.schemas import PhotoUploadOut

router = APIRouter(prefix="/api/uploads", tags=["Photo Upload History"])


@router.get("/history", response_model=list[PhotoUploadOut])
async def get_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    uploads = (
        db.query(PhotoUpload)
        .filter(PhotoUpload.user_id == current_user.id)
        .order_by(PhotoUpload.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return uploads


@router.get("/history/{upload_id}", response_model=PhotoUploadOut)
async def get_upload_detail(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    upload = db.query(PhotoUpload).filter(PhotoUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload record not found")
    if upload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this upload")
    return upload
