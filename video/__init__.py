"""
IBVAP - Video Subsystem Facade
Provides clean, high-performance streaming, ingestion, processing, and recording abstractions.
"""
from video.rtsp.rtsp_client import RTSPClient
from video.rtsp.stream_manager import StreamManager, stream_manager
from video.rtsp.reconnect import ReconnectPolicy, CircuitBreaker
from video.ingestion.frame_reader import FrameReader
from video.ingestion.frame_buffer import CircularFrameBuffer
from video.ingestion.frame_queue import FrameQueue, OverflowPolicy
from video.processing.pipeline import VideoProcessingPipeline, video_pipeline
from video.processing.synchronizer import MultiCameraSynchronizer
from video.recording.recorder import VideoRecorder
from video.recording.evidence_clip import EvidenceClipGenerator, evidence_generator

__all__ = [
    "RTSPClient",
    "StreamManager",
    "stream_manager",
    "ReconnectPolicy",
    "CircuitBreaker",
    "FrameReader",
    "CircularFrameBuffer",
    "FrameQueue",
    "OverflowPolicy",
    "VideoProcessingPipeline",
    "video_pipeline",
    "MultiCameraSynchronizer",
    "VideoRecorder",
    "EvidenceClipGenerator",
    "evidence_generator"
]
