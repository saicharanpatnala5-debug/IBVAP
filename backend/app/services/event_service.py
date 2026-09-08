"""
IBVAP - Event and Detection Ingestion Service
Validates detections against virtual fences, tracks objects, and creates atomic events.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.event import Event
from app.models.zone import Zone
from app.models.track import Track
from app.models.detection import Detection
from app.ai.geometry import is_point_in_polygon
from app.ai.tracking_engine import tracker_engine
from app.core.logging import logger

class EventService:
    async def process_detection(
        self,
        db: AsyncSession,
        camera_id: str,
        track_id: str,
        bbox: List[float],
        class_name: str = "person",
        confidence: float = 0.90,
        evidence_frame_url: Optional[str] = None
    ) -> List[Event]:
        """
        Process a single object detection frame:
        1. Update persistent track.
        2. Check against all camera zones (virtual fences).
        3. If inside a restricted zone, create a ZONE_INTRUSION event.
        4. If dwell time exceeds threshold, create a LOITERING event.
        """
        generated_events = []
        track_data = tracker_engine.update_track(
            camera_id=camera_id,
            track_id=track_id,
            bbox=bbox,
            class_name=class_name,
            confidence=confidence
        )

        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        point = [cx, cy]

        # Fetch zones for this camera
        res = await db.execute(select(Zone).where(Zone.camera_id == camera_id, Zone.is_active == True))
        zones = res.scalars().all()

        for zone in zones:
            if is_point_in_polygon(point, zone.polygon_coords):
                # Intrusion detected!
                risk_pts = 30 if zone.zone_type == "RED_RESTRICTED" else 15
                ev = Event(
                    event_id=f"EV-{uuid.uuid4().hex[:8].upper()}",
                    camera_id=camera_id,
                    track_id=track_id,
                    zone_id=zone.zone_id,
                    event_type="ZONE_INTRUSION",
                    confidence=confidence,
                    timestamp=datetime.now(timezone.utc),
                    risk_delta=risk_pts,
                    evidence_frame_url=evidence_frame_url,
                    metadata_json={
                        "zone_name": zone.name,
                        "zone_type": zone.zone_type,
                        "target_class": class_name,
                        "dwell_seconds": track_data.get("dwell_seconds", 0.0),
                        "description": f"{class_name.capitalize()} {track_id} entered {zone.name} ({zone.zone_type})"
                    }
                )
                db.add(ev)
                generated_events.append(ev)

                # Check loitering rule
                dwell = track_data.get("dwell_seconds", 0.0)
                if dwell >= 15.0:
                    loiter_ev = Event(
                        event_id=f"EV-{uuid.uuid4().hex[:8].upper()}",
                        camera_id=camera_id,
                        track_id=track_id,
                        zone_id=zone.zone_id,
                        event_type="LOITERING",
                        confidence=confidence,
                        timestamp=datetime.now(timezone.utc),
                        risk_delta=15,
                        evidence_frame_url=evidence_frame_url,
                        metadata_json={
                            "zone_name": zone.name,
                            "dwell_seconds": round(dwell, 1),
                            "description": f"{class_name.capitalize()} {track_id} stationary in {zone.name} for {dwell:.1f}s"
                        }
                    )
                    db.add(loiter_ev)
                    generated_events.append(loiter_ev)

        if generated_events:
            await db.commit()
            for g in generated_events:
                await db.refresh(g)

        return generated_events

    async def get_events(
        self,
        db: AsyncSession,
        camera_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Event]:
        query = select(Event)
        if camera_id:
            query = query.where(Event.camera_id == camera_id)
        if event_type:
            query = query.where(Event.event_type == event_type)
        query = query.order_by(Event.timestamp.desc()).limit(limit).offset(offset)
        res = await db.execute(query)
        return list(res.scalars().all())

event_service = EventService()
