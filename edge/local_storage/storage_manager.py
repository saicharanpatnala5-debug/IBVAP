"""
IBVAP - Master Edge Storage Coordinator
Monitors disk quotas, local event queues, and evidence lifecycle.
"""

import psutil
from typing import Dict, Any
from edge.local_storage.sqlite_queue import edge_queue
from edge.local_storage.ring_buffer import edge_ring_buffer

class EdgeStorageManager:
    def get_system_storage_report(self) -> Dict[str, Any]:
        queue_stats = edge_queue.get_queue_stats()
        ring_stats = edge_ring_buffer.get_storage_stats()
        disk = psutil.disk_usage("/") if hasattr(psutil, "disk_usage") else None

        return {
            "offline_queue": queue_stats,
            "evidence_buffer": ring_stats,
            "disk_free_gb": round(disk.free / (1024**3), 2) if disk else 50.0,
            "storage_health": "HEALTHY" if queue_stats["capacity_utilization_pct"] < 90.0 else "WARNING"
        }

edge_storage_manager = EdgeStorageManager()
