"""
IBVAP - Route Exporters
"""
from app.api.routes.auth import router as auth_router
from app.api.routes.cameras import router as cameras_router
from app.api.routes.zones import router as zones_router
from app.api.routes.events import router as events_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.alerts import router as alerts_router
from app.api.routes.anpr import router as anpr_router
from app.api.routes.faces import router as faces_router
from app.api.routes.search import router as search_router
from app.api.routes.health import router as health_router
from app.api.routes.audit import router as audit_router
from app.api.routes.demo import router as demo_router
from app.api.routes.streams import router as streams_router
from app.api.routes.detections import router as detections_router
from app.api.routes.tracks import router as tracks_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.analytics import router as analytics_router

__all__ = [
    "auth_router",
    "cameras_router",
    "zones_router",
    "events_router",
    "incidents_router",
    "alerts_router",
    "anpr_router",
    "faces_router",
    "search_router",
    "health_router",
    "audit_router",
    "demo_router",
    "streams_router",
    "detections_router",
    "tracks_router",
    "vehicles_router",
    "analytics_router"
]
