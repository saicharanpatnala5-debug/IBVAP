"""
IBVAP - Incident and Timeline Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class IncidentTimelineItem(BaseModel):
    time: str
    timestamp: datetime
    camera_id: str
    event_type: str
    description: str
    confidence: float
    evidence_frame_url: Optional[str] = None
    risk_points: int

class IncidentStatusUpdate(BaseModel):
    status: str # ACTIVE, ACKNOWLEDGED, INVESTIGATING, RESOLVED, CLOSED
    operator_notes: Optional[str] = None
    assigned_to: Optional[str] = None

class IncidentResponse(BaseModel):
    incident_id: str
    title: str
    severity: str
    risk_score: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    lead_camera_id: str
    contributing_event_ids: List[str] = []
    contributing_factors_json: List[Dict[str, Any]] = []
    assigned_to: Optional[str] = None
    operator_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IncidentDetailResponse(IncidentResponse):
    timeline: List[IncidentTimelineItem] = []
    predicted_next_camera: Optional[Dict[str, Any]] = None
