"""
IBVAP - ANPR and Vehicle Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class VehiclePlateCreate(BaseModel):
    camera_id: str
    plate_text: str
    ocr_confidence: float
    vehicle_track_id: Optional[str] = None
    vehicle_class: str = "car"
    vehicle_color: Optional[str] = None
    direction: Optional[str] = None
    evidence_frame_url: Optional[str] = None

class VehiclePlateResponse(BaseModel):
    plate_id: str
    vehicle_track_id: Optional[str] = None
    camera_id: str
    plate_text: str
    ocr_confidence: float
    vehicle_class: str
    vehicle_color: Optional[str] = None
    direction: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    is_watchlist_match: bool
    evidence_frame_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PlateSearchRequest(BaseModel):
    plate_query: str
    sector: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_confidence: float = 0.50
