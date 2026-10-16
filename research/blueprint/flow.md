# Project flow

Purpose: how one project moves through the engineer from John's brief to the morning report, with the EARS requirements the findings gave for each stage.

Diagram: `docs/diagrams/engineer-project-flow.mmd`. Approval tiers: T0 automatic, T1 digest line, T2 hard gate (decisions.md). Requirements numbered F1-F42 here are blueprint requirements derived from the findings cited; R and Q numbers refer to `research/requirements/autonomous-engineer.md`.

## Run defaults
Every number below is an untested default unless a citation says otherwise; the named spike sets the real value, and the builder keeps them in `templates/run-defaults.yaml`.
| Setting | Default | Source or spike |
| --- | --- | --- |
| `--max-turns` per task session | 60 | about 60 turns is the findings' unvalidated trial box (engineer-feasibility spike 6); SP05, SP36 |
| `--max-budget-usd` per task session | 5 | builder default; SP05, SP35 |
| Wall-clock timeout per task | 45 minutes | upper end of the 15-45 minute task cap (engineer-planning §Tensions, worker inference); SP35 |
| Attempts per task | 2, then a blocked note | engineer-planning E121 |
| Breaker | no git diff in 3 attempts, or same failing tests 5 times | engineer-context §Q7.4 (frankbria) |
| Denials of one kind before the night stops (F29) | 5 | builder default; SP04, SP30 |
| Trials per decision | 3, configurable | engineer-feasibility §Q3 |
| T1 default-on-timeout | 24 h, reversible items only; reminder at 12 h; at most 5 open T1 items | worker inference (engineer-human-loop §Tensions); SP30 |
| Night window and digest time | Unattended runs 22:00-07:00 US Eastern; daily digest at 07:30 | builder default; John may change it in `run-defaults.yaml` |
| `cleanupPeriodDays` | 7 | builder default for "low" (engineer-human-loop E91) |
| Context ceiling before Explore subagents | about 128K-256K tokens | engineer-models §Q3 (worker inference); SP42 |

## Stage 0: size gate (interactive)
A change John can describe in one sentence skips intake and planning and becomes a single task (engineer-intake A1; engineer-protocol E24).
- F1 When a brief describes a diff in one sentence, the engineer shall skip intake and planning and run it as one task with its own check.

## Stage 1: intake (interactive, John present; ruling 11)
Restate, open phase, explore branch, closed phase, glossary, stop rule (decisions.md area 1). Intake also reads the project's own rules and data limits into `docs/plan/profile.yaml` (ruling 8, 9).
- F2 When John gives a brief, the engineer shall restate any "do X with Y" as a question about the problem and record goal, constraints and ruled-out options for him to confirm before design (engineer-intake P5, P12).
- F3 While intake is open, the engineer shall ask one open question per turn along the coverage list (engineer-intake E14, E18).
- F4 When John answers "I don't know" or names no option, the engineer shall run the research skill and show at most 5 verified options with one marked recommendation (engineer-intake U7, U8, P15).
- F5 When a candidate URL or repo cannot be opened, the engineer shall drop it before John sees it (engineer-intake U7, U8).
- F6 When John overrides an objection, the engineer shall record an "accepted over objection" ADR in `docs/adr/` (engineer-intake P20, P24).
- F7 When an adopted repo has its own agent rules, the engineer shall record them in `profile.yaml` and raise any conflict with unattended work to John before planning (ruling 8; engineer-existing-systems J39, J40).
- F8 When every coverage heading is Clear or Deferred, John says done, or the question cap is hit, the engineer shall end intake (engineer-intake E25, E28, E30).

## Stage 2: as-is scan (when an existing system is involved)
Access inventory by name, config snapshots, script graph then per-module notes, credential inventory by metadata, as-is pack (decisions.md area 2). Runs in `claude -p` workers after John grants read access; John signs off the context diagram and system-of-record table.
- F9 When a project involves an existing system, the engineer shall produce the as-is pack, every row marked observed, inferred or asserted, before proposing changes (engineer-existing-systems B3, B4).
- F10 The engineer shall inventory credentials by name and metadata only and shall not run `n8n export:credentials --decrypted` or TruffleHog with verification (engineer-existing-systems S40, B19).
- F11 When the map is written, the engineer shall keep it out of CLAUDE.md and load it by path (engineer-existing-systems M29-M31).

## Stage 3: feasibility trials
Map, bound, sandbox, decide, record (decisions.md area 4). Tool gaps run the bounded discovery pass (area 3).
- F12 When a choice depends on a behavioural claim (auth, rate limits, webhooks, pagination, UI-only behaviour), the engineer shall test it in a trial instead of trusting documentation (engineer-feasibility B20).
- F13 When trials start, the engineer shall run at most 3 paths (configurable), each with its pass line written before the run (engineer-feasibility B9).
- F14 While a trial runs, the engineer shall hold credentials only in the host proxy, never inside the trial container (engineer-feasibility C17, C23, C24).
- F15 When a trial reaches its box end or fails two fixes on one blocker, the engineer shall record `inconclusive` or the failure in `dead-ends.md` with `retry-when` and stop it (engineer-feasibility B4, B17, B29).
- F16 When a tool or path is considered, the engineer shall first search `dead-ends.md`, `docs/adr/` and the tool registry (engineer-tool-discovery E120; engineer-feasibility B29).
- F17 When a trial ends, the supervisor shall write `result.json`, tear down the container and worktree, and sweep orphans at the next start (engineer-feasibility C3, C19, C22).

## Stage 4: plan, before-brief, approval, project setup list
Plan set under `docs/plan/` (decisions.md area 7), three-page before-brief (area 8), John signs brief, acceptance, integrations and costs, gates. The project's setup list follows the setup.md pattern.
- F18 Before building, the engineer shall write the plan set and the before-brief and treat them as the single source of truth (R8; engineer-planning §Q1).
- F19 When John approves by an allowlisted Telegram reply or a PR approval from his account, the engineer shall write `approval.json` with the sha256 of each signed file (`brief.md`, `requirements.md`, `integrations.yaml`, `profile.yaml`; repo-composition.md, Plan set) and tag `plan-approved-N` (engineer-planning E27, E29, E30).
- F20 If an approved file's hash no longer matches, then the engineer shall refuse code edits until the change is re-approved (engineer-planning §Q2, S2).
- F21 When the plan is approved, the engineer shall produce one ordered setup list, long waits first, with a verification per row and the reason for every human-only row (R11, R12; engineer-feasibility D44, D52).

## Stage 5: task loop (unattended)
The supervisor computes `ready` from the `tasks.json` DAG and runs one task at a time (parallel implementers rejected, engineer-context §Q7 Rejected).
- F22 When a task is ready, the supervisor shall start one fresh `claude -p` in its own worktree and branch with `--max-turns`, `--max-budget-usd` and a wall-clock timeout set from Run defaults (engineer-context §Q4; engineer-protocol E37, E38).
- F23 While a task runs, the engineer shall not edit tests, CI, hooks, `.claude/` or `audit/` (engineer-protocol E11).
- F24 When the implementer stops, the Stop/TaskCompleted hook shall run the task's evidence command and the `docs/DEPENDENTS.md` check and block with exit 2 on failure (engineer-protocol E15; engineer-context §Q7.3).
- F25 When the gate passes, `audit.sh` shall rerun the checks at HEAD with a test count above zero, then the supervisor shall start the auditor through `run-task` with the `auditor` profile, and the auditor shall return `PASS`, `FAIL` or `NEEDS-JOHN` bound to that HEAD SHA as JSON, which the supervisor writes to `audit/AUDIT-<id>.md` in its records clone and pushes to the `engineer-records` branch (repo-composition.md, Records) (engineer-protocol E138, E150, §Q2).
- F26 If the same FAIL repeats, then the supervisor shall mark the task `NEEDS-JOHN` and continue with other ready tasks (engineer-protocol §Q3; R14).
- F27 If a task fails twice, makes no git diff in 3 attempts, or repeats the same failing tests 5 times, then the supervisor shall write a blocked note and stop that task (engineer-context §Q7.4).
- F28 When a task passes audit, the engineer shall open one PR with a Conventional Commit title; when its paths are Tier 1, the supervisor shall have the broker's `automerge` job run `gh pr merge --auto`, because R16 self-merge is on from day one under GitHub Pro; when its paths are Tier 2, it shall add a T1 "merge PR?" line and enable auto-merge only once John's own approving review exists on GitHub (engineer-protocol E44, E54; ruling 2) (updated 2026-10-16, John's decision).
- F29 If the denial limit in Run defaults is reached for one kind of denial in a night, then the supervisor shall stop the night and report them in the digest (engineer-human-loop §Q6).

## Stage 6: change of course
- F30 When a change of course is needed, the engineer shall write a change record tiered Minor, Moderate or Major, update every dependent document named in `docs/DEPENDENTS.md` in the same change, and block dependent tasks until it is `applied` (R9; engineer-planning E37-E42).
- F31 When a change is Major (goal, scope, acceptance, cost or risk ceiling, irreversible or external action), the engineer shall park that branch and send one T1 line, continuing unaffected tasks (engineer-planning §Q3).

## Stage 7: security
- F32 When a PR touches auth, data or config, the engineer shall run the deterministic scanners and `/security-review`, and shall accept an LLM finding only with file:line, repro and scope (engineer-security E70, E82).
- F33 If a new Critical or High deterministic finding, a secret or a failing auth test appears, then the gate shall block merge and deploy (engineer-security §Q7, worker thresholds).
- F34 When a milestone ends, the engineer shall write `security/REPORT.md` and `BRIEF.md` stating scope, method, findings, severity, remediation, retest and what it does not assure (R20; engineer-security E127-E131).

## Stage 8: deploy
- F35 When a deploy is due, the engineer shall deploy a preview by platform CLI with a narrow token and run the 11-item pre-promote checklist (engineer-deploy E6, §Q10).
- F36 When the checklist passes, the engineer shall add a T1 promote line with default "hold" unless `profile.yaml` gates promotes as T2 (ruling 9; engineer-deploy E123).
- F37 If a watch window after promote fails, then the engineer shall roll back automatically and notify John (engineer-deploy E117, E118).
- F38 When an action spends money, deletes data or submits to an app store, the engineer shall send a separate T2 Telegram prompt requiring typed confirmation and shall never apply a default on timeout (engineer-human-loop §Q6; engineer-deploy E97-E100).

## Stage 9: morning report and digest
- F39 When a night reaches a terminal state, the supervisor shall write `RUN_STATUS.json` as `done`, `blocked`, `stopped_by_bound` or `crashed`, render `MORNING.md` from `events.jsonl` and commit a copy to the `engineer-records` branch, and send one numbered Telegram digest with a recommended default and reply token per line (engineer-context §Q7.5; engineer-protocol E103, §Q6).
- The digest also carries: re-login needed and gated browser actions (engineer-browser §Implications 5), inconclusive dead-ends (engineer-tool-discovery §Open for John), pages to publish (ruling 7), and denials (F29). T1 lines that are reversible take their default after 24 h; the 24 h figure is worker inference (engineer-human-loop §Q6, spike SP30).
- Publishing: under Path A an interactive or Remote Control session publishes the committed brief by day (ruling 7; engineer-briefing E53).

## Stage 10: resume after limits, crashes and reboots
- F40 When a session limit message appears, the supervisor shall rely on `autoContinueAtUsageLimit`, record `waiting_for_reset` with the parsed reset time, and if the run still ended, resume with `--resume <session_id>`; when a weekly limit appears it shall end the night `stopped_by_bound` (ruling 5; engineer-protocol E108, E115-E117).
- After a crash or reboot, systemd restarts the supervisor, which reconciles from `events.jsonl` before starting work and pings "supervisor died" on stop (engineer-protocol E124, E125). A new session re-reads state through the SessionStart hook (engineer-context §Q7.1).

## Host rules (every stage) (updated 2026-10-16, John's decision)
- F41 When a login page, CAPTCHA or bot challenge appears, the engineer shall stop the task, record a blocked note naming the host and kind, and notify John through Remote Control or Telegram with a T1 "re-login or clear the challenge on noVNC" line, and shall not attempt to bypass it; it shall not use stealth plugins, user-agent spoofing, proxy rotation or CAPTCHA solvers (engineer-host E17, E18, §Implications).
- F42 When the engineer host is set up, the operator shall log in with an interactive `claude auth login` (`/login`) rather than `setup-token`, so that Remote Control works; when `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set in a run's environment, the wrappers shall refuse to start (engineer-host E105, §Implications; ruling 1).

## Stage 11: close
The after-brief reuses the before-brief's skeleton and diagram ids, built from observed facts with unverified items marked (engineer-briefing §Q2), and `architecture.yaml` is updated in the same commit as any system change (engineer-briefing E70).
