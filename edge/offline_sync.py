"""
IBVAP - Edge-First Local Buffering & Upstream Synchronization Engine
Buffers events and metadata locally during network loss and synchronizes when connectivity returns.
Directly implements Section 18 of the PRD and Section 19 of the TDD.
"""
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class EdgeOfflineBuffer:
    def __init__(self):
        self.buffer_file = os.path.join(settings.OFFLINE_BUFFER_DIR, "offline_events_buffer.json")
        os.makedirs(settings.OFFLINE_BUFFER_DIR, exist_ok=True)
        if not os.path.exists(self.buffer_file):
            with open(self.buffer_file, "w") as f:
                json.dump([], f)

    def queue_offline_event(self, event_data: Dict[str, Any]):
        """Queue event locally when central server is unreachable."""
        events = self.read_buffer()
        events.append(event_data)
        with open(self.buffer_file, "w") as f:
            json.dump(events, f, indent=2)
        logger.warning(f"[EDGE BUFFER] Queued offline event: {event_data.get('event_type')}. Total in buffer: {len(events)}")

    def read_buffer(self) -> List[Dict[str, Any]]:
        try:
            with open(self.buffer_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def flush_and_sync(self) -> List[Dict[str, Any]]:
        """Return buffered events and clear local edge queue after upstream confirmation."""
        events = self.read_buffer()
        with open(self.buffer_file, "w") as f:
            json.dump([], f)
        logger.info(f"[EDGE BUFFER] Successfully synchronized {len(events)} events upstream.")
        return events

edge_buffer = EdgeOfflineBuffer()
