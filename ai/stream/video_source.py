"""
IBVAP - Video Source Abstraction
Unified interface for RTSP, file, and webcam video sources.
Every source provides real frames or honest failure — never fake connectivity.
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from enum import Enum
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

logger = logging.getLogger("ibvap.video_source")


class SourceStatus(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"
    END_OF_STREAM = "END_OF_STREAM"


class VideoSource(ABC):
    """Abstract video source. All implementations must provide real frames or honest failure."""

    def __init__(self, source_id: str):
        self.source_id = source_id
        self.status = SourceStatus.DISCONNECTED
        self.frames_read = 0
        self.frames_dropped = 0
        self.last_frame_time: Optional[float] = None
        self.connect_time: Optional[float] = None
        self.reconnect_count = 0
        self._source_fps: float = 0.0

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the video source. Returns True on success."""
        pass

    @abstractmethod
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a single frame. Returns (success, frame) — never fake frames."""
        pass

    @abstractmethod
    def release(self) -> None:
        """Release the video source."""
        pass

    def reconnect(self, max_retries: int = 5, backoff_base: float = 2.0, max_backoff: float = 30.0) -> bool:
        """Reconnect with bounded exponential backoff."""
        for attempt in range(max_retries):
            backoff = min(backoff_base ** attempt, max_backoff)
            logger.info(f"[{self.source_id}] Reconnect attempt {attempt+1}/{max_retries}, backoff={backoff:.1f}s")
            time.sleep(backoff)
            self.reconnect_count += 1
            if self.connect():
                logger.info(f"[{self.source_id}] Reconnected successfully after {attempt+1} attempts")
                return True
        logger.error(f"[{self.source_id}] Failed to reconnect after {max_retries} attempts")
        self.status = SourceStatus.OFFLINE
        return False

    def get_fps(self) -> float:
        """Returns the source FPS (from metadata or measured)."""
        return self._source_fps

    def get_stats(self) -> Dict[str, Any]:
        """Returns real telemetry for this source."""
        return {
            "source_id": self.source_id,
            "status": self.status.value,
            "frames_read": self.frames_read,
            "frames_dropped": self.frames_dropped,
            "source_fps": round(self._source_fps, 1),
            "reconnect_count": self.reconnect_count,
            "last_frame_time": self.last_frame_time,
            "uptime_seconds": round(time.time() - self.connect_time, 1) if self.connect_time else 0,
        }


class FileSource(VideoSource):
    """Video source from a local file (MP4, AVI, etc.)."""

    def __init__(self, file_path: str, source_id: str = "FILE", loop: bool = True):
        super().__init__(source_id)
        self.file_path = file_path
        self.loop = loop
        self.cap: Optional[Any] = None
        self.total_frames = 0

    def connect(self) -> bool:
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available — cannot open video file")
            self.status = SourceStatus.ERROR
            return False

        import os
        if not os.path.isfile(self.file_path):
            logger.error(f"Video file not found: {self.file_path}")
            self.status = SourceStatus.ERROR
            return False

        self.cap = cv2.VideoCapture(self.file_path)
        if self.cap.isOpened():
            self._source_fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            self.status = SourceStatus.ONLINE
            self.connect_time = time.time()
            logger.info(f"[{self.source_id}] Opened video file: {self.file_path} ({self.total_frames} frames, {self._source_fps:.1f} FPS)")
            return True

        self.status = SourceStatus.ERROR
        logger.error(f"Failed to open video file: {self.file_path}")
        return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.cap is None or not self.cap.isOpened():
            self.status = SourceStatus.OFFLINE
            return False, None

        ret, frame = self.cap.read()
        if ret and frame is not None:
            self.frames_read += 1
            self.last_frame_time = time.time()
            return True, frame

        if self.loop:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.frames_read += 1
                self.last_frame_time = time.time()
                return True, frame

        self.status = SourceStatus.END_OF_STREAM
        return False, None

    def release(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = SourceStatus.DISCONNECTED


class RTSPSource(VideoSource):
    """Video source from an RTSP/RTMP stream with real connectivity tracking."""

    def __init__(self, stream_url: str, source_id: str = "RTSP"):
        super().__init__(source_id)
        self.stream_url = stream_url
        self.cap: Optional[Any] = None

    def connect(self) -> bool:
        if not CV2_AVAILABLE:
            logger.error("OpenCV not available")
            self.status = SourceStatus.ERROR
            return False

        if not self.stream_url:
            logger.error(f"[{self.source_id}] Empty stream URL")
            self.status = SourceStatus.ERROR
            return False

        self.status = SourceStatus.CONNECTING
        try:
            # Use FFMPEG backend for RTSP — more robust
            self.cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)
            if self.cap.isOpened():
                self._source_fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
                self.status = SourceStatus.ONLINE
                self.connect_time = time.time()
                logger.info(f"[{self.source_id}] Connected to RTSP: {self.stream_url}")
                return True
        except Exception as e:
            logger.error(f"[{self.source_id}] RTSP connect failed: {e}")

        self.status = SourceStatus.OFFLINE
        return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.cap is None or not self.cap.isOpened():
            self.status = SourceStatus.OFFLINE
            return False, None

        ret, frame = self.cap.read()
        if ret and frame is not None:
            self.frames_read += 1
            self.last_frame_time = time.time()
            return True, frame

        self.frames_dropped += 1
        self.status = SourceStatus.OFFLINE
        return False, None

    def release(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = SourceStatus.DISCONNECTED


class WebcamSource(VideoSource):
    """Video source from a local USB webcam."""

    def __init__(self, device_id: int = 0, source_id: str = "WEBCAM"):
        super().__init__(source_id)
        self.device_id = device_id
        self.cap: Optional[Any] = None

    def connect(self) -> bool:
        if not CV2_AVAILABLE:
            self.status = SourceStatus.ERROR
            return False

        self.cap = cv2.VideoCapture(self.device_id)
        if self.cap.isOpened():
            self._source_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
            self.status = SourceStatus.ONLINE
            self.connect_time = time.time()
            logger.info(f"[{self.source_id}] Webcam {self.device_id} opened")
            return True

        self.status = SourceStatus.ERROR
        return False

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.cap is None or not self.cap.isOpened():
            self.status = SourceStatus.OFFLINE
            return False, None

        ret, frame = self.cap.read()
        if ret and frame is not None:
            self.frames_read += 1
            self.last_frame_time = time.time()
            return True, frame

        self.frames_dropped += 1
        return False, None

    def release(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = SourceStatus.DISCONNECTED


def create_source(source_uri: str, source_id: str = "SRC") -> VideoSource:
    """Factory: creates the appropriate VideoSource from a URI string."""
    if source_uri.startswith("rtsp://") or source_uri.startswith("rtmp://"):
        return RTSPSource(stream_url=source_uri, source_id=source_id)
    elif source_uri.isdigit():
        return WebcamSource(device_id=int(source_uri), source_id=source_id)
    else:
        return FileSource(file_path=source_uri, source_id=source_id)
