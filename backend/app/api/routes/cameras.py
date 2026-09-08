"""
IBVAP - Camera Management & Topology Routes
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.camera import Camera, CameraTopologyEdge
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse, CameraTopologyCreate, CameraTopologyResponse, TopologyGraphResponse
from app.services.camera_service import camera_service
from app.video.rtsp_manager import rtsp_manager
from app.ai.multicamera import multicamera_engine

router = APIRouter(prefix="/cameras", tags=["Cameras"])

@router.get("", response_model=List[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    return await camera_service.get_all(db)

@router.post("", response_model=CameraResponse)
async def register_camera(camera_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    existing = await camera_service.get_by_id(db, camera_in.camera_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Camera {camera_in.camera_id} already registered")
    
    cam = await camera_service.create(db, camera_in)
    rtsp_manager.register_stream(cam.camera_id, cam.stream_url)
    return cam

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    cam = await camera_service.get_by_id(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(camera_id: str, camera_in: CameraUpdate, db: AsyncSession = Depends(get_db)):
    cam = await camera_service.update(db, camera_id, camera_in)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.get("/{camera_id}/stream")
async def get_stream_metadata(camera_id: str, db: AsyncSession = Depends(get_db)):
    cam = await camera_service.get_by_id(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    status_info = rtsp_manager.get_stream_status(camera_id)
    return {
        "camera_id": cam.camera_id,
        "name": cam.name,
        "stream_url": cam.stream_url,
        "resolution": cam.resolution,
        "telemetry": status_info
    }

@router.get("/{camera_id}/predict-handoff")
async def get_predictive_handoff(camera_id: str):
    """Predict candidate next camera based on multi-camera graph topology."""
    handoff = multicamera_engine.predict_next_camera(camera_id)
    if not handoff:
        return {"has_prediction": False, "message": f"No candidate outgoing topology edges from {camera_id}"}
    return {"has_prediction": True, "handoff": handoff}

@router.get("/topology/graph", response_model=TopologyGraphResponse)
async def get_topology_graph(db: AsyncSession = Depends(get_db)):
    nodes = await camera_service.get_all(db)
    edges = await camera_service.get_topology_edges(db)
    return {"nodes": nodes, "edges": edges}

@router.post("/topology/edge", response_model=CameraTopologyResponse)
async def add_topology_edge(edge_in: CameraTopologyCreate, db: AsyncSession = Depends(get_db)):
    return await camera_service.add_topology_edge(db, edge_in)
