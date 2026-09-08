"""
IBVAP - Face Analytics and Watchlist Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FaceSightingResponse(BaseModel):
    face_id: str
    track_id: Optional[str] = None
    camera_id: str
    name: Optional[str] = "Unknown Person"
    identity_code: Optional[str] = None
    similarity_score: float
    confidence: float
    is_authorized: bool
    review_required: bool
    evidence_frame_url: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class WatchlistCreate(BaseModel):
    category: str # VEHICLE, PERSON, SUSPICIOUS
    identifier_code: str
    name_label: str
    description: Optional[str] = None
    risk_priority: str = "HIGH"

class WatchlistResponse(WatchlistCreate):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
