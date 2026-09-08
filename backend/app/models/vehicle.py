"""
IBVAP - Vehicle Entity Model
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Boolean
from typing import Optional
from app.core.database import Base, TimestampMixin

class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vehicle_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    camera_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(30), nullable=False) # car, truck, motorcycle, bus
    make: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    estimated_speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    plate_number: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    is_hotlisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
