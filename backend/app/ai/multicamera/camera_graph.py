"""
IBVAP - Multi-Camera Graph Topology Engine
Models physical camera adjacency, travel distances, and transit probabilities.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

class CameraGraph:
    def __init__(self):
        # Directed graph with transition probabilities and transit times (min, max sec)
        self.adj: Dict[str, List[Dict[str, Any]]] = {
            "CAM-01": [
                {"to_camera": "CAM-03", "prob": 0.78, "min_t": 15, "max_t": 45, "dist_m": 60},
                {"to_camera": "CAM-02", "prob": 0.22, "min_t": 20, "max_t": 60, "dist_m": 85}
            ],
            "CAM-02": [
                {"to_camera": "CAM-04", "prob": 0.85, "min_t": 10, "max_t": 30, "dist_m": 40}
            ],
            "CAM-03": [
                {"to_camera": "CAM-07", "prob": 0.82, "min_t": 25, "max_t": 70, "dist_m": 110}
            ],
            "CAM-07": [
                {"to_camera": "CAM-08", "prob": 0.90, "min_t": 15, "max_t": 40, "dist_m": 50}
            ]
        }

    def get_next_candidates(self, camera_id: str) -> List[Dict[str, Any]]:
        return self.adj.get(camera_id, [])

camera_graph = CameraGraph()
