"""
IBVAP - Tactical Intelligence Analytics Router
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
async def get_analytics_summary(current_user=Depends(get_current_user)):
    """Returns executive border security summary metrics."""
    return {
        "active_border_cameras": 6,
        "total_detections_today": 14280,
        "active_incidents": 1,
        "unacknowledged_alerts": 2,
        "hotlist_vehicle_hits": 2,
        "average_inference_fps": 24.8,
        "system_security_state": "ELEVATED_DEFENSE_STATUS"
    }

@router.get("/hourly-breaches")
async def get_hourly_breaches(current_user=Depends(get_current_user)):
    """Returns 24-hour hourly trend of perimeter violations."""
    return [
        {"hour": f"{h:02d}:00", "breaches": (h * 3 + 1) % 7} for h in range(24)
    ]

@router.get("/risk-distribution")
async def get_risk_distribution(current_user=Depends(get_current_user)):
    """Returns distribution of events across severity bands."""
    return {
        "NORMAL": 12450,
        "LOW": 1420,
        "MEDIUM": 320,
        "HIGH": 78,
        "CRITICAL": 12
    }

@router.get("/camera-uptime")
async def get_camera_uptime(current_user=Depends(get_current_user)):
    """Returns 30-day availability percentage for all camera vantage points."""
    return [
        {"camera_id": "CAM-01", "name": "Approach Road North", "uptime_pct": 99.95},
        {"camera_id": "CAM-02", "name": "North Gate ANPR", "uptime_pct": 99.88},
        {"camera_id": "CAM-03", "name": "Thermal Fence West", "uptime_pct": 99.99},
        {"camera_id": "CAM-04", "name": "Tower 360 PTZ", "uptime_pct": 99.75},
        {"camera_id": "CAM-05", "name": "South Transit", "uptime_pct": 99.90},
        {"camera_id": "CAM-07", "name": "Inner Strategic Depot", "uptime_pct": 100.0}
    ]
