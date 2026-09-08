"""
IBVAP - Face Analytics & Authorized Watchlist Models
Supports human-in-the-loop face recognition prototype with strict confidence metrics.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin

class FaceSighting(Base):
    __tablename__ = "face_sightings"

    face_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    track_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), default="Unknown Person")
    identity_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Authorized personnel ID
    similarity_score: Mapped[float] = mapped_column(Float, default=0.0) # 0.0 - 1.0 Cosine similarity
    confidence: Mapped[float] = mapped_column(Float, default=0.85) # Face detection quality score
    is_authorized: Mapped[bool] = mapped_column(Boolean, default=False)
    review_required: Mapped[bool] = mapped_column(Boolean, default=True) # Human verification required
    evidence_frame_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(20), index=True) # VEHICLE, PERSON, SUSPICIOUS
    identifier_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # e.g. Plate number or Personnel ID
    name_label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_priority: Mapped[str] = mapped_column(String(20), default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
