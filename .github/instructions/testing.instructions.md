---
applyTo: 'tests/**/*.py'
---
# Testing Instructions

- Use Pytest and follow existing fixture and test organization patterns.
- Test expected behavior, invalid input, boundary cases and regressions.
- Keep tests isolated, deterministic and independent of execution order.
- Use FastAPI TestClient or an appropriate async client for API tests; isolate persistence and external services.
- Assert observable behavior and meaningful response details, not implementation internals.
- Run relevant tests using `python -m pytest`; report failures and coverage when configured. Never weaken tests to make them pass.