"""Demo hooks: narrow command guard, read-only lint and bounded final checks."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / '.venv' / 'bin' / 'python'
if not PYTHON.exists():
    PYTHON = ROOT / '.venv' / 'Scripts' / 'python.exe'


def run(args, timeout):
    if not PYTHON.exists():
        return False, 'Project virtual environment is missing.'
    try:
        result = subprocess.run([str(PYTHON), *args], cwd=ROOT,
                                capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, (result.stdout + result.stderr)[-1600:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, type(exc).__name__


def handle(mode, event):
    name = str(event.get('toolName', '')).lower()
    args = event.get('toolArgs', {})
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {'command': args}
    if not isinstance(args, dict):
        args = {}
    if mode == 'pre':
        command = str(args.get('command', ''))
        if name in {'bash', 'powershell', 'run_in_terminal', 'terminal', 'execute'}:
            patterns = [r'\bgit\s+reset\s+--hard\b', r'\bgit\s+clean\s+-[a-z]*f',
                        r'\bgit\s+push\s+[^\n;&|]*(?:--force(?:-with-lease)?\b|\s-f\b)',
                        r'\brm\s+-[a-z]*r[a-z]*f\b', r'\brm\s+-[a-z]*f[a-z]*r\b']
            if any(re.search(pattern, command, re.I) for pattern in patterns):
                return {'permissionDecision': 'deny', 'permissionDecisionReason':
                        'Demo guard: destructive command requires manual handling.'}
        return {}
    if mode == 'post':
        if name not in {'edit', 'create', 'str_replace_editor', 'apply_patch'}:
            return {}
        if not (ROOT / 'app').exists() and not (ROOT / 'tests').exists():
            return {}
        ok, detail = run(['-m', 'ruff', 'check', '.'], 20)
        return {} if ok else {'additionalContext': 'Ruff check failed or unavailable:\n' + detail}
    if mode == 'stop':
        # Only validate application work with a changed Python source/test file.
        # Include committed changes only via explicit validation by the orchestrator/CI.
        result = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all'],
                                cwd=ROOT, capture_output=True, text=True, timeout=5)
        if result.returncode or not any(re.search(r'(?:^|[ /])(?:app|tests)/.*\.py"?$', line)
                                        for line in result.stdout.splitlines()):
            return {}
        failures = []
        for args in [['-m','ruff','check','.'], ['-m','ruff','format','--check','.'],
                     ['-m','pytest','--cov=app','--cov-fail-under=80']]:
            ok, detail = run(args, 30)
            if not ok:
                failures.append(' '.join(args) + ': ' + detail)
        if failures:
            print('Quality checks failed; inspect results before PR.', file=sys.stderr)
            if not event.get('stop_hook_active'):
                return {'decision':'block','reason':'Quality checks failed. If approval or clarification is needed, report it rather than editing. Otherwise resolve in scope or report blockers. Do not commit or create PR.\n' + '\n'.join(failures)}
        return {}
    raise ValueError('Unknown hook mode')


if __name__ == '__main__':
    print(json.dumps(handle(sys.argv[1], json.load(sys.stdin))))
