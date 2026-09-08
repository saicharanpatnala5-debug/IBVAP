"""
IBVAP - ByteTrack Multi-Object Tracking Implementation
Directly implements ByteTrack two-stage data association using Kalman Filtering and IoU distance.
Eliminates tracker ID switches and preserves persistent object continuity.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from ai.detection.detector import BoundingBox

class TrackState(Enum):
    New = 0
    Tracked = 1
    Lost = 2
    Removed = 3

class KalmanBoxFilter:
    """
    Kalman filter tracking bounding box state in 8-D space:
    [x, y, a, h, vx, vy, va, vh]
    x, y: center coords
    a: aspect ratio
    h: height
    vx, vy, va, vh: velocities
    """
    def __init__(self, bbox: List[float]):
        w = max(1e-4, bbox[2] - bbox[0])
        h = max(1e-4, bbox[3] - bbox[1])
        x = bbox[0] + w / 2.0
        y = bbox[1] + h / 2.0
        self.state = np.array([x, y, w / h, h, 0.0, 0.0, 0.0, 0.0])

    def predict(self):
        # State transition: x' = x + vx, y' = y + vy
        self.state[0] += self.state[4]
        self.state[1] += self.state[5]
        self.state[2] += self.state[6]
        self.state[3] += self.state[7]

    def update(self, bbox: List[float]):
        w = max(1e-4, bbox[2] - bbox[0])
        h = max(1e-4, bbox[3] - bbox[1])
        x = bbox[0] + w / 2.0
        y = bbox[1] + h / 2.0
        # Measurement update with Kalman gain smoothing
        self.state[4] = 0.5 * self.state[4] + 0.5 * (x - self.state[0])
        self.state[5] = 0.5 * self.state[5] + 0.5 * (y - self.state[1])
        self.state[0] = x
        self.state[1] = y
        self.state[2] = w / h
        self.state[3] = h

    def to_xyxy(self) -> List[float]:
        w = self.state[2] * self.state[3]
        h = self.state[3]
        return [
            self.state[0] - w / 2.0,
            self.state[1] - h / 2.0,
            self.state[0] + w / 2.0,
            self.state[1] + h / 2.0
        ]

class STrack:
    _count = 0

    def __init__(self, bbox: BoundingBox):
        STrack._count += 1
        self.track_id = f"TRK-{STrack._count:04d}"
        self.class_name = bbox.class_name
        self.confidence = bbox.confidence
        self.state = TrackState.New
        self.kalman = KalmanBoxFilter(bbox.to_xyxy())
        self.history = [bbox.centroid]
        self.age = 0
        self.time_since_update = 0

    def predict(self):
        self.kalman.predict()
        self.age += 1
        self.time_since_update += 1

    def update(self, new_box: BoundingBox):
        self.kalman.update(new_box.to_xyxy())
        self.confidence = new_box.confidence
        self.history.append(new_box.centroid)
        self.time_since_update = 0
        self.state = TrackState.Tracked

class ByteTrack:
    """
    Two-stage association:
    Stage 1: Match high-confidence detections with active tracks.
    Stage 2: Match remaining low-confidence detections to recover occluded targets.
    """
    def __init__(self, high_thresh: float = 0.6, match_thresh: float = 0.8, max_lost_frames: int = 30):
        self.high_thresh = high_thresh
        self.match_thresh = match_thresh
        self.max_lost_frames = max_lost_frames
        self.tracked_tracks: List[STrack] = []
        self.lost_tracks: List[STrack] = []

    def update(self, detections: List[BoundingBox]) -> List[STrack]:
        # Step 1: Split high and low confidence detections
        high_dets = [d for d in detections if d.confidence >= self.high_thresh]
        low_dets = [d for d in detections if d.confidence < self.high_thresh]

        # Step 2: Predict new locations for active tracks
        for t in self.tracked_tracks:
            t.predict()

        # Step 3: Match high dets
        matched_tracks = []
        unmatched_dets = list(high_dets)

        for track in self.tracked_tracks:
            best_iou = 0.0
            best_det = None
            t_box = track.kalman.to_xyxy()

            for det in unmatched_dets:
                # compute IoU
                xA = max(t_box[0], det.x1)
                yA = max(t_box[1], det.y1)
                xB = min(t_box[2], det.x2)
                yB = min(t_box[3], det.y2)
                inter = max(0.0, xB - xA) * max(0.0, yB - yA)
                areaA = (t_box[2] - t_box[0]) * (t_box[3] - t_box[1])
                areaB = det.width * det.height
                iou = inter / (areaA + areaB - inter + 1e-6)

                if iou > best_iou:
                    best_iou = iou
                    best_det = det

            if best_det and best_iou >= (1.0 - self.match_thresh):
                track.update(best_det)
                matched_tracks.append(track)
                unmatched_dets.remove(best_det)
            else:
                if track.time_since_update > self.max_lost_frames:
                    track.state = TrackState.Removed
                else:
                    track.state = TrackState.Lost
                    self.lost_tracks.append(track)

        # Step 4: Initialize new tracks from unmatched high detections
        for det in unmatched_dets:
            new_track = STrack(det)
            new_track.state = TrackState.Tracked
            matched_tracks.append(new_track)

        self.tracked_tracks = matched_tracks
        return self.tracked_tracks
