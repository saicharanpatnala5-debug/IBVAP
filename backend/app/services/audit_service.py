"""
IBVAP - Audit Logging Service
DPDP Act 2023 compliance logging for all security-relevant actions.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogCreate

class AuditService:
    async def log_action(
        self,
        db: AsyncSession,
        actor: str,
        action: str,
        object_type: str,
        object_id: Optional[str] = None,
        result: str = "SUCCESS",
        source_ip: str = "127.0.0.1",
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        log_entry = AuditLog(
            log_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            actor=actor,
            action=action,
            object_type=object_type,
            object_id=object_id,
            timestamp=datetime.now(timezone.utc),
            result=result,
            source_ip=source_ip,
            details_json=details or {}
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    async def get_logs(self, db: AsyncSession, limit: int = 100) -> list:
        res = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit))
        return list(res.scalars().all())

audit_service = AuditService()
