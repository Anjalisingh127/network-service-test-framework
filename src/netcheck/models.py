"""Domain models used by the framework."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServiceConfig:
    """Validated input describing one TCP service check."""

    name: str
    host: str
    port: int
    timeout_seconds: float = 2.0
    request: str | None = None
    expected_response: str | None = None
