"""
IBVAP - Async Camera Pipeline
Per-camera processing pipeline that reads from a video source,
samples frames at a target FPS, and dispatches to the detection pipeline.
"""
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
import numpy as np

from ai.stream.video_source import VideoSource, create_source, SourceStatus
from ai.detection.real_detector import get_detector

logger = logging.getLogger("ibvap.camera_pipeline")


class CameraPipeline:
    """
    Per-camera processing pipeline:
    video_source → frame_sampler → detector → tracker → event_callback
    """

    def __init__(
        self,
        camera_id: str,
        source_uri: str,
        analytics_fps: int = 10,
        on_event: Optional[Callable] = None,
    ):
        self.camera_id = camera_id
        self.source = create_source(source_uri, source_id=camera_id)
        self.detector = get_detector()
        self.analytics_fps = analytics_fps
        self.on_event = on_event

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_count = 0
        self._detection_count = 0
        self._last_result: Optional[Dict[str, Any]] = None

    def start(self) -> bool:
        """Start the camera pipeline in a background thread."""
        if not self.source.connect():
            logger.error(f"[{self.camera_id}] Failed to connect to source")
            return False

        self._running = True
        self._thread = threading.Thread(
            target=self._processing_loop,
            name=f"cam-{self.camera_id}",
            daemon=True,
        )
        self._thread.start()
        logger.info(f"[{self.camera_id}] Pipeline started")
        return True

    def stop(self):
        """Stop the camera pipeline."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self.source.release()
        logger.info(f"[{self.camera_id}] Pipeline stopped")

    def _processing_loop(self):
        """Main processing loop — reads, samples, detects."""
        source_fps = self.source.get_fps() or 25.0
        skip_interval = max(1, int(source_fps / self.analytics_fps))
        frame_idx = 0

        while self._running:
            ret, frame = self.source.read()

            if not ret or frame is None:
                if self.source.status in (SourceStatus.OFFLINE, SourceStatus.ERROR):
                    logger.warning(f"[{self.camera_id}] Source offline, attempting reconnect")
                    if not self.source.reconnect():
                        logger.error(f"[{self.camera_id}] Reconnect failed, stopping")
                        break
                    continue
                elif self.source.status == SourceStatus.END_OF_STREAM:
                    logger.info(f"[{self.camera_id}] End of stream")
                    break
                continue

            frame_idx += 1

            # Frame sampling
            if frame_idx % skip_interval != 0:
                continue

            self._frame_count += 1

            # Run detection
            t0 = time.perf_counter()
            detections = self.detector.detect(frame)
            det_ms = (time.perf_counter() - t0) * 1000.0
            self._detection_count += len(detections)

            result = {
                "camera_id": self.camera_id,
                "frame_number": self._frame_count,
                "detections": [d.to_dict() for d in detections],
                "detection_count": len(detections),
                "detection_ms": round(det_ms, 2),
                "source_status": self.source.status.value,
            }
            self._last_result = result

            # Dispatch event
            if self.on_event and detections:
                try:
                    self.on_event(result)
                except Exception as e:
                    logger.error(f"[{self.camera_id}] Event callback error: {e}")

        self._running = False

    def get_status(self) -> Dict[str, Any]:
        """Returns pipeline status."""
        return {
            "camera_id": self.camera_id,
            "is_running": self._running,
            "frames_processed": self._frame_count,
            "total_detections": self._detection_count,
            "source_status": self.source.status.value,
            "source_stats": self.source.get_stats(),
            "detector_ready": self.detector.is_ready(),
            "last_result": self._last_result,
        }


class CameraPipelineManager:
    """Manages multiple camera pipelines."""

    def __init__(self):
        self.pipelines: Dict[str, CameraPipeline] = {}

    def add_camera(self, camera_id: str, source_uri: str, **kwargs) -> bool:
        """Add and start a camera pipeline."""
        if camera_id in self.pipelines:
            logger.warning(f"Camera {camera_id} already exists")
            return False
        pipeline = CameraPipeline(camera_id, source_uri, **kwargs)
        self.pipelines[camera_id] = pipeline
        return pipeline.start()

    def remove_camera(self, camera_id: str):
        """Stop and remove a camera pipeline."""
        if camera_id in self.pipelines:
            self.pipelines[camera_id].stop()
            del self.pipelines[camera_id]

    def get_all_status(self) -> List[Dict[str, Any]]:
        """Returns status for all camera pipelines."""
        return [p.get_status() for p in self.pipelines.values()]

    def stop_all(self):
        """Stop all camera pipelines."""
        for p in self.pipelines.values():
            p.stop()
        self.pipelines.clear()


pipeline_manager = CameraPipelineManager()
