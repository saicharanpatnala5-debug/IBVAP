"""
IBVAP - Camera and Topology Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

class CameraBase(BaseModel):
    name: str
    site: str = "BOP-Alpha"
    sector: str = "Sector-B"
    latitude: float = 28.6139
    longitude: float = 77.2090
    stream_url: str
    fps: float = 25.0
    resolution: str = "1920x1080"
    is_simulated: bool = False
    config_json: Optional[Dict[str, Any]] = {}

class CameraCreate(CameraBase):
    camera_id: str = Field(..., description="Unique camera identifier, e.g. CAM-01")

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    site: Optional[str] = None
    sector: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    stream_url: Optional[str] = None
    status: Optional[str] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    is_active: Optional[bool] = None
    config_json: Optional[Dict[str, Any]] = None

class CameraResponse(CameraBase):
    camera_id: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CameraTopologyCreate(BaseModel):
    from_camera_id: str
    to_camera_id: str
    transition_probability: float = 0.75
    min_transit_seconds: float = 10.0
    max_transit_seconds: float = 60.0
    distance_meters: float = 80.0

class CameraTopologyResponse(CameraTopologyCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TopologyGraphResponse(BaseModel):
    nodes: List[CameraResponse]
    edges: List[CameraTopologyResponse]
