"""
IBVAP - Immutable Audit Log Model
Compliant with Digital Personal Data Protection Act (DPDP Act, 2023) and border security governance.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, JSON, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    actor: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # Username / System process
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # LOGIN, CAMERA_ADDED, ALERT_ACK, ZONE_MODIFIED, EXPORT
    object_type: Mapped[str] = mapped_column(String(50), index=True) # camera, zone, incident, alert, user
    object_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    result: Mapped[str] = mapped_column(String(20), default="SUCCESS") # SUCCESS, FAILURE, DENIED
    source_ip: Mapped[Optional[str]] = mapped_column(String(50), default="127.0.0.1")
    details_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
