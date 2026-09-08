"""
IBVAP - Incident & Event Fusion Service
Correlates raw events into high-level incidents and generates explainable evidence.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.event import Event
from app.ai.event_fusion import event_fusion_engine
from app.ai.risk_engine import risk_engine
from app.core.logging import logger

class IncidentService:
    async def create_fused_incident(
        self,
        db: AsyncSession,
        camera_id: str,
        events: List[Event]
    ) -> Incident:
        """
        Execute AI Event Fusion across events to construct a unified incident.
        """
        event_dicts = [
            {
                "event_id": e.event_id,
                "camera_id": e.camera_id,
                "event_type": e.event_type,
                "confidence": e.confidence,
                "timestamp": e.timestamp,
                "risk_delta": e.risk_delta,
                "evidence_frame_url": e.evidence_frame_url,
                "metadata_json": e.metadata_json
            }
            for e in events
        ]

        fused = event_fusion_engine.fuse_events_into_incident(camera_id, event_dicts)
        
        incident = Incident(
            incident_id=fused["incident_id"],
            title=fused["title"],
            severity=fused["severity"],
            risk_score=fused["risk_score"],
            status="ACTIVE",
            lead_camera_id=fused["lead_camera_id"],
            contributing_event_ids=fused["contributing_event_ids"],
            contributing_factors_json=fused["contributing_factors_json"],
            start_time=fused["start_time"],
            end_time=fused["end_time"]
        )
        db.add(incident)
        await db.commit()
        await db.refresh(incident)

        logger.info(f"Fused {len(events)} events into Incident {incident.incident_id} [{incident.severity}]")
        return incident

    async def get_all(self, db: AsyncSession, status: Optional[str] = None, limit: int = 50) -> List[Incident]:
        query = select(Incident)
        if status:
            query = query.where(Incident.status == status)
        query = query.order_by(Incident.start_time.desc()).limit(limit)
        res = await db.execute(query)
        return list(res.scalars().all())

    async def get_by_id(self, db: AsyncSession, incident_id: str) -> Optional[Incident]:
        res = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
        return res.scalar_one_or_none()

    async def update_status(
        self,
        db: AsyncSession,
        incident_id: str,
        status: str,
        notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Optional[Incident]:
        incident = await self.get_by_id(db, incident_id)
        if not incident:
            return None
        incident.status = status
        if notes:
            incident.operator_notes = (incident.operator_notes or "") + f"\n[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {notes}"
        if assigned_to:
            incident.assigned_to = assigned_to
        await db.commit()
        await db.refresh(incident)
        return incident

incident_service = IncidentService()
