"""Structured logging with request correlation.

JSON lines by default so an edge/central deployment can ship logs without a
parser. A ``request_id`` context variable threads through handlers, services
and the error envelope.
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from typing import Any

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
actor_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("actor", default=None)

_RESERVED = frozenset(
    {
        "args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName",
        "levelname", "levelno", "lineno", "module", "msecs", "message", "msg", "name",
        "pathname", "process", "processName", "relativeCreated", "stack_info",
        "thread", "threadName", "taskName",
    }
)

# Substrings that must never reach a log line in cleartext.
_SENSITIVE_KEYS = ("password", "secret", "token", "credential", "authorization", "api_key")


def _scrub(key: str, value: Any) -> Any:
    lowered = key.lower()
    if any(marker in lowered for marker in _SENSITIVE_KEYS):
        return "***"
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if rid := request_id_var.get():
            payload["request_id"] = rid
        if actor := actor_var.get():
            payload["actor"] = actor
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = _scrub(key, value)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(*, level: str = "INFO", json_output: bool = True) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter()
        if json_output
        else logging.Formatter("%(asctime)s %(levelname)-8s %(name)s :: %(message)s")
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # uvicorn duplicates access logs through its own handlers.
    for noisy in ("uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy).handlers.clear()
        logging.getLogger(noisy).propagate = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
