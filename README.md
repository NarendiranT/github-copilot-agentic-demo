# github-copilot-agentic-demo

End-to-end agentic AI-driven SDLC using GitHub Copilot.

## Python environment

This repository uses a local virtual environment named `.venv`, created with Python 3.12 or newer. Application dependencies are not installed yet.

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

