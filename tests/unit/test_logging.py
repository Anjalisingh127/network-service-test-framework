"""Unit tests for structured diagnostic logging."""

import json
import logging
import socket
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from netcheck.client import TCPClient
from netcheck.logging_config import JsonFormatter, configure_logging
from netcheck.models import ServiceConfig

pytestmark = pytest.mark.unit


def test_json_formatter_emits_machine_readable_fields() -> None:
    record = logging.LogRecord(
        name="netcheck",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="TCP service check completed",
        args=(),
        exc_info=None,
    )
    record.service_name = "database"
    record.status = "timed_out"
    record.latency_ms = 1000.0

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "WARNING"
    assert payload["service_name"] == "database"
    assert payload["status"] == "timed_out"
    assert payload["latency_ms"] == 1000.0
    assert "timestamp" in payload


def test_client_writes_failure_diagnostics_to_json_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        socket,
        "create_connection",
        MagicMock(side_effect=ConnectionRefusedError("actively refused")),
    )
    log_path = tmp_path / "netcheck.jsonl"
    logger = configure_logging(log_path)
    service = ServiceConfig(name="api", host="127.0.0.1", port=65530)

    result = TCPClient(logger=logger).check_connectivity(service)
    for handler in logger.handlers:
        handler.flush()
    payload = json.loads(log_path.read_text(encoding="utf-8").strip())

    assert result.success is False
    assert payload["service_name"] == "api"
    assert payload["host"] == "127.0.0.1"
    assert payload["port"] == 65530
    assert payload["status"] == "connection_refused"
    assert payload["success"] is False
    assert payload["error"] == "actively refused"


def test_reconfiguration_does_not_duplicate_handlers(tmp_path: Path) -> None:
    logger = configure_logging(tmp_path / "first.jsonl")
    logger = configure_logging(tmp_path / "second.jsonl")

    assert len(logger.handlers) == 2
