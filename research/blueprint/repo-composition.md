# Repo composition

Purpose: how the engineer's template repo, its plugin, the VM and each project repo are laid out, and which outside ideas are kept or dropped.

The engineer ships as one template-plus-plugin repo with a pinned bootstrap, the same shape as this research repo (engineer-runtime P1, P5). Plugin changes below are recommendations; nothing in `plugin/` was changed by this research (engineer-tool-discovery §Implications).

## Template repo
```
plugin/
  skills/      interview, research, tool-scan, repo-triage, spike, system-map, setup   (existing, changed)
               as-is, plan, browser, deploy, security-review, digest                    (new)
  agents/      researcher, synthesizer, verifier, spike-worker                          (existing)
               mapper, merger, planner, implementer, plan-reviewer, auditor, triage-reader (new)
  hooks/       hooks.json + scripts (table below); source only, installed root-owned (Enforcement)
  scripts/     playwright-mcp.sh (existing)
  .mcp.json    playwright, deepwiki, firecrawl (existing)
scripts/
  setup-root.sh  bootstrap.sh  doctor.sh  cloud-setup.sh
  supervisor/    loop, ready-from-DAG, bounds and breaker, events, morning, telegram send and poll,
                 reply parser, reset parser, reconcile
  trial/         launch, proxy config, teardown, startup sweep
  broker/        agent-run job allowlist and jobs (push and PR, mint child token, API calls)
  snapshot/      attio, clay, n8n, outreach, slack config exports to JSON
  checks/        audit.sh, test-diff guard, pre-merge refusal, parity check, contrast check,
                 vet-card, staleness, integrations-vs-.env.example, n8n export
templates/
  managed-settings.json, egress-allowlist.txt, systemd units (supervisor, chrome-xvfb, novnc),
  superpowers/ (vendored at bb92a77 minus the dropped skills), project skeleton (below)
tests/
  check.sh, check-mermaid.sh (existing), test-fm.sh, rules/ (existing)
  supervisor/, broker/, parser/   unit tests for the builder's own scripts (spikes SP04-SP17)
  fixtures/seeded-flaw/   unsigned webhook, SSRF fetch, logged token (engineer-security §Implications 4)
plugin/evals/           claude plugin eval cases for the changed skills (existing folder)
.github/workflows/ci.yml   claude plugin validate --strict, tests/check.sh, tests/check-mermaid.sh,
                           gitleaks --redact, pinned scanners; Actions pinned by full SHA (engineer-security E41)
.claude/                settings.json and symlinks to plugin/skills and plugin/agents, as in this repo;
                        used only by the builder session, never by unattended runs
docs/versions.md        every pin the builder chooses (engineer-runtime §Repo composition, inference)
```

## Skills
| Skill | Status | What changes or what it does | Evidence |
| --- | --- | --- | --- |
| interview | Change | Size gate, restate step, open phase, explore branch, closed phase, budget, stop rule, glossary playback, approval checkpoint; reads adopted repo rules into `profile.yaml` (ruling 8) | engineer-intake §Repo composition, U20, A18 |
| research | Change | Build mode: D0-D2, cap of 3 workers, 10-minute box, no gap round, outputs to the project repo | engineer-tool-discovery §Implications |
| tool-scan | Change | Stop at first pass, capability-card input, route result in the row, wider MCP discovery | engineer-tool-discovery §Implications |
| repo-triage | Change | Fix its 11 vetting gaps (OSV, Scorecard API, licence, footprint, manifest scripts, typosquat, MCP static checks, version, a path without DeepWiki, aligned verdicts) | engineer-tool-discovery §Implications |
| spike | Change | Add "trial" mode: pre-authorised path list, credential manifest, domain allowlist, turn, budget and time box, two fixes per blocker, supervisor-owned `result.json`; `inconclusive` verdict in both modes | engineer-feasibility §Implications 1-3; engineer-tool-discovery §Implications |
| system-map | Change | As-is input contract, to-be view via `classDef`, model file with parity check, agent output, dark theme with contrast check, SVG kept, open-questions path, default checker run | engineer-briefing §Q7, E108-E116 |
| setup | Change | Becomes the tool-name probe behind `doctor.sh` | engineer-runtime P37, P38 |
| as-is | New | Five-step brownfield protocol; lead holds status lines only | engineer-existing-systems §Implications 1 |
| plan | New | 8-file plan set, task contract check, change records | engineer-planning §Implications |
| browser | New | Ladder API or MCP, flow script, exploratory Playwright, then John; routing table checked in | engineer-browser §Implications 1 |
| deploy | New | Platform matrix as decision table; pre-promote checklist | engineer-deploy §Implications 1, §Q10 |
| security-review | New | Output schema is the evidence contract (file:line, CWE, severity, repro, scope) | engineer-security §Implications 1 |
| digest | New | Renders T1 lines and T2 prompts from `events.jsonl` | engineer-human-loop §Implications |

## Agents
| Agent | Model tier | Tools | Evidence |
| --- | --- | --- | --- |
| planner (plan and debug) | Opus or Fable class | Read, write plan files | engineer-context §Q3 |
| implementer | Sonnet class | Full, inside worktree and sandbox | engineer-context §Q3 |
| plan-reviewer | Sonnet class, fresh context | No Write or Edit | engineer-planning §Q2; engineer-models E41 |
| auditor | Sonnet class or higher, never Haiku | Read, Glob, Grep, Bash; writes only `audit/AUDIT-<id>.md`, at most 15 lines, `PASS`, `FAIL` or `NEEDS-JOHN` | engineer-protocol §Q3, E35 |
| mapper and merger | Explore, Haiku override possible | Read-only; note per module with `path:line` | engineer-existing-systems M26, M27 |
| triage-reader | Any | Read-only, no secrets, no outbound; returns JSON from untrusted text | engineer-security §Q6, E123 |
| Haiku roles (test runner, scout, summariser) | Haiku 5.5 | Only after SP32 | engineer-context §Q3 |

## Hooks
| Event | What it does | Evidence |
| --- | --- | --- |
| SessionStart `startup|resume|compact` | Prints open tasks, last progress entry, plan and approval status; probe fails closed when unattended | engineer-context §Q7.1; engineer-runtime P43 |
| PreToolUse | Deny writes to tests, `conftest.py`, CI, hooks, `.claude/`, `audit/`, CODEOWNERS, protected paths; destructive git; approval-hash check; deploy command allowlist and spend checks; vendor model CLIs; browser target classifier with domain allowlist; kill-switch file; dead-end reminder | engineer-protocol §Implications; engineer-planning S2; engineer-deploy §Implications 2; engineer-models §Q7.3; engineer-browser §Implications 4; engineer-human-loop E163 |
| PostToolUse | Lint and typecheck; mermaid-lint on `.mmd`; `updatedToolOutput` redaction pending SP14 | engineer-protocol §Implications; engineer-briefing E71; engineer-human-loop E66 |
| Stop / TaskCompleted | Run the task's evidence command, `docs/DEPENDENTS.md` check, security gate checks; exit 2 blocks; log if it fails open after eight blocks | engineer-context §Q7.3; engineer-security E154 |
| StopFailure, Notification | Event taps into `events.jsonl` | engineer-protocol §Q9 |

## State files
| File | Where | Written by | Evidence |
| --- | --- | --- | --- |
| `events.jsonl` | VM state dir per project, outside worktrees (blueprint inference) | Supervisor only | engineer-protocol §Implications |
| `RUN_STATUS.json` | Same | Supervisor `trap`: `done`, `blocked`, `stopped_by_bound`, `crashed`, plus `waiting_for_reset` while waiting | engineer-context §Q7.5; engineer-protocol E115 |
| `MORNING.md` | Same, copied into the project repo `docs/runs/` | Supervisor | engineer-protocol §Q6 |
| Per-night counter | VM state dir, outside the container | Supervisor | engineer-context §Q7.4 |
| `decisions/approvals.jsonl` | Project repo, committed | Supervisor parser | engineer-human-loop §Q6 |
| `docs/plan/approval.json` + tag `plan-approved-N` | Project repo | Written only after John's identified reply or PR approval | engineer-planning E29, E30 |
| `tasks.json` | `docs/plan/` | Planner; implementer edits only `status` and `passes` | engineer-planning E95; engineer-intake A37 |
| `PROGRESS.md` | Project root | Each task session | engineer-planning E118 |
| `dead-ends.md` | Project root and template | Trials, discovery | engineer-tool-discovery E121; engineer-feasibility B29 |
| `docs/plan/architecture.yaml` | Project repo | The system model; Mermaid views generated with a parity check | engineer-briefing E39 |
| `audit/AUDIT-<id>.md`, `audit/waivers.md` | Project repo | Auditor; waivers by John | engineer-protocol §Q3 |
| `trials/<id>/result.json` | VM state dir | Supervisor | engineer-feasibility C19, C53 |
| `/etc/claude-code/managed-settings.json` | VM, root-owned | `setup-root.sh` | engineer-human-loop E148 |
| Kill-switch file `/var/lib/engineer/STOP` (path is a builder default) | VM, directory owned by `supervisor`, not writable by `engineer` | John (`sudo touch`) or supervisor; the PreToolUse hook and the supervisor stop when it exists | engineer-human-loop E158 |

## Enforcement: who owns it
The engineer must not be able to rewrite its own checks (engineer-protocol E11, E15). Deny rules are "not a security boundary" (engineer-human-loop E142-E145), so the real boundaries are file ownership, the sandbox, the broker and the server.
- Managed settings: `/etc/claude-code/managed-settings.json`, root-owned, read at the highest precedence; holds deny rules and `disableBypassPermissionsMode`, and no level including CLI flags overrides it (engineer-human-loop E148, §Q9).
- Hooks: the `plugin/hooks/` folder is source only. `setup-root.sh` copies hook scripts to root-owned `/opt/engineer/hooks/` and registers them in the managed-settings file. Whether managed settings accept hook entries is not in the findings: untested default, confirmed by SP10; if not, the builder installs the plugin from a root-owned `/opt/engineer/plugin/` copy and records the mechanism in `docs/versions.md`. Command hooks run outside the sandbox with full access (engineer-human-loop §Q9), so hook scripts read only.
- Supervisor, `audit.sh`, reply parser, state dir: run as `supervisor`; `engineer` cannot write them.
- Secrets: only `secretbroker` reads them; `engineer` calls `sudo agent-run <job>` (engineer-human-loop E58-E60).
- Git: `engineer` has no push credential; branches go up through an `agent-run` job that never pushes to the default branch, and server-side branch protection refuses it anyway (engineer-protocol E41, E77; SP18).

## MCP server configs
| Server | Where configured | Transport | Notes |
| --- | --- | --- | --- |
| Playwright, DeepWiki, Firecrawl | `plugin/.mcp.json` (existing) | stdio / HTTP | Pinned version plus `tools/list` hash (engineer-security E117, E119) |
| Attio MCP | User scope on the VM (`claude mcp add --scope user`), never a project `.mcp.json`, because `-p` shows no MCP trust prompt (engineer-security E110) | Hosted (engineer-existing-systems S-table) | Reads only; writes go through REST scripts (engineer-browser A11) |
| n8n instance MCP | User scope | Served by John's n8n 2.13+ instance (engineer-deploy E51) | Only workflows flagged "Available in MCP" |
| Outreach MCP | User scope, once the app exists | Not stated in the findings | engineer-browser A43 |
| Vercel MCP | User scope, only if Vercel is used | OAuth remote (engineer-deploy E38) | Read-only |
URLs and auth for the four vendor servers are not in the findings: the builder takes them from vendor docs, records them with the `tools/list` hash in `docs/versions.md`, and SP55 and SP56 run first.

## Schemas (builder starting defaults)
Field lists cited where the findings give them; everything else is "builder decides and records in the schema file under `templates/schemas/`".
- `tasks.json` item: `id`, `title`, `status` (`todo|ready|running|done|blocked|needs_john`), `depends_on`, `requirement_ids`, `files`, `files_to_read`, `check` (the evidence command), `evidence_result`, `passes`, `attempts`, `blocked_note` (engineer-planning setup 2; engineer-context §Q7.2; `attempts` and `blocked_note` builder-added).
- `events.jsonl` line: `ts`, `project`, `task_id`, `session_id`, `event` (`task_start|task_end|gate|audit|denial|limit|reset_wait|resume|approval_ask|approval_answer|crash|reconcile`), `exit_code`, `cost_usd`, `head_sha`, `detail` (builder default).
- `RUN_STATUS.json`: `state` (`done|blocked|stopped_by_bound|crashed|waiting_for_reset`), `reason`, `reset_at`, `last_task`, `counts`, `started`, `ended` (states from engineer-context §Q7.5 and engineer-protocol E115; other fields builder default).
- `profile.yaml`: `hard_gates` (default the three), `t2_extra`, `promote` (`hold`), `self_merge` (`false`), `data_classes` per path (`public|internal|customer|health`, engineer-models §Q7), `allowed_processors`, `adopted_rules` (quote plus `path:line`, ruling 8), `unattended` (`true|false`).
- `integrations.yaml` service: `id` (same as `architecture.yaml`), `purpose`, `auth`, `env_vars` (names), `price` with date, `owner_action`, `fallback` (engineer-planning §Q1), plus the 12 checklist fields of engineer-feasibility §Q7: auth type, token lifetime and rotation, scopes and grantor, rate limit and 429, pagination, webhook signature, webhook retries and reconciliation, idempotency, sandbox vs production, API version, plan or role gating, residency and terms; and `edges` (from, to, data, direction) for the generated map.

## Project skeleton (written into each project repo)
```
CLAUDE.md               under 200 lines, "# Compact instructions"; no generated overview
.env.example            names only
docs/plan/              brief.md (3 pages, signed), brief-after.md, requirements.md (EARS),
                        architecture.yaml + generated architecture.mmd, integrations.yaml (the one
                        integration map), contracts/, tasks.json, approval.json, plan.approved.vN,
                        changes/NNNN-<slug>.md, profile.yaml (gates, privacy, data classes, adopted rules)
docs/adr/NNNN-*.md      MADR, the one decision-record path (ruling 10)
docs/map/               as-is pack, notes/<module>.md, snapshots/<tool>.json
docs/DEPENDENTS.md      doc-change manifest
docs/setup.md           the project's ordered setup list
docs/runs/              copied MORNING.md files
tests/acceptance/       frozen acceptance checks
flows/<app>/<task>.spec.ts   recorded browser flows with pre- and postconditions
security/               ASVS checklist, findings.json, allowlist.md, REPORT.md, BRIEF.md
audit/                  AUDIT-<id>.md, waivers.md
decisions/approvals.jsonl
dead-ends.md  PROGRESS.md
model-routing.json, reviews/   only if a second model is enabled
```
Sources: engineer-planning §Q1-Q3; engineer-existing-systems §Repo composition; engineer-browser §Implications 3; engineer-security §Implications 2; engineer-models §Q6.

## MCP servers, connectors, browser tooling
- MCP in `.mcp.json`: Playwright (alternate driver, explicit `--user-data-dir`), DeepWiki, Firecrawl, all pinned with a `tools/list` hash (engineer-security E117, E119). Attio MCP is read-mostly: its writes ask for confirmation (engineer-browser A11), so writes go through REST scripts. n8n instance MCP for workflow edits (engineer-deploy E51). Outreach MCP once an app exists (engineer-browser A43). Vercel MCP stays read-only (engineer-deploy E38).
- claude.ai connectors (Exa, Parallel Search, Context7, Mermaid Chart): usable in interactive `/login` sessions; under Path B the unattended runs lose them (engineer-human-loop E186) and research falls back to the bundled MCP servers (blueprint inference).
- Browser: Playwright CLI skill primary, Playwright MCP alternate, Playwright Test Agents for record and heal, headed Chrome on Xvfb, noVNC for John (engineer-browser T4, T1, T39, S38). Claude in Chrome only on John's machine, attended (engineer-browser T17).

## Superpowers, Beads, Ralph and others
| Source | Kept | Dropped | Evidence |
| --- | --- | --- | --- |
| Superpowers pinned at commit bb92a77 (version label unverified) | Brainstorming hard gate; "decide nothing" plan hygiene; writing-plans; ledger; fresh subagent per task; verification-before-completion; two-part task review; worktree skill; installed pinned by bootstrap | TDD iron law; its task sizing (no numeric cap); local merge to main and the finishing menu (replaced by always-PR) | engineer-planning E21, E25, E81, E82; engineer-context §Q7.1; engineer-protocol E14, E19, E20, E40, E41; engineer-runtime P17 |
| Beads | Upgrade path above about 50 tasks or several agents; `--with-beads` flag | Not in v1; `bd remember` overlaps auto memory; 2026-08-11 data-loss incident | engineer-context §Q1, §Q7 Alternatives; engineer-planning E105; engineer-runtime P19 |
| Ralph | One task per loop, fresh context, one commit per iteration, bash-loop shape under the supervisor | The in-session plugin and unbounded loop (6,239 iterations, about 11.7 hours, issue 1699) | engineer-planning E86; engineer-context §Q7 Rejected; engineer-human-loop E179, E180 |
| cwc-long-running-agents | Read-only evaluator, default FAIL, kill-switch hook idea | As a dependency (README seen only as an excerpt) | engineer-protocol E32-E34; engineer-human-loop E163 |
| spec-kit | NEEDS CLARIFICATION marker, read-only checklist gate, [P] marker, `/clarify` shape | Wholesale install | engineer-planning E3, E5; engineer-intake E23, A12 |
| BMAD | correct-course change tiers | The framework | engineer-planning E37, E38 |
| Spec Guard | sha256 approval binding (idea only) | As a dependency | engineer-planning E29, E61 |
| frankbria | Breaker thresholds (no diff in 3, same failure in 5) | Code | engineer-context §Q7.4 |

How the dropped Superpowers parts are switched off: the template vendors Superpowers at `bb92a77` as plain files, the way John's GTM repo does (engineer-existing-systems J3), without the `test-driven-development` and `finishing-a-development-branch` skill folders (TDD iron law; finishing menu and local merge). Its task sizing is overridden by a CLAUDE.md line that the `plan` skill's task contract wins; Superpowers' own `using-superpowers` skill says CLAUDE.md instructions take precedence over skills (Superpowers `using-superpowers/SKILL.md`, "User Instructions", as vendored in `/home/user/attio-project/.claude/skills/`, read 2026-10-16). Local merge to main is blocked by the missing push credential and branch protection, not by prose.
