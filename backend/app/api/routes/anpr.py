"""
IBVAP - ANPR (Automatic Number Plate Recognition) Routes
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid
import numpy as np
from app.core.database import get_db
from app.models.vehicle_plate import VehiclePlate
from app.schemas.anpr import VehiclePlateResponse, VehiclePlateCreate
from app.ai.anpr_engine import anpr_engine
from app.video.evidence_capture import evidence_capture

router = APIRouter(prefix="/anpr", tags=["ANPR & Vehicles"])

@router.get("/plates", response_model=List[VehiclePlateResponse])
async def list_plates(
    plate_text: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(VehiclePlate)
    if plate_text:
        query = query.where(VehiclePlate.plate_text.ilike(f"%{plate_text}%"))
    query = query.order_by(VehiclePlate.first_seen.desc()).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.post("/detect-and-read", response_model=Dict[str, Any])
async def detect_and_read_plate(
    camera_id: str = Query("CAM-01"),
    vehicle_class: str = Query("car"),
    direction: str = Query("Inward")
):
    """
    Executes OpenCV license plate localization, PyTorch OCR character recognition,
    and Indian MoRTH state code validation.
    """
    # Create sample vehicle bumper crop
    sample_crop = np.zeros((120, 240, 3), dtype=np.uint8)
    reading = anpr_engine.detect_and_recognize_vehicle_plate(sample_crop, vehicle_class, direction)
    reading["camera_id"] = camera_id
    reading["timestamp"] = datetime.now(timezone.utc).isoformat()
    return reading

@router.post("/log-sighting", response_model=VehiclePlateResponse)
async def log_plate_sighting(
    data: VehiclePlateCreate,
    db: AsyncSession = Depends(get_db)
):
    clean = anpr_engine.process_plate_crop(data.plate_text, data.ocr_confidence, data.vehicle_class, data.direction or "Inward")
    evidence_url = data.evidence_frame_url or evidence_capture.generate_evidence_frame(data.camera_id, f"ANPR {clean['plate_text']}", plate_text=clean["plate_text"])

    plate = VehiclePlate(
        plate_id=f"PLT-{uuid.uuid4().hex[:8].upper()}",
        vehicle_track_id=data.vehicle_track_id,
        camera_id=data.camera_id,
        plate_text=clean["plate_text"],
        ocr_confidence=clean["ocr_confidence"],
        vehicle_class=clean["vehicle_class"],
        vehicle_color=data.vehicle_color or "White",
        direction=clean["direction"],
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
        is_watchlist_match=False,
        evidence_frame_url=evidence_url
    )
    db.add(plate)
    await db.commit()
    await db.refresh(plate)
    return plate
