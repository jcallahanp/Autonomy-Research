# Planning (Area 7) - digest
Source: research/findings/engineer-planning.md; verification: 19 of 20, 1 unverified (corrected in text 2026-10-16)

## Decision
Write a small, committed plan set before any code, not a framework's full template stack. Have John sign only the owner-facing parts with a hash-bound approval. Route every change of course through tiered change records. Size tasks by an explicit contract. Confidence medium; the caps, tiers and file list are worker inference (Q6).
- The plan set is 8 files under `docs/plan/`: `brief.md` (1-2 pages), `requirements.md` (EARS, 15-40 lines), `architecture.md` (one plain Mermaid flowchart at container level), `integrations.yaml`, `contracts/`, `tasks.json`, `tests/acceptance/`, and MADR decisions for real choices only. That is about 150-250 human-reviewed lines (Q1; worker inference). Large sets are "very verbose" (E6, E8). A Spec-Kit-style spec gained 9.2 points at "roughly 28 times the tokens" (E14). More scaffolding "did not consistently improve FR coverage" (E15). Context files add over 20% cost (E17).
- The plan set is written after a Superpowers-style brainstorm with its hard gate (E25, E26).
- John signs the brief, the acceptance criteria, the integrations and costs, and the gates. He does not sign the architecture, schema, contracts or tasks; a fresh-context reviewer checks those (Q2).
- Approval is recorded in `docs/plan/approval.json`, which holds the sha256 of each approved file and goes stale on any edit (Spec Guard pattern, E29, E30), plus an annotated tag `plan-approved-N`. An in-session Approve records no identity (E27). A hook refuses code edits on a hash mismatch (worker inference; spike S2).
- Change control uses Minor, Moderate and Major tiers from BMAD correct-course, with explicit approval for Major (E37, E38). Changed decisions get superseding ADRs (E34). Work stays blocked until every flagged document is updated or waived (E40, E42). Edits follow a six-step order (Q3). All of this is enforced by the wave 1 exit-2 Stop/TaskCompleted hook over `docs/DEPENDENTS.md` (E118, E119).
- Drift checks run deterministic tools first: the manifest gate on the current diff, lychee with 429 handling (E49, E50), and Schemathesis or Atlas only where they apply (E51, E54). The milestone LLM audit is advisory and must cite plan and code lines. Unfiltered, an LLM flags 98% of items; filtered, 14% at precision 0.63 (E55, E56).
- Tasks: keep Superpowers' fresh subagent per task (E82). Replace its sizing with a task contract: one fresh session, one commit and one runnable check per task, about 1-4 files and about 100 lines (worker inference; spike S8). METR's noise-adjusted 80% horizon for Opus 4.6 is 1h16m (E63). SWE-Bench Pro tasks average 107 lines over 4.1 files, and the best models score about 23% (E68). Working one feature at a time was "critical" (E72). Over-splitting also loses (E96, E98).
- Tasks live in a `tasks.json` DAG, and the supervisor computes `ready`. Each session is bounded by `--max-turns`. Each task gets "two attempts per task, then a blocked note" (E121).

## Alternatives and rejected
- OpenSpec CLI for proposals, deltas and archive: kept as alternative. Lighter; Thoughtworks Assess, April 2026; licence unchecked (E9).
- Kiro's three files written by hand: kept as alternative (E1).
- spec-kit as prompt patterns only (NEEDS CLARIFICATION marker, read-only checklist gate, [P] marker): kept as alternative (E3, E5, E88).
- Danger JS: kept as alternative, if the repo works through GitHub PRs (E46).
- A docs-gate LLM verifier: kept as alternative. Search-highlight evidence only (Open questions 12).
- Beads: kept as alternative, if multi-agent claims or cross-session dependency queries become necessary (E105).
- Ralph one-item-per-loop with the supervisor owning the bounds: kept as alternative (E86).
- Plannotator: kept as an optional plan viewer, not as the record (E27).
- spec-kit wholesale: rejected. Verbose (E6, E8).
- BMAD as a framework: rejected. Heavy; only correct-course is borrowed (Q6).
- Kiro IDE: rejected. Not Claude Code; "Session Too Long" (E92).
- Tessl: rejected. Beta, described only through the Fowler article (Q6).
- Spec Guard, Plannotator, Verdict or Doc-Drift as dependencies: rejected. Small or unvetted; copy the ideas (E29, E61).
- ExitPlanMode approval alone: rejected. No identity recorded (E27, E116).
- Dredd: rejected. Archived 2024-11-08 (E52).
- Pact for a solo repo: rejected. It needs a Broker (E53).
- Whole-document LLM comparison: rejected. 98% flag rate unfiltered (E55).
- spec-kit or Kiro as change engines: rejected. Their docs are silent on amendment (E44, E45).
- Semver for the plan: rejected. No tool documents it (worker inference).
- Taskmaster auto-expand as the sizing authority: rejected. Thresholds not read (Q6).
- Parallel fan-out by default: rejected. Cost rises and quality does not (E110).
- Mermaid C4 syntax as default: rejected. Experimental (E122).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
|---|---|---|---|---|
| Plan-set templates (Markdown, EARS, YAML, JSON, MADR) | The 8-file plan set | Repo `docs/plan/` | Free, nothing to install (Q6) | E3, E10, E24 |
| Superpowers brainstorming + subagent-driven-development | Hard-gated brainstorm; fresh subagent per task | Plugin | Free (vendored) | E25, E82 |
| `approval.json` + PreToolUse/startup hash-check hook | Binds John's approval to file hashes | Repo + Claude Code hook | Free | E29, E30; S2 |
| Annotated git tag `plan-approved-N` | Marks the approved version | git | Free | Q2 |
| GitHub protected-branch review | Identity-bearing approval route where John can use it | GitHub | Not stated | E31, E32 |
| Stop/TaskCompleted exit-2 hook over `docs/DEPENDENTS.md` | Blocks resume until dependents are updated | Claude Code hook | Free | E119, E62 |
| lychee | Link check on changed docs, 429 tuned | CLI/CI | Not stated | E49, E50 |
| Schemathesis (only with OpenAPI) | Schema-conformance tests | CLI/CI | MIT | E51 |
| Atlas (only with a database) | Schema diff against a dev DB, migration lint | CLI/CI | Not stated | E54 |
| Milestone LLM audit (Sonnet-class) | Advisory plan-versus-diff check that cites lines | Claude Code | Unmeasured (Q4) | E55, E56, E58 |
| `tasks.json` DAG | Task store; agent edits only the status field | Repo | Free | E95, E118 |

## Setup steps
| Step | Automated or John | How it is verified |
|---|---|---|
| 1. Add the `docs/plan/` 8-file template with the "decide nothing" ban and the NEEDS CLARIFICATION marker | Automated | S1: plan set for one real John project, review time measured |
| 2. Define the `tasks.json` schema (`files`, `depends_on`, `requirement_ids`, `check`, `files_to_read`, `passes`) | Automated | S9: accurate `files` lists; S12: format A/B |
| 3. Add `approval.json` and the startup/PreToolUse hash check; `permissions.deny` on `plan.approved.vN` | Automated | S2 in the cloud runtime |
| 4. Approve the brief, acceptance criteria, integrations and costs, and gates, by his own message or a PR approval from his account | **John** (by hand) | `approval.json` is written only after that; S4 checks mobile PR approval |
| 5. Turn on branch protection on his repos where self-approval works | **John** (settings) | S4; single-user self-approval unverified (Open questions 31) |
| 6. Add the change-record template, `docs/DEPENDENTS.md` and the Stop-hook extension | Automated | S5 on the current engine version |
| 7. Add lychee on changed docs | Automated | S7, with and without `--accept 429` |
| 8. Add the milestone LLM audit | Automated | S6: precision hand-labelled on 3 past repos |

## Repo composition
- Files: `docs/plan/{brief.md, requirements.md, architecture.md, integrations.yaml, contracts/, tasks.json, decisions/NNNN-*.md}` and `tests/acceptance/` (Q1). Also `docs/plan/approval.json`, a read-only `plan.approved.vN` plus a CHANGELOG, `docs/plan/changes/NNNN-<slug>.md` change records, `docs/DEPENDENTS.md` and `PROGRESS.md` (Q2, Q3, E118).
- Hooks: a startup and PreToolUse approval-hash check (S2); the wave 1 exit-2 Stop/TaskCompleted gate, extended so a task cannot resume while a change record it depends on is not `applied` (Implications).
- Skills and agents: a planner step that checks the task contract (one check, a files list, a line estimate, named interface seams; Implications). A fresh-context reviewer for the parts John does not sign (Q2). A milestone LLM auditor (Q4).
- Scripts: a supervisor that computes `ready` from the DAG and detects file overlap (Implications); an `integrations.yaml` check against `.env.example` (Q1).
- Superpowers: keep the brainstorming hard gate, the "decide nothing" plan hygiene and the fresh-subagent executor (E21, E25, E82). Drop its task sizing, which has no numeric cap (E81). The "2-5 minute steps" figure is not in the 7.0.0 file read (Q5).
- Beads: deferred; `tasks.json` DAG first (Tools evaluated).
- Ralph: keep one task, fresh context and one commit per iteration; drop the unbounded loop (E86; Tools evaluated).
- spec-kit: keep the NEEDS CLARIFICATION marker, the read-only checklist gate and the [P] marker (E3, E5, E109).

## Spikes
| Spike | Probe | Pass criterion |
|---|---|---|
| S1 | Write the plan set for one real John project | Time his review; no pass line given |
| S2 | Hook that blocks code edits on an approval-hash mismatch, in the cloud runtime | Edits blocked; `permissions.deny` stops edits to `plan.approved.vN` |
| S3 | Agent adherence: 1-page brief versus the full set, on one task | Adherence comparison |
| S4 | John approves a PR on a single-user repo with branch rules, from the GitHub mobile app | The approval is possible |
| S5 | Exit-2 Stop-hook gate limited to the current diff, current engine version | The gate blocks (JSON decision versus exit 2) |
| S6 | LLM plan-versus-diff audit on 3 past John repos | Precision labelled by hand |
| S7 | lychee on changed files, with and without `--accept 429` | False broken-link rate |
| S8 | 10 John-style tasks at about 50, 100 and 300 lines on Sonnet 5.5 and Opus 5.5 | Pass on first check, turns, context use; sets the real caps |
| S9 | Planner emits `files` lists | Lists are accurate |
| S10 | One-commit tasks versus Superpowers right-sizing, on a repo where John saw hallucination | Comparison |
| S11 | Read METR's raw data | Current Claude 80% horizons |
| S12 | YAML versus JSON, and Markdown versus JSON (wave 1 spike 7) task lists | Plan-following comparison |

## Requirements served
- R8: the 8-file plan set covers requirements, architecture, data schema (`contracts/`), the key map (`integrations.yaml`), the task breakdown (`tasks.json`) and acceptance scenarios (`tests/acceptance/`). It is committed and hash-approved as the source of truth (Q1, Q2).
- R9: change records with tiers, superseding ADRs, a six-step update order and a block until dependents are updated. Major changes (goal, scope, acceptance, cost or risk ceiling, or an irreversible or external action) wait for John (Q3; E37, E40, E42).
- R14: Major changes stop that branch only, go to John as one batched entry each, and unaffected tasks continue. Minor and Moderate changes appear as an FYI list (Q3).
- R17 (in part): deterministic drift gates plus an advisory audit that cites plan and code lines (Q4).
- R18: two attempts per task then a blocked note, `--max-turns`, and re-splitting past about 50% context or after 2 failed corrections (E121, E102; Q5 rule 5).
- R10 (in part): `integrations.yaml` lists each service's purpose, auth, and free or paid with price. Privacy risks are not covered here (Q1).
- R22 (in part): `brief.md` is the owner-facing 1-2 pages and `tasks.json` is the machine plan. Diagrams-first and dark theme are not covered (Q1).
- Q2: all plan state is in committed files, and `PROGRESS.md` holds progress (E118).
- Q4: one runnable check per task; no check, no task (Q5 rule 1).
- Q5: brief 1-2 pages; task text self-contained and context-bounded (Q1, Q5).
- Q6: `integrations.yaml` and the brief state each paid service's price (Q1, Q2).

## GTM scenario
- Scan as-is: gap. Planning starts from intake and feasibility outputs.
- Fix Attio tables and views: gap for the mechanism (UI-only configuration is not covered). Planning gives the generic structure: a `tasks.json` entry per change with a runnable check, and change records if Attio's limits force a replan (Q3, Q5).
- Set up Clay workflows: `integrations.yaml` row (auth, env var name, price, owner action, fallback; Q1). The workflow build itself is a gap here.
- Clean data: gap. Contracts or Atlas apply only if a schema or database exists (Q4).
- Finish tooling: tasks split per the contract, each with one check (Q5). Nothing GTM-specific.

## Tensions
- R16 (self-merge of routine changes) against the approval route. Approval needs John's own message or a PR approval from his account, and GitHub self-approval on a single-user repo is unverified (Open questions 31; S4). How an approval sent over the R14 SMS-style channel carries his identity is not addressed.
- Stop-hook blocking: the hooks docs say a JSON decision or exit 2 both block, but doc-sentinel saw only exit 2 work. Unresolved since wave 1 (E120; S5).
- Task format: `tasks.json` was chosen over the plan-set note's `tasks.yaml` (Q1 Contradictions). JSON versus Markdown is still open from intake (E117; S12).
- Decision-record paths differ between areas: planning puts MADR files in `docs/plan/decisions/`, and feasibility puts them in `docs/adr/` (engineer-feasibility.md Q10). Pick one.
- The key-map formats overlap: planning's `integrations.yaml` and feasibility's `integration-matrix.md` plus integration cards hold overlapping per-service facts. Neither findings file reconciles them.
- Is decomposition still needed? Anthropic removed the sprint construct for Opus 4.6 (E76), while the Claude Code docs and Ralph still narrow tasks (E73, E84). This is reconciled by rule 8 (revisit caps per model release), but untested.
- The numeric caps (15-45 minutes, 1-4 files, about 100 lines, 50% context) and the tier boundaries are unmeasured (Open questions 33).
- Unverified: the 25-39pp split-class claim was corrected after verification and is conditional on stripped spec detail (Verification). Third-party METR readings disagree with METR's note (Open questions 16-17). The ISCAP 78.2% and 87.4% figures and the BMAD line numbers were not re-checked (Verification).
- The LLM audit's cost is unmeasured (Q4), against Q1 (outcome before cost) and the Sonnet-class choice.
- The DocPrism precision is for docstring versus code, not plan versus code (Open questions 25).

## Open for John
- Whether Moderate changes (tasks, order, approach) need his approval or stay FYI (Open questions 32).
- How he approves: a message on the batch channel, or a GitHub PR approval (S4). Whether R16 self-merge has limits such as production deploys (requirements Gaps).
- Confirm what he signs: the brief, the acceptance criteria, the integrations and costs, and the gates (Q2 step 1).
- Whether to allow the Express path for low-risk defaults the agent states aloud (Q2 step 7).
