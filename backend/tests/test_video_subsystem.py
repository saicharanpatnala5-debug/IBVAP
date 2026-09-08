"""
IBVAP - Video Subsystem Test Suite
Tests RTSP client, frame reader, circular buffer, frame queue, processing pipeline,
multi-camera synchronizer, and forensic evidence clip generation.
"""
import os
import sys
import time
import tempfile
import numpy as np
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from video.rtsp.rtsp_client import RTSPClient
from video.rtsp.reconnect import ReconnectPolicy, CircuitBreaker
from video.rtsp.stream_manager import StreamManager
from video.ingestion.frame_reader import FrameReader
from video.ingestion.frame_buffer import CircularFrameBuffer
from video.ingestion.frame_queue import FrameQueue, OverflowPolicy
from video.processing.pipeline import VideoProcessingPipeline
from video.processing.synchronizer import MultiCameraSynchronizer
from video.recording.evidence_clip import EvidenceClipGenerator

def test_rtsp_client_synthetic():
    client = RTSPClient(camera_id="TEST-CAM-01", stream_url="synthetic", target_fps=30.0)
    assert client.open() is True
    assert client.is_connected is True
    assert client.is_synthetic is True

    for _ in range(5):
        ret, frame = client.read_frame()
        assert ret is True
        assert frame is not None
        assert frame.shape == (360, 640, 3)

    telemetry = client.get_telemetry()
    assert telemetry["camera_id"] == "TEST-CAM-01"
    assert telemetry["total_frames"] == 5
    assert telemetry["fps"] > 0
    client.close()
    assert client.is_connected is False

def test_reconnect_policy_and_circuit_breaker():
    policy = ReconnectPolicy(base_delay=1.0, max_delay=10.0, multiplier=2.0, jitter_pct=0.1)
    d1 = policy.compute_delay(1)
    d2 = policy.compute_delay(2)
    d3 = policy.compute_delay(3)
    assert 0.8 <= d1 <= 1.2
    assert 1.6 <= d2 <= 2.4
    assert 3.2 <= d3 <= 4.8

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)
    assert breaker.can_attempt() is True
    assert breaker.state == CircuitBreaker.CLOSED

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.can_attempt() is True
    
    # 3rd failure trips the breaker
    breaker.record_failure()
    assert breaker.state == CircuitBreaker.OPEN
    assert breaker.can_attempt() is False

    # Wait for recovery timeout
    time.sleep(0.25)
    assert breaker.can_attempt() is True
    assert breaker.state == CircuitBreaker.HALF_OPEN

    # Success closes the breaker
    breaker.record_success()
    assert breaker.state == CircuitBreaker.CLOSED

def test_frame_reader_and_queue():
    client = RTSPClient(camera_id="TEST-CAM-02", stream_url="synthetic")
    client.open()
    reader = FrameReader(client)
    reader.start()

    time.sleep(0.15)
    ret, frame, ts = reader.get_latest_frame()
    assert ret is True
    assert frame is not None
    assert frame.shape == (360, 640, 3)
    assert ts > 0
    reader.stop()
    client.close()

    # Test FrameQueue with DROP_OLDEST
    fq = FrameQueue(maxsize=3, policy=OverflowPolicy.DROP_OLDEST)
    fq.put("frame_1")
    fq.put("frame_2")
    fq.put("frame_3")
    assert fq.qsize() == 3

    # Putting 4th frame should drop frame_1
    fq.put("frame_4")
    assert fq.qsize() == 3
    assert fq.dropped_count == 1
    assert fq.get() == "frame_2"
    assert fq.get() == "frame_3"
    assert fq.get() == "frame_4"

def test_circular_frame_buffer():
    buf = CircularFrameBuffer(max_frames=5)
    test_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    for i in range(8):
        buf.append(test_frame, metadata={"seq": i})

    assert len(buf) == 5
    all_frames = buf.get_all()
    assert len(all_frames) == 5
    # Oldest retained frame should be seq 3
    assert all_frames[0][2]["seq"] == 3
    assert all_frames[-1][2]["seq"] == 7

    recent = buf.get_recent_frames(seconds=10.0)
    assert len(recent) == 5

def test_video_processing_pipeline():
    pipeline = VideoProcessingPipeline()
    raw_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Test Letterbox
    letterboxed, ratio, pad = pipeline.letterbox(raw_frame, target_shape=(640, 640))
    assert letterboxed.shape == (640, 640, 3)
    assert ratio == 640 / 1280

    # Test Low-light enhancement
    enhanced = pipeline.enhance_low_light(letterboxed)
    assert enhanced.shape == (640, 640, 3)

    # Test Watermark
    watermarked = pipeline.apply_hud_watermark(letterboxed, "CAM-01")
    assert watermarked.shape == (640, 640, 3)

    # Test Complete Pipeline
    output, meta = pipeline.process(raw_frame, "CAM-01", target_size=(640, 640), enhance=True)
    assert output.shape == (640, 640, 3)
    assert meta["camera_id"] == "CAM-01"
    assert meta["enhanced"] is True

def test_multi_camera_synchronizer():
    sync = MultiCameraSynchronizer(tolerance_ms=40.0)
    f1 = np.ones((50, 50, 3), dtype=np.uint8)
    f2 = np.ones((50, 50, 3), dtype=np.uint8) * 2

    now = time.time()
    sync.add_frame("CAM-A", f1, timestamp=now)
    sync.add_frame("CAM-B", f2, timestamp=now + 0.015) # 15ms diff, within 40ms

    pair = sync.get_synchronized_pair("CAM-A", "CAM-B")
    assert pair is not None
    frame_a, frame_b, diff_ms = pair
    assert np.array_equal(frame_a, f1)
    assert np.array_equal(frame_b, f2)
    assert 10.0 <= diff_ms <= 20.0

def test_evidence_clip_generator():
    with tempfile.TemporaryDirectory() as tmp_dir:
        generator = EvidenceClipGenerator(output_dir=tmp_dir)
        frames = [np.ones((240, 320, 3), dtype=np.uint8) * i for i in range(10)]

        manifest = generator.package_evidence_clip(
            incident_id="INC-TEST-001",
            camera_id="CAM-03",
            frames=frames,
            fps=10.0,
            metadata={"test": True}
        )

        assert manifest["incident_id"] == "INC-TEST-001"
        assert manifest["frame_count"] == 10
        assert manifest["duration_seconds"] == 1.0
        assert os.path.exists(manifest["video_path"])
        assert os.path.exists(manifest["manifest_path"])
        assert len(manifest["sha256_digest"]) == 64
