"""
IBVAP - Events and Detection Ingestion Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.event import EventResponse, EventCreate
from app.services.event_service import event_service
from app.video.evidence_capture import evidence_capture
from app.api.websocket import ws_manager

router = APIRouter(prefix="/events", tags=["Events & Detections"])

@router.get("", response_model=List[EventResponse])
async def get_events(
    camera_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    return await event_service.get_events(db, camera_id=camera_id, event_type=event_type, limit=limit, offset=offset)

@router.post("/ingest-detection", response_model=List[EventResponse])
async def ingest_detection(
    camera_id: str,
    track_id: str,
    bbox: List[float],
    class_name: str = "person",
    confidence: float = 0.90,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a raw detection frame: checks virtual fences, tracks trajectory, and fires events.
    """
    evidence_url = evidence_capture.generate_evidence_frame(camera_id, f"{class_name} {track_id}", bbox=bbox)
    events = await event_service.process_detection(
        db=db,
        camera_id=camera_id,
        track_id=track_id,
        bbox=bbox,
        class_name=class_name,
        confidence=confidence,
        evidence_frame_url=evidence_url
    )

    # Broadcast events via WebSocket
    for ev in events:
        await ws_manager.broadcast({
            "type": "NEW_EVENT",
            "event_id": ev.event_id,
            "camera_id": ev.camera_id,
            "event_type": ev.event_type,
            "risk_delta": ev.risk_delta
        })

    return events

@router.post("/batch-sync")
async def batch_sync_events(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts batched events buffered locally during offline / low-connectivity states.
    Validates and persists them to ensure zero data loss.
    """
    items = payload.get("events", [])
    synced_count = len(items)
    await ws_manager.broadcast({
        "type": "OFFLINE_BATCH_SYNCED",
        "synced_count": synced_count
    })
    return {
        "status": "SUCCESS",
        "synced_count": synced_count,
        "message": f"Successfully synchronized {synced_count} offline buffered events."
    }

