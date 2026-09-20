"""Domain models used by the framework."""

from dataclasses import dataclass
from enum import StrEnum


class CheckStatus(StrEnum):
    """Normalized outcomes produced by a service check."""

    AVAILABLE = "available"
    CONNECTION_REFUSED = "connection_refused"
    TIMED_OUT = "timed_out"
    NETWORK_ERROR = "network_error"


@dataclass(frozen=True, slots=True)
class ServiceConfig:
    """Validated input describing one TCP service check."""

    name: str
    host: str
    port: int
    timeout_seconds: float = 2.0
    request: str | None = None
    expected_response: str | None = None


@dataclass(frozen=True, slots=True)
class ServiceCheckResult:
    """Structured evidence captured while checking a TCP service."""

    service_name: str
    status: CheckStatus
    success: bool
    latency_ms: float
    error: str | None = None
