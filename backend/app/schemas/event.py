"""
IBVAP - Event and Detection Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class DetectionResponse(BaseModel):
    detection_id: str
    camera_id: str
    track_id: Optional[str] = None
    class_name: str
    confidence: float
    bbox: List[float]
    frame_time: datetime
    attributes: Optional[Dict[str, Any]] = {}

    model_config = ConfigDict(from_attributes=True)

class TrackResponse(BaseModel):
    track_id: str
    camera_id: str
    global_track_id: Optional[str] = None
    class_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    trajectory: List[Dict[str, Any]] = []
    velocity_vector: Optional[Dict[str, float]] = {}
    dwell_seconds: float = 0.0
    status: str

    model_config = ConfigDict(from_attributes=True)

class EventCreate(BaseModel):
    camera_id: str
    track_id: Optional[str] = None
    zone_id: Optional[str] = None
    event_type: str
    confidence: float = 0.90
    risk_delta: int = 20
    evidence_frame_url: Optional[str] = None
    evidence_clip_url: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = {}

class EventResponse(BaseModel):
    event_id: str
    camera_id: str
    track_id: Optional[str] = None
    zone_id: Optional[str] = None
    event_type: str
    confidence: float
    timestamp: datetime
    risk_delta: int
    evidence_frame_url: Optional[str] = None
    evidence_clip_url: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = {}

    model_config = ConfigDict(from_attributes=True)

class EventFilterParams(BaseModel):
    camera_id: Optional[str] = None
    event_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_confidence: Optional[float] = None
    limit: int = 50
    offset: int = 0
