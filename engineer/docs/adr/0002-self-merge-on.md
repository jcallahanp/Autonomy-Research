# ADR 0002: Self-merge on from day one under GitHub Pro

Status: accepted 2026-10-16

## Context
- R16 asks the engineer to merge routine changes itself (blueprint requirements-trace.md).
- The blueprint kept self-merge off until John chose a GitHub route and two weeks of shadow mode passed (blueprint decisions.md, ruling 2; SP19).
- Branch protection and CODEOWNERS on private repos need a paid GitHub plan (engineer-protocol E50, E53); `gh pr merge --auto` merges once required checks pass (engineer-protocol E54, E59).

## Decision
- John bought GitHub Pro. Self-merge (R16) is on from day one, with no shadow or trial weeks.
- `profile.yaml` defaults to `self_merge: true`.
- Tier 1 PRs merge through the broker's `automerge` job after the gate and the auditor pass (blueprint flow.md F28).
- Tier 2 PRs merge only after John's own approving review on GitHub; the broker enables auto-merge for them only once that review exists.
- Enforcement is server-side: branch protection, required checks, CODEOWNERS on Tier 2 paths, no bypass, no force push.

## Consequences
- SP18 runs on setup day and must pass before `setup-root.sh --lock`; SP19 and setup step 41 are dropped.
- A wrong Tier 1 classification merges without John; the audit, the test-diff guard and CODEOWNERS are the controls.
- Every merge is an event in `events.jsonl` and appears in `MORNING.md` and the digest.
