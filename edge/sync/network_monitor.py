"""
IBVAP - Forward Edge Backhaul Network Health Monitor
Monitors upstream connectivity (optical fiber, satellite, cellular 4G/5G).
"""

import time
from typing import Dict, Any
import urllib.request
import urllib.error

class NetworkMonitor:
    def __init__(self, central_server_url: str = "http://127.0.0.1:8000"):
        self.central_server_url = central_server_url
        self.is_connected = False
        self.last_check_time = 0.0
        self.latency_ms = 0.0
        self.consecutive_failures = 0

    def check_connectivity(self) -> bool:
        """Pings upstream health endpoint."""
        url = f"{self.central_server_url}/api/health/live"
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "IBVAP-Edge-Node/2.0"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    self.latency_ms = (time.perf_counter() - t0) * 1000.0
                    self.is_connected = True
                    self.consecutive_failures = 0
                    self.last_check_time = time.time()
                    return True
        except Exception:
            pass

        self.is_connected = False
        self.consecutive_failures += 1
        self.last_check_time = time.time()
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "backhaul_connected": self.is_connected,
            "latency_ms": round(self.latency_ms, 1),
            "consecutive_failures": self.consecutive_failures,
            "link_quality": "EXCELLENT" if self.latency_ms < 50 and self.is_connected else ("DEGRADED" if self.is_connected else "OFFLINE_ISOLATED")
        }

network_monitor = NetworkMonitor()
