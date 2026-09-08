"""
IBVAP - ANPR & Vehicle Intelligence Models
Stores plate detection, OCR confidence, multi-frame readings, and suspicious watchlist correlation.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class VehiclePlate(Base):
    __tablename__ = "vehicle_plates"

    plate_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    vehicle_track_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    plate_text: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    ocr_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    vehicle_class: Mapped[str] = mapped_column(String(30), default="car") # car, truck, bus, motorcycle
    vehicle_color: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(30), nullable=True) # North, South, Inward, Outward
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_watchlist_match: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    evidence_frame_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
