"""
IBVAP - Reconnect Watchdog & Circuit Breaker Pattern
"""
import time
import random
from typing import Optional

class ReconnectPolicy:
    """Calculates exponential backoff delays with random jitter."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        multiplier: float = 2.0,
        jitter_pct: float = 0.20
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter_pct = jitter_pct

    def compute_delay(self, attempt: int) -> float:
        """Computes backoff delay for given attempt index."""
        raw_delay = min(self.max_delay, self.base_delay * (self.multiplier ** max(0, attempt - 1)))
        jitter = raw_delay * self.jitter_pct * (random.random() * 2.0 - 1.0)
        return max(0.1, raw_delay + jitter)

class CircuitBreaker:
    """
    Prevents hammering unreachable endpoints when connection drops.
    States: CLOSED (normal), OPEN (tripped/blackout), HALF_OPEN (probing link).
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 4, recovery_timeout: float = 15.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def record_success(self):
        """Resets breaker to CLOSED state upon successful connection."""
        self.failure_count = 0
        self.state = self.CLOSED

    def record_failure(self):
        """Increments failure count and trips circuit if threshold exceeded."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN

    def can_attempt(self) -> bool:
        """Returns True if connection probe is permitted."""
        if self.state == self.CLOSED:
            return True
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = self.HALF_OPEN
                return True
            return False
        if self.state == self.HALF_OPEN:
            return True
        return False
