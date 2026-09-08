"""
IBVAP - High-Performance Circular Ring Buffer
Maintains sliding temporal pre-event and post-event video frames in edge RAM.
"""

from collections import deque
from typing import List, Optional, Any
import numpy as np

class CircularFrameBuffer:
    def __init__(self, capacity: int = 150): # 150 frames = 6 seconds at 25 FPS
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def append_frame(self, frame: Optional[np.ndarray], metadata: Optional[dict] = None):
        """Appends frame and metadata to the circular buffer."""
        self.buffer.append({
            "frame": frame,
            "metadata": metadata or {}
        })

    def get_buffered_sequence(self) -> List[dict]:
        """Returns snapshot of current buffer sequence for event clip synthesis."""
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()

    @property
    def current_size(self) -> int:
        return len(self.buffer)
