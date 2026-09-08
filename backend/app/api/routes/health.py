"""
IBVAP - System & Camera Health Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.health import SystemHealthSummary
from app.services.health_service import health_service

router = APIRouter(prefix="/health", tags=["Health & Telemetry"])

@router.get("", response_model=SystemHealthSummary)
@router.get("/summary", response_model=SystemHealthSummary)
async def get_system_health(db: AsyncSession = Depends(get_db)):
    return await health_service.get_system_health(db)
