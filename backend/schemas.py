from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PhotoUploadCreate(BaseModel):
    file_name: str
    file_path: str
    file_url: Optional[str] = None
    predicted_species: Optional[str] = None
    predicted_confidence: Optional[float] = None
    actual_species: Optional[str] = None
    status: str = "uploaded"
    notes: Optional[str] = None


class PredictionFeedbackCreate(BaseModel):
    photo_id: Optional[int] = None
    predicted_species: str
    actual_species: str
    confidence: Optional[float] = None
    notes: Optional[str] = None


class TrainingExampleCreate(BaseModel):
    photo_path: str
    predicted_species: str
    actual_species: str
    confidence: Optional[float] = None
    metadata: Optional[str] = None


class PhotoUploadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_name: str
    file_path: str
    file_url: Optional[str] = None
    predicted_species: Optional[str] = None
    predicted_confidence: Optional[float] = None
    actual_species: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: str
