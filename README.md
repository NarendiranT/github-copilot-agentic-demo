# github-copilot-agentic-demo

End-to-end agentic AI-driven SDLC using GitHub Copilot.

## Python environment

This repository uses a local virtual environment named `.venv`, created with Python 3.12 or newer. Install application and development dependencies into that environment; do not create a second one.

Detected on setup:

- Operating system: macOS (Darwin arm64)
- Interpreter used: Python 3.12.7 (`/usr/local/bin/python3.12`)
- Virtual environment: `.venv`
- VS Code interpreter: `${workspaceFolder}/.venv/bin/python`

### Create the environment

From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
```

On Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
```

Use another `python3.x` binary only if it is Python 3.12 or newer.

### Activate the environment

macOS and Linux:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```cmd
.venv\Scripts\activate.bat
```

Deactivate with `deactivate`.

### VS Code

The workspace is configured to use the virtual environment as the Python interpreter in [.vscode/settings.json](.vscode/settings.json). Open the repository folder in VS Code and select the interpreter at `.venv/bin/python` if it is not selected automatically (Command Palette: **Python: Select Interpreter**).

New integrated terminals should activate `.venv` when the Python extension is installed.

### Verify

```bash
.venv/bin/python -c "import sys; assert sys.version_info >= (3, 12); print(sys.executable); print(sys.version)"
.venv/bin/python -m pip --version
```

`.venv`, Python cache files (`__pycache__/`, `*.pyc`), and environment secret files (including `.env`) are listed in [.gitignore](.gitignore) and should not be committed.

## Dependencies

Application and development dependencies are declared separately in [pyproject.toml](pyproject.toml). Requires Python 3.12 or newer and the existing `.venv`. The application code lives in the `app` package and is run from the repository root (see [Run the application](#run-the-application)).

Application:

- FastAPI
- Uvicorn
- SQLAlchemy with the `asyncio` extra, so async engines can use aiosqlite
- aiosqlite
- Pydantic Settings

Development (`dev` extra):

- Ruff
- Pytest
- Pytest-asyncio
- Pytest-cov
- HTTPX

Upgrade pip before installing, as shown under [Create the environment](#create-the-environment).

### Install application dependencies

macOS and Linux:

```bash
.venv/bin/python -m pip install -e .
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\python -m pip install -e .
```

### Install development dependencies

This also installs the application dependencies.

macOS and Linux:

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

### Validate

macOS and Linux:

```bash
.venv/bin/python -m pip check
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m pytest
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\python -m pip check
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m pytest
```

Ruff is configured for linting, formatting, and import sorting (the `I` / isort rule set). Pytest is configured for asynchronous tests (`asyncio_mode = "auto"`). The coverage target is 80% (`--cov-fail-under=80` and `[tool.coverage.report] fail_under`).

`pytest` runs the suite in `tests/` and enforces the 80% coverage gate. `pip check`, `ruff check .`, and `ruff format --check .` pass. Ruff excludes `.github/hooks` (`extend-exclude` in `pyproject.toml`).

## Run the application

Prerequisite: the existing `.venv` with the development dependencies installed (see [Install development dependencies](#install-development-dependencies)).

From the repository root, start the server.

macOS and Linux:

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Check the health endpoint (no authentication required):

```bash
curl http://127.0.0.1:8000/health
```

Expected response (HTTP 200): `{"status":"healthy"}`

Interactive API documentation (Swagger UI) is available at <http://127.0.0.1:8000/docs>.

### Blog API

Blogs have `id`, `title`, `content`, `created_at` and `updated_at` (UTC). `title` and `content` are required and must not be blank; surrounding whitespace is trimmed.

| Method and path | Success | Notes |
| --- | --- | --- |
| `POST /blogs` | 201 | Body: `title`, `content` |
| `GET /blogs` | 200 | Ordered by `id` |
| `GET /blogs/{id}` | 200 | |
| `PATCH /blogs/{id}` | 200 | Updates only the supplied fields; body must not be empty |
| `DELETE /blogs/{id}` | 204 | Empty body |

A missing blog returns 404; invalid input or ids return 422.

Blogs are stored in SQLite and persist across restarts. Set `DATABASE_URL` to change the database (default `sqlite+aiosqlite:///./db.sqlite3`, ignored by Git).

### Verification

Checked on Python 3.12.3 in `.venv` after `pip install -e ".[dev]"`. This is a snapshot from the initial environment setup, before any application code existed, so its "no tests present" and `0.00%` coverage results are historical:

- `pip check` reported no broken requirements.
- Resolved direct dependencies: FastAPI 0.165.0, Uvicorn 0.54.0, SQLAlchemy 2.1.9 (asyncio extra, which installed greenlet 3.5.6), aiosqlite 0.22.1, Pydantic Settings 2.16.3, Ruff 0.17.6, Pytest 9.2.0, Pytest-asyncio 1.5.0, Pytest-cov 7.1.0, HTTPX 0.28.1.
- Imports succeeded for those packages. An in-memory `sqlite+aiosqlite` async connection returned `1`. Pydantic Settings loaded a default value.
- `ruff check .` and `ruff format --check .` passed.
- Pytest loaded `pyproject.toml` with `asyncio_mode=auto`, function-scoped asyncio loops, and the 80% coverage gate. With no tests present, the run failed that gate (`total coverage: 0.00%`) rather than failing configuration parsing.

Starlette's `TestClient` still imports HTTPX, and warns that `httpx2` is preferred. HTTPX remains the configured development HTTP client, as specified.

