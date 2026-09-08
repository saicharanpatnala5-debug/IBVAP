"""
IBVAP - 4-Tier Priority Edge Upstream Synchronization Engine
Prioritizes Critical Alarms > Watchlist Matches > Fused Incidents > Routine Telemetry.
"""

import time
import json
import urllib.request
from typing import Dict, Any, List
from edge.config import edge_config
from edge.local_storage.sqlite_queue import edge_queue
from edge.sync.network_monitor import network_monitor
from edge.sync.payload_builder import payload_builder
from edge.sync.retry_policy import ExponentialBackoffRetry

class EdgeSyncManager:
    def __init__(self):
        self.config = edge_config
        self.retry_policy = ExponentialBackoffRetry()
        self.last_sync_time = 0.0
        self.total_synced_events = 0

    def synchronize_batch(self) -> Dict[str, Any]:
        """
        Executes a single synchronization cycle:
        1. Checks connectivity
        2. Peeks priority batch from SQLite queue
        3. Packs, digests, and sends to central server
        4. Acknowledges on 200 OK
        """
        is_online = network_monitor.check_connectivity()
        if not is_online:
            self.retry_policy.record_failure()
            return {
                "status": "BACKHAUL_OFFLINE",
                "synced_count": 0,
                "pending_queue": edge_queue.get_queue_stats()["unsynced_events"]
            }

        # 2. Fetch prioritized batch
        batch = edge_queue.peek_uncommitted_batch(limit=self.config.batch_sync_limit)
        if not batch:
            return {"status": "IDLE_EMPTY_QUEUE", "synced_count": 0}

        # 3. Pack Payload
        compressed, digest, meta = payload_builder.pack_events(self.config.edge_node_id, batch)

        # 4. Transmit to upstream sync endpoint
        url = f"{self.config.central_server_url}/api/edge/sync"
        req = urllib.request.Request(
            url,
            data=compressed,
            headers={
                "Content-Type": "application/octet-stream",
                "X-Edge-Node-ID": self.config.edge_node_id,
                "X-Payload-SHA256": digest,
                "X-Compression": "zlib"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                if resp.status in (200, 201):
                    # 5. Acknowledge sync locally
                    event_ids = [e["event_id"] for e in batch]
                    edge_queue.acknowledge_sync(event_ids)
                    self.total_synced_events += len(batch)
                    self.retry_policy.record_success()
                    self.last_sync_time = time.time()
                    return {
                        "status": "SUCCESS",
                        "synced_count": len(batch),
                        "compression_ratio": meta["compression_ratio"],
                        "total_synced_all_time": self.total_synced_events
                    }
        except Exception as e:
            self.retry_policy.record_failure()
            return {"status": "TRANSMIT_FAILED", "error": str(e), "synced_count": 0}

        return {"status": "UNKNOWN_ERROR", "synced_count": 0}

edge_sync_manager = EdgeSyncManager()
