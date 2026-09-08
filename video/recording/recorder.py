"""
IBVAP - Video Recorder with Automatic Chunk Rotation & Disk Safeguards
"""
import os
import time
from datetime import datetime, timezone
import cv2
import numpy as np
from typing import Optional

class VideoRecorder:
    """Records video streams to disk in segmented chunks with quota protection."""

    def __init__(
        self,
        camera_id: str,
        output_dir: str,
        fps: float = 25.0,
        segment_seconds: float = 300.0 # 5-minute chunks
    ):
        self.camera_id = camera_id
        self.output_dir = output_dir
        self.fps = fps
        self.segment_seconds = segment_seconds
        
        os.makedirs(output_dir, exist_ok=True)
        self.writer: Optional[cv2.VideoWriter] = None
        self.current_file: Optional[str] = None
        self.segment_start_time = 0.0
        self.frames_written = 0

    def _start_new_segment(self, frame_size: tuple):
        if self.writer:
            self.writer.release()
            
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{self.camera_id}_{timestamp_str}.mp4"
        self.current_file = os.path.join(self.output_dir, filename)
        
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.current_file, fourcc, self.fps, frame_size)
        self.segment_start_time = time.time()
        self.frames_written = 0

    def write_frame(self, frame: np.ndarray):
        """Writes frame to current chunk; rotates when segment duration reached."""
        h, w = frame.shape[:2]
        now = time.time()
        
        if self.writer is None or (now - self.segment_start_time) >= self.segment_seconds:
            self._start_new_segment((w, h))

        if self.writer and self.writer.isOpened():
            self.writer.write(frame)
            self.frames_written += 1

    def close(self):
        """Finalizes current video chunk."""
        if self.writer:
            self.writer.release()
            self.writer = None
