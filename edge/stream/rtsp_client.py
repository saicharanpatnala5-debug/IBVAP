"""
IBVAP - Rugged Forward Edge RTSP Ingestion Client
Implements automatic reconnect with exponential backoff.
Never reports ONLINE without actual frame delivery.
"""

import time
import logging
from typing import Optional, Tuple
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger("ibvap.edge.rtsp")


class EdgeRTSPClient:
    def __init__(self, camera_id: str, stream_url: str):
        self.camera_id = camera_id
        self.stream_url = stream_url
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_backoff_sec = 30.0
        self.cap = None
        self.frames_read = 0
        self.frames_dropped = 0
        self.last_frame_time: Optional[float] = None

    def connect(self) -> bool:
        """
        Establishes stream connection.
        Returns False (not True) when no valid stream URL is provided.
        """
        if not CV2_AVAILABLE:
            logger.error(f"[{self.camera_id}] OpenCV not available")
            self.is_connected = False
            return False

        if not self.stream_url:
            logger.warning(f"[{self.camera_id}] No stream URL configured")
            self.is_connected = False
            return False

        try:
            self.cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)
            if self.cap.isOpened():
                # Verify we can actually read a frame
                ret, test_frame = self.cap.read()
                if ret and test_frame is not None:
                    self.is_connected = True
                    self.reconnect_attempts = 0
                    self.frames_read += 1
                    self.last_frame_time = time.time()
                    logger.info(f"[{self.camera_id}] Connected to: {self.stream_url}")
                    return True
                else:
                    self.cap.release()
                    self.cap = None
        except Exception as e:
            logger.error(f"[{self.camera_id}] Connection failed: {e}")

        self.is_connected = False
        return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Reads a single video frame with automatic reconnect.
        Returns (False, None) when no real frame is available — never fakes a frame.
        """
        if not self.is_connected:
            backoff = min(2.0 ** self.reconnect_attempts, self.max_backoff_sec)
            time.sleep(backoff)
            self.reconnect_attempts += 1
            if not self.connect():
                return False, None

        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.frames_read += 1
                self.last_frame_time = time.time()
                return True, frame
            else:
                self.frames_dropped += 1
                self.is_connected = False
                return False, None

        # No valid capture — never return (True, None) which fakes connectivity
        self.is_connected = False
        return False, None

    def get_stats(self) -> dict:
        """Returns real connection statistics."""
        return {
            "camera_id": self.camera_id,
            "is_connected": self.is_connected,
            "frames_read": self.frames_read,
            "frames_dropped": self.frames_dropped,
            "reconnect_attempts": self.reconnect_attempts,
            "last_frame_time": self.last_frame_time,
        }

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_connected = False
