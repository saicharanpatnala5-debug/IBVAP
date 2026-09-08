"""
IBVAP - Persistent Object Track Model
Maintains object identity across frames, trajectory history, velocity and dwell time.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Track(Base):
    __tablename__ = "tracks"

    track_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True) # Local track ID (e.g. P-17, V-42)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    global_track_id: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True) # Cross-camera global ID
    class_name: Mapped[str] = mapped_column(String(50), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Trajectory list of centroids: [{"x": 100, "y": 200, "t": "2026-09-05T02:14:32Z"}]
    trajectory: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    velocity_vector: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, default=dict) # {"vx": 1.2, "vy": -0.8}
    dwell_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE") # ACTIVE, LOST, ENDED
    appearance_embedding_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
