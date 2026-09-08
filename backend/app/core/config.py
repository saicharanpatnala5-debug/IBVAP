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
    VERSION: str = "1.0.0-SIH2026"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

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

    # Explainable Risk Scoring Engine Weights (Calibrated for Border Security MVP)
    WEIGHT_ZONE_INTRUSION: int = 30
    WEIGHT_NIGHT_CONTEXT: int = 15
    WEIGHT_LOITERING: int = 15
    WEIGHT_INWARD_DIRECTION: int = 20
    WEIGHT_UNKNOWN_VEHICLE: int = 20
    WEIGHT_MULTIPLE_OBJECTS: int = 10

    # Risk Severity Thresholds
    RISK_THRESHOLD_NORMAL: int = 29
    RISK_THRESHOLD_LOW: int = 59
    RISK_THRESHOLD_MEDIUM: int = 89
    RISK_THRESHOLD_HIGH: int = 119
    # 120+ is CRITICAL

    # Loitering & Trajectory thresholds
    LOITERING_DWELL_SECONDS: float = 20.0
    CONFIRMATION_MIN_FRAMES: int = 3

    # Storage Paths
    STORAGE_DIR: str = "./storage"
    SNAPSHOTS_DIR: str = "./storage/snapshots"
    CLIPS_DIR: str = "./storage/clips"
    OFFLINE_BUFFER_DIR: str = "./storage/buffer"

    # Video & Stream Ingestion
    RTSP_RECONNECT_MAX_RETRIES: int = 5
    RTSP_RECONNECT_BACKOFF_SECONDS: float = 3.0
    STREAM_HEARTBEAT_INTERVAL: float = 5.0
    CAMERA_HEALTH_CHECK_INTERVAL: float = 10.0

    # Edge Deployment & Synchronization
    EDGE_MODE: bool = False
    OFFLINE_SYNC_INTERVAL: float = 30.0

settings = Settings()

# Ensure directories exist
for p in [settings.STORAGE_DIR, settings.SNAPSHOTS_DIR, settings.CLIPS_DIR, settings.OFFLINE_BUFFER_DIR]:
    os.makedirs(p, exist_ok=True)
