"""
IBVAP - Camera and Topology Models
Supports RTSP camera onboarding, health monitoring, and logical graph topology.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

class Camera(Base, TimestampMixin):
    __tablename__ = "cameras"

    camera_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    site: Mapped[str] = mapped_column(String(100), default="BOP-Alpha") # Border Out Post
    sector: Mapped[str] = mapped_column(String(50), default="Sector-B")
    latitude: Mapped[float] = mapped_column(Float, nullable=False, default=28.6139)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, default=77.2090)
    stream_url: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ONLINE", index=True) # ONLINE, OFFLINE, DEGRADED
    fps: Mapped[float] = mapped_column(Float, default=25.0)
    resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False)
    config_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    # Relationships
    zones = relationship("Zone", back_populates="camera", cascade="all, delete-orphan", lazy="selectin")
    health_records = relationship("CameraHealth", back_populates="camera", cascade="all, delete-orphan", lazy="selectin")
    events = relationship("Event", back_populates="camera", lazy="selectin")
    alerts = relationship("Alert", back_populates="camera", lazy="selectin")

class CameraHealth(Base):
    __tablename__ = "camera_health"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    fps: Mapped[float] = mapped_column(Float, default=25.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=120.0)
    packet_loss_pct: Mapped[float] = mapped_column(Float, default=0.0)
    frame_drops: Mapped[int] = mapped_column(Integer, default=0)
    ai_fps: Mapped[float] = mapped_column(Float, default=22.0)
    status: Mapped[str] = mapped_column(String(20), default="HEALTHY")
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    camera = relationship("Camera", back_populates="health_records")

class CameraTopologyEdge(Base):
    __tablename__ = "camera_topology"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    to_camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    transition_probability: Mapped[float] = mapped_column(Float, default=0.75) # 0.0 - 1.0
    min_transit_seconds: Mapped[float] = mapped_column(Float, default=10.0)
    max_transit_seconds: Mapped[float] = mapped_column(Float, default=60.0)
    distance_meters: Mapped[float] = mapped_column(Float, default=80.0)
