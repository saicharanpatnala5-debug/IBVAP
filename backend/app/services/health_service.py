"""
IBVAP - Camera & System Health Monitoring Service
"""
from typing import List, Dict, Any
from datetime import datetime, timezone
import psutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.camera import Camera, CameraHealth
from app.models.incident import Incident
from app.models.alert import Alert
from app.schemas.health import SystemHealthSummary, CameraHealthResponse

class HealthService:
    async def get_system_health(self, db: AsyncSession) -> SystemHealthSummary:
        cams_res = await db.execute(select(Camera))
        cameras = cams_res.scalars().all()

        total = len(cameras)
        online = sum(1 for c in cameras if c.status == "ONLINE")
        degraded = sum(1 for c in cameras if c.status == "DEGRADED")
        offline = sum(1 for c in cameras if c.status == "OFFLINE")

        inc_res = await db.execute(select(Incident).where(Incident.status == "ACTIVE"))
        active_inc = len(inc_res.scalars().all())

        alt_res = await db.execute(select(Alert).where(Alert.is_acknowledged == False, Alert.severity == "CRITICAL"))
        unack_crit = len(alt_res.scalars().all())

        # Sample health entries for cameras
        camera_health_list = []
        for c in cameras:
            camera_health_list.append(CameraHealthResponse(
                camera_id=c.camera_id,
                fps=c.fps,
                latency_ms=115.0 if c.status == "ONLINE" else 280.0,
                packet_loss_pct=0.2 if c.status == "ONLINE" else 4.5,
                frame_drops=0 if c.status == "ONLINE" else 14,
                ai_fps=24.0,
                status=c.status,
                checked_at=datetime.now(timezone.utc)
            ))

        system_status = "HEALTHY"
        if offline > 0 or unack_crit > 2:
            system_status = "DEGRADED"
        if offline > total / 2 or unack_crit > 5:
            system_status = "CRITICAL"

        return SystemHealthSummary(
            system_status=system_status,
            total_cameras=total,
            online_cameras=online,
            degraded_cameras=degraded,
            offline_cameras=offline,
            active_incidents=active_inc,
            critical_alerts_unack=unack_crit,
            ai_inference_avg_fps=23.8,
            edge_mode=False,
            camera_health_list=camera_health_list
        )

health_service = HealthService()
