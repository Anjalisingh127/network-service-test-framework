"""Unit tests for configuration-driven check orchestration."""

from unittest.mock import MagicMock

import pytest

from netcheck.client import TCPClient
from netcheck.models import CheckStatus, ServiceCheckResult, ServiceConfig
from netcheck.runner import run_checks

pytestmark = pytest.mark.unit


def result_for(service: ServiceConfig) -> ServiceCheckResult:
    return ServiceCheckResult(
        service_name=service.name,
        host=service.host,
        port=service.port,
        status=CheckStatus.AVAILABLE,
        success=True,
        latency_ms=1.0,
    )


def test_routes_services_to_connectivity_or_response_checks() -> None:
    connectivity = ServiceConfig(name="port-check", host="localhost", port=8000)
    response = ServiceConfig(
        name="response-check",
        host="localhost",
        port=8001,
        request="PING",
        expected_response="PONG",
    )
    client = MagicMock(spec=TCPClient)
    client.check_connectivity.return_value = result_for(connectivity)
    client.check_response.return_value = result_for(response)

    results = run_checks([connectivity, response], client=client)

    assert [result.service_name for result in results] == [
        "port-check",
        "response-check",
    ]
    client.check_connectivity.assert_called_once_with(connectivity)
    client.check_response.assert_called_once_with(response)


def test_empty_service_input_returns_empty_results() -> None:
    client = MagicMock(spec=TCPClient)

    assert run_checks([], client=client) == []
    client.check_connectivity.assert_not_called()
    client.check_response.assert_not_called()
