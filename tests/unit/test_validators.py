"""Unit tests for reusable result assertions."""

import pytest

from netcheck.models import CheckStatus, ServiceCheckResult
from netcheck.validators import assert_response_matches, assert_status, assert_success

pytestmark = pytest.mark.unit


def make_result(
    *,
    status: CheckStatus = CheckStatus.RESPONSE_MATCH,
    success: bool = True,
    expected: str | None = "PONG",
    actual: str | None = "PONG",
) -> ServiceCheckResult:
    return ServiceCheckResult(
        service_name="echo",
        host="127.0.0.1",
        port=9001,
        status=status,
        success=success,
        latency_ms=2.5,
        expected_response=expected,
        actual_response=actual,
    )


def test_successful_result_passes_all_assertions() -> None:
    result = make_result()

    assert_success(result)
    assert_status(result, CheckStatus.RESPONSE_MATCH)
    assert_response_matches(result)


def test_failed_assertion_contains_diagnostic_evidence() -> None:
    result = make_result(
        status=CheckStatus.RESPONSE_MISMATCH,
        success=False,
        actual="ERROR",
    )

    with pytest.raises(AssertionError) as error:
        assert_success(result)

    message = str(error.value)
    assert "endpoint=127.0.0.1:9001" in message
    assert "expected='PONG'" in message
    assert "actual='ERROR'" in message


def test_status_assertion_reports_expected_and_actual_status() -> None:
    result = make_result(status=CheckStatus.TIMED_OUT, success=False)

    with pytest.raises(
        AssertionError, match="Expected status 'available', got 'timed_out'"
    ):
        assert_status(result, CheckStatus.AVAILABLE)


def test_response_assertion_requires_expected_value() -> None:
    result = make_result(expected=None, actual="PONG")

    with pytest.raises(AssertionError, match="No expected response"):
        assert_response_matches(result)
