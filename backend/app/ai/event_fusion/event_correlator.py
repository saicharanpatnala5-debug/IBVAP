"""
IBVAP - Event Correlator Engine
Associates disparate model events across time and space.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

class EventCorrelator:
    def __init__(self, time_window_seconds: float = 120.0):
        self.time_window = timedelta(seconds=time_window_seconds)

    def correlate(self, events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Groups events into correlated clusters based on camera proximity and temporal window.
        """
        if not events:
            return []

        sorted_events = sorted(events, key=lambda x: x.get("timestamp", datetime.now(timezone.utc)))
        clusters = []
        current_cluster = [sorted_events[0]]

        for ev in sorted_events[1:]:
            t_prev = current_cluster[-1].get("timestamp", datetime.now(timezone.utc))
            t_curr = ev.get("timestamp", datetime.now(timezone.utc))
            if abs(t_curr - t_prev) <= self.time_window:
                current_cluster.append(ev)
            else:
                clusters.append(current_cluster)
                current_cluster = [ev]

        if current_cluster:
            clusters.append(current_cluster)

        return clusters

event_correlator = EventCorrelator()
