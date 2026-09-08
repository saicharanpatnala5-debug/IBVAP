"""
IBVAP - High-Throughput Edge AI Inference Engine
Optimized for low-latency INT8 / FP16 quantized inference on rugged forward edge SBCs.
"""

import time
import numpy as np
from typing import Dict, Any, List, Optional
from edge.inference.edge_detector import edge_detector
from edge.inference.edge_tracker import edge_tracker
from edge.inference.edge_zone_evaluator import edge_zone_evaluator

class EdgeInferenceEngine:
    def __init__(self, node_id: str = "EDGE-NODE-ALPHA-01"):
        self.node_id = node_id
        self.frames_processed = 0
        self.inference_times_ms: List[float] = []

    def process_edge_frame(
        self,
        camera_id: str,
        frame: Optional[np.ndarray],
        zone_polygon: Optional[List[List[float]]] = None,
        is_night: bool = True
    ) -> Dict[str, Any]:
        """
        Processes a single video frame locally at the edge:
        1. Object Detection (Person & Vehicle)
        2. Multi-Object Tracking & Velocity Estimation
        3. Ray-Casting Virtual Fence Containment
        4. Edge Risk Pre-scoring
        """
        t0 = time.perf_counter()
        self.frames_processed += 1

        # 1. Detect Objects
        detections = edge_detector.detect(frame, is_night=is_night)

        # 2. Track Objects
        tracks = edge_tracker.update_tracks(camera_id, detections)

        # 3. Virtual Fence Polygonal Zone Evaluation
        breaches = []
        if zone_polygon:
            for trk in tracks:
                breach_info = edge_zone_evaluator.evaluate_track(trk, zone_polygon)
                if breach_info["is_breach"]:
                    breaches.append(breach_info)

        # 4. Quick Edge Risk Pre-Score
        risk_score = 15 if is_night else 0
        if breaches:
            risk_score += 50
        if len(tracks) > 2:
            risk_score += 20

        severity = "NORMAL"
        if risk_score >= 80:
            severity = "CRITICAL"
        elif risk_score >= 50:
            severity = "HIGH"
        elif risk_score >= 30:
            severity = "MEDIUM"

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.inference_times_ms.append(elapsed_ms)
        if len(self.inference_times_ms) > 100:
            self.inference_times_ms.pop(0)

        return {
            "edge_node_id": self.node_id,
            "camera_id": camera_id,
            "timestamp": time.time(),
            "detections_count": len(detections),
            "active_tracks_count": len(tracks),
            "tracks": tracks,
            "breaches": breaches,
            "risk_score": risk_score,
            "severity": severity,
            "latency_ms": round(elapsed_ms, 2),
            "fps": round(1000.0 / max(elapsed_ms, 0.001), 1)
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        avg_ms = sum(self.inference_times_ms) / len(self.inference_times_ms) if self.inference_times_ms else 0.0
        return {
            "node_id": self.node_id,
            "total_frames": self.frames_processed,
            "avg_latency_ms": round(avg_ms, 2),
            "avg_fps": round(1000.0 / max(avg_ms, 0.001), 1) if avg_ms > 0 else 0.0
        }

edge_engine = EdgeInferenceEngine()
