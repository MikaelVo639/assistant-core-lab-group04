import json
import logging
import sys

# Only these fields are emitted, so keys and full user messages cannot leak into logs.
_EXTRA = ("intent", "degraded", "chars")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        out = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        out.update({k: getattr(record, k) for k in _EXTRA if hasattr(record, k)})
        return json.dumps(out)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
