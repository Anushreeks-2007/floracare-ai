from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    photo_uploads: Mapped[list["PhotoUpload"]] = relationship(back_populates="user")
    prediction_logs: Mapped[list["PredictionLog"]] = relationship(back_populates="user")
    feedback_entries: Mapped[list["UserFeedback"]] = relationship(back_populates="user")


class PhotoUpload(Base):
    __tablename__ = "photo_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    prediction_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship(back_populates="photo_uploads")
    prediction_logs: Mapped[list["PredictionLog"]] = relationship(back_populates="photo_upload")
    feedback_entries: Mapped[list["UserFeedback"]] = relationship(back_populates="photo_upload")


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    photo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("photo_uploads.id"), nullable=True)
    predicted_label: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    actual_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped[Optional[User]] = relationship(back_populates="prediction_logs")
    photo_upload: Mapped[Optional[PhotoUpload]] = relationship(back_populates="prediction_logs")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    photo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("photo_uploads.id"), nullable=True)
    predicted_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    corrected_label: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship(back_populates="feedback_entries")
    photo_upload: Mapped[Optional[PhotoUpload]] = relationship(back_populates="feedback_entries")
