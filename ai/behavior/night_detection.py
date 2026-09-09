"""
IBVAP - Night-Time Movement Detection Engine
Combines REAL frame luminance measurement with configurable time windows.
Never defaults to a hardcoded luminance value.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

logger = logging.getLogger("ibvap.behavior.night")


class NightMovementDetector:
    def __init__(self, night_start_hour: int = 19, night_end_hour: int = 5,
                 luminance_threshold: float = 60.0):
        self.night_start_hour = night_start_hour
        self.night_end_hour = night_end_hour
        self.luminance_threshold = luminance_threshold

    def is_night_surveillance_window(self, check_time: Optional[datetime] = None) -> bool:
        """Check if current time is within night surveillance window."""
        t = check_time or datetime.now(timezone.utc)
        hour = t.hour
        # Night is between night_start (7 PM) and night_end (5 AM)
        return hour >= self.night_start_hour or hour < self.night_end_hour

    def measure_luminance(self, frame: np.ndarray) -> float:
        """
        Measures REAL mean luminance of the frame.
        Returns the average pixel intensity (0-255 scale).
        """
        if frame is None or frame.size == 0:
            return 0.0

        if CV2_AVAILABLE and len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return float(np.mean(gray))
        elif len(frame.shape) == 2:
            return float(np.mean(frame))
        else:
            return float(np.mean(frame))

    def evaluate_night_activity(
        self,
        frame: Optional[np.ndarray] = None,
        frame_mean_luminance: Optional[float] = None,
        check_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates night/low-light conditions using REAL frame analysis.
        
        Args:
            frame: The actual video frame to measure luminance from
            frame_mean_luminance: Pre-computed luminance (used if frame is None)
            check_time: Optional datetime override for testing
        """
        is_night = self.is_night_surveillance_window(check_time)

        # Measure REAL luminance from the actual frame
        if frame is not None:
            measured_luminance = self.measure_luminance(frame)
        elif frame_mean_luminance is not None:
            measured_luminance = frame_mean_luminance
        else:
            # No frame or luminance provided — can only use time-based detection
            measured_luminance = None

        is_low_light = False
        if measured_luminance is not None:
            is_low_light = measured_luminance < self.luminance_threshold

        return {
            "is_night_operation": is_night or is_low_light,
            "is_night_window": is_night,
            "low_light_mode": is_low_light,
            "measured_luminance": round(measured_luminance, 1) if measured_luminance is not None else None,
            "luminance_threshold": self.luminance_threshold,
            "optical_enhancement_recommended": is_low_light,
            "risk_weight_bonus": 15 if (is_night or is_low_light) else 0
        }


night_detector = NightMovementDetector()
