"""End-to-end integration test for the YAML-driven service workflow."""

from pathlib import Path

import pytest

from netcheck.models import CheckStatus
from netcheck.runner import run_from_config
from netcheck.validators import assert_response_matches, assert_success

from ..fixtures.tcp_server import LocalTCPServer

pytestmark = pytest.mark.integration


def test_runs_yaml_service_check_against_local_server(
    local_tcp_server: LocalTCPServer,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "services.yaml"
    config_path.write_text(
        f"""
services:
  - name: local-echo
    host: {local_tcp_server.host}
    port: {local_tcp_server.port}
    timeout_seconds: 1
    request: PING
    expected_response: PONG
""",
        encoding="utf-8",
    )

    results = run_from_config(config_path)

    assert len(results) == 1
    assert results[0].status is CheckStatus.RESPONSE_MATCH
    assert_success(results[0])
    assert_response_matches(results[0])
