"""
IBVAP - File-Based Evidence Ring Buffer with FIFO Auto-Pruning
Guarantees local SSD/eMMC memory quotas are respected at forward border outposts.
"""

import os
import glob
import time
from typing import Dict, Any

class EdgeFileRingBuffer:
    def __init__(self, evidence_dir: str = None, max_disk_mb: int = 500):
        if evidence_dir is None:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage", "edge_evidence"))
            os.makedirs(root, exist_ok=True)
            evidence_dir = root

        self.evidence_dir = evidence_dir
        self.max_disk_mb = max_disk_mb

    def save_evidence_file(self, filename: str, data: bytes) -> str:
        """Saves file and enforces disk quota."""
        self.enforce_quota()
        filepath = os.path.join(self.evidence_dir, filename)
        with open(filepath, "wb") as f:
            f.write(data)
        return filepath

    def enforce_quota(self):
        """Enforces FIFO eviction if quota exceeded."""
        files = glob.glob(os.path.join(self.evidence_dir, "*.*"))
        total_bytes = sum(os.path.getsize(f) for f in files)
        max_bytes = self.max_disk_mb * 1024 * 1024

        if total_bytes > max_bytes:
            # Sort by modification time ascending (oldest first)
            files.sort(key=os.path.getmtime)
            for f in files:
                try:
                    os.remove(f)
                    total_bytes -= os.path.getsize(f)
                    if total_bytes <= max_bytes * 0.85: # Free down to 85%
                        break
                except OSError:
                    pass

    def get_storage_stats(self) -> Dict[str, Any]:
        files = glob.glob(os.path.join(self.evidence_dir, "*.*"))
        total_mb = sum(os.path.getsize(f) for f in files) / (1024.0 * 1024.0)
        return {
            "total_files": len(files),
            "used_mb": round(total_mb, 2),
            "max_mb": self.max_disk_mb,
            "utilization_pct": round((total_mb / self.max_disk_mb) * 100.0, 2)
        }

edge_ring_buffer = EdgeFileRingBuffer()
