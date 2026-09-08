"""
IBVAP - Health and Telemetry Schemas
"""
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, ConfigDict

class CameraHealthResponse(BaseModel):
    camera_id: str
    fps: float
    latency_ms: float
    packet_loss_pct: float
    frame_drops: int
    ai_fps: float
    status: str
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SystemHealthSummary(BaseModel):
    system_status: str # HEALTHY, DEGRADED, CRITICAL
    total_cameras: int
    online_cameras: int
    degraded_cameras: int
    offline_cameras: int
    active_incidents: int
    critical_alerts_unack: int
    ai_inference_avg_fps: float
    edge_mode: bool
    camera_health_list: List[CameraHealthResponse] = []
