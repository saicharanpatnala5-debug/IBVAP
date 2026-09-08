"""
IBVAP - Multi-Camera Graph Topology and Predictive Camera Handoff Engine
Models physical site layout as a directed graph to predict next candidate camera views.
Directly implements Section 16 & Section 26 of PRD.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

class MultiCameraTopologyEngine:
    """
    Manages camera topological network:
    Node: Camera
    Edge: Transition probability, physical distance, minimum and maximum transit times.
    """

    def __init__(self):
        # Default in-memory topology for demonstration
        # Cam-01 -> Cam-02 (40%) and Cam-03 (60%)
        # Cam-03 -> Cam-07 (80%)
        self.edges = {
            "CAM-01": [
                {"to_camera_id": "CAM-03", "probability": 0.78, "min_sec": 15, "max_sec": 45, "distance_m": 60},
                {"to_camera_id": "CAM-02", "probability": 0.22, "min_sec": 20, "max_sec": 60, "distance_m": 85}
            ],
            "CAM-02": [
                {"to_camera_id": "CAM-04", "probability": 0.85, "min_sec": 10, "max_sec": 30, "distance_m": 40}
            ],
            "CAM-03": [
                {"to_camera_id": "CAM-07", "probability": 0.82, "min_sec": 25, "max_sec": 70, "distance_m": 110}
            ],
            "CAM-07": [
                {"to_camera_id": "CAM-08", "probability": 0.90, "min_sec": 15, "max_sec": 40, "distance_m": 50}
            ]
        }

    def predict_next_camera(self, current_camera_id: str) -> Optional[Dict[str, Any]]:
        """
        Predicts which camera the tracked target is most likely to appear on next,
        along with transition probability and expected arrival time window.
        """
        candidates = self.edges.get(current_camera_id, [])
        if not candidates:
            return None

        # Pick candidate with highest probability
        best_candidate = max(candidates, key=lambda x: x["probability"])
        now = datetime.now(timezone.utc)
        eta_min = now + timedelta(seconds=best_candidate["min_sec"])
        eta_max = now + timedelta(seconds=best_candidate["max_sec"])

        return {
            "source_camera_id": current_camera_id,
            "predicted_camera_id": best_candidate["to_camera_id"],
            "probability_pct": round(best_candidate["probability"] * 100, 1),
            "expected_transit_seconds": f"{best_candidate['min_sec']}-{best_candidate['max_sec']}s",
            "distance_meters": best_candidate["distance_m"],
            "eta_window": f"{eta_min.strftime('%H:%M:%S')} - {eta_max.strftime('%H:%M:%S')}",
            "recommended_action": f"Auto-focus and pre-arm detection pipeline on {best_candidate['to_camera_id']}"
        }

    def associate_cross_camera_track(
        self,
        track_exit: Dict[str, Any],
        track_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates spatial-temporal matching score between a target that exited Camera A
        and a target that subsequently entered Camera B.
        """
        cam_a = track_exit.get("camera_id")
        cam_b = track_entry.get("camera_id")
        time_diff = abs((track_entry.get("time") - track_exit.get("time")).total_seconds())

        matching_edge = None
        for edge in self.edges.get(cam_a, []):
            if edge["to_camera_id"] == cam_b:
                matching_edge = edge
                break

        if not matching_edge:
            return {"is_match": False, "confidence": 0.1, "reason": "No direct topological path"}

        # Check transit time plausibility
        if matching_edge["min_sec"] * 0.7 <= time_diff <= matching_edge["max_sec"] * 1.5:
            confidence = 0.88 * matching_edge["probability"]
            return {
                "is_match": True,
                "confidence": round(confidence, 2),
                "global_track_id": track_exit.get("global_track_id") or f"GLOBAL-{track_exit.get('track_id')}",
                "reason": f"Plausible transit time ({time_diff:.1f}s) across topology path {cam_a} -> {cam_b}"
            }
        else:
            return {
                "is_match": False,
                "confidence": 0.35,
                "reason": f"Transit time ({time_diff:.1f}s) outside expected window ({matching_edge['min_sec']}-{matching_edge['max_sec']}s)"
            }

multicamera_engine = MultiCameraTopologyEngine()
