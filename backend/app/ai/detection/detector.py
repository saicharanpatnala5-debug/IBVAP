"""
IBVAP - Core Object Detector Abstraction
Provides high-performance object detection interface supporting YOLO26, YOLO11, ONNX Runtime, and CPU simulation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import time

@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str
    track_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def centroid(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    @property
    def aspect_ratio(self) -> float:
        return self.width / max(0.001, self.height)

    def to_xyxy(self) -> List[float]:
        return [self.x1, self.y1, self.x2, self.y2]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bbox": [round(self.x1, 4), round(self.y1, 4), round(self.x2, 4), round(self.y2, 4)],
            "confidence": round(self.confidence, 4),
            "class_id": self.class_id,
            "class_name": self.class_name,
            "track_id": self.track_id,
            "centroid": [round(c, 4) for c in self.centroid],
            "attributes": self.attributes
        }

class BaseDetector:
    """
    Abstract detector interface with NMS (Non-Maximum Suppression) and batch inference hooks.
    """

    def __init__(self, confidence_threshold: float = 0.45, iou_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.classes = ["person", "bicycle", "car", "motorcycle", "bus", "truck"]

    def compute_iou(self, boxA: List[float], boxB: List[float]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return iou

    def apply_nms(self, boxes: List[BoundingBox]) -> List[BoundingBox]:
        if not boxes:
            return []

        sorted_boxes = sorted(boxes, key=lambda b: b.confidence, reverse=True)
        selected: List[BoundingBox] = []

        while sorted_boxes:
            current = sorted_boxes.pop(0)
            selected.append(current)
            sorted_boxes = [
                b for b in sorted_boxes
                if b.class_id != current.class_id or self.compute_iou(current.to_xyxy(), b.to_xyxy()) < self.iou_threshold
            ]

        return selected

    def detect(self, frame: np.ndarray) -> List[BoundingBox]:
        """Override with specific model inference."""
        raise NotImplementedError
