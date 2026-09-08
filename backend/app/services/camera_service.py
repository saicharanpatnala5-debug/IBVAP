"""
IBVAP - Camera Management Service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.camera import Camera, CameraHealth, CameraTopologyEdge
from app.schemas.camera import CameraCreate, CameraUpdate, CameraTopologyCreate
from app.core.logging import logger

class CameraService:
    async def get_all(self, db: AsyncSession) -> List[Camera]:
        res = await db.execute(select(Camera).order_by(Camera.camera_id))
        return list(res.scalars().all())

    async def get_by_id(self, db: AsyncSession, camera_id: str) -> Optional[Camera]:
        res = await db.execute(select(Camera).where(Camera.camera_id == camera_id))
        return res.scalar_one_or_none()

    async def create(self, db: AsyncSession, data: CameraCreate) -> Camera:
        camera = Camera(**data.model_dump())
        db.add(camera)
        await db.commit()
        await db.refresh(camera)
        logger.info(f"Registered camera {camera.camera_id} - {camera.name}")
        return camera

    async def update(self, db: AsyncSession, camera_id: str, data: CameraUpdate) -> Optional[Camera]:
        camera = await self.get_by_id(db, camera_id)
        if not camera:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)
        await db.commit()
        await db.refresh(camera)
        return camera

    async def add_topology_edge(self, db: AsyncSession, data: CameraTopologyCreate) -> CameraTopologyEdge:
        edge = CameraTopologyEdge(**data.model_dump())
        db.add(edge)
        await db.commit()
        await db.refresh(edge)
        return edge

    async def get_topology_edges(self, db: AsyncSession) -> List[CameraTopologyEdge]:
        res = await db.execute(select(CameraTopologyEdge))
        return list(res.scalars().all())

camera_service = CameraService()
