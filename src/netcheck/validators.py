"""Reusable assertions for service-check results."""

from netcheck.models import CheckStatus, ServiceCheckResult


def assert_success(result: ServiceCheckResult) -> None:
    """Assert that a service check succeeded with useful failure evidence."""
    assert result.success, _diagnostic(result)


def assert_status(result: ServiceCheckResult, expected: CheckStatus) -> None:
    """Assert the normalized outcome of a service check."""
    assert result.status is expected, (
        f"Expected status {expected.value!r}, got {result.status.value!r}; "
        f"{_diagnostic(result)}"
    )


def assert_response_matches(result: ServiceCheckResult) -> None:
    """Assert exact equality between the expected and actual response."""
    assert result.expected_response is not None, "No expected response was configured"
    assert result.actual_response == result.expected_response, _diagnostic(result)


def _diagnostic(result: ServiceCheckResult) -> str:
    return (
        f"service={result.service_name!r}, endpoint={result.host}:{result.port}, "
        f"status={result.status.value!r}, latency_ms={result.latency_ms}, "
        f"expected={result.expected_response!r}, actual={result.actual_response!r}, "
        f"error={result.error!r}"
    )
