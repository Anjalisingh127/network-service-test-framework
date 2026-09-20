"""TCP connectivity and availability checks."""

import socket
from collections.abc import Callable
from time import perf_counter

from netcheck.models import CheckStatus, ServiceCheckResult, ServiceConfig


class TCPClient:
    """Check configured TCP endpoints and return structured outcomes."""

    def __init__(self, clock: Callable[[], float] = perf_counter) -> None:
        self._clock = clock

    def check_connectivity(self, service: ServiceConfig) -> ServiceCheckResult:
        """Attempt one TCP connection within the configured timeout."""
        started_at = self._clock()
        try:
            with socket.create_connection(
                (service.host, service.port), timeout=service.timeout_seconds
            ):
                return self._result(
                    service=service,
                    started_at=started_at,
                    status=CheckStatus.AVAILABLE,
                    success=True,
                )
        except ConnectionRefusedError as exc:
            return self._result(
                service,
                started_at,
                CheckStatus.CONNECTION_REFUSED,
                error=str(exc),
            )
        except TimeoutError as exc:
            return self._result(
                service,
                started_at,
                CheckStatus.TIMED_OUT,
                error=str(exc),
            )
        except OSError as exc:
            return self._result(
                service,
                started_at,
                CheckStatus.NETWORK_ERROR,
                error=str(exc),
            )

    def _result(
        self,
        service: ServiceConfig,
        started_at: float,
        status: CheckStatus,
        success: bool = False,
        error: str | None = None,
    ) -> ServiceCheckResult:
        elapsed_ms = max(0.0, (self._clock() - started_at) * 1000)
        return ServiceCheckResult(
            service_name=service.name,
            status=status,
            success=success,
            latency_ms=round(elapsed_ms, 3),
            error=error,
        )
