"""
IBVAP - Night-Time Movement Detection Engine
Low-light optical validation and nighttime surveillance window rules.
"""
from datetime import datetime, timezone
from typing import Dict, Any

class NightMovementDetector:
    def __init__(self, night_start_hour: int = 19, night_end_hour: int = 5):
        self.night_start_hour = night_start_hour
        self.night_end_hour = night_end_hour

    def is_night_surveillance_window(self, check_time: datetime = None) -> bool:
        t = check_time or datetime.now(timezone.utc)
        hour = t.hour
        # Night is between 19:00 (7 PM) and 05:00 (5 AM)
        return hour >= self.night_start_hour or hour < self.night_end_hour

    def evaluate_night_activity(self, frame_mean_luminance: float = 42.0) -> Dict[str, Any]:
        is_night = self.is_night_surveillance_window()
        is_low_light = frame_mean_luminance < 60.0

        return {
            "is_night_operation": is_night or is_low_light,
            "low_light_mode": is_low_light,
            "optical_enhancement_applied": True if is_low_light else False,
            "risk_weight_bonus": 15 if (is_night or is_low_light) else 0
        }

night_detector = NightMovementDetector()
