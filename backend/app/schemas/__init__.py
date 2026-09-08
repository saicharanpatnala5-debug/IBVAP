"""
IBVAP - Schemas Registry
"""
from app.schemas.auth import Token, TokenData, UserLogin, UserCreate, UserResponse
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse, CameraTopologyCreate, TopologyGraphResponse
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse
from app.schemas.event import DetectionResponse, TrackResponse, EventCreate, EventResponse, EventFilterParams
from app.schemas.incident import IncidentResponse, IncidentDetailResponse, IncidentStatusUpdate, IncidentTimelineItem
from app.schemas.alert import AlertResponse, AlertAcknowledgeRequest, AlertEscalateRequest, ExplainabilityCard
from app.schemas.anpr import VehiclePlateCreate, VehiclePlateResponse, PlateSearchRequest
from app.schemas.face import FaceSightingResponse, WatchlistCreate, WatchlistResponse
from app.schemas.search import VideoIntelligenceSearchQuery, VideoIntelligenceSearchResponse, SearchResultItem
from app.schemas.health import CameraHealthResponse, SystemHealthSummary
from app.schemas.audit import AuditLogCreate, AuditLogResponse
from app.schemas.demo import DemoScenarioStep, DemoScenarioTriggerRequest, DemoScenarioStatus

__all__ = [
    "Token", "TokenData", "UserLogin", "UserCreate", "UserResponse",
    "CameraCreate", "CameraUpdate", "CameraResponse", "CameraTopologyCreate", "TopologyGraphResponse",
    "ZoneCreate", "ZoneUpdate", "ZoneResponse",
    "DetectionResponse", "TrackResponse", "EventCreate", "EventResponse", "EventFilterParams",
    "IncidentResponse", "IncidentDetailResponse", "IncidentStatusUpdate", "IncidentTimelineItem",
    "AlertResponse", "AlertAcknowledgeRequest", "AlertEscalateRequest", "ExplainabilityCard",
    "VehiclePlateCreate", "VehiclePlateResponse", "PlateSearchRequest",
    "FaceSightingResponse", "WatchlistCreate", "WatchlistResponse",
    "VideoIntelligenceSearchQuery", "VideoIntelligenceSearchResponse", "SearchResultItem",
    "CameraHealthResponse", "SystemHealthSummary",
    "AuditLogCreate", "AuditLogResponse",
    "DemoScenarioStep", "DemoScenarioTriggerRequest", "DemoScenarioStatus"
]
