"""
IBVAP - Runtime Mode System
Controls whether the platform operates in production, demo, or test mode.
Production mode NEVER produces simulated/synthetic/fake outputs.
"""
import os
from enum import Enum
from typing import Optional


class IBVAPMode(str, Enum):
    PRODUCTION = "production"
    DEMO = "demo"
    TEST = "test"


_current_mode: Optional[IBVAPMode] = None


def get_mode() -> IBVAPMode:
    """Returns the current IBVAP operating mode."""
    global _current_mode
    if _current_mode is not None:
        return _current_mode

    mode_str = os.environ.get("IBVAP_MODE", "").lower().strip()
    if mode_str == "production":
        _current_mode = IBVAPMode.PRODUCTION
    elif mode_str == "test":
        _current_mode = IBVAPMode.TEST
    else:
        _current_mode = IBVAPMode.DEMO
    return _current_mode


def set_mode(mode: IBVAPMode) -> None:
    """Override the current mode (useful for testing)."""
    global _current_mode
    _current_mode = mode


def is_production() -> bool:
    """Returns True if running in production mode. No fake outputs allowed."""
    return get_mode() == IBVAPMode.PRODUCTION


def is_demo() -> bool:
    """Returns True if running in demo/evaluation mode. Controlled simulation allowed."""
    return get_mode() == IBVAPMode.DEMO


def is_test() -> bool:
    """Returns True if running in test mode. Deterministic fixtures/mocks allowed."""
    return get_mode() == IBVAPMode.TEST


def require_real_inference() -> bool:
    """Returns True if the current mode requires genuine AI inference (no synthetic fallbacks)."""
    return is_production()
