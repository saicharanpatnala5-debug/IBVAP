"""
IBVAP - Video Intelligence Search Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class VideoIntelligenceSearchQuery(BaseModel):
    query_text: Optional[str] = None # e.g. "vehicles in Sector B between 1am and 4am"
    sector: Optional[str] = None
    camera_id: Optional[str] = None
    object_class: Optional[str] = None # person, car, truck
    plate_text: Optional[str] = None
    track_id: Optional[str] = None
    severity: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_confidence: Optional[float] = 0.5
    limit: int = 50

class SearchResultItem(BaseModel):
    result_type: str # INCIDENT, EVENT, SIGHTING, VEHICLE
    id: str
    camera_id: str
    sector: str
    timestamp: datetime
    title: str
    description: str
    confidence: float
    evidence_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class VideoIntelligenceSearchResponse(BaseModel):
    total_found: int
    execution_time_ms: float
    results: List[SearchResultItem]
