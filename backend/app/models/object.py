"""
IBVAP - Detected Object Model
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Boolean, Text
from typing import Optional
from app.core.database import Base, TimestampMixin

class DetectedObject(Base, TimestampMixin):
    __tablename__ = "detected_objects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    object_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    camera_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_w: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_h: Mapped[float] = mapped_column(Float, nullable=False)
    is_occluded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
