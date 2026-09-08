"""
IBVAP - AI Event Fusion Engine
Unifies multiple discrete detections and events within spatial-temporal windows into a single actionable Incident.
Directly implements Section 16 (Differentiating Feature) of the PRD.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import uuid

class EventFusionEngine:
    """
    Event Fusion replaces alert fatigue by transforming:
    [Vehicle Detected] + [Person Exits] + [Restricted Zone Entry] + [Loitering]
    into:
    ONE INCIDENT: 'Coordinated Vehicle Drop-Off & Perimeter Intrusion'
    """

    def fuse_events_into_incident(
        self,
        camera_id: str,
        events: List[Dict[str, Any]],
        existing_incident_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Takes a list of correlated events and generates an aggregated incident with
        cumulative risk score, fused title, and chronological timeline.
        """
        if not events:
            return {}

        incident_id = existing_incident_id or f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        event_types = set(e.get("event_type") for e in events)
        total_risk = sum(e.get("risk_delta", 15) for e in events)
        
        # Determine fused incident title
        if "ZONE_INTRUSION" in event_types and "ANPR_DETECTION" in event_types:
            title = f"Vehicle Drop-off & Zone Intrusion Breach at {camera_id}"
        elif "ZONE_INTRUSION" in event_types and "LOITERING" in event_types:
            title = f"Perimeter Intrusion with Prolonged Loitering at {camera_id}"
        elif "ZONE_INTRUSION" in event_types:
            title = f"Unauthorized Virtual Fence Breach at {camera_id}"
        elif "ANPR_DETECTION" in event_types:
            title = f"Vehicle Sighting & ANPR Log at {camera_id}"
        else:
            title = f"Suspicious Activity Cluster at {camera_id}"

        # Severity mapping
        if total_risk >= 120:
            severity = "CRITICAL"
        elif total_risk >= 90:
            severity = "HIGH"
        elif total_risk >= 60:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Build chronological timeline
        timeline = []
        for e in sorted(events, key=lambda x: x.get("timestamp", datetime.now(timezone.utc))):
            t_obj = e.get("timestamp")
            time_str = t_obj.strftime("%H:%M:%S") if isinstance(t_obj, datetime) else str(t_obj)
            timeline.append({
                "time": time_str,
                "timestamp": t_obj if isinstance(t_obj, datetime) else datetime.now(timezone.utc),
                "camera_id": e.get("camera_id", camera_id),
                "event_type": e.get("event_type"),
                "description": e.get("metadata_json", {}).get("description", f"{e.get('event_type')} registered"),
                "confidence": e.get("confidence", 0.90),
                "evidence_frame_url": e.get("evidence_frame_url"),
                "risk_points": e.get("risk_delta", 20)
            })

        contributing_factors = []
        for e in events:
            contributing_factors.append({
                "factor": e.get("event_type").replace("_", " ").title(),
                "points": e.get("risk_delta", 20),
                "confidence": e.get("confidence", 0.90)
            })

        return {
            "incident_id": incident_id,
            "title": title,
            "severity": severity,
            "risk_score": total_risk,
            "status": "ACTIVE",
            "lead_camera_id": camera_id,
            "contributing_event_ids": [e.get("event_id") for e in events if "event_id" in e],
            "contributing_factors_json": contributing_factors,
            "timeline": timeline,
            "start_time": timeline[0]["timestamp"] if timeline else datetime.now(timezone.utc),
            "end_time": timeline[-1]["timestamp"] if timeline else datetime.now(timezone.utc)
        }

event_fusion_engine = EventFusionEngine()
