"""
IBVAP - Loitering Detection Engine
Monitors dwell duration and centroid displacement to detect unauthorized lingering/loitering.
Supports both normalized and pixel coordinates, and per-track temporal evaluation.
"""
from typing import List, Dict, Any, Tuple, Union, Optional
import math
import time

class LoiteringDetector:
    def __init__(
        self,
        dwell_threshold_seconds: float = 20.0,
        stationary_radius: float = 50.0,  # pixels (or 0.05 if normalized)
        cooldown_seconds: float = 15.0
    ):
        self.dwell_threshold = dwell_threshold_seconds
        self.stationary_radius = stationary_radius
        self.cooldown_seconds = cooldown_seconds
        self._last_alert: Dict[str, float] = {}

    def _extract_coords(self, point: Union[Dict[str, Any], Tuple[float, float], List[float]]) -> Tuple[float, float]:
        if isinstance(point, dict):
            return float(point.get("x", 0.0)), float(point.get("y", 0.0))
        elif isinstance(point, (tuple, list)) and len(point) >= 2:
            return float(point[0]), float(point[1])
        return 0.0, 0.0

    def evaluate_loitering(
        self,
        trajectory: List[Union[Dict[str, Any], Tuple[float, float], List[float]]],
        dwell_seconds: float,
        track_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate if target has remained within a localized radius for longer than dwell threshold.
        """
        if dwell_seconds < self.dwell_threshold or len(trajectory) < 5:
            return {
                "is_loitering": False,
                "is_new_alert": False,
                "dwell_seconds": round(dwell_seconds, 1),
                "displacement_radius": 0.0,
                "alert_escalation": "NONE"
            }

        # Calculate bounding radius of recent trajectory points (last 15 points)
        recent = trajectory[-min(15, len(trajectory)):]
        coords = [self._extract_coords(p) for p in recent]
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]

        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)
        displacement = math.sqrt(dx**2 + dy**2)

        # Dynamic radius adaptation: if coordinates are normalized (0..1), scale threshold
        max_coord = max(max(xs, default=0.0), max(ys, default=0.0))
        effective_radius = self.stationary_radius if max_coord > 1.5 else (self.stationary_radius / 1000.0)

        is_loitering = displacement <= effective_radius

        is_new_alert = False
        if is_loitering and track_id:
            now = time.time()
            last = self._last_alert.get(track_id, 0.0)
            if now - last >= self.cooldown_seconds:
                is_new_alert = True
                self._last_alert[track_id] = now
        elif is_loitering:
            is_new_alert = True

        severity = "NONE"
        if is_loitering:
            if dwell_seconds >= 60.0:
                severity = "CRITICAL"
            elif dwell_seconds >= 40.0:
                severity = "HIGH"
            else:
                severity = "MEDIUM"

        return {
            "is_loitering": is_loitering,
            "is_new_alert": is_new_alert,
            "dwell_seconds": round(dwell_seconds, 1),
            "displacement_radius": round(displacement, 3),
            "alert_escalation": severity
        }

    def evaluate_track(
        self,
        track_id: str,
        points: List[Tuple[float, float]],
        timestamps: List[float]
    ) -> Dict[str, Any]:
        """
        Directly evaluates track history from tracker.
        """
        if not points or not timestamps or len(points) < 5:
            return {"is_loitering": False, "is_new_alert": False, "dwell_seconds": 0.0}

        dwell = timestamps[-1] - timestamps[0]
        return self.evaluate_loitering(points, dwell, track_id=track_id)

loitering_detector = LoiteringDetector()
