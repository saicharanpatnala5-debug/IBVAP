"""
IBVAP - Unified ANPR (Automatic Number Plate Recognition) Pipeline
Connects OpenCV plate localization -> Real OCR extraction -> syntax validation.
"""
from typing import Dict, Any, Optional
import re
import numpy as np

try:
    from ai.anpr.plate_detector import plate_detector
    from ai.anpr.ocr import plate_ocr
    from ai.anpr.validator import plate_validator
except ImportError:
    from app.ai.anpr.plate_detector import plate_detector
    from app.ai.anpr.ocr import plate_ocr
    from app.ai.anpr.validator import plate_validator


class ANPRPipeline:
    def __init__(self):
        self.detector = plate_detector
        self.ocr = plate_ocr
        self.validator = plate_validator

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
        direction: str = "Inward",
        track_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End-to-end ANPR from a raw vehicle image crop.
        Returns UNKNOWN when no plate is found or OCR fails.
        """
        # Step 1: Detect plate region
        det_res = self.detector.detect_plate(vehicle_crop)

        if det_res is None:
            return {
                "plate_text": "UNKNOWN",
                "plate_norm": "",
                "state_code": "",
                "plate_bbox": [],
                "detector_confidence": 0.0,
                "ocr_confidence": 0.0,
                "confidence_percentage": "0%",
                "agreement_ratio": 0.0,
                "verification_status": "NO_PLATE_DETECTED",
                "requires_human_verification": True,
                "is_verified": False,
                "char_confidences": [],
                "is_valid_registration_syntax": False,
                "is_high_security_plate": False,
                "vehicle_class": vehicle_class,
                "direction": direction,
                "deskew_angle": 0.0,
            }

        # Step 2: Run real OCR on detected plate crop
        ocr_res = self.ocr.recognize(det_res.plate_crop, track_id=track_id, vehicle_class=vehicle_class)

        raw_conf = ocr_res.get("confidence", 0.0)
        plate_text = ocr_res.get("plate_text", "UNKNOWN")
        final_confidence = raw_conf
        agreement_ratio = 1.0
        is_confirmed = raw_conf >= 0.7

        # Step 3: Multi-frame voting if track_id available
        if track_id and plate_text != "UNKNOWN":
            try:
                from ai.anpr.multi_frame_voter import multi_frame_voter
                multi_frame_voter.add_reading(track_id, plate_text, raw_conf)
                consensus = multi_frame_voter.get_consensus(track_id)
                if consensus:
                    plate_text = consensus["plate_text"]
                    agreement_ratio = consensus["agreement_ratio"]
                    is_confirmed = consensus["is_consensus"]
                    final_confidence = consensus["confidence"]
            except ImportError:
                try:
                    from app.ai.anpr.multi_frame_voter import multi_frame_voter
                    multi_frame_voter.add_reading(track_id, plate_text, raw_conf)
                    consensus = multi_frame_voter.get_consensus(track_id)
                    if consensus:
                        plate_text = consensus["plate_text"]
                        agreement_ratio = consensus["agreement_ratio"]
                        is_confirmed = consensus["is_consensus"]
                        final_confidence = consensus["confidence"]
                except ImportError:
                    pass

        req_human = final_confidence < 0.70 or not is_confirmed

        return {
            "plate_text": plate_text,
            "plate_norm": re.sub(r"[^A-Za-z0-9]", "", plate_text).upper() if plate_text != "UNKNOWN" else "",
            "state_code": ocr_res.get("state_code", ""),
            "plate_bbox": det_res.bbox,
            "detector_confidence": round(det_res.confidence, 4),
            "ocr_confidence": round(final_confidence, 4),
            "confidence_percentage": f"{int(final_confidence * 100)}%",
            "agreement_ratio": agreement_ratio,
            "verification_status": "Requires Human Verification" if req_human else "OCR Verified",
            "requires_human_verification": req_human,
            "is_verified": not req_human,
            "char_confidences": ocr_res.get("char_confidences", []),
            "is_valid_registration_syntax": ocr_res.get("is_valid_syntax", False),
            "is_high_security_plate": bool(ocr_res.get("is_high_security_plate", False)) and not req_human,
            "vehicle_class": vehicle_class,
            "direction": direction,
            "deskew_angle": ocr_res.get("deskew_angle", 0.0),
        }


anpr_engine = ANPRPipeline()
