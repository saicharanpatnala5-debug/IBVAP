"""
IBVAP - AI Package Registry
"""
from app.ai.geometry import is_point_in_polygon, calculate_velocity_and_direction
from app.ai.risk_engine import risk_engine, RiskScoringEngine
from app.ai.event_fusion import event_fusion_engine, EventFusionEngine
from app.ai.multicamera import multicamera_engine, MultiCameraTopologyEngine
from app.ai.tracking_engine import tracker_engine, TrajectoryTracker
from app.ai.anpr_engine import anpr_engine, ANPRPipeline
from app.ai.face_engine import face_engine, FaceAnalyticsEngine

__all__ = [
    "is_point_in_polygon",
    "calculate_velocity_and_direction",
    "risk_engine",
    "RiskScoringEngine",
    "event_fusion_engine",
    "EventFusionEngine",
    "multicamera_engine",
    "MultiCameraTopologyEngine",
    "tracker_engine",
    "TrajectoryTracker",
    "anpr_engine",
    "ANPRPipeline",
    "face_engine",
    "FaceAnalyticsEngine"
]

from app.ai.detection.yolo26_detector import YOLO26Detector, yolo26_detector
