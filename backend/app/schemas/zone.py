"""
IBVAP - Virtual Fence and Polygonal Zone Schemas
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ZoneBase(BaseModel):
    name: str
    zone_type: str = "RED_RESTRICTED" # GREEN_NORMAL, YELLOW_MONITORING, RED_RESTRICTED
    # List of normalized [x, y] vertices: [[0.1, 0.1], [0.4, 0.1], [0.4, 0.5], [0.1, 0.5]]
    polygon_coords: List[List[float]] = Field(..., min_length=3)
    alert_level: str = "HIGH"
    rules: Optional[Dict[str, Any]] = {}
    is_active: bool = True

class ZoneCreate(ZoneBase):
    zone_id: str
    camera_id: str

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    zone_type: Optional[str] = None
    polygon_coords: Optional[List[List[float]]] = None
    alert_level: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ZoneResponse(ZoneBase):
    zone_id: str
    camera_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
