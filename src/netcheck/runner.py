"""Orchestrate configured TCP service checks."""

from collections.abc import Iterable
from pathlib import Path

from netcheck.client import TCPClient
from netcheck.config import load_services
from netcheck.models import ServiceCheckResult, ServiceConfig


def run_checks(
    services: Iterable[ServiceConfig],
    client: TCPClient | None = None,
) -> list[ServiceCheckResult]:
    """Run the correct check for each service in input order."""
    tcp_client = client or TCPClient()
    return [
        tcp_client.check_response(service)
        if service.request is not None
        else tcp_client.check_connectivity(service)
        for service in services
    ]


def run_from_config(
    path: str | Path,
    client: TCPClient | None = None,
) -> list[ServiceCheckResult]:
    """Load YAML test data and execute all configured service checks."""
    return run_checks(load_services(path), client=client)
