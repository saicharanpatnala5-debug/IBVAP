"""
IBVAP - Microsecond Ray-Casting Edge Polygonal Zone Containment
Evaluates targets against virtual fences on forward edge nodes in < 2 microseconds.
"""

from typing import List, Dict, Any

class EdgeZoneEvaluator:
    def check_point_in_polygon(self, x: float, y: float, polygon: List[List[float]]) -> bool:
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

    def evaluate_track(self, track: Dict[str, Any], polygon: List[List[float]]) -> Dict[str, Any]:
        # Test footprint of target (bottom-center of bounding box)
        bbox = track["bbox"]
        footprint_x = (bbox[0] + bbox[2]) / 2.0
        footprint_y = bbox[3]

        is_inside = self.check_point_in_polygon(footprint_x, footprint_y, polygon)
        return {
            "track_id": track["track_id"],
            "class_name": track["class_name"],
            "is_breach": is_inside,
            "footprint": [footprint_x, footprint_y]
        }

edge_zone_evaluator = EdgeZoneEvaluator()
