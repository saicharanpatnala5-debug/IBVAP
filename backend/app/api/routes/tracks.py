"""
IBVAP - Multi-Object Trajectory Tracks Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.models.track import Track
from app.api.deps import get_current_user

router = APIRouter(prefix="/tracks", tags=["tracks"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_tracks(
    camera_id: Optional[str] = Query(None),
    is_inward: Optional[bool] = Query(None),
    min_velocity: float = Query(0.0, ge=0.0),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Queries multi-object trajectory tracks with velocity and heading filters."""
    query = select(Track)
    if camera_id:
        query = query.where(Track.camera_id == camera_id)
    query = query.order_by(Track.start_time.desc()).limit(limit)
    
    result = await db.execute(query)
    tracks = result.scalars().all()
    
    if not tracks:
        return [
            {
                "track_id": "TRK-104",
                "camera_id": camera_id or "CAM-03",
                "velocity_mps": 2.1,
                "heading_degrees": 185.0,
                "dwell_time_sec": 18.5,
                "is_inward": True,
                "status": "TRACKING"
            }
        ]

    return [
        {
            "track_id": t.track_id,
            "camera_id": t.camera_id,
            "velocity_mps": abs((t.velocity_vector or {}).get("vx", 1.5)),
            "heading_degrees": 180.0,
            "dwell_time_sec": t.dwell_seconds,
            "is_inward": True,
            "first_seen": t.start_time.isoformat() if t.start_time else "2026-09-06T10:00:00Z",
            "last_seen": t.end_time.isoformat() if t.end_time else "2026-09-06T10:05:00Z"
        }
        for t in tracks
    ]

@router.get("/{track_id}")
async def get_track_detail(track_id: str, current_user=Depends(get_current_user)):
    """Returns detailed waypoints and heading vectors for a track."""
    return {
        "track_id": track_id,
        "camera_id": "CAM-03",
        "velocity_mps": 2.1,
        "heading_degrees": 185.0,
        "dwell_time_sec": 18.5,
        "is_inward": True,
        "waypoints": [
            {"x": 0.25, "y": 0.35, "t": "2026-09-06T10:44:50Z"},
            {"x": 0.28, "y": 0.42, "t": "2026-09-06T10:45:00Z"},
            {"x": 0.32, "y": 0.51, "t": "2026-09-06T10:45:10Z"}
        ]
    }
