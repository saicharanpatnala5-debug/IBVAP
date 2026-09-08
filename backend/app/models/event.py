"""
IBVAP - Event Model
Semantically meaningful occurrences derived from detections and tracks.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    track_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("tracks.track_id"), index=True, nullable=True)
    zone_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("zones.zone_id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True) 
    # ZONE_INTRUSION, LOITERING, NIGHT_MOVEMENT, DIRECTION_BREACH, ANPR_DETECTION, FACE_SIGHTING, CAMERA_DEGRADED
    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    risk_delta: Mapped[int] = mapped_column(Float, default=20) # Contributing score to risk engine
    evidence_frame_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    evidence_clip_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    camera = relationship("Camera", back_populates="events")
    zone = relationship("Zone", back_populates="events")
