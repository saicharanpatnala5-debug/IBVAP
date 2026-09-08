"""
IBVAP - Virtual Fence and Polygonal Zones
Supports Green (Normal), Yellow (Monitoring), and Red (Restricted Perimeter) zones.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import String, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

class Zone(Base, TimestampMixin):
    __tablename__ = "zones"

    zone_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(30), default="RED_RESTRICTED") # GREEN_NORMAL, YELLOW_MONITORING, RED_RESTRICTED
    # Coordinates list of [x, y] normalized or pixel vertices: [[x1, y1], [x2, y2], ...]
    polygon_coords: Mapped[List[List[float]]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_level: Mapped[str] = mapped_column(String(20), default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict) # e.g. {"dwell_threshold": 15, "direction": "inward"}

    camera = relationship("Camera", back_populates="zones")
    events = relationship("Event", back_populates="zone")
