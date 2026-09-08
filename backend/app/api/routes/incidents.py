"""
IBVAP - Incident & Event Fusion Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.incident import IncidentResponse, IncidentDetailResponse, IncidentStatusUpdate
from app.services.incident_service import incident_service
from app.ai.multicamera import multicamera_engine

router = APIRouter(prefix="/incidents", tags=["Incidents & Event Fusion"])

@router.get("", response_model=List[IncidentResponse])
async def list_incidents(status: Optional[str] = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await incident_service.get_all(db, status=status, limit=limit)

@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident_detail(incident_id: str, db: AsyncSession = Depends(get_db)):
    incident = await incident_service.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    handoff = multicamera_engine.predict_next_camera(incident.lead_camera_id)
    
    # Construct detail timeline
    timeline = []
    for f in incident.contributing_factors_json:
        timeline.append({
            "time": incident.start_time.strftime("%H:%M:%S"),
            "timestamp": incident.start_time,
            "camera_id": incident.lead_camera_id,
            "event_type": f.get("factor", "Incident Event"),
            "description": f"Registered {f.get('factor')}",
            "confidence": f.get("confidence", 0.92),
            "evidence_frame_url": None,
            "risk_points": f.get("points", 20)
        })

    res = IncidentDetailResponse(
        incident_id=incident.incident_id,
        title=incident.title,
        severity=incident.severity,
        risk_score=incident.risk_score,
        status=incident.status,
        start_time=incident.start_time,
        end_time=incident.end_time,
        lead_camera_id=incident.lead_camera_id,
        contributing_event_ids=incident.contributing_event_ids,
        contributing_factors_json=incident.contributing_factors_json,
        assigned_to=incident.assigned_to,
        operator_notes=incident.operator_notes,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        timeline=timeline,
        predicted_next_camera=handoff
    )
    return res

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    status_update: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await incident_service.update_status(
        db,
        incident_id=incident_id,
        status=status_update.status,
        notes=status_update.operator_notes,
        assigned_to=status_update.assigned_to
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")
    return updated
