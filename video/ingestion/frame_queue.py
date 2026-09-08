"""
IBVAP - Lossy/Lossless Real-Time Ingestion Queue with Drop-Oldest Strategy
"""
import queue
import threading
from typing import Optional, Any

class OverflowPolicy:
    DROP_OLDEST = "DROP_OLDEST"
    DROP_NEWEST = "DROP_NEWEST"
    BLOCK = "BLOCK"

class FrameQueue:
    """
    High-speed thread-safe frame queue.
    Under high CPU load, DROP_OLDEST ensures inference never works on stale frames.
    """

    def __init__(self, maxsize: int = 30, policy: str = OverflowPolicy.DROP_OLDEST):
        self.maxsize = maxsize
        self.policy = policy
        self._queue = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()
        self.dropped_count = 0

    def put(self, item: Any, block: bool = False, timeout: Optional[float] = None) -> bool:
        """Puts frame into queue according to overflow policy."""
        with self._lock:
            if self._queue.full():
                if self.policy == OverflowPolicy.DROP_OLDEST:
                    try:
                        self._queue.get_nowait()
                        self.dropped_count += 1
                    except queue.Empty:
                        pass
                elif self.policy == OverflowPolicy.DROP_NEWEST:
                    self.dropped_count += 1
                    return False

            try:
                self._queue.put(item, block=block, timeout=timeout)
                return True
            except queue.Full:
                self.dropped_count += 1
                return False

    def get(self, block: bool = True, timeout: Optional[float] = 0.1) -> Any:
        """Pulls next frame from queue."""
        return self._queue.get(block=block, timeout=timeout)

    def qsize(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()
