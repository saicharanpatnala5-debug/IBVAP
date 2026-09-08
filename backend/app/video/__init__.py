"""
IBVAP - Video Ingest and Evidence Capture Registry
"""
from app.video.rtsp_manager import rtsp_manager, RTSPManager
from app.video.evidence_capture import evidence_capture, EvidenceCaptureService

__all__ = ["rtsp_manager", "RTSPManager", "evidence_capture", "EvidenceCaptureService"]
