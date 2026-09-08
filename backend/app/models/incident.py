"""
IBVAP - Incident Model
Grouped sequence of correlated events representing a high-level operational security incident (Event Fusion).
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Integer, Float, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", index=True) # NORMAL, LOW, MEDIUM, HIGH, CRITICAL
    risk_score: Mapped[int] = mapped_column(Integer, default=60, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True) # ACTIVE, ACKNOWLEDGED, INVESTIGATING, RESOLVED, CLOSED
    start_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    lead_camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    
    # List of event_ids fused into this incident
    contributing_event_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    # Explainable AI factors: [{"factor": "Restricted Zone Entry", "points": 30, "confidence": 0.94}, ...]
    contributing_factors_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    assigned_to: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    operator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")
