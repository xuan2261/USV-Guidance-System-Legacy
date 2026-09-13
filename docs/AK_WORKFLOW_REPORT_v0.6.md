# AK workflow report — v0.6

Workflow contract applied: `ak-research → ak-brainstorm → ak-plan → ak-cook → ak-debug/audit → ak-test → ak-code-review → review`.

## Research
Current GitHub Actions runner, Docker execution, artifact-retention and current GitHub-owned action versions were checked against official GitHub documentation/repositories.

## Brainstorm decision
Move machine-dependent qualification into reproducible GitHub-hosted CI without bypassing legacy Q10 or Phase 1.1 parity guards.

## Plan / cook
Added three workflows: static, Phase 1.1 ROS 2, and legacy ROS 1. Heavy jobs are manual; evidence upload is unconditional.

## Debug / audit
Security controls: read-only token, no secrets, no `pull_request_target`, no privileged/network/device mounts, pinned action SHAs, no persisted checkout credentials. CI bind mounts use root only inside disposable qualification containers to avoid GitHub-runner UID mismatch; the host runner remains an ephemeral VM.

## Test / review
YAML parse, policy assertions, Bash/Python/XML checks, existing model/geodesy differential tests, and ZIP integrity are required before release. GitHub-hosted runtime execution remains external evidence until workflows are actually run in a repository.
