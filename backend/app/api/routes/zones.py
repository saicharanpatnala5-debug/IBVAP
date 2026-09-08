"""
IBVAP - Virtual Fence and Polygonal Zones Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse

router = APIRouter(prefix="/zones", tags=["Virtual Fence & Zones"])

@router.get("", response_model=List[ZoneResponse])
async def list_zones(camera_id: str = None, db: AsyncSession = Depends(get_db)):
    query = select(Zone)
    if camera_id:
        query = query.where(Zone.camera_id == camera_id)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("", response_model=ZoneResponse)
async def create_zone(zone_in: ZoneCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Zone).where(Zone.zone_id == zone_in.zone_id))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Zone ID already exists")

    zone = Zone(**zone_in.model_dump())
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone

@router.delete("/{zone_id}")
async def delete_zone(zone_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Zone).where(Zone.zone_id == zone_id))
    zone = res.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    await db.delete(zone)
    await db.commit()
    return {"status": "SUCCESS", "message": f"Zone {zone_id} deleted"}
