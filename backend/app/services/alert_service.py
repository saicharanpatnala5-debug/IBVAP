"""
IBVAP - Alert Management Service
Generates actionable alerts with Explainable AI Cards and tracks operator acknowledgements.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.alert import Alert
from app.models.incident import Incident
from app.ai.risk_engine import risk_engine
from app.core.logging import logger

class AlertService:
    async def create_alert_for_incident(
        self,
        db: AsyncSession,
        incident: Incident,
        camera_id: str,
        evidence_frame_url: Optional[str] = None
    ) -> Alert:
        """
        Creates an actionable alert accompanied by a transparent Explainability Card.
        """
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        
        # Build explainability card
        why_list = [f.get("factor") for f in incident.contributing_factors_json] if incident.contributing_factors_json else ["Zone Intrusion Breach"]
        card = risk_engine.build_explainability_card(
            what=incident.title,
            who="Detected Target",
            where=f"{camera_id} (Sector-B)",
            when=incident.start_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            why_factors=why_list,
            confidence=0.94,
            risk_score=incident.risk_score,
            severity=incident.severity,
            evidence_frame=evidence_frame_url
        )

        alert = Alert(
            alert_id=alert_id,
            incident_id=incident.incident_id,
            camera_id=camera_id,
            severity=incident.severity,
            score=incident.risk_score,
            title=incident.title,
            description=f"Security alert triggered at {camera_id}. Severity: {incident.severity}. Risk Score: {incident.risk_score}.",
            explainability_card=card,
            evidence_frame_url=evidence_frame_url,
            is_acknowledged=False
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        logger.info(f"Dispatched Alert {alert_id} for Incident {incident.incident_id}")
        return alert

    async def acknowledge_alert(
        self,
        db: AsyncSession,
        alert_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None
    ) -> Optional[Alert]:
        res = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
        alert = res.scalar_one_or_none()
        if not alert:
            return None

        alert.is_acknowledged = True
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by = acknowledged_by
        await db.commit()
        await db.refresh(alert)
        return alert

    async def get_active_alerts(self, db: AsyncSession, limit: int = 50) -> List[Alert]:
        query = select(Alert).order_by(Alert.is_acknowledged.asc(), Alert.created_at.desc()).limit(limit)
        res = await db.execute(query)
        return list(res.scalars().all())

alert_service = AlertService()
