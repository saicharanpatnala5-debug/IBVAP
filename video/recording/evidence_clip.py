"""
IBVAP - Forensic Evidence Clip Generator with Cryptographic SHA-256 Digest
"""
import os
import time
import json
import hashlib
from datetime import datetime, timezone
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

class EvidenceClipGenerator:
    """
    Combines pre-event buffer + active event + post-event buffer into
    a tamper-evident MP4 video clip with a cryptographic SHA-256 manifest.
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def compute_sha256(filepath: str) -> str:
        """Calculates SHA-256 digest of generated file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def package_evidence_clip(
        self,
        incident_id: str,
        camera_id: str,
        frames: List[np.ndarray],
        fps: float = 25.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Encodes list of frames into an MP4 clip and produces a SHA-256 signed manifest.
        """
        if not frames:
            raise ValueError("No frames provided for evidence packaging")

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        video_filename = f"EVIDENCE_{incident_id}_{camera_id}_{timestamp_str}.mp4"
        video_path = os.path.join(self.output_dir, video_filename)

        h, w = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(video_path, fourcc, fps, (w, h))

        for frame in frames:
            writer.write(frame)
        writer.release()

        # Compute SHA-256 integrity hash
        file_sha256 = self.compute_sha256(video_path)
        file_size = os.path.getsize(video_path)

        manifest = {
            "incident_id": incident_id,
            "camera_id": camera_id,
            "video_file": video_filename,
            "video_path": video_path,
            "file_size_bytes": file_size,
            "sha256_digest": file_sha256,
            "frame_count": len(frames),
            "duration_seconds": round(len(frames) / fps, 2),
            "fps": fps,
            "resolution": f"{w}x{h}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }

        manifest_filename = f"MANIFEST_{incident_id}_{camera_id}_{timestamp_str}.json"
        manifest_path = os.path.join(self.output_dir, manifest_filename)
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(manifest, mf, indent=2)

        manifest["manifest_path"] = manifest_path
        return manifest

evidence_generator = EvidenceClipGenerator(r"C:\Users\SAI CHARAN\OneDrive\Desktop\IBVAP\backend\storage\evidence")
