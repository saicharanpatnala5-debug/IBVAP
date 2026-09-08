"""
IBVAP - Multi-Camera Temporal Frame Synchronizer
Aligns frames across disparate cameras within a millisecond temporal window.
"""
import time
import collections
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple

class MultiCameraSynchronizer:
    """
    Pairs frames from multiple non-synchronized camera feeds.
    Matches frames that fall within a narrow tolerance window (e.g. 30ms).
    """

    def __init__(self, tolerance_ms: float = 35.0, history_len: int = 60):
        self.tolerance_sec = tolerance_ms / 1000.0
        self.history_len = history_len
        self._buffers: Dict[str, collections.deque] = collections.defaultdict(
            lambda: collections.deque(maxlen=history_len)
        )
        self._lock = threading.Lock()

    def add_frame(self, camera_id: str, frame: np.ndarray, timestamp: Optional[float] = None):
        """Adds a captured frame for temporal alignment."""
        ts = timestamp if timestamp is not None else time.time()
        with self._lock:
            self._buffers[camera_id].append((ts, frame))

    def get_synchronized_pair(
        self,
        camera_id_1: str,
        camera_id_2: str
    ) -> Optional[Tuple[np.ndarray, np.ndarray, float]]:
        """
        Finds the closest matching frame pair between two cameras within tolerance.
        Returns (frame_1, frame_2, temporal_difference_ms) or None.
        """
        with self._lock:
            q1 = self._buffers.get(camera_id_1)
            q2 = self._buffers.get(camera_id_2)
            if not q1 or not q2:
                return None

            best_pair = None
            min_diff = float("inf")

            for t1, f1 in reversed(q1):
                for t2, f2 in reversed(q2):
                    diff = abs(t1 - t2)
                    if diff < min_diff and diff <= self.tolerance_sec:
                        min_diff = diff
                        best_pair = (f1, f2, min_diff * 1000.0)
                    if diff > self.tolerance_sec * 2:
                        break

            return best_pair
