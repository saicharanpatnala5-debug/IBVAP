"""
IBVAP - ByteTrack-class Trajectory Tracker
Maintains persistent IDs, bounding box trajectories, velocity and dwell times.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from app.ai.geometry import calculate_velocity_and_direction

class TrajectoryTracker:
    """
    In-memory tracker managing active tracks per camera.
    """

    def __init__(self):
        self.active_tracks: Dict[str, Dict[str, Any]] = {}

    def update_track(
        self,
        camera_id: str,
        track_id: str,
        bbox: List[float],
        class_name: str = "person",
        confidence: float = 0.90
    ) -> Dict[str, Any]:
        """
        Updates trajectory with new bounding box [x1, y1, x2, y2].
        Calculates centroid, velocity vector, dwell time, and direction.
        """
        now = datetime.now(timezone.utc)
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0

        track_key = f"{camera_id}_{track_id}"
        if track_key not in self.active_tracks:
            self.active_tracks[track_key] = {
                "track_id": track_id,
                "camera_id": camera_id,
                "class_name": class_name,
                "start_time": now,
                "last_seen": now,
                "trajectory": [],
                "dwell_seconds": 0.0,
                "status": "ACTIVE"
            }

        track = self.active_tracks[track_key]
        track["last_seen"] = now
        track["dwell_seconds"] = (now - track["start_time"]).total_seconds()
        track["trajectory"].append({
            "x": round(cx, 4),
            "y": round(cy, 4),
            "t": now.timestamp()
        })

        # Keep trajectory history bounded (last 50 positions)
        if len(track["trajectory"]) > 50:
            track["trajectory"] = track["trajectory"][-50:]

        vel_info = calculate_velocity_and_direction(track["trajectory"])
        track["velocity"] = vel_info

        return track

    def get_track(self, camera_id: str, track_id: str) -> Optional[Dict[str, Any]]:
        return self.active_tracks.get(f"{camera_id}_{track_id}")

tracker_engine = TrajectoryTracker()
