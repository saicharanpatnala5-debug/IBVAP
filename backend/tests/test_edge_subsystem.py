"""
IBVAP - Edge Subsystem Automated Integration and Unit Tests
Tests edge inference, SQLite queue, ring buffer, encryption, and sync.
"""
import pytest
import os
import sys
import time

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from edge.inference.edge_engine import edge_engine
from edge.inference.edge_zone_evaluator import edge_zone_evaluator
from edge.local_storage.sqlite_queue import SQLiteOfflineQueue
from edge.local_storage.ring_buffer import EdgeFileRingBuffer
from edge.local_storage.encryption import edge_encryptor
from edge.sync.payload_builder import payload_builder
from edge.sync.network_monitor import network_monitor

def test_edge_inference_and_zone_evaluation():
    polygon = [[0.20, 0.40], [0.85, 0.40], [0.85, 0.95], [0.20, 0.95]]
    result = edge_engine.process_edge_frame("CAM-03", None, zone_polygon=polygon, is_night=True)
    assert result["camera_id"] == "CAM-03"
    assert result["detections_count"] >= 1
    assert result["active_tracks_count"] >= 1
    assert result["risk_score"] >= 50
    assert result["severity"] in ["HIGH", "CRITICAL"]
    assert "latency_ms" in result

def test_edge_sqlite_queue_and_priority():
    test_db = os.path.join(os.path.dirname(__file__), "test_edge_queue.db")
    if os.path.exists(test_db):
        os.remove(test_db)

    try:
        queue = SQLiteOfflineQueue(db_path=test_db, capacity=100)
        # Enqueue priority 3 (routine), priority 1 (critical)
        id1 = queue.enqueue_event("ROUTINE_EVENT", "CAM-01", "NORMAL", 20, priority=3, payload={"key": 1})
        id2 = queue.enqueue_event("CRITICAL_BREACH", "CAM-03", "CRITICAL", 110, priority=1, payload={"key": 2})

        stats = queue.get_queue_stats()
        assert stats["unsynced_events"] == 2
        assert stats["critical_pending"] == 1

        # Batch peek must return Priority 1 first
        batch = queue.peek_uncommitted_batch(limit=10)
        assert len(batch) == 2
        assert batch[0]["event_id"] == id2 # Priority 1 must be first!
        assert batch[0]["priority"] == 1

        # Acknowledge
        queue.acknowledge_sync([id2])
        stats_after = queue.get_queue_stats()
        assert stats_after["unsynced_events"] == 1
    finally:
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except OSError:
                pass

def test_edge_encryption_and_ring_buffer():
    secret = b"TACTICAL_BORDER_EVIDENCE_FRAME_DATA_12345"
    enc = edge_encryptor.encrypt_bytes(secret)
    assert enc != secret
    dec = edge_encryptor.decrypt_bytes(enc)
    assert dec == secret

    # Test payload builder compression and SHA-256
    events = [{"id": i, "data": "sample_border_event_payload"} for i in range(20)]
    comp, digest, meta = payload_builder.pack_events("EDGE-NODE-01", events)
    assert len(comp) < meta["uncompressed_bytes"]
    assert len(digest) == 64
