"""
IBVAP - Incident Builder Engine
Fuses multi-event clusters into unified Incident entities with chronological timelines.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

class IncidentBuilder:
    def build_incident(self, camera_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        total_risk = sum(e.get("risk_delta", 20) for e in events)
        
        event_types = set(e.get("event_type") for e in events)
        if "ZONE_INTRUSION" in event_types and "ANPR_DETECTION" in event_types:
            title = f"Vehicle Drop-off & Perimeter Breach at {camera_id}"
        elif "ZONE_INTRUSION" in event_types:
            title = f"Unauthorized Virtual Fence Breach at {camera_id}"
        else:
            title = f"Suspicious Activity Incident at {camera_id}"

        timeline = []
        for e in events:
            timeline.append({
                "time": e.get("timestamp", datetime.now(timezone.utc)).strftime("%H:%M:%S"),
                "event_type": e.get("event_type"),
                "points": e.get("risk_delta", 20),
                "confidence": e.get("confidence", 0.90)
            })

        severity = "CRITICAL" if total_risk >= 120 else "HIGH" if total_risk >= 90 else "MEDIUM" if total_risk >= 60 else "LOW"

        return {
            "incident_id": incident_id,
            "title": title,
            "severity": severity,
            "risk_score": total_risk,
            "camera_id": camera_id,
            "timeline": timeline,
            "event_count": len(events)
        }

incident_builder = IncidentBuilder()
