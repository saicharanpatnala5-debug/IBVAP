"""
IBVAP - Intelligent Border Video Analytics Platform
Main Application Factory & Lifespan Orchestrator
SIH 2026 | Problem Statement: SIH26187 (SSB / Ministry of Home Affairs)
"""
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging, logger
from app.api.websocket import ws_manager
from app.api.routes import (
    auth_router, cameras_router, zones_router, events_router, incidents_router,
    alerts_router, anpr_router, faces_router, search_router, health_router,
    audit_router, demo_router, streams_router, detections_router,
    tracks_router, vehicles_router, analytics_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    setup_logging()
    logger.info("Initializing IBVAP Backend System...")
    await init_db()
    logger.info("Database schema synchronized.")
    yield
    # Shutdown tasks
    logger.info("Shutting down IBVAP Backend System...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Software-Defined AI Video Intelligence Platform transforming existing CCTV infrastructure into smart border surveillance.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve stored evidence frames & clips statically
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# Serve static dashboard assets & CCTV sample videos
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")
if os.path.exists(VIDEOS_DIR):
    app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount API routes
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(cameras_router, prefix=settings.API_V1_STR)
app.include_router(zones_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(anpr_router, prefix=settings.API_V1_STR)
app.include_router(faces_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)
app.include_router(streams_router, prefix=settings.API_V1_STR)
app.include_router(detections_router, prefix=settings.API_V1_STR)
app.include_router(tracks_router, prefix=settings.API_V1_STR)
app.include_router(vehicles_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)

# Real-Time WebSockets for Alerts & Telemetry
@app.websocket("/ws/alerts")
@app.websocket("/ws/telemetry")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

@app.get("/dashboard", include_in_schema=False)
@app.get("/ui", include_in_schema=False)
async def serve_dashboard():
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"status": "Frontend dashboard static file not found"}

@app.get("/", include_in_schema=False)
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.exists(static_file):
            return FileResponse(static_file)
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
        "sih_scenario_endpoint": "/api/demo/run-scenario"
    }
