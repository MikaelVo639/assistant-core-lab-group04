"""Configure structured application logs separately from CLI answers."""

import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Serialize the approved metadata fields without exception payloads."""

    def format(self, record: logging.LogRecord) -> str:
        data = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        for key in ("intent", "latency_ms", "session", "degraded"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Install one JSON stderr handler, replacing only handlers owned by this setup."""
    logger = logging.getLogger("assistant_core")
    for previous in logger.handlers[:]:
        if previous.name == "assistant_core.json":
            logger.removeHandler(previous)
            previous.close()
    handler = logging.StreamHandler(sys.stderr)
    handler.name = "assistant_core.json"
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
