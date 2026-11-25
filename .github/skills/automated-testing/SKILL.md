---
name: automated-testing
description: Design and run Pytest tests for changed Python and FastAPI behavior; use to verify acceptance criteria, regressions and coverage.
---

# Automated testing

1. Map acceptance criteria to positive, negative, boundary and regression tests.
2. Inspect existing fixtures and test conventions; isolate database state and external services using appropriate test doubles.
3. Add or update test files only. Do not change production behavior to make a test pass.
4. Run focused tests then the configured full suite and coverage checks using the project environment. Apply the configured coverage threshold (80% if configured).
5. Report requirement-to-test mapping, commands, pass/fail counts, coverage and failures. Send production defects to Developer; distinguish unrun checks from passes.
