"""
IBVAP - Circular Zero-Copy Rolling Frame Buffer
Maintains pre-event video context (last N seconds) for forensic evidence extraction.
"""
import collections
import threading
import time
import numpy as np
from typing import List, Tuple, Optional, Any

class CircularFrameBuffer:
    """
    Thread-safe circular ring buffer.
    Stores rolling window of frames to capture pre-event footage (e.g. 10 seconds before breach).
    """

    def __init__(self, max_frames: int = 250):
        self.max_frames = max_frames
        self._buffer = collections.deque(maxlen=max_frames)
        self._lock = threading.Lock()

    def append(self, frame: np.ndarray, timestamp: Optional[float] = None, metadata: Optional[Any] = None):
        """Appends frame and metadata to circular buffer."""
        ts = timestamp if timestamp is not None else time.time()
        with self._lock:
            self._buffer.append((ts, frame, metadata))

    def get_recent_frames(self, seconds: float = 10.0) -> List[Tuple[float, np.ndarray, Any]]:
        """
        Retrieves all frames recorded within the last `seconds` duration.
        """
        cutoff = time.time() - seconds
        with self._lock:
            return [(ts, f, m) for ts, f, m in self._buffer if ts >= cutoff]

    def get_all(self) -> List[Tuple[float, np.ndarray, Any]]:
        """Returns snapshot copy of all frames in buffer."""
        with self._lock:
            return list(self._buffer)

    def clear(self):
        """Clears all frames from buffer."""
        with self._lock:
            self._buffer.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)
