"""
IBVAP - Evidence Capture Service
Captures and stores evidence frames/clips for incidents.
Provides SHA-256 integrity hashing for forensic chain-of-custody.
"""
import os
import hashlib
import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

logger = logging.getLogger("ibvap.evidence")


class EvidenceService:
    """Captures, hashes, and stores evidence frames linked to incidents."""

    def __init__(self, evidence_dir: str = "./storage/evidence"):
        self.evidence_dir = evidence_dir
        os.makedirs(evidence_dir, exist_ok=True)

    def capture_snapshot(
        self,
        frame: np.ndarray,
        camera_id: str,
        incident_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Captures and stores an evidence frame with integrity hash.
        Returns evidence record or None on failure.
        """
        if frame is None or frame.size == 0 or not CV2_AVAILABLE:
            return None

        timestamp = datetime.now(timezone.utc)
        ts_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{camera_id}_{incident_id}_{ts_str}.jpg"
        filepath = os.path.join(self.evidence_dir, filename)

        try:
            # Encode as JPEG with high quality
            success, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if not success:
                return None

            image_bytes = buf.tobytes()

            # Compute SHA-256 hash for integrity verification
            sha256_hash = hashlib.sha256(image_bytes).hexdigest()

            # Write to disk
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            # Create evidence record
            record = {
                "evidence_id": f"EVD-{sha256_hash[:12].upper()}",
                "incident_id": incident_id,
                "camera_id": camera_id,
                "filepath": filepath,
                "filename": filename,
                "timestamp": timestamp.isoformat(),
                "sha256": sha256_hash,
                "file_size_bytes": len(image_bytes),
                "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                "metadata": metadata or {},
            }

            # Write sidecar JSON
            json_path = filepath.replace('.jpg', '.json')
            with open(json_path, 'w') as f:
                json.dump(record, f, indent=2)

            logger.info(f"Evidence captured: {filename} (SHA256: {sha256_hash[:16]}...)")
            return record

        except Exception as e:
            logger.error(f"Evidence capture failed: {e}")
            return None

    def verify_integrity(self, filepath: str, expected_hash: str) -> bool:
        """Verifies file integrity against stored SHA-256 hash."""
        try:
            with open(filepath, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            return actual_hash == expected_hash
        except Exception:
            return False


evidence_service = EvidenceService()
