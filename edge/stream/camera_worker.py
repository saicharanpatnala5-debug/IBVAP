"""
IBVAP - Per-Camera Ingestion & Inference Dispatch Worker
Connects stream ingestion to edge inference and offline buffer storage.
"""

from typing import Dict, List, Optional, Any
from edge.stream.rtsp_client import EdgeRTSPClient
from edge.stream.frame_buffer import CircularFrameBuffer
from edge.stream.stream_validator import StreamValidator
from edge.inference.edge_engine import edge_engine
from edge.local_storage.sqlite_queue import edge_queue

class CameraWorker:
    def __init__(self, camera_id: str, stream_url: str = ""):
        self.camera_id = camera_id
        self.client = EdgeRTSPClient(camera_id, stream_url)
        self.buffer = CircularFrameBuffer(capacity=125)
        self.validator = StreamValidator(target_fps=25.0)
        self.is_running = False

    def step(self, zone_polygon: Optional[List[List[float]]] = None) -> Dict[str, Any]:
        """Executes a single processing cycle."""
        ret, frame = self.client.read_frame()
        health = self.validator.record_frame()
        self.buffer.append_frame(frame, health)

        # Skip inference if no real frame was received
        if not ret or frame is None:
            return {
                "camera_id": self.camera_id,
                "status": "NO_FRAME",
                "fps": 0.0,
                "risk_score": 0,
                "severity": "NORMAL",
                "breaches": [],
            }

        # Run Edge Inference
        result = edge_engine.process_edge_frame(
            camera_id=self.camera_id,
            frame=frame,
            zone_polygon=zone_polygon,
            is_night=True
        )

        # If a breach or high risk event occurred, enqueue locally
        if result["risk_score"] >= 50 or result["breaches"]:
            edge_queue.enqueue_event(
                event_type="EDGE_PERIMETER_BREACH",
                camera_id=self.camera_id,
                severity=result["severity"],
                risk_score=result["risk_score"],
                priority=1 if result["severity"] == "CRITICAL" else 2,
                payload=result
            )

        return result

class CameraWorkerPool:
    def __init__(self):
        self.workers: Dict[str, CameraWorker] = {}

    def get_or_create_worker(self, camera_id: str, stream_url: str = "") -> CameraWorker:
        if camera_id not in self.workers:
            self.workers[camera_id] = CameraWorker(camera_id, stream_url)
        return self.workers[camera_id]

camera_worker_pool = CameraWorkerPool()
