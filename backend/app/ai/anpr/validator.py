"""
IBVAP - Multi-Frame Temporal ANPR Voting Validator
Directly implements Section 21 failure mitigation: aggregates readings across consecutive frames.
"""
from typing import List, Dict, Any
from collections import Counter

class MultiFramePlateValidator:
    def __init__(self, window_size: int = 5, min_agreement_ratio: float = 0.60):
        self.window_size = window_size
        self.min_agreement_ratio = min_agreement_ratio
        self.track_readings: Dict[str, List[Dict[str, Any]]] = {}

    def add_reading(self, vehicle_track_id: str, plate_text: str, confidence: float = 0.90) -> Dict[str, Any]:
        if vehicle_track_id not in self.track_readings:
            self.track_readings[vehicle_track_id] = []

        readings = self.track_readings[vehicle_track_id]
        readings.append({"plate": plate_text, "confidence": confidence})
        if len(readings) > self.window_size:
            readings.pop(0)

        # Weighted majority vote by character & OCR confidence
        weight_by_plate = {}
        count_by_plate = {}
        for r in readings:
            p = r["plate"]
            c = r["confidence"]
            weight_by_plate[p] = weight_by_plate.get(p, 0.0) + c
            count_by_plate[p] = count_by_plate.get(p, 0) + 1

        top_plate = max(weight_by_plate.keys(), key=lambda k: weight_by_plate[k])
        agreement_ratio = count_by_plate[top_plate] / len(readings)
        weighted_conf = weight_by_plate[top_plate] / max(count_by_plate[top_plate], 1)
        is_verified = (agreement_ratio >= self.min_agreement_ratio) and (weighted_conf >= 0.70)

        return {
            "verified_plate": top_plate,
            "agreement_ratio": round(agreement_ratio, 2),
            "weighted_confidence": round(weighted_conf, 4),
            "sample_count": len(readings),
            "is_confirmed": is_verified,
            "requires_human_verification": not is_verified or weighted_conf < 0.70
        }

plate_validator = MultiFramePlateValidator()
