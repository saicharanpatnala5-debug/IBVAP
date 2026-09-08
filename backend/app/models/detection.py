"""
IBVAP - Detection Model
Raw computer vision perception output (person, vehicle, etc.) with bounding box and confidence.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Detection(Base):
    __tablename__ = "detections"

    detection_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    track_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    class_name: Mapped[str] = mapped_column(String(50), index=True) # person, car, truck, bus, motorcycle
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    # [x1, y1, x2, y2] normalized bounding box coordinates
    bbox: Mapped[List[float]] = mapped_column(JSON, nullable=False)
    frame_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
