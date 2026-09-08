"""
IBVAP - Forward Edge Node Autonomous Tactical Daemon
Standard: Smart India Hackathon (SIH 2026) | Problem Statement: SIH26187
Ministry of Home Affairs / Sashastra Seema Bal (SSB), Police-II Division

Launches the complete forward edge station:
- Ingestion Workers for forward cameras
- Microsecond edge inference & virtual fence evaluation
- 50,000 capacity ACID local offline buffering
- 4-Tier priority upstream backhaul synchronization
"""

import os
import sys
import time
import argparse

# Ensure root & backend directories are in path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from edge.config import edge_config
from edge.inference.edge_engine import edge_engine
from edge.stream.camera_worker import camera_worker_pool
from edge.local_storage.sqlite_queue import edge_queue
from edge.local_storage.storage_manager import edge_storage_manager
from edge.sync.network_monitor import network_monitor
from edge.sync.sync_manager import edge_sync_manager

def run_edge_daemon(duration_sec: int = 10, simulate_blackout: bool = False):
    print("=" * 82)
    print("  IBVAP - FORWARD BORDER OUTPOST (BOP) EDGE NODE RUNTIME")
    print(f"  Node ID:     {edge_config.edge_node_id}")
    print(f"  Jurisdiction: {edge_config.bop_id} | {edge_config.sector}")
    print(f"  Central Host: {edge_config.central_server_url}")
    print(f"  Max Buffer:   {edge_config.max_buffered_events:,} events (ACID SQLite WAL)")
    print("=" * 82)

    start_time = time.time()
    cycle = 0

    print("\n[EDGE TACTICAL AUTONOMOUS PIPELINE TELEMETRY]")
    print("-" * 82)
    print(f"{'CYCLE':<7} | {'CAMERA':<8} | {'EDGE FPS':<10} | {'RISK':<6} | {'QUEUE DEPTH':<14} | {'BACKHAUL':<12} | {'SYNC STATUS':<14}")
    print("-" * 82)

    while (time.time() - start_time) < duration_sec:
        cycle += 1
        cam_id = "CAM-03" # Sensitive border fence zero-tolerance camera
        worker = camera_worker_pool.get_or_create_worker(cam_id)

        # 1. Step camera ingestion + edge inference
        zone_polygon = [[0.20, 0.40], [0.85, 0.40], [0.85, 0.95], [0.20, 0.95]]
        result = worker.step(zone_polygon=zone_polygon)

        # 2. Check Backhaul & Synchronize
        if simulate_blackout:
            backhaul_status = "OFFLINE"
            sync_res = {"status": "BUFFERED_LOCALLY", "synced_count": 0}
        else:
            backhaul_status = "ONLINE" if network_monitor.check_connectivity() else "OFFLINE"
            sync_res = edge_sync_manager.synchronize_batch()

        queue_stats = edge_queue.get_queue_stats()

        print(f"#{cycle:<6} | {cam_id:<8} | {result['fps']:<10.1f} | {result['risk_score']:<6} | {queue_stats['unsynced_events']:<14} | {backhaul_status:<12} | {sync_res['status']:<14}")
        time.sleep(1.0)

    print("-" * 82)
    print("\n[EDGE OPERATIONAL AUDIT REPORT]")
    report = edge_storage_manager.get_system_storage_report()
    perf = edge_engine.get_performance_stats()
    print(f"  - Total Inferred Frames:   {perf['total_frames']}")
    print(f"  - Average Inference Speed: {perf['avg_fps']} FPS ({perf['avg_latency_ms']} ms)")
    print(f"  - Local Buffer Depth:      {report['offline_queue']['unsynced_events']} pending / {report['offline_queue']['capacity']} capacity")
    print(f"  - Free Disk Capacity:      {report['disk_free_gb']} GB")
    print(f"  - Edge Storage Health:     {report['storage_health']}")
    print("=" * 82)
    print("  [OK] EDGE NODE AUTONOMOUS SEQUENCE COMPLETED SUCCESSFULLY")
    print("=" * 82)

def main():
    parser = argparse.ArgumentParser(description="IBVAP Autonomous Edge Node Daemon")
    parser.add_argument("--duration", type=int, default=5, help="Runtime duration in seconds")
    parser.add_argument("--simulate-blackout", action="store_true", help="Simulate forward backhaul loss")
    args = parser.parse_args()

    run_edge_daemon(duration_sec=args.duration, simulate_blackout=args.simulate_blackout)

if __name__ == "__main__":
    main()
