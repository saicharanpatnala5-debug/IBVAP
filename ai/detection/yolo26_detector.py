"""
IBVAP - YOLO26 Compatibility Wrapper
Delegates all detection to the real YOLOv8n detector (real_detector.py).
Preserves the YOLO26Detector class name and API for backward compatibility
with existing tests and imports.

The real inference is performed by ai.detection.real_detector.RealDetector.
"""
import time
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from ai.detection.detector import BaseDetector, BoundingBox
    from ai.detection.real_detector import get_detector, RealDetector
except ImportError:
    from app.ai.detection.detector import BaseDetector, BoundingBox
    from app.ai.detection.real_detector import get_detector, RealDetector


class YOLO26Detector(BaseDetector):
    """
    Backward-compatible wrapper that delegates to the real YOLOv8n detector.
    Maintains the YOLO26Detector API so existing code/tests don't break.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.45,
        iou_threshold: float = 0.45,
        weights_path: Optional[str] = None,
        enable_small_target_head: bool = True,
        enable_multi_spectral: bool = True,
        precision: str = "FP16"
    ):
        super().__init__(confidence_threshold=confidence_threshold, iou_threshold=iou_threshold)

        # Delegate to real detector
        self._real = get_detector()

        # Backward-compat attributes
        self.architecture = self._real.model_name
        self.version = self._real.model_version
        self.precision = precision
        self.input_size = (640, 640)
        self.classes = [
            "person", "vehicle", "drone", "military_rucksack", "weapon", "wildlife"
        ]
        self.threat_classes = self.classes
        self.threat_weights = {
            "person": 0.85, "vehicle": 0.75, "drone": 0.95,
            "military_rucksack": 0.80, "weapon": 0.99, "wildlife": 0.10
        }

    def detect(self, frame: np.ndarray, is_thermal: bool = False) -> List[BoundingBox]:
        """Delegates to the real YOLOv8n detector."""
        return self._real.detect(frame, is_thermal=is_thermal)

    def detect_multi_spectral(
        self, optical_frame: np.ndarray, thermal_frame: np.ndarray
    ) -> List[BoundingBox]:
        """
        Multi-spectral detection — runs real detection on optical frame.
        True dual-spectrum fusion requires specialized hardware/models.
        """
        optical_dets = self._real.detect(optical_frame, is_thermal=False)
        thermal_dets = self._real.detect(thermal_frame, is_thermal=True)

        # Merge and deduplicate detections
        all_dets = optical_dets + thermal_dets
        for d in thermal_dets:
            d.attributes["spectral_mode"] = "thermal"
        for d in optical_dets:
            d.attributes["spectral_mode"] = "optical"

        return self.apply_nms(all_dets) if all_dets else []

    def detect_border_threats(
        self, frame: np.ndarray, is_thermal: bool = False
    ) -> Dict[str, Any]:
        """Generates real threat assessment metadata from actual detections."""
        start = time.perf_counter()
        detections = self.detect(frame, is_thermal=is_thermal)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        # Build real threat summary
        threat_summary = {}
        for d in detections:
            cls = d.class_name
            threat_summary[cls] = threat_summary.get(cls, 0) + 1

        is_high_threat = any(
            cls in ("person", "weapon", "drone") for cls in threat_summary
        )

        health = self._real.get_health()

        return {
            "model": self.architecture,
            "version": self.version,
            "device": health.get("device", "cpu"),
            "latency_ms": round(elapsed_ms, 2),
            "mAP_50_95": None,  # Not measured — would require validation set
            "is_high_threat": is_high_threat,
            "threat_summary": threat_summary,
            "total_detections": len(detections),
            "detections": [d.to_dict() for d in detections],
            "status": "ONLINE_ACTIVE" if self._real.is_ready() else "MODEL_UNAVAILABLE",
        }


# Global singleton — backward compatibility
yolo26_detector = YOLO26Detector()
