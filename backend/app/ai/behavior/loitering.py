"""
IBVAP - Loitering Detection Engine
Monitors dwell duration inside high-security zones with centroid displacement thresholding.
"""
from typing import List, Dict, Any, Tuple
import math

class LoiteringDetector:
    def __init__(self, dwell_threshold_seconds: float = 20.0, stationary_radius: float = 0.05):
        self.dwell_threshold = dwell_threshold_seconds
        self.stationary_radius = stationary_radius

    def evaluate_loitering(self, trajectory: List[Dict[str, Any]], dwell_seconds: float) -> Dict[str, Any]:
        """
        Evaluate if target has remained within a localized radius for longer than dwell threshold.
        """
        if dwell_seconds < self.dwell_threshold or len(trajectory) < 5:
            return {"is_loitering": False, "dwell_seconds": dwell_seconds}

        # Calculate bounding radius of recent trajectory points
        recent = trajectory[-15:]
        xs = [p["x"] for p in recent]
        ys = [p["y"] for p in recent]
        displacement = math.sqrt((max(xs) - min(xs))**2 + (max(ys) - min(ys))**2)

        is_loitering = displacement <= self.stationary_radius
        return {
            "is_loitering": is_loitering,
            "dwell_seconds": round(dwell_seconds, 1),
            "displacement_radius": round(displacement, 3),
            "alert_escalation": "HIGH" if dwell_seconds > 45.0 else "MEDIUM"
        }

loitering_detector = LoiteringDetector()
