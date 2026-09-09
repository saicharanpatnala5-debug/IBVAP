"""
IBVAP - Virtual Fence Intrusion Detector
High-precision Ray-Casting algorithm for polygonal restricted zone boundary breach detection.
Includes alert cooldown timers and per-track state deduplication to prevent alert storms.
"""
from typing import List, Dict, Any, Tuple, Optional
import time

try:
    from ai.detection.detector import BoundingBox
except ImportError:
    from app.ai.detection.detector import BoundingBox

class IntrusionDetector:
    def __init__(self, cooldown_seconds: float = 10.0):
        self.cooldown_seconds = cooldown_seconds
        # Maps (zone_name, track_id) -> last_alert_timestamp
        self._last_alert: Dict[str, float] = {}
        # Maps (zone_name, track_id) -> entry_timestamp
        self._entry_times: Dict[str, float] = {}
        # Tracks active state
        self._active_in_zone: Dict[str, bool] = {}

    def check_point_in_polygon(self, point: Tuple[float, float], polygon: List[List[float]]) -> bool:
        if not polygon or len(polygon) < 3:
            return False
        x, y = point[0], point[1]
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]

        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    def evaluate_intrusion(
        self,
        bbox: BoundingBox,
        zone_polygon: List[List[float]],
        zone_name: str = "Red Zone",
        current_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluate if bounding box footprint is inside zone polygon.
        Applies cooldown logic per track_id so rapid consecutive frames do not spam alerts.
        """
        now = current_time if current_time is not None else time.time()
        track_id = bbox.track_id or "UNTRACKED"
        key = f"{zone_name}:{track_id}"

        # Test lower center of bounding box (footprint of target)
        footprint = ((bbox.x1 + bbox.x2) / 2.0, bbox.y2)
        is_breach = self.check_point_in_polygon(footprint, zone_polygon)

        is_new_breach = False
        breach_type = "NONE"
        dwell_seconds = 0.0

        if is_breach:
            if key not in self._entry_times:
                # First time detected inside zone
                self._entry_times[key] = now
                breach_type = "BOUNDARY_CROSSING"
                is_new_breach = True
                self._last_alert[key] = now
            else:
                dwell_seconds = max(0.0, now - self._entry_times[key])
                breach_type = "ZONE_DWELL"
                # Check cooldown
                last_alert = self._last_alert.get(key, 0.0)
                if now - last_alert >= self.cooldown_seconds:
                    is_new_breach = True
                    self._last_alert[key] = now

            self._active_in_zone[key] = True
        else:
            # Target has exited the zone
            if self._active_in_zone.get(key, False):
                self._active_in_zone[key] = False
                self._entry_times.pop(key, None)

        return {
            "is_intrusion": is_breach,
            "is_new_breach": is_new_breach,
            "zone_name": zone_name,
            "track_id": track_id,
            "breach_type": breach_type,
            "dwell_seconds": round(dwell_seconds, 1),
            "footprint": footprint,
            "confidence": bbox.confidence if is_breach else 0.0
        }

    def reset_cooldown(self, zone_name: Optional[str] = None, track_id: Optional[str] = None):
        if zone_name and track_id:
            key = f"{zone_name}:{track_id}"
            self._last_alert.pop(key, None)
            self._entry_times.pop(key, None)
            self._active_in_zone.pop(key, None)
        else:
            self._last_alert.clear()
            self._entry_times.clear()
            self._active_in_zone.clear()

intrusion_detector = IntrusionDetector()
