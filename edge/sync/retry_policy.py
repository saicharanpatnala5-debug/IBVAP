"""
IBVAP - Jittered Exponential Backoff Retry Policy
Prevents thundering herd on forward border base stations after network recovery.
"""

import time
import random

class ExponentialBackoffRetry:
    def __init__(self, initial_delay: float = 1.0, max_delay: float = 60.0, factor: float = 2.0):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor
        self.attempts = 0

    def get_delay(self) -> float:
        delay = min(self.initial_delay * (self.factor ** self.attempts), self.max_delay)
        jitter = random.uniform(0.8, 1.2) # Jitter factor +/- 20%
        return delay * jitter

    def record_failure(self):
        self.attempts += 1

    def record_success(self):
        self.attempts = 0
