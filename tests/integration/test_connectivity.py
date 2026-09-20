"""Integration tests for real local TCP connections."""

import pytest

from netcheck.client import TCPClient
from netcheck.models import CheckStatus, ServiceConfig

from ..fixtures.tcp_server import LocalTCPServer

pytestmark = pytest.mark.integration


def test_connects_to_available_local_service(local_tcp_server: LocalTCPServer) -> None:
    service = ServiceConfig(
        name="local-test-service",
        host=local_tcp_server.host,
        port=local_tcp_server.port,
        timeout_seconds=1,
    )

    result = TCPClient().check_connectivity(service)

    assert result.success is True
    assert result.status is CheckStatus.AVAILABLE
    assert result.service_name == "local-test-service"
    assert result.latency_ms >= 0


def test_validates_response_from_local_service(
    local_tcp_server: LocalTCPServer,
) -> None:
    service = ServiceConfig(
        name="local-response-service",
        host=local_tcp_server.host,
        port=local_tcp_server.port,
        timeout_seconds=1,
        request="PING",
        expected_response="PONG",
    )

    result = TCPClient().check_response(service)

    assert result.success is True
    assert result.status is CheckStatus.RESPONSE_MATCH
    assert result.expected_response == "PONG"
    assert result.actual_response == "PONG"
