---
applyTo: '**/*.py'
---
# Python Instructions

- Target the project's configured Python version.
- Use type hints for public interfaces and docstrings for non-obvious behavior.
- Prefer small functions, meaningful names, absolute imports and standard-library utilities.
- Use context managers for resource cleanup; catch specific exceptions and preserve exception causes.
- Avoid mutable default arguments, wildcard imports and unnecessary global state.
- Use async for non-blocking I/O; never block the event loop.
- Follow Ruff configuration in `pyproject.toml`. When configured, run `python -m ruff check .` and `python -m ruff format --check .`.
