"""
IBVAP - Edge Video Stream Telemetry & Health Validator
Monitors FPS, jitter, latency, and packet loss estimation.
"""

import time
from typing import Dict, Any

class StreamValidator:
    def __init__(self, target_fps: float = 25.0):
        self.target_fps = target_fps
        self.last_frame_time = time.time()
        self.frame_intervals = []
        self.total_frames = 0
        self.dropped_frames = 0

    def record_frame(self) -> Dict[str, Any]:
        now = time.time()
        interval = now - self.last_frame_time
        self.last_frame_time = now
        self.total_frames += 1

        self.frame_intervals.append(interval)
        if len(self.frame_intervals) > 50:
            self.frame_intervals.pop(0)

        expected_interval = 1.0 / self.target_fps
        if interval > expected_interval * 1.5:
            self.dropped_frames += 1

        avg_interval = sum(self.frame_intervals) / len(self.frame_intervals) if self.frame_intervals else expected_interval
        current_fps = 1.0 / avg_interval if avg_interval > 0 else 0.0

        return {
            "current_fps": round(current_fps, 2),
            "target_fps": self.target_fps,
            "packet_loss_est_pct": round((self.dropped_frames / max(self.total_frames, 1)) * 100.0, 2),
            "health": "OPTIMAL" if current_fps >= self.target_fps * 0.8 else "DEGRADED"
        }
