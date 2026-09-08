"""
IBVAP - Central Multi-Camera Stream Supervisor
"""
import threading
from typing import Dict, List, Optional, Any
from video.rtsp.rtsp_client import RTSPClient

class StreamManager:
    """Orchestrates multiple camera streams across border vantage points."""

    def __init__(self):
        self._lock = threading.Lock()
        self.clients: Dict[str, RTSPClient] = {}

    def register_stream(
        self,
        camera_id: str,
        stream_url: str,
        use_synthetic_fallback: bool = True,
        target_fps: float = 25.0
    ) -> RTSPClient:
        """Registers and initializes a camera stream."""
        with self._lock:
            if camera_id in self.clients:
                self.clients[camera_id].close()
            client = RTSPClient(camera_id, stream_url, use_synthetic_fallback, target_fps)
            client.open()
            self.clients[camera_id] = client
            return client

    def get_stream(self, camera_id: str) -> Optional[RTSPClient]:
        """Retrieves active stream client by camera ID."""
        with self._lock:
            return self.clients.get(camera_id)

    def stop_stream(self, camera_id: str):
        """Stops and removes stream client."""
        with self._lock:
            if camera_id in self.clients:
                self.clients[camera_id].close()
                del self.clients[camera_id]

    def stop_all(self):
        """Stops all active camera streams."""
        with self._lock:
            for client in self.clients.values():
                client.close()
            self.clients.clear()

    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Returns telemetry for all registered streams."""
        with self._lock:
            return [client.get_telemetry() for client in self.clients.values()]

stream_manager = StreamManager()
