"""Structured logging configuration for test evidence and diagnostics."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

LOG_FIELDS = (
    "service_name",
    "host",
    "port",
    "status",
    "success",
    "latency_ms",
    "error",
    "expected_response",
    "actual_response",
)


class JsonFormatter(logging.Formatter):
    """Render one log event as a stable JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in LOG_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(
    log_path: str | Path | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure the framework logger with console and optional file output."""
    logger = logging.getLogger("netcheck")
    logger.setLevel(level)
    logger.propagate = False

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    formatter = JsonFormatter()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_path is not None:
        output_path = Path(log_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(output_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
