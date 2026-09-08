"""
IBVAP - Virtual Fence Intrusion Detector
High-precision Ray-Casting algorithm for polygonal restricted zone boundary breach detection.
"""
from typing import List, Dict, Any, Tuple
from ai.detection.detector import BoundingBox

class IntrusionDetector:
    def check_point_in_polygon(self, point: Tuple[float, float], polygon: List[List[float]]) -> bool:
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

    def evaluate_intrusion(self, bbox: BoundingBox, zone_polygon: List[List[float]], zone_name: str = "Red Zone") -> Dict[str, Any]:
        # Test lower center of bounding box (footprint of target)
        footprint = ((bbox.x1 + bbox.x2) / 2.0, bbox.y2)
        is_breach = self.check_point_in_polygon(footprint, zone_polygon)

        return {
            "is_intrusion": is_breach,
            "zone_name": zone_name,
            "footprint": footprint,
            "confidence": bbox.confidence if is_breach else 0.0
        }

intrusion_detector = IntrusionDetector()
