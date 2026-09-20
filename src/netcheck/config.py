"""Load and validate YAML service definitions."""

from pathlib import Path
from typing import Any

import yaml

from netcheck.exceptions import ConfigurationError
from netcheck.models import ServiceConfig


def load_services(path: str | Path) -> list[ServiceConfig]:
    """Return validated service definitions from a YAML file."""
    config_path = Path(path)
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigurationError(f"Cannot read configuration: {config_path}") from exc
    except yaml.YAMLError as exc:
        message = f"Invalid YAML in configuration: {config_path}"
        raise ConfigurationError(message) from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("services"), list):
        raise ConfigurationError("Configuration must contain a 'services' list")
    if not raw["services"]:
        raise ConfigurationError("The 'services' list cannot be empty")

    services = [
        _parse_service(item, index) for index, item in enumerate(raw["services"])
    ]
    names = [service.name for service in services]
    if len(names) != len(set(names)):
        raise ConfigurationError("Service names must be unique")
    return services


def _parse_service(item: Any, index: int) -> ServiceConfig:
    location = f"services[{index}]"
    if not isinstance(item, dict):
        raise ConfigurationError(f"{location} must be a mapping")

    name = _required_text(item, "name", location)
    host = _required_text(item, "host", location)
    port = item.get("port")
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ConfigurationError(f"{location}.port must be an integer from 1 to 65535")

    timeout = item.get("timeout_seconds", 2.0)
    valid_timeout = not isinstance(timeout, bool) and isinstance(timeout, (int, float))
    if not valid_timeout or timeout <= 0:
        raise ConfigurationError(f"{location}.timeout_seconds must be positive")

    request = _optional_text(item, "request", location)
    expected = _optional_text(item, "expected_response", location)
    if expected is not None and request is None:
        raise ConfigurationError(
            f"{location}.request is required when expected_response is provided"
        )

    return ServiceConfig(
        name=name,
        host=host,
        port=port,
        timeout_seconds=float(timeout),
        request=request,
        expected_response=expected,
    )


def _required_text(item: dict[str, Any], key: str, location: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{location}.{key} must be a non-empty string")
    return value.strip()


def _optional_text(item: dict[str, Any], key: str, location: str) -> str | None:
    value = item.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ConfigurationError(f"{location}.{key} must be a non-empty string")
    return value
