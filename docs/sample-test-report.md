# Sample Test Report

This evidence comes from the first complete GitHub Actions run after CI was
introduced.

| Field | Verified value |
| --- | --- |
| Commit | `66bddc4210c08dac6dcbd29fe8507d67acd6996d` |
| Workflow | CI |
| Trigger | Push to `main` |
| Environment | GitHub-hosted Ubuntu runner, Python 3.12 |
| Result | Success |
| Automated tests | 34 passed |
| Unit tests | 31 passed |
| Integration tests | 3 passed |
| Job duration | 13 seconds |
| Workflow duration | 16 seconds |
| Report artifact | `network-service-test-reports` |
| Artifact size | 13.4 KB |

The run completed Ruff linting, Ruff formatting verification, separate unit and
integration suites, full report generation, and artifact upload successfully.

[View the verified workflow run](https://github.com/Anjalisingh127/network-service-test-framework/actions/runs/35520638883)
