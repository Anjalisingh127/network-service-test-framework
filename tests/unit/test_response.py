"""Unit tests for request and expected-response validation."""

import socket
from unittest.mock import MagicMock

import pytest

from netcheck.client import TCPClient
from netcheck.models import CheckStatus, ServiceConfig

pytestmark = pytest.mark.unit


def make_service(expected: str | None = "PONG") -> ServiceConfig:
    return ServiceConfig(
        name="echo",
        host="127.0.0.1",
        port=9001,
        request="PING",
        expected_response=expected,
    )


def configure_connection(monkeypatch: pytest.MonkeyPatch, response: bytes) -> MagicMock:
    connection = MagicMock()
    connection.recv.return_value = response
    context = MagicMock()
    context.__enter__.return_value = connection
    monkeypatch.setattr(socket, "create_connection", MagicMock(return_value=context))
    return connection


def test_sends_request_and_records_matching_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = configure_connection(monkeypatch, b"PONG")

    result = TCPClient().check_response(make_service())

    connection.sendall.assert_called_once_with(b"PING")
    connection.settimeout.assert_called_once_with(2.0)
    assert result.status is CheckStatus.RESPONSE_MATCH
    assert result.success is True
    assert result.expected_response == "PONG"
    assert result.actual_response == "PONG"


def test_records_expected_and_actual_on_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_connection(monkeypatch, b"ERROR")

    result = TCPClient().check_response(make_service())

    assert result.status is CheckStatus.RESPONSE_MISMATCH
    assert result.success is False
    assert result.expected_response == "PONG"
    assert result.actual_response == "ERROR"


def test_accepts_nonempty_response_when_no_expected_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_connection(monkeypatch, b"service-ready")

    result = TCPClient().check_response(make_service(expected=None))

    assert result.status is CheckStatus.RESPONSE_RECEIVED
    assert result.success is True
    assert result.actual_response == "service-ready"


def test_reports_empty_response(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_connection(monkeypatch, b"")

    result = TCPClient().check_response(make_service())

    assert result.status is CheckStatus.EMPTY_RESPONSE
    assert result.success is False
    assert result.actual_response == ""


def test_reports_timeout_while_waiting_for_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = configure_connection(monkeypatch, b"unused")
    connection.recv.side_effect = TimeoutError("receive timed out")

    result = TCPClient().check_response(make_service())

    assert result.status is CheckStatus.TIMED_OUT
    assert result.success is False
    assert result.error == "receive timed out"


def test_requires_request_before_response_validation() -> None:
    service = ServiceConfig(name="no-request", host="localhost", port=9001)

    with pytest.raises(ValueError, match="request is required"):
        TCPClient().check_response(service)


def test_preserves_undecodable_response_as_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_connection(monkeypatch, b"\xff")

    result = TCPClient().check_response(make_service())

    assert result.status is CheckStatus.RESPONSE_MISMATCH
    assert result.actual_response == "\ufffd"
