from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FeedbackCreate(BaseModel):
    photo_id: Optional[int] = None
    predicted_label: Optional[str] = None
    corrected_label: str = Field(..., min_length=1)
    notes: Optional[str] = None


class PhotoUploadOut(BaseModel):
    id: int
    filename: str
    original_name: str
    file_url: Optional[str]
    prediction_label: Optional[str]
    confidence: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionLogOut(BaseModel):
    id: int
    predicted_label: str
    confidence: Optional[float]
    actual_label: Optional[str]
    model_version: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
