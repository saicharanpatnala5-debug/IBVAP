"""
IBVAP - License Plate Entity Model
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Boolean
from typing import Optional
from app.core.database import Base, TimestampMixin

class LicensePlate(Base, TimestampMixin):
    __tablename__ = "license_plates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plate_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    camera_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    state_code: Mapped[str] = mapped_column(String(5), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    is_hotlisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    snapshot_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
