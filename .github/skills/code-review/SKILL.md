---
name: code-review
description: Independently review a proposed code change against requirements, repository standards, security and test evidence before pull request approval.
---

# Code review

1. Inspect the actual diff, affected code, acceptance criteria and validation evidence.
2. Check correctness, regressions, API compatibility, access control, input validation, secret handling and error paths as applicable.
3. Review maintainability, concurrency and resource handling; check tests cover important behavior and failure cases.
4. Report actionable findings with severity, file/line evidence, impact and suggested correction. Separate blockers from optional improvements.
5. Return PASS only when no blocking findings or missing required checks remain; otherwise return CHANGES_REQUIRED. Do not edit files or approve/merge a PR.
