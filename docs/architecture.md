# Architecture

## Design goal

The framework separates test data, network execution, result validation, and
reporting. A new TCP endpoint can be tested by changing YAML instead of rewriting
socket code or duplicating assertions.

## Data flow

1. `config.py` reads YAML and validates required fields, types, ranges, and
   service-name uniqueness.
2. `models.py` represents immutable service definitions and structured results.
3. `runner.py` selects connectivity or request/response validation for each
   configured service.
4. `client.py` opens the TCP connection, applies timeouts, sends optional data,
   receives a response, measures latency, and normalizes failures.
5. `validators.py` provides reusable assertions with endpoint and response
   evidence in failure messages.
6. `logging_config.py` writes machine-readable JSON diagnostics.
7. pytest produces console, HTML, and JSON test results locally and in CI.

## Modules

| Module | Responsibility |
| --- | --- |
| `config` | Load and validate YAML test data |
| `models` | Immutable configuration and result objects |
| `client` | TCP connectivity and response execution |
| `runner` | Orchestrate checks in configuration order |
| `validators` | Reusable result assertions |
| `logging_config` | JSON-lines console and file logging |
| `exceptions` | Framework-specific configuration errors |

## Failure model

Network exceptions are translated into stable statuses:

- `connection_refused`
- `timed_out`
- `network_error`
- `response_mismatch`
- `empty_response`

Results retain the service name, host, port, latency, error message, and expected
and actual response where applicable. This makes a failed check diagnosable from
the report without reproducing it first.

## Reliability decisions

- Integration tests use `127.0.0.1` and an operating-system-assigned port.
- Tests never rely on Google, DNS, a public API, or an internet connection.
- Timeout and operating-system failures are covered with controlled unit tests.
- `perf_counter` measures elapsed time without depending on wall-clock changes.
- Generated reports and runtime logs are excluded from source control.
