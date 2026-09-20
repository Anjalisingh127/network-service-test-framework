"""Unit tests for normalized TCP connectivity outcomes."""

import socket
from unittest.mock import MagicMock

import pytest

from netcheck.client import TCPClient
from netcheck.models import CheckStatus, ServiceConfig

pytestmark = pytest.mark.unit


@pytest.fixture
def service() -> ServiceConfig:
    return ServiceConfig(name="example", host="127.0.0.1", port=9001)


def test_reports_available_service(
    monkeypatch: pytest.MonkeyPatch, service: ServiceConfig
) -> None:
    connection = MagicMock()
    create_connection = MagicMock(return_value=connection)
    monkeypatch.setattr(socket, "create_connection", create_connection)
    clock = iter([5.0, 5.012]).__next__

    result = TCPClient(clock=clock).check_connectivity(service)

    assert result.success is True
    assert result.host == "127.0.0.1"
    assert result.port == 9001
    assert result.status is CheckStatus.AVAILABLE
    assert result.latency_ms == 12.0
    assert result.error is None
    connection.__exit__.assert_called_once()
    create_connection.assert_called_once_with(("127.0.0.1", 9001), timeout=2.0)


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (ConnectionRefusedError("connection refused"), CheckStatus.CONNECTION_REFUSED),
        (TimeoutError("connection timed out"), CheckStatus.TIMED_OUT),
        (OSError("network unreachable"), CheckStatus.NETWORK_ERROR),
    ],
)
def test_normalizes_connection_failures(
    monkeypatch: pytest.MonkeyPatch,
    service: ServiceConfig,
    exception: OSError,
    expected_status: CheckStatus,
) -> None:
    monkeypatch.setattr(socket, "create_connection", MagicMock(side_effect=exception))
    clock = iter([10.0, 10.025]).__next__

    result = TCPClient(clock=clock).check_connectivity(service)

    assert result.success is False
    assert result.status is expected_status
    assert result.latency_ms == 25.0
    assert result.error == str(exception)


def test_never_reports_negative_latency(
    monkeypatch: pytest.MonkeyPatch, service: ServiceConfig
) -> None:
    monkeypatch.setattr(
        socket,
        "create_connection",
        MagicMock(side_effect=TimeoutError("timed out")),
    )
    clock = iter([10.0, 9.0]).__next__

    result = TCPClient(clock=clock).check_connectivity(service)

    assert result.latency_ms == 0.0
