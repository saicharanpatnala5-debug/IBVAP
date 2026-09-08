"""
IBVAP - Audit Logs Routes
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["Audit & Governance"])

@router.get("", response_model=List[AuditLogResponse])
async def get_audit_logs(limit: int = Query(100, le=500), db: AsyncSession = Depends(get_db)):
    return await audit_service.get_logs(db, limit=limit)
