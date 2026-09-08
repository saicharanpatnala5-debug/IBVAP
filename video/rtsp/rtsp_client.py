"""
IBVAP - RTSP Client with Latency-Optimized Buffering & Synthetic Fallback
"""
import time
import cv2
import numpy as np
from typing import Optional, Tuple, Dict, Any

class RTSPClient:
    """
    High-throughput, low-latency RTSP streaming client.
    Supports real IP camera streams with zero-latency buffer flushing and
    graceful synthetic tactical frame generation for offline demo/testing.
    """

    def __init__(
        self,
        camera_id: str,
        stream_url: str,
        use_synthetic_fallback: bool = True,
        target_fps: float = 25.0
    ):
        self.camera_id = camera_id
        self.stream_url = stream_url
        self.use_synthetic_fallback = use_synthetic_fallback
        self.target_fps = target_fps
        self.frame_interval = 1.0 / max(target_fps, 1.0)
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_synthetic = False
        self.is_connected = False
        self.frame_count = 0
        self.last_frame_time = 0.0
        self.start_time = 0.0
        self.fps_smoothed = target_fps

    def open(self) -> bool:
        """Opens connection to RTSP stream or activates synthetic mode."""
        self.start_time = time.time()
        self.last_frame_time = time.time()
        
        # Check if URL is synthetic or empty
        if not self.stream_url or self.stream_url.lower() in ("synthetic", "none", "demo"):
            self.is_synthetic = True
            self.is_connected = True
            return True

        try:
            # Low-latency OpenCV VideoCapture flags
            self.cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)
            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.is_connected = True
                self.is_synthetic = False
                return True
        except Exception:
            pass

        if self.use_synthetic_fallback:
            self.is_synthetic = True
            self.is_connected = True
            return True

        self.is_connected = False
        return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Reads next frame from stream.
        Returns (success: bool, frame: np.ndarray or None).
        """
        if not self.is_connected:
            return False, None

        if self.is_synthetic:
            return self._generate_synthetic_frame()

        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self._update_telemetry()
                return True, frame
            # If real capture dropped, fallback if permitted
            if self.use_synthetic_fallback:
                self.is_synthetic = True
                return self._generate_synthetic_frame()

        return False, None

    def _generate_synthetic_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Generates realistic tactical border surveillance test footage."""
        now = time.time()
        elapsed = now - self.last_frame_time
        if elapsed < self.frame_interval:
            time.sleep(max(0.0, self.frame_interval - elapsed))

        self.frame_count += 1
        self.last_frame_time = time.time()
        
        # 640x360 tactical frame
        h, w = 360, 640
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = (15, 22, 18) # Dark tactical night-vision slate
        
        # Subtle horizontal scanlines
        frame[::4, :] = (20, 28, 22)
        
        # Reticle & perimeter fence guide
        cv2.rectangle(frame, (20, 20), (w - 20, h - 20), (35, 120, 70), 1)
        cv2.line(frame, (w // 2, 25), (w // 2, 45), (35, 120, 70), 1)
        cv2.line(frame, (w // 2, h - 45), (w // 2, h - 25), (35, 120, 70), 1)
        
        # Synthetic moving target (simulating approaching vehicle or pedestrian)
        step = (self.frame_count * 3) % (w - 120)
        target_x = 50 + step
        target_y = 140 + int(20 * np.sin(self.frame_count * 0.1))
        cv2.rectangle(frame, (target_x, target_y), (target_x + 50, target_y + 70), (40, 180, 220), 2)
        cv2.putText(frame, "TARGET #104 [VEL: 2.1 m/s]", (target_x - 10, target_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (40, 180, 220), 1)

        # HUD Watermark
        cv2.putText(frame, f"IBVAP TACTICAL SENSOR // {self.camera_id}", (30, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (60, 220, 120), 1)
        cv2.putText(frame, f"FPS: {self.fps_smoothed:.1f} | FRAME: {self.frame_count:06d}", (30, 62),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (160, 180, 170), 1)
        
        self._update_telemetry()
        return True, frame

    def _update_telemetry(self):
        now = time.time()
        delta = now - self.last_frame_time if self.last_frame_time > 0 else 0.04
        if delta > 0:
            instant_fps = 1.0 / delta
            self.fps_smoothed = 0.9 * self.fps_smoothed + 0.1 * instant_fps

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns live stream telemetry metrics."""
        return {
            "camera_id": self.camera_id,
            "is_connected": self.is_connected,
            "is_synthetic": self.is_synthetic,
            "fps": round(self.fps_smoothed, 2),
            "total_frames": self.frame_count,
            "uptime_seconds": round(time.time() - self.start_time, 1) if self.start_time > 0 else 0.0
        }

    def close(self):
        """Releases all stream handles."""
        self.is_connected = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
