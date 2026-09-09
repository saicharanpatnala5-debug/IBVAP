"""
IBVAP - High-Level Multi-Object Tracker
Provides per-camera multi-object tracking using ByteTrack 2-stage association and Kalman filtering.
Computes real trajectory metrics: speed, velocity vectors, heading degrees, and dwell times.
"""
from typing import List, Dict, Any, Optional
import numpy as np
import time

try:
    from ai.detection.detector import BoundingBox
    from ai.tracking.bytetrack import ByteTrack, STrack
    from ai.tracking.trajectory import trajectory_engine
except ImportError:
    from app.ai.detection.detector import BoundingBox
    from app.ai.tracking.bytetrack import ByteTrack, STrack
    from app.ai.tracking.trajectory import trajectory_engine

class MultiObjectTracker:
    def __init__(self, max_history: int = 100, max_idle_seconds: float = 60.0):
        self.bytetrack = ByteTrack()
        self.trajectory_history: Dict[str, Dict[str, Any]] = {}
        self.max_history = max_history
        self.max_idle_seconds = max_idle_seconds

    def reset(self):
        if hasattr(self.bytetrack, 'reset'):
            self.bytetrack.reset()
        else:
            self.bytetrack = ByteTrack()
        self.trajectory_history.clear()

    def track_frame(self, detections: List[BoundingBox]) -> List[BoundingBox]:
        active_stracks = self.bytetrack.update(detections)
        tracked_boxes = []

        now = time.time()
        active_ids = set()

        for t in active_stracks:
            box_coords = t.kalman.to_xyxy()
            bbox = BoundingBox(
                x1=box_coords[0],
                y1=box_coords[1],
                x2=box_coords[2],
                y2=box_coords[3],
                confidence=t.confidence,
                class_id=0,
                class_name=t.class_name,
                track_id=t.track_id
            )
            active_ids.add(t.track_id)

            # Update trajectory history
            if t.track_id not in self.trajectory_history:
                self.trajectory_history[t.track_id] = {"points": [], "timestamps": []}

            hist = self.trajectory_history[t.track_id]
            hist["points"].append(bbox.centroid)
            hist["timestamps"].append(now)

            # Cap history size
            if len(hist["points"]) > self.max_history:
                hist["points"].pop(0)
                hist["timestamps"].pop(0)

            # Compute kinematic & behavioral metrics
            metrics = trajectory_engine.analyze(hist["points"], hist["timestamps"])
            bbox.attributes.update(metrics)
            tracked_boxes.append(bbox)

        # Cleanup stale tracks no longer observed
        stale_ids = [
            tid for tid, h in self.trajectory_history.items()
            if tid not in active_ids and h["timestamps"] and (now - h["timestamps"][-1] > self.max_idle_seconds)
        ]
        for tid in stale_ids:
            del self.trajectory_history[tid]

        return tracked_boxes

    def get_track_history(self, track_id: str) -> Optional[Dict[str, Any]]:
        return self.trajectory_history.get(track_id)


_camera_trackers: Dict[str, MultiObjectTracker] = {}

def get_tracker(camera_id: str = "CAM-01") -> MultiObjectTracker:
    if camera_id not in _camera_trackers:
        _camera_trackers[camera_id] = MultiObjectTracker()
    return _camera_trackers[camera_id]

def reset_tracker(camera_id: Optional[str] = None):
    if camera_id:
        if camera_id in _camera_trackers:
            _camera_trackers[camera_id].reset()
    else:
        for t in _camera_trackers.values():
            t.reset()

tracker = get_tracker("default")
