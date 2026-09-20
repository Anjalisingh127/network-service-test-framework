# Testing Strategy

## Test layers

### Unit tests

The unit suite validates configuration rules, status normalization, response
matching, latency calculation, JSON logging, orchestration, and reusable
assertions. Network outcomes such as refusal and timeout are injected so the
tests remain fast and repeatable.

### Integration tests

The integration suite starts a local TCP server on `127.0.0.1` using an
operating-system-assigned port. It verifies:

1. A real TCP connection can be established.
2. A `PING` request receives and validates a `PONG` response.
3. A YAML service definition drives the complete load-to-assert workflow.

The fixture is stopped after each test and does not use a fixed shared port.

## Commands

```powershell
python -m pytest -m unit -v
python -m pytest -m integration -v
python -m pytest -v
python -m ruff check .
python -m ruff format --check .
```

## Reports

`pytest-html` creates a self-contained report for human review.
`pytest-json-report` creates machine-readable evidence for automation and later
analysis. Both are generated under `reports/` and uploaded by GitHub Actions.

## CI gates

The pipeline must complete these gates on Python 3.12:

1. Install the project and development dependencies.
2. Run Ruff lint checks.
3. Verify Ruff formatting.
4. Run the unit suite.
5. Run the integration suite.
6. Generate HTML and JSON reports.
7. Upload the report artifact, including when a test fails.
