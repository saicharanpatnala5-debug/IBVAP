"""
IBVAP - Common Tactical API Schemas
Standardized pagination, geographic points, telemetry envelopes, and status responses.
"""
from typing import Generic, TypeVar, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="1-indexed page number")
    page_size: int = Field(50, ge=1, le=200, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    ascending: bool = Field(False, description="Ascending sort flag")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    page: int
    page_size: int
    has_next: bool

class GeoCoordinate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: Optional[float] = Field(None, description="Altitude in meters")

class NormalizedBBox(BaseModel):
    x1: float = Field(..., ge=0.0, le=1.0)
    y1: float = Field(..., ge=0.0, le=1.0)
    x2: float = Field(..., ge=0.0, le=1.0)
    y2: float = Field(..., ge=0.0, le=1.0)

class TacticalStatusResponse(BaseModel):
    status: str = "SUCCESS"
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None
