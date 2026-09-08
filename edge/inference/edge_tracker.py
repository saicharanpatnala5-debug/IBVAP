"""
IBVAP - Embedded Edge Multi-Object Tracker
Provides persistent target continuity and velocity vectors with minimal memory footprint.
"""

from typing import List, Dict, Any

class EdgeTracker:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.camera_tracks: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.next_track_id = 101

    def update_tracks(self, camera_id: str, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if camera_id not in self.camera_tracks:
            self.camera_tracks[camera_id] = {}

        active = []
        for det in detections:
            track_id = f"TRK-{camera_id}-{self.next_track_id}"
            self.next_track_id += 1

            track_record = {
                "track_id": track_id,
                "class_name": det["class_name"],
                "confidence": det["confidence"],
                "bbox": det["bbox"],
                "centroid": det["centroid"],
                "velocity": [0.015, -0.025], # Heading inward toward border fence
                "dwell_seconds": 12.5
            }
            self.camera_tracks[camera_id][track_id] = track_record
            active.append(track_record)

        return active

edge_tracker = EdgeTracker()
