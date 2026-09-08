"""
IBVAP - Unified ANPR (Automatic Number Plate Recognition) Pipeline
Connects OpenCV plate localization -> PyTorch/OCR sequence extraction -> syntax validation.
"""
from typing import Dict, Any, Optional
import numpy as np

try:
    from ai.anpr.plate_detector import plate_detector
    from ai.anpr.ocr import plate_ocr
except ImportError:
    from app.ai.anpr.plate_detector import plate_detector
    from app.ai.anpr.ocr import plate_ocr

class ANPRPipeline:
    def __init__(self):
        self.detector = plate_detector
        self.ocr = plate_ocr

    def process_plate_crop(
        self,
        plate_text_raw: str,
        ocr_confidence: float = 0.94,
        vehicle_class: str = "car",
        direction: str = "Inward"
    ) -> Dict[str, Any]:
        """Validates and processes raw plate readings."""
        syntax = self.ocr.validate_indian_syntax(plate_text_raw)
        return {
            "plate_text": syntax["clean_text"],
            "ocr_confidence": round(ocr_confidence, 4),
            "vehicle_class": vehicle_class,
            "direction": direction,
            "is_valid_registration_syntax": syntax["is_valid"],
            "is_high_confidence": ocr_confidence >= 0.80
        }

    def detect_and_recognize_vehicle_plate(
        self,
        vehicle_crop: np.ndarray,
        vehicle_class: str = "car",
        direction: str = "Inward"
    ) -> Dict[str, Any]:
        """
        End-to-end ANPR from a raw vehicle image crop.
        """
        det_res = self.detector.detect_plate(vehicle_crop)
        ocr_res = self.ocr.recognize(det_res.plate_crop)

        return {
            "plate_text": ocr_res["plate_text"],
            "state_code": ocr_res["state_code"],
            "plate_bbox": det_res.bbox,
            "detector_confidence": round(det_res.confidence, 4),
            "ocr_confidence": ocr_res["confidence"],
            "char_confidences": ocr_res["char_confidences"],
            "is_valid_registration_syntax": ocr_res["is_valid_syntax"],
            "is_high_security_plate": ocr_res["is_high_security_plate"],
            "vehicle_class": vehicle_class,
            "direction": direction
        }

anpr_engine = ANPRPipeline()
