"""
IBVAP - Multi-Channel Emergency Notification Service
Dispatches tactical alerts via WebSockets, radio links, and field SMS/emails.
"""
import time
from typing import Dict, Any, Optional
from app.core.logging import logger
from app.api.websocket import ws_manager

class NotificationService:
    """Manages emergency alert distribution with rate-limiting and de-duplication."""

    def __init__(self):
        self._last_alert_time: Dict[str, float] = {}
        self.cooldown_seconds = 5.0
        self.dispatched_count = 0

    async def notify_alert(
        self,
        alert_data: Dict[str, Any],
        incident_id: str,
        severity: str = "HIGH"
    ) -> bool:
        """Dispatches real-time breach notifications to connected command posts."""
        now = time.time()
        dedup_key = f"{alert_data.get('camera_id')}_{alert_data.get('summary')}"
        
        if dedup_key in self._last_alert_time:
            if now - self._last_alert_time[dedup_key] < self.cooldown_seconds:
                logger.debug(f"Notification suppressed due to cooldown: {dedup_key}")
                return False

        self._last_alert_time[dedup_key] = now
        self.dispatched_count += 1

        payload = {
            "type": "TACTICAL_ALERT",
            "incident_id": incident_id,
            "severity": severity,
            "alert": alert_data,
            "dispatched_at": now
        }

        # 1. WebSocket Broadcast to /ws/alerts
        await ws_manager.broadcast_alert(payload)

        # 2. Simulated QRT Field Radio & Siren Trigger
        if severity in ("HIGH", "CRITICAL"):
            logger.info(f"[TACTICAL DISPATCH] SIREN & QRT RADIO ENGAGED for Incident {incident_id} ({severity})")

        return True

    async def notify_incident_escalation(
        self,
        incident_id: str,
        new_status: str,
        summary: str
    ):
        """Notifies command center of incident status changes."""
        payload = {
            "type": "INCIDENT_STATUS_CHANGE",
            "incident_id": incident_id,
            "status": new_status,
            "summary": summary,
            "timestamp": time.time()
        }
        await ws_manager.broadcast_alert(payload)

notification_service = NotificationService()
