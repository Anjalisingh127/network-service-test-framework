# Network Service Test Automation Framework

A configurable Python and pytest framework for deterministic TCP service validation.

Development is in progress. The first milestone implements validated YAML test data
and unit-tested domain models. Connectivity, response validation, diagnostics,
reporting, and CI are added in subsequent validated milestones.

## Local setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -m unit -v
ruff check .
```
