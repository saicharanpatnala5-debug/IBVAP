"""
IBVAP - Forward Edge Node Configuration Subsystem
Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
Deployment Site: Border Out Post (BOP) Alpha - Sector B Strategic Sector
"""

import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class EdgeConfig:
    edge_node_id: str = os.getenv("EDGE_NODE_ID", "EDGE-NODE-ALPHA-01")
    bop_id: str = os.getenv("BOP_ID", "BOP-ALPHA")
    sector: str = os.getenv("SECTOR", "Sector-B")
    
    # Upstream Backhaul Server
    central_server_url: str = os.getenv("CENTRAL_SERVER_URL", "http://127.0.0.1:8000")
    api_key: str = os.getenv("EDGE_API_KEY", "IBVAP_EDGE_TACTICAL_TOKEN_ALPHA_01")
    
    # Storage & Buffering
    storage_root: str = os.getenv("EDGE_STORAGE_ROOT", os.path.join(os.path.dirname(__file__), "..", "storage"))
    buffer_dir: str = os.path.join(storage_root, "edge_buffer")
    evidence_dir: str = os.path.join(storage_root, "edge_evidence")
    sqlite_db_path: str = os.path.join(buffer_dir, "edge_events.db")
    max_buffered_events: int = int(os.getenv("LOCAL_BUFFER_CAPACITY", "50000"))
    
    # Synchronization
    sync_interval_seconds: float = float(os.getenv("SYNC_INTERVAL_SECONDS", "15.0"))
    heartbeat_interval_seconds: float = 5.0
    batch_sync_limit: int = 50
    compression_enabled: bool = True
    
    # Inference & Hardware Profile
    hardware_accel: str = os.getenv("HARDWARE_ACCELERATION", "AUTO") # CUDA, TENSORRT, DIRECTML, CPU
    inference_fps_limit: float = 25.0
    
    # Monitored Forward Cameras
    camera_ids: List[str] = field(default_factory=lambda: ["CAM-01", "CAM-02", "CAM-03", "CAM-07"])
    
    def __post_init__(self):
        os.makedirs(self.buffer_dir, exist_ok=True)
        os.makedirs(self.evidence_dir, exist_ok=True)

edge_config = EdgeConfig()
