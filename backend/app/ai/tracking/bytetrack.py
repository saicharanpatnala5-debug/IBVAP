"""
IBVAP - ByteTrack Multi-Object Tracking Implementation
Directly implements ByteTrack two-stage data association using Kalman Filtering and IoU distance.
Eliminates tracker ID switches and preserves persistent object continuity.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
try:
    from ai.detection.detector import BoundingBox
except ImportError:
    from app.ai.detection.detector import BoundingBox

class TrackState(Enum):
    New = 0
    Tracked = 1
    Lost = 2
    Removed = 3

class KalmanBoxFilter:
    """
    Standard 8-D Linear Kalman Filter for multi-object tracking:
    State space: [x_c, y_c, a, h, vx, vy, va, vh]
    x_c, y_c: Bounding box center coordinates
    a: Aspect ratio (width / height)
    h: Height
    vx, vy, va, vh: Respective velocity components
    """
    _motion_mat = np.eye(8, 8, dtype=np.float32)
    for i in range(4):
        _motion_mat[i, i + 4] = 1.0

    _update_mat = np.eye(4, 8, dtype=np.float32)

    _std_weight_position = 1.0 / 20.0
    _std_weight_velocity = 1.0 / 160.0

    def __init__(self, bbox: List[float]):
        w = max(1e-4, bbox[2] - bbox[0])
        h = max(1e-4, bbox[3] - bbox[1])
        x = bbox[0] + w / 2.0
        y = bbox[1] + h / 2.0
        self.mean = np.array([x, y, w / h, h, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        pos_var = max(4.0, (0.05 * h) ** 2)
        vel_var = max(25.0, (0.25 * h) ** 2)
        std = [pos_var, pos_var, 0.01, pos_var, vel_var, vel_var, 0.01, vel_var]
        self.covariance = np.diag(std).astype(np.float32)

    @property
    def state(self) -> np.ndarray:
        return self.mean

    @state.setter
    def state(self, val: Any):
        self.mean = np.asarray(val, dtype=np.float32)

    def predict(self):
        h = max(1.0, float(self.mean[3]))
        q_pos = max(1.0, (0.02 * h) ** 2)
        q_vel = max(2.0, (0.05 * h) ** 2)
        Q = np.diag([q_pos, q_pos, 0.001, q_pos, q_vel, q_vel, 0.001, q_vel]).astype(np.float32)

        self.mean = np.dot(self._motion_mat, self.mean)
        self.covariance = np.linalg.multi_dot((self._motion_mat, self.covariance, self._motion_mat.T)) + Q

    def update(self, bbox: List[float]):
        w = max(1e-4, bbox[2] - bbox[0])
        h = max(1e-4, bbox[3] - bbox[1])
        x = bbox[0] + w / 2.0
        y = bbox[1] + h / 2.0
        z = np.array([x, y, w / h, h], dtype=np.float32)

        r_pos = max(2.0, (0.03 * h) ** 2)
        R = np.diag([r_pos, r_pos, 0.05, r_pos]).astype(np.float32)

        # Innovation and Kalman Gain
        innovation = z - np.dot(self._update_mat, self.mean)
        S = np.linalg.multi_dot((self._update_mat, self.covariance, self._update_mat.T)) + R
        K = np.linalg.multi_dot((self.covariance, self._update_mat.T, np.linalg.inv(S)))

        self.mean = self.mean + np.dot(K, innovation)
        I = np.eye(8, dtype=np.float32)
        self.covariance = np.dot(I - np.dot(K, self._update_mat), self.covariance)

    def to_xyxy(self) -> List[float]:
        w = max(1.0, float(self.mean[2] * self.mean[3]))
        h = max(1.0, float(self.mean[3]))
        x1 = float(self.mean[0] - w / 2.0)
        y1 = float(self.mean[1] - h / 2.0)
        x2 = float(self.mean[0] + w / 2.0)
        y2 = float(self.mean[1] + h / 2.0)
        return [x1, y1, x2, y2]

class STrack:
    _counts: Dict[str, int] = {}

    @classmethod
    def reset_counts(cls):
        cls._counts.clear()

    def __init__(self, bbox: BoundingBox):
        cname = bbox.class_name.lower()
        if cname == "person":
            cls_key = "P"
        elif cname in ("vehicle", "car", "truck", "bus", "motorcycle", "heavy_vehicle", "train"):
            cls_key = "HV" if cname in ("truck", "bus", "train", "heavy_vehicle") else "V"
        elif cname in ("animal", "dog", "cat", "bird", "horse", "cow"):
            cls_key = "A"
        else:
            cls_key = "OBJ"

        current_val = STrack._counts.get(cls_key, 100) + 1
        STrack._counts[cls_key] = current_val
        self.track_id = f"TRK-{cls_key}{current_val}"
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


def _is_compatible_class(c1: str, c2: str) -> bool:
    c1, c2 = c1.lower(), c2.lower()
    if c1 == c2:
        return True
    vehicles = {"vehicle", "car", "truck", "bus", "motorcycle", "heavy_vehicle", "train"}
    if c1 in vehicles and c2 in vehicles:
        return True
    animals = {"animal", "dog", "cat", "bird", "horse", "cow"}
    if c1 in animals and c2 in animals:
        return True
    return False


def _match_tracks_to_detections(
    tracks: List[STrack],
    detections: List[BoundingBox],
    min_iou: float
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    Priority cost-matrix IoU + distance matching between tracks and detections.
    Sorts all candidate pairs by descending similarity score and greedily pairs the
    highest-overlap matches first. Eliminates track hijacking and ID switches in dense clusters.
    """
    if len(tracks) == 0 or len(detections) == 0:
        return [], list(range(len(tracks))), list(range(len(detections)))

    iou_mat = np.zeros((len(tracks), len(detections)), dtype=np.float32)
    for t_idx, trk in enumerate(tracks):
        t_box = trk.kalman.to_xyxy()
        t_cx = (t_box[0] + t_box[2]) / 2.0
        t_cy = (t_box[1] + t_box[3]) / 2.0
        t_scale = max(1.0, (t_box[2] - t_box[0] + t_box[3] - t_box[1]) / 2.0)

        for d_idx, det in enumerate(detections):
            if not _is_compatible_class(det.class_name, trk.class_name):
                continue
            xA = max(t_box[0], det.x1)
            yA = max(t_box[1], det.y1)
            xB = min(t_box[2], det.x2)
            yB = min(t_box[3], det.y2)
            inter = max(0.0, xB - xA) * max(0.0, yB - yA)
            areaA = max(1e-4, (t_box[2] - t_box[0]) * (t_box[3] - t_box[1]))
            areaB = max(1e-4, det.width * det.height)
            iou = inter / (areaA + areaB - inter + 1e-6)

            # Proximity fallback when targets move fast or during temporary occlusion
            d_cx = (det.x1 + det.x2) / 2.0
            d_cy = (det.y1 + det.y2) / 2.0
            dist = np.hypot(t_cx - d_cx, t_cy - d_cy)
            proximity = max(0.0, 1.0 - (dist / (3.0 * t_scale)))

            combined_score = max(iou, 0.40 * proximity) if iou > 0 or proximity > 0.5 else 0.0
            iou_mat[t_idx, d_idx] = combined_score

    matched_tracks = set()
    matched_dets = set()
    matches = []

    # Sort pairs by descending similarity score
    sorted_flat_indices = np.argsort(-iou_mat, axis=None)
    for idx in sorted_flat_indices:
        t_idx, d_idx = np.unravel_index(idx, iou_mat.shape)
        if iou_mat[t_idx, d_idx] < min_iou:
            break
        if t_idx in matched_tracks or d_idx in matched_dets:
            continue
        matched_tracks.add(t_idx)
        matched_dets.add(d_idx)
        matches.append((t_idx, d_idx))

    unmatched_tracks = [i for i in range(len(tracks)) if i not in matched_tracks]
    unmatched_dets = [i for i in range(len(detections)) if i not in matched_dets]
    return matches, unmatched_tracks, unmatched_dets


class ByteTrack:
    """
    ByteTrack two-stage data association:
    Stage 1: Match high-confidence detections with active tracks using priority IoU assignment.
    Stage 2: Match remaining low-confidence detections to recover occluded targets.
    Maintains persistent IDs across occlusions and eliminates ID switches.
    """
    def __init__(self, high_thresh: float = 0.45, match_thresh: float = 0.70, max_lost_frames: int = 25):
        self.high_thresh = high_thresh
        self.match_thresh = match_thresh
        self.max_lost_frames = max_lost_frames
        self.tracked_tracks: List[STrack] = []

    def reset(self):
        self.tracked_tracks.clear()
        STrack.reset_counts()

    def update(self, detections: List[BoundingBox]) -> List[STrack]:
        # Step 1: Predict Kalman state for all existing tracks
        for t in self.tracked_tracks:
            t.predict()

        high_dets = [d for d in detections if d.confidence >= self.high_thresh]
        low_dets = [d for d in detections if d.confidence < self.high_thresh]

        # Stage 1: Priority IoU match high-confidence detections with active tracks
        min_iou_stage1 = 1.0 - self.match_thresh
        matches1, u_tracks1, u_dets1 = _match_tracks_to_detections(self.tracked_tracks, high_dets, min_iou_stage1)

        for t_idx, d_idx in matches1:
            self.tracked_tracks[t_idx].update(high_dets[d_idx])

        # Stage 2: Match remaining tracks with low-confidence detections (recovering occluded targets)
        remaining_tracks = [self.tracked_tracks[i] for i in u_tracks1]
        matches2, u_tracks2, u_dets2 = _match_tracks_to_detections(remaining_tracks, low_dets, 0.40)

        for t_idx, d_idx in matches2:
            remaining_tracks[t_idx].update(low_dets[d_idx])

        # Step 3: Retain valid tracks in tracking pool, retire lost tracks
        active_tracks = []
        for t in self.tracked_tracks:
            if t.time_since_update <= self.max_lost_frames:
                active_tracks.append(t)
            else:
                t.state = TrackState.Removed

        # Step 4: Initialize new tracks from unmatched high-confidence detections
        for d_idx in u_dets1:
            new_track = STrack(high_dets[d_idx])
            new_track.state = TrackState.Tracked
            active_tracks.append(new_track)

        self.tracked_tracks = active_tracks
        # Return currently active tracks that were matched or newly created in this frame
        return [t for t in self.tracked_tracks if t.time_since_update == 0]

