"""
IBVAP - High-Level Multi-Object Tracker
"""
from typing import List, Dict, Any
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
    def __init__(self):
        self.bytetrack = ByteTrack()
        self.trajectory_history: Dict[str, Dict[str, Any]] = {}

    def track_frame(self, detections: List[BoundingBox]) -> List[BoundingBox]:
        active_stracks = self.bytetrack.update(detections)
        tracked_boxes = []

        now = time.time()
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

            # Update trajectory history
            if t.track_id not in self.trajectory_history:
                self.trajectory_history[t.track_id] = {"points": [], "timestamps": []}

            hist = self.trajectory_history[t.track_id]
            hist["points"].append(bbox.centroid)
            hist["timestamps"].append(now)

            metrics = trajectory_engine.analyze(hist["points"], hist["timestamps"])
            bbox.attributes.update(metrics)
            tracked_boxes.append(bbox)

        return tracked_boxes

tracker = MultiObjectTracker()
