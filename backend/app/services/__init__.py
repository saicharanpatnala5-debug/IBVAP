"""
IBVAP - Services Registry
"""
from app.services.camera_service import camera_service, CameraService
from app.services.event_service import event_service, EventService
from app.services.incident_service import incident_service, IncidentService
from app.services.alert_service import alert_service, AlertService
from app.services.search_service import search_service, SearchService
from app.services.audit_service import audit_service, AuditService
from app.services.health_service import health_service, HealthService

__all__ = [
    "camera_service", "CameraService",
    "event_service", "EventService",
    "incident_service", "IncidentService",
    "alert_service", "AlertService",
    "search_service", "SearchService",
    "audit_service", "AuditService",
    "health_service", "HealthService"
]
