"""TCP connectivity and availability checks."""

import socket
from collections.abc import Callable
from logging import Logger, getLogger
from time import perf_counter

from netcheck.models import CheckStatus, ServiceCheckResult, ServiceConfig


class TCPClient:
    """Check configured TCP endpoints and return structured outcomes."""

    def __init__(
        self,
        clock: Callable[[], float] = perf_counter,
        logger: Logger | None = None,
    ) -> None:
        self._clock = clock
        self._logger = logger or getLogger("netcheck")

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

    def check_response(self, service: ServiceConfig) -> ServiceCheckResult:
        """Send the configured request and validate the received response."""
        if service.request is None:
            raise ValueError("A request is required for response validation")

        started_at = self._clock()
        try:
            with socket.create_connection(
                (service.host, service.port), timeout=service.timeout_seconds
            ) as connection:
                connection.settimeout(service.timeout_seconds)
                connection.sendall(service.request.encode("utf-8"))
                response_bytes = connection.recv(65_536)
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

        actual_response = response_bytes.decode("utf-8", errors="replace")
        if not response_bytes:
            return self._result(
                service,
                started_at,
                CheckStatus.EMPTY_RESPONSE,
                actual_response=actual_response,
            )

        if service.expected_response is None:
            return self._result(
                service,
                started_at,
                CheckStatus.RESPONSE_RECEIVED,
                success=True,
                actual_response=actual_response,
            )

        matches = actual_response == service.expected_response
        status = (
            CheckStatus.RESPONSE_MATCH if matches else CheckStatus.RESPONSE_MISMATCH
        )
        return self._result(
            service,
            started_at,
            status,
            success=matches,
            actual_response=actual_response,
        )

    def _result(
        self,
        service: ServiceConfig,
        started_at: float,
        status: CheckStatus,
        success: bool = False,
        error: str | None = None,
        actual_response: str | None = None,
    ) -> ServiceCheckResult:
        elapsed_ms = max(0.0, (self._clock() - started_at) * 1000)
        result = ServiceCheckResult(
            service_name=service.name,
            host=service.host,
            port=service.port,
            status=status,
            success=success,
            latency_ms=round(elapsed_ms, 3),
            error=error,
            expected_response=service.expected_response,
            actual_response=actual_response,
        )
        self._log_result(result)
        return result

    def _log_result(self, result: ServiceCheckResult) -> None:
        log = self._logger.info if result.success else self._logger.warning
        log(
            "TCP service check completed",
            extra={
                "service_name": result.service_name,
                "host": result.host,
                "port": result.port,
                "status": result.status.value,
                "success": result.success,
                "latency_ms": result.latency_ms,
                "error": result.error,
                "expected_response": result.expected_response,
                "actual_response": result.actual_response,
            },
        )
