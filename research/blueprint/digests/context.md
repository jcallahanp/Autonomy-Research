# Context and memory (Area 9) - digest
Source: research/findings/engineer-context.md; verification: 18 of 20 verified, 2 unverified (findings "Verification", 2026-10-16)

The findings file has no E-numbers. Evidence references here are the findings section (Q1-Q7, Implications, Tools evaluated) plus a short name for the source page cited there.

## Decision
- Keep state in repo files, not in the model. Each session starts with a fresh context, and after compaction only root CLAUDE.md, auto memory and the plan come back from disk (Q1, Summary; memory, context-window docs).
- A `SessionStart` hook with `startup|resume|compact` matchers prints the open tasks, the last progress entry and the plan status. This is the documented fix for hook context being summarised away (Q7.1; hooks-guide, context-window).
- Use hooks for enforcement, not prose. CLAUDE.md is "context, not enforced configuration". A command-type Stop/TaskCompleted hook runs the task's evidence command and the `docs/DEPENDENTS.md` check, and blocks with exit 2 (Q7.3; memory, hooks docs, issue 75720: the attribution to an Anthropic maintainer is unverified and was corrected to "repository collaborator").
- Run each task as one fresh `claude -p` session under an outer supervisor. The supervisor sets `--max-turns`, `--max-budget-usd` and a wall-clock timeout, because every bound defaults to none ("No limit by default."). It allows two attempts per task, then writes a blocked note. A breaker trips on no git diff in 3 attempts or the same failing tests in 5 (Q4, Q7.4; cli-reference, frankbria circuit_breaker.sh, night-loop-audit).
- End state: `RUN_STATUS.json` from a `trap` handler, with `done | blocked | stopped_by_bound | crashed`, plus one push at the terminal state, "1 note = 1 decision request" (Q7.5; agent-loop, headless docs).
- Model tiers: Opus/Fable-class for planning and debugging, Sonnet-class for implementation and review, and Haiku 5.5 only for narrow checkable roles, and only after a paired test on John's tasks shows no loss (Q3 table, Q7.6; costs page, claude-haiku-5-5 page). The Haiku/Sonnet Terminal-Bench figures, 39.2% vs 70.6%, are a WebFetch paraphrase (Q3).
- Rotate sessions by step count or task boundary, and re-read the acceptance checklist at each task start. This is a worker inference resting partly on the step-count study (arXiv 2609.01660), which verification marked unverified because its PDF would not open as text (Q7.8; Verification).

## Alternatives and rejected
- Beads: alternative. The task-store upgrade when there are more than about 50 tasks or several agents or machines (worker inference); the 2026-08-11 data-loss incident is documented (Q7 Alternatives; Tools evaluated).
- `/goal`: alternative. Used inside one task with a turn clause; it is not a bound on its own (Q7 Alternatives; goal docs).
- Official Ralph plugin: alternative only with `--max-iterations` and `--completion-promise` set and the supervisor owning the bounds (Q7 Alternatives; ralph-wiggum README:60,134).
- A single Sonnet agent with `/goal`: alternative, the cheapest shape, to be spiked first (Q7 Alternatives).
- cwc-long-running-agents: alternative template. Its README was seen only as an Exa excerpt in this run (Q7 Alternatives; Open questions 11).
- GitHub Issues as a human mirror of `tasks.json`, and OpenSpec as a spec framework: alternatives (Q7 Alternatives).
- Ralph plugin as shipped: rejected. Unlimited by default, the same growing context and no no-op detection; one run reached 6,239 iterations over about 11.7 hours (Q7 Rejected; issue 1699).
- Unbounded `max_iterations: 0` loops and `/loop` for overnight work: rejected (Q7 Rejected).
- Agent teams: rejected, "approximately 7x more tokens" (Q7 Rejected; costs page).
- Native task list as the only store: rejected. It is model-gated and session-scoped (Q7 Rejected; tools-reference, interactive-mode).
- CLAUDE.md alone as the doc-update guard: rejected, because it is advisory (Q7 Rejected; memory docs).
- LLM-only completion judge: rejected, because the evaluator is "inclined to be generous" (Q7 Rejected; harness-design post).
- Haiku as default implementer, and a Haiku reviewer without execution evidence: rejected (Q7 Rejected; claude-haiku-5-5, arXiv 2610.01471).
- Parallel implementers on one repo: rejected (Q7 Rejected; architecture.md:13).
- eng-skills as a dependency: rejected (0 stars); its idea is copied (Q7 Rejected).
- Cline, Aider, Devin and OpenHands as engines: rejected, because Claude Code is fixed by ruling. Their ideas only are kept (Q7 Rejected; Tools evaluated).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| CLAUDE.md (under 200 lines, `# Compact instructions`) + auto memory | Instruction and learned memory, reloaded after compaction | Engineer repo, on the VM John controls (per engineer-runtime.md) | Included in Max | Q1, Q7.1; memory docs |
| SessionStart hook (startup/resume/compact) | Re-injects tasks, progress and plan status | Claude Code hooks | Included | Q7.1; hooks-guide |
| Stop / TaskCompleted command hooks | Run the evidence command and the DEPENDENTS check; exit 2 blocks | Claude Code hooks | Included | Q6, Q7.3; hooks docs |
| PreToolUse hooks | Deny writes to `.claude/` and destructive git; filter test and log output | Claude Code hooks | Included | Q7.3, Q7.7; costs page |
| Superpowers 7.0.0 (commit bb92a77) | Brainstorm, plan and git-ignored ledger process layer | Plugin | Free (MIT) | Q1, Q7.1 |
| `claude -p` with `--max-turns`, `--max-budget-usd`, timeout | Bounded fresh session per task | Supervisor on the VM | Max plan | Q4; cli-reference |
| Supervisor script (own build) | Attempt counter, USD and wall-clock caps, breaker, `RUN_STATUS.json`, push | VM, counter file outside the container | Free | Q7.4-5; frankbria thresholds |
| Subagents with per-agent `model:` and `effort:` | Planner, implementer, reviewer and narrow Haiku roles | Claude Code | Included | Q3 table; sub-agents docs |
| `promptCacheTtl=1h` | Keeps the cache across gaps over 5 minutes | API-key runs only | 1-hour cache write is 2x base input | Q5; prompt-caching docs |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1. Write root CLAUDE.md with Compact instructions, and turn auto memory on | Automated | Line count under 200; spike 2 (compaction fidelity) |
| 2. Add SessionStart hook (startup, resume, compact) | Automated | Spike 2: seeded decisions survive `/compact` |
| 3. Create `tasks.json`, `PROGRESS.md`, `docs/DEPENDENTS.md`, ADR folder | Automated | Stop hook reads them; spike 7 (task loss over 3 compactions) |
| 4. Add Stop/TaskCompleted evidence and manifest hook; PreToolUse denies and filters | Automated | Spike 3 (exit 2 vs JSON; under `-p` and Routines) |
| 5. Build the supervisor with caps, attempt counter outside the container, breaker and `RUN_STATUS.json` trap | Automated | Spike 4 (exit codes, `result.subtype`, no-diff detection) |
| 6. Define subagent files with explicit model and effort | Automated | Spike 6 (paired tier test) |
| 7. Choose and connect the push channel | Not settled here; deferred to engineer-runtime.md | Open questions ("Which push channel ... least brittle") |
| 8. Supply 20-30 real tasks for the tier test | John's repos are the source; whether John picks them is not stated | Spike 6, pass^3 |

## Repo composition
- Files: `tasks.json` (id, status, evidence_command, evidence_result, depends_on), `PROGRESS.md`, `docs/DEPENDENTS.md`, ADRs that supersede rather than delete, `RUN_STATUS.json`, and a per-night counter file outside the container (Q7.2, Q7.4-5).
- Hooks: SessionStart (startup, resume, compact); Stop and TaskCompleted evidence and manifest gate with logging when it fails open after eight blocks; PreToolUse deny on `.claude/` and destructive git; PreToolUse output filters (Q7.3, Q7.7).
- Agents: planner/debugger (Opus/Fable), implementer and reviewer (Sonnet, the reviewer without Write/Edit), Haiku test runner, scout, summariser and citation checker after measurement (Q3 table).
- Scripts: supervisor loop with caps, breaker and trap (Q7.4-5).
- Superpowers: keep brainstorming, writing-plans and the ledger (Q7.1). Beads: drop for v1, keep as the upgrade path; its `bd remember`/`prime` overlaps with auto memory (Q1 overlap map). Ralph: drop the in-session plugin; keep "one item per loop" and the bash-loop shape under the supervisor (Q1, Q7.4).
- For the researcher plugin: add a compact-matched SessionStart hook echoing PLAN.md status; test the Haiku verifier on seeded bad citations (Implications 9).

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1. Context-rot onset | Fixed task set with a 20-30 item checklist at clean vs 150K vs 400K context, 10 runs each | Findings state metrics only (strict pass, requirement coverage); no threshold set |
| 2. Compaction fidelity | Seed decisions, force `/compact` and auto-compact, with and without Compact Instructions and the SessionStart hook; also the Superpowers ledger on a long plan | Seeded decisions present after compaction (metric: decisions lost in diff) |
| 3. Stop hook behaviour | Exit 2 vs JSON block on the current version, under `claude -p`, cloud sessions and Routines; doc gate with an unchanged named doc | Hook blocks finish when the doc is not updated; false-positive rate measured |
| 4. Supervisor bounds | `--max-turns` and `--max-budget-usd` exit codes and `result.subtype` under Routines; stub supervisor on a real repo; Ralph via `-p` with a cap on a toy repo | Bounds reported reliably; "no git diff in 3 attempts" detected |
| 5. Session rotation and re-read | Step-count rotation (40 vs 100 tool calls) vs token threshold; with vs without forced re-read after compaction | Higher checklist coverage decides (no number given) |
| 6. Tier measurement | Paired test on 20-30 of John's tasks per role, 3 repeats; Haiku verifier on seeded bad citations; done-gate plus reviewer on one ticket | Cheaper tier pass^3 not lower than the stronger tier (Implications 7) |
| 7. Task store | `CLAUDE_CODE_ENABLE_TASKS` on the engine model; Beads vs `tasks.json` over 3 forced compactions; nesting depth | Task loss compared; no threshold given |
| 8. Completion honesty and trimming | "Done" claims with failed checks, with and without the Stop-hook verifier; truncation-hook effect; cache hit rate across `-p` runs | Fewer false "done" claims; trimming must not lower pass rate (Implications 8) |

## Requirements served
- R9: the `docs/DEPENDENTS.md` manifest checked by the Stop hook blocks the turn until mapped documents change or a waiver is recorded (Implications 3; a worker inference, spike 3).
- R15: an unattended supervisor runs one bounded `claude -p` per task overnight (Q7.4).
- R17: the fresh-context reviewer without Write/Edit checks the diff against the plan and checklist (Q7.3). Engineer-protocol replaces it with an auditor.
- R18: turn, budget, wall-clock and attempt caps plus the git-diff breaker stop the loop and write state (Q4, Q7.4).
- Q1: tiers move down only after the paired test shows no loss (Implications 7).
- Q2: state lives in `tasks.json`, `PROGRESS.md` and the plan, and is re-read through the SessionStart compact hook (Implications 1).
- Q3: `RUN_STATUS.json` always ends `done | blocked | stopped_by_bound | crashed` (Implications 6).
- Q4: done is the evidence command's exit code, never the model's claim (Implications 2).
- Q5: CLAUDE.md under 200 lines; sessions rotated before state decays (Q7.7-8).

## GTM scenario
- Scan as-is: gap. This area gives no mapping mechanism. It gives only the state carriers in which the as-is map would live.
- Fix Attio tables and views, set up Clay workflows, clean data: gap for the mechanism. The area supplies the run discipline only: one task per bounded `claude -p`, an evidence command per task in `tasks.json`, and a blocked note after two attempts (Q7.2, Q7.4).
- Finish tooling: the same supervisor and done-gate apply. Doc changes are forced by `docs/DEPENDENTS.md` (Q7.3).

## Tensions
- Reviewer design: this area keeps a fresh-context Sonnet reviewer comparing diff against plan (Q7.3). Engineer-protocol replaces it with a script-first auditor and a same-model judge, and rejects Haiku as that auditor (engineer-protocol Q8).
- Haiku verifier: the repo fixes `model: haiku` for the verifier, but its recall on seeded errors is unmeasured (Q3 Contradictions 2).
- Push channel: Q7.5 routes the terminal push through "Channels or Remote Control per engineer-runtime.md". Engineer-protocol moves it to a supervisor `curl`, because Channels needs an open session.
- Stop-hook blocking: the docs say JSON `decision: block` or exit 2 both work, but one PR reports only exit 2 blocked. This is unresolved (Q6 Contradictions; spike 3).
- Step count vs context length as the driver of decay is unresolved (Q2 Contradictions 1). The rotation rule (Q7.8) rests partly on arXiv 2609.01660, which verification marked unverified.
- Subagent nesting: the docs summary says three layers by default, against the brief's assumption of none; the exact wording is unchecked (Q1 Contradictions 1).
- The issue-75720 endorsement was attributed to an Anthropic maintainer. Verification found only "Collaborator", so the hook-as-gate design rests on docs, not that quote (Verification).
- No study measures Claude Code on a multi-hour coding task. Every context-rot threshold is borrowed from non-Claude agents (Open questions, "Unsettled").
- Opus 5.5 and Sonnet 5.5 per-token prices: the pricing page was not opened (Open questions).

## Open for John
- Whether Beads is ever adopted, or `tasks.json` stays the store (Q7 Alternatives).
- Which real tasks from his repos form the paired tier test (Q3, spike 6).
- The push channel, deferred to engineer-runtime.md (Open questions).
