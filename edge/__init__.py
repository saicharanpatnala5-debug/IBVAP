"""
IBVAP - Intelligent Border Video Analytics Platform (Edge Computing Subsystem)
Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division
"""

from edge.config import edge_config
from edge.inference.edge_engine import EdgeInferenceEngine, edge_engine
from edge.local_storage.sqlite_queue import SQLiteOfflineQueue, edge_queue
from edge.local_storage.storage_manager import EdgeStorageManager, edge_storage_manager
from edge.sync.network_monitor import NetworkMonitor, network_monitor
from edge.sync.sync_manager import EdgeSyncManager, edge_sync_manager
from edge.stream.camera_worker import CameraWorker, camera_worker_pool

__all__ = [
    "edge_config",
    "EdgeInferenceEngine", "edge_engine",
    "SQLiteOfflineQueue", "edge_queue",
    "EdgeStorageManager", "edge_storage_manager",
    "NetworkMonitor", "network_monitor",
    "EdgeSyncManager", "edge_sync_manager",
    "CameraWorker", "camera_worker_pool"
]
