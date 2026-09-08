"""
IBVAP - Alert Model
Actionable operator notification raised by incidents with severity, explainability card, and audit state.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base, TimestampMixin

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String(50), ForeignKey("incidents.incident_id"), index=True)
    camera_id: Mapped[str] = mapped_column(String(50), ForeignKey("cameras.camera_id"), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", index=True) # NORMAL, LOW, MEDIUM, HIGH, CRITICAL
    score: Mapped[int] = mapped_column(Integer, default=95)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Explainable AI Card (WHAT, WHO, WHERE, WHEN, WHY, CONFIDENCE, EVIDENCE)
    explainability_card: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    evidence_frame_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    evidence_clip_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalated_to: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    incident = relationship("Incident", back_populates="alerts")
    camera = relationship("Camera", back_populates="alerts")
