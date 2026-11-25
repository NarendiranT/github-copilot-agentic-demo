Repository Instructions

## Project
- Backend: FastAPI. Use the existing Python `.venv`.
- Inspect relevant code, tests and configuration; follow existing patterns and applicable scoped instructions.

## Engineering
- Prefer simple, maintainable, secure and testable solutions. Reuse existing components.
- Keep changes focused; preserve user edits, existing behavior and public contracts.
- Validate untrusted input, protect secrets and personal data, and apply least privilege.
- Handle errors explicitly; never weaken security controls or bypass validation.
- Add or update relevant tests and documentation. Run configured quality checks and review the final diff.

## Agent Workflow and Safety
- Clarify material ambiguities and obtain approval for complex or high-impact plans.
- Perform routine in-scope work autonomously within tool permissions.
- Obtain approval for dependency changes, breaking contracts, architecture/security changes, destructive operations, external side effects, Git commits/pushes/merges and deployments.
- Stop and report blockers after two unsuccessful correction attempts.
- Report changes, actual validation results, unverified checks and remaining risks.