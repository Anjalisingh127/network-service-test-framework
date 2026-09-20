"""Unit tests for YAML configuration loading."""

from pathlib import Path

import pytest

from netcheck.config import load_services
from netcheck.exceptions import ConfigurationError

pytestmark = pytest.mark.unit


def write_config(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "services.yaml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def test_loads_valid_service_configuration(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
services:
  - name: echo
    host: 127.0.0.1
    port: 9001
    timeout_seconds: 1.5
    request: PING
    expected_response: PONG
""",
    )

    services = load_services(path)

    assert len(services) == 1
    assert services[0].name == "echo"
    assert services[0].port == 9001
    assert services[0].timeout_seconds == 1.5
    assert services[0].expected_response == "PONG"


def test_uses_default_timeout(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        "services:\n  - name: echo\n    host: localhost\n    port: 9001\n",
    )

    assert load_services(path)[0].timeout_seconds == 2.0


@pytest.mark.parametrize("port", [0, 65536, "9001", True])
def test_rejects_invalid_port(tmp_path: Path, port: object) -> None:
    path = write_config(
        tmp_path,
        f"services:\n  - name: echo\n    host: localhost\n    port: {port!r}\n",
    )

    with pytest.raises(ConfigurationError, match="port"):
        load_services(path)


def test_rejects_empty_service_list(tmp_path: Path) -> None:
    path = write_config(tmp_path, "services: []\n")

    with pytest.raises(ConfigurationError, match="cannot be empty"):
        load_services(path)


def test_rejects_duplicate_names(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
services:
  - name: duplicate
    host: localhost
    port: 9001
  - name: duplicate
    host: localhost
    port: 9002
""",
    )

    with pytest.raises(ConfigurationError, match="unique"):
        load_services(path)


def test_requires_request_for_expected_response(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
services:
  - name: echo
    host: localhost
    port: 9001
    expected_response: PONG
""",
    )

    with pytest.raises(ConfigurationError, match="request is required"):
        load_services(path)


def test_reports_missing_file_as_configuration_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="Cannot read configuration"):
        load_services(tmp_path / "missing.yaml")
