"""Configure structured application logs separately from CLI answers."""

import json
import logging
import sys

LOGGER_NAME = "assistant_core"
HANDLER_NAME = "assistant_core.json"
LOG_FIELDS = ("intent", "latency_ms", "session", "degraded")


class JsonFormatter(logging.Formatter):
    """Serialize the standard record fields and approved request metadata."""

    def format(self, record: logging.LogRecord) -> str:
        data = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in LOG_FIELDS:
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Install one JSON stderr handler on the application logger.

    Repeated calls replace only the handler installed by this function. Other
    application or test handlers are left untouched.
    """
    logger = logging.getLogger(LOGGER_NAME)
    for previous in logger.handlers[:]:
        if previous.name == HANDLER_NAME:
            logger.removeHandler(previous)
            previous.close()

    handler = logging.StreamHandler(sys.stderr)
    handler.name = HANDLER_NAME
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False
