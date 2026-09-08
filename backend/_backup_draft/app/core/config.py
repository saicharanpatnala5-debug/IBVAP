"""Application configuration.

All settings are environment-driven (PRD s9: "secrets outside source code").
The prefix is ``IBVAP_``; nested models use ``__`` as the delimiter, e.g.
``IBVAP_RISK__NIGHT_CONTEXT=15``.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Severity = Literal["normal", "low", "medium", "high", "critical"]

_DEV_SECRET = "change-me-dev-only-secret-key"  # noqa: S105 - sentinel, not a credential


class RiskWeights(BaseModel):
    """Weighted, explainable risk factors.

    PRD s12 states these numbers are *illustrative* and must be calibrated on
    prototype data. They are therefore configuration, never constants in the
    scoring code.
    """

    restricted_zone_intrusion: int = 30
    night_context: int = 15
    prolonged_loitering: int = 15
    inward_direction: int = 20
    correlated_signals: int = 10
    vehicle_stopped: int = 10
    unrecognised_plate: int = 12
    low_visibility: int = 5
    perimeter_line_crossing: int = 25
    unknown_face: int = 10

    model_config = {"extra": "forbid"}


class SeverityBands(BaseModel):
    """Lower bound of each severity band (PRD s12 table)."""

    low: int = 30
    medium: int = 60
    high: int = 90
    critical: int = 120

    @model_validator(mode="after")
    def _monotonic(self) -> SeverityBands:
        if not (self.low < self.medium < self.high < self.critical):
            raise ValueError("severity band thresholds must be strictly increasing")
        return self

    def classify(self, score: int) -> Severity:
        if score >= self.critical:
            return "critical"
        if score >= self.high:
            return "high"
        if score >= self.medium:
            return "medium"
        if score >= self.low:
            return "low"
        return "normal"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="IBVAP_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Runtime ---------------------------------------------------------
    environment: Literal["development", "test", "staging", "production"] = "development"
    project_name: str = "IBVAP API"
    api_v1_prefix: str = "/api"
    log_level: str = "INFO"
    log_json: bool = True

    # --- Secrets ---------------------------------------------------------
    secret_key: str = _DEV_SECRET
    credential_key: str | None = None

    # --- Storage ---------------------------------------------------------
    database_url: str = "postgresql+asyncpg://ibvap:ibvap@localhost:5432/ibvap"
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20
    redis_url: str | None = None

    # Dev/demo convenience: create tables on boot instead of running Alembic.
    # Forced off outside development/test.
    auto_create_schema: bool = False

    # --- Auth ------------------------------------------------------------
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 1_209_600
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    jwt_issuer: str = "ibvap"
    jwt_audience: str = "ibvap-api"

    # --- CORS ------------------------------------------------------------
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    # --- Night context ---------------------------------------------------
    default_timezone: str = "Asia/Kolkata"
    night_start_hour: int = Field(default=18, ge=0, le=23)
    night_end_hour: int = Field(default=6, ge=0, le=23)

    # --- Event engine ----------------------------------------------------
    loiter_seconds: int = Field(default=30, gt=0)
    fusion_window_seconds: int = Field(default=60, gt=0)
    track_stale_seconds: int = Field(default=15, gt=0)
    alert_min_severity: Severity = "medium"
    plate_min_confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    cross_camera_min_similarity: float = Field(default=0.72, ge=0.0, le=1.0)
    max_ingest_frames_per_batch: int = Field(default=512, gt=0)

    # --- Camera health ---------------------------------------------------
    camera_offline_after_seconds: int = Field(default=20, gt=0)
    camera_degraded_min_fps: float = Field(default=8.0, gt=0)
    camera_degraded_max_latency_ms: int = Field(default=1_500, gt=0)

    # --- Retention (PRD s17) --------------------------------------------
    event_retention_days: int = Field(default=90, gt=0)
    evidence_retention_days: int = Field(default=30, gt=0)
    audit_retention_days: int = Field(default=365, gt=0)

    # --- Nested ----------------------------------------------------------
    risk: RiskWeights = Field(default_factory=RiskWeights)
    severity_bands: SeverityBands = Field(default_factory=SeverityBands)

    # --- Seed ------------------------------------------------------------
    bootstrap_admin_email: str = "admin@ibvap.local"
    bootstrap_admin_password: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v: object) -> object:
        # Accept both JSON arrays and comma-separated lists.
        if isinstance(v, str) and not v.strip().startswith("["):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("default_timezone")
    @classmethod
    def _known_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"unknown IANA timezone: {v!r}") from exc
        return v

    @model_validator(mode="after")
    def _harden_non_dev(self) -> Settings:
        if self.is_production_like:
            if self.secret_key == _DEV_SECRET or len(self.secret_key) < 32:
                raise ValueError(
                    "IBVAP_SECRET_KEY must be set to a unique value of >=32 chars "
                    f"when IBVAP_ENVIRONMENT={self.environment}"
                )
            if self.auto_create_schema:
                raise ValueError(
                    "auto_create_schema is unsafe outside development; run Alembic migrations"
                )
            if "*" in self.cors_origins:
                raise ValueError("wildcard CORS origin is not allowed outside development")
        return self

    @property
    def is_production_like(self) -> bool:
        return self.environment in ("staging", "production")

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.default_timezone)

    def new_secret(self) -> str:
        """Helper for the seed script / operator tooling."""
        return secrets.token_urlsafe(48)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
