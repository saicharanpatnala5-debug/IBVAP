"""
IBVAP - Model Registry
Imports all models so SQLAlchemy declarative metadata discovers every table.
"""
from app.models.camera import Camera, CameraHealth, CameraTopologyEdge
from app.models.zone import Zone
from app.models.detection import Detection
from app.models.track import Track
from app.models.event import Event
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.vehicle_plate import VehiclePlate
from app.models.face_watchlist import FaceSighting, Watchlist
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.object import DetectedObject
from app.models.vehicle import Vehicle
from app.models.plate import LicensePlate

__all__ = [
    "Camera",
    "CameraHealth",
    "CameraTopologyEdge",
    "Zone",
    "Detection",
    "Track",
    "Event",
    "Incident",
    "Alert",
    "VehiclePlate",
    "FaceSighting",
    "Watchlist",
    "AuditLog",
    "User",
    "DetectedObject",
    "Vehicle",
    "LicensePlate"
]
