"""
IBVAP - Global Cross-Camera Tracking & Predictive Handoff Engine
Directly implements Section 16 (Predictive Camera Handoff) of the PRD.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from ai.multicamera.camera_graph import camera_graph

class GlobalTrackingEngine:
    def predict_camera_handoff(self, current_camera_id: str) -> Optional[Dict[str, Any]]:
        candidates = camera_graph.get_next_candidates(current_camera_id)
        if not candidates:
            return None

        best = max(candidates, key=lambda x: x["prob"])
        now = datetime.now(timezone.utc)
        eta_min = now + timedelta(seconds=best["min_t"])
        eta_max = now + timedelta(seconds=best["max_t"])

        return {
            "source_camera": current_camera_id,
            "predicted_camera": best["to_camera"],
            "probability_pct": round(best["prob"] * 100, 1),
            "expected_transit_window": f"{best['min_t']}-{best['max_t']} seconds",
            "distance_meters": best["dist_m"],
            "eta_window": f"{eta_min.strftime('%H:%M:%S')} - {eta_max.strftime('%H:%M:%S')}",
            "tactical_action": f"Auto-focus and arm intrusion detector on {best['to_camera']}"
        }

global_tracking_engine = GlobalTrackingEngine()
