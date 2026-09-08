try:
    from ai.detection.detector import BaseDetector, BoundingBox
    from ai.detection.person_detector import PersonDetector
    from ai.detection.vehicle_detector import VehicleDetector
    from ai.detection.yolo26_detector import YOLO26Detector, yolo26_detector
except ImportError:
    from app.ai.detection.detector import BaseDetector, BoundingBox
    from app.ai.detection.person_detector import PersonDetector
    from app.ai.detection.vehicle_detector import VehicleDetector
    from app.ai.detection.yolo26_detector import YOLO26Detector, yolo26_detector
__all__ = ['BaseDetector', 'BoundingBox', 'PersonDetector', 'VehicleDetector', 'YOLO26Detector', 'yolo26_detector']
