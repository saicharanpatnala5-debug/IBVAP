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
        self.track_readings: Dict[str, List[str]] = {}

    def add_reading(self, vehicle_track_id: str, plate_text: str) -> Dict[str, Any]:
        if vehicle_track_id not in self.track_readings:
            self.track_readings[vehicle_track_id] = []

        readings = self.track_readings[vehicle_track_id]
        readings.append(plate_text)
        if len(readings) > self.window_size:
            readings.pop(0)

        # Majority vote
        counts = Counter(readings)
        top_plate, top_count = counts.most_common(1)[0]
        agreement_ratio = top_count / len(readings)
        is_verified = agreement_ratio >= self.min_agreement_ratio

        return {
            "verified_plate": top_plate,
            "agreement_ratio": round(agreement_ratio, 2),
            "sample_count": len(readings),
            "is_confirmed": is_verified
        }

plate_validator = MultiFramePlateValidator()
