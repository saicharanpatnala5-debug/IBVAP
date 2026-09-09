"""
IBVAP - Core Configuration
Pydantic v2 settings configuration with environment override.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "IBVAP - Intelligent Border Video Analytics Platform"
    VERSION: str = "2.0.0-SIH2026"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # Runtime Mode: "production" | "demo" | "test"
    # production = genuine inference only, no synthetic fallbacks
    # demo = controlled simulation allowed, clearly labeled
    # test = deterministic fixtures/mocks allowed
    IBVAP_MODE: str = "demo"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ibvap.db"

    # JWT & Auth
    SECRET_KEY: str = "sih2026-ibvap-deep-border-intelligence-super-secure-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*"
    ]

    # ── Object Detection ──
    DETECTION_CONFIDENCE: float = 0.25
    DETECTION_IOU_THRESHOLD: float = 0.45
    DETECTION_MODEL_PATH: str = "yolov8n.pt"
    DETECTION_IMG_SIZE: int = 640

    # ── Tracking ──
    TRACK_HIGH_THRESH: float = 0.6
    TRACK_MATCH_THRESH: float = 0.8
    TRACK_MAX_LOST_FRAMES: int = 30
    TRACK_TRAJECTORY_WINDOW: int = 100

    # ── ANPR ──
    ANPR_CONFIDENCE: float = 0.5
    ANPR_MIN_PLATE_ASPECT: float = 2.0
    ANPR_MAX_PLATE_ASPECT: float = 5.5
    ANPR_MULTI_FRAME_WINDOW: int = 5
    ANPR_VOTING_MIN_AGREEMENT: float = 0.6

    # ── Face Detection & Recognition ──
    FACE_DETECTION_CONFIDENCE: float = 0.65
    FACE_MIN_SHARPNESS: float = 40.0
    FACE_MATCH_THRESHOLD: float = 0.6
    FACE_EMBEDDING_DIM: int = 512

    # ── Analytics Pipeline ──
    ANALYTICS_FPS: int = 10
    MAX_QUEUE_DEPTH: int = 30

    # ── Explainable Risk Scoring Engine Weights ──
    WEIGHT_ZONE_INTRUSION: int = 30
    WEIGHT_NIGHT_CONTEXT: int = 15
    WEIGHT_LOITERING: int = 15
    WEIGHT_INWARD_DIRECTION: int = 20
    WEIGHT_UNKNOWN_VEHICLE: int = 20
    WEIGHT_MULTIPLE_OBJECTS: int = 10
    WEIGHT_WATCHLIST_MATCH: int = 35
    WEIGHT_CROSS_CAMERA: int = 15
    WEIGHT_REPEATED_INTRUSION: int = 20

    # Risk Severity Thresholds
    RISK_THRESHOLD_NORMAL: int = 29
    RISK_THRESHOLD_LOW: int = 59
    RISK_THRESHOLD_MEDIUM: int = 89
    RISK_THRESHOLD_HIGH: int = 119
    # 120+ is CRITICAL

    # ── Virtual Fence ──
    ZONE_COOLDOWN_SECONDS: float = 30.0
    ZONE_ALERT_DEDUP_SECONDS: float = 10.0

    # Loitering & Trajectory thresholds
    LOITERING_DWELL_SECONDS: float = 20.0
    LOITERING_DISPLACEMENT_RADIUS: float = 0.05
    CONFIRMATION_MIN_FRAMES: int = 3

    # ── Night Detection ──
    NIGHT_START_HOUR: int = 19
    NIGHT_END_HOUR: int = 5
    NIGHT_LUMINANCE_THRESHOLD: float = 60.0

    # Storage Paths
    STORAGE_DIR: str = "./storage"
    SNAPSHOTS_DIR: str = "./storage/snapshots"
    CLIPS_DIR: str = "./storage/clips"
    OFFLINE_BUFFER_DIR: str = "./storage/buffer"
    EVIDENCE_DIR: str = "./storage/evidence"

    # Video & Stream Ingestion
    RTSP_RECONNECT_MAX_RETRIES: int = 5
    RTSP_RECONNECT_BACKOFF_SECONDS: float = 3.0
    STREAM_HEARTBEAT_INTERVAL: float = 5.0
    CAMERA_HEALTH_CHECK_INTERVAL: float = 10.0
    STREAM_READ_TIMEOUT_MS: int = 5000

    # Edge Deployment & Synchronization
    EDGE_MODE: bool = False
    OFFLINE_SYNC_INTERVAL: float = 30.0
    EDGE_QUEUE_MAX_SIZE: int = 10000

settings = Settings()

# Set IBVAP_MODE environment variable so mode.py picks it up
os.environ.setdefault("IBVAP_MODE", settings.IBVAP_MODE)

# Ensure directories exist
for p in [settings.STORAGE_DIR, settings.SNAPSHOTS_DIR, settings.CLIPS_DIR,
          settings.OFFLINE_BUFFER_DIR, settings.EVIDENCE_DIR]:
    os.makedirs(p, exist_ok=True)

