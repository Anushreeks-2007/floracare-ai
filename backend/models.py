from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    photos = relationship("PhotoUpload", back_populates="user")
    feedbacks = relationship("PredictionFeedback", back_populates="user")
    training_examples = relationship("TrainingExample", back_populates="user")


class PhotoUpload(Base):
    __tablename__ = "photo_uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=True)
    predicted_species = Column(String(200), nullable=True)
    predicted_confidence = Column(Float, nullable=True)
    actual_species = Column(String(200), nullable=True)
    status = Column(String(50), default="uploaded")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="photos")
    feedback = relationship("PredictionFeedback", back_populates="photo", uselist=False)


class PredictionFeedback(Base):
    __tablename__ = "prediction_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    photo_id = Column(Integer, ForeignKey("photo_uploads.id"), nullable=True, index=True)
    predicted_species = Column(String(200), nullable=False)
    actual_species = Column(String(200), nullable=False)
    confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="feedbacks")
    photo = relationship("PhotoUpload", back_populates="feedback")


class TrainingExample(Base):
    __tablename__ = "training_examples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    photo_path = Column(String(500), nullable=False)
    predicted_species = Column(String(200), nullable=False)
    actual_species = Column(String(200), nullable=False)
    confidence = Column(Float, nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="training_examples")
