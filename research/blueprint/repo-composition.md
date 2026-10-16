# Repo composition

Purpose: how the engineer's template repo, its plugin, the VM and each project repo are laid out, and which outside ideas are kept or dropped.

The engineer ships as one template-plus-plugin repo with a pinned bootstrap, the same shape as this research repo (engineer-runtime P1, P5). Plugin changes below are recommendations; nothing in `plugin/` was changed by this research (engineer-tool-discovery §Implications).

## Template repo
Seeded from the Autonomy-Research repo (this research repo): John creates the private GitHub repo `engineer-template` under his account and pushes a full copy of Autonomy-Research into it, history included (setup.md step 1; name and method are builder defaults; a copy, not a submodule, so the builder can change any file). "Existing" below means a file carried over by that copy; `research/findings/engineer-*.md` and `research/blueprint/` come along as the builder's reference. The VM reads it with a read-only deploy key into `/srv/engineer-template` (root) and the builder's checkout `~engineer/engineer-template`; builder commits reach GitHub only as branches pushed by the `push-branch` broker job with the bot PAT, merged by John (setup.md steps 5, 19-21). Stage 1 replaces this: the template is `engineer/` in Autonomy-Research, read from `/srv/autonomy-research`, with no builder checkout on the VM; repo changes are made in a claude.ai/code cloud session as PRs John merges (setup.md step 21) (updated 2026-10-16, stage-1 plan).

**Stage 1** (updated 2026-10-16, stage-1 plan): there is no separate `engineer-template` repo yet (Open decision 1). The template tree below lives under top-level `engineer/` in Autonomy-Research: `plugin/` in the tree is `engineer/plugin/` (the research-agent's own `plugin/` does not change), `scripts/` is `engineer/scripts/` plus sudo-target wrappers in `engineer/bin/`, tests are `tests/engineer/<area>/`, `docs/versions.md` is `engineer/docs/versions.md`, and John's six decisions are ADRs in `engineer/docs/adr/`. The droplet clones this repo read-only to `/srv/autonomy-research`; `setup-root.sh --install` copies `engineer/` to `/opt/engineer/` and the research-agent skills and agents from `plugin/` into `/opt/engineer/plugin/` unchanged. Not in stage 1: `trial/`, `snapshot/`, the changed research skills, `mint-child`, `oauth-capture` and the TOTP wrapper.
```
plugin/
  skills/      interview, research, tool-scan, repo-triage, spike, system-map, setup   (existing, changed)
               as-is, plan, browser, deploy, security-review, digest                    (new)
               brainstorming, writing-plans, subagent-driven-development, executing-plans,
               verification-before-completion, using-git-worktrees, using-superpowers
                                                  (Superpowers subset vendored at bb92a77)
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
  checks/        verify-all.sh, audit.sh, test-diff guard, pre-merge refusal, parity check, contrast check,
                 vet-card, staleness, integrations-vs-.env.example, n8n export
templates/
  managed-settings.json, egress-install.txt, egress-allowlist.txt, run-defaults.yaml (flow.md),
  schemas/ (tasks, events, run-status, profile, integrations), verify-all checks,
  systemd units (engineer-supervisor, chrome-xvfb, novnc, engineer-remote-control, engineer-channels,
  engineer-egress-proxy; (updated 2026-10-16, stage-1 plan)), project skeleton (below)
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
| plan | New | The plan set (Plan set below), task contract check, change records | engineer-planning §Implications |
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
| auditor | Sonnet class or higher, never Haiku | Read, Glob, Grep, Bash; writes no file; returns JSON `{verdict: PASS|FAIL|NEEDS-JOHN, head_sha, lines[≤15]}`, which the supervisor writes to `audit/AUDIT-<id>.md` | engineer-protocol §Q3, E35, E150 |
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
| `MORNING.md` | Same; copied to `docs/runs/` on the `engineer-records` branch (Records) | Supervisor | engineer-protocol §Q6 |
| Per-night counter | VM state dir, outside the container | Supervisor | engineer-context §Q7.4 |
| `decisions/approvals.jsonl` | `engineer-records` branch of the project repo, committed (Records) | Supervisor parser | engineer-human-loop §Q6 |
| Live plan approval `$STATE_DIR/approvals/<project>.json` (updated 2026-10-16, stage-1 plan) | VM state dir, owned by `supervisor` | Supervisor only, after John's identified reply or PR approval; the approval-hash hook reads this file, because `engineer` could forge one in its own clone | engineer-planning E29, E30 |
| `docs/plan/approval.json` + tag `plan-approved-N` | Copy on the `engineer-records` branch (Records) (updated 2026-10-16, stage-1 plan) | Supervisor | engineer-planning E29, E30 |
| `tasks.json` | `docs/plan/` | Planner; implementer edits only `status` and `passes` | engineer-planning E95; engineer-intake A37 |
| `PROGRESS.md` | Project root | Each task session | engineer-planning E118 |
| `dead-ends.md` | Project root and template | Trials, discovery | engineer-tool-discovery E121; engineer-feasibility B29 |
| `docs/plan/architecture.yaml` | Project repo | The system model; Mermaid views generated with a parity check | engineer-briefing E39 |
| `audit/AUDIT-<id>.md` | `engineer-records` branch (Records); its verdict also goes in the task PR description | Supervisor, from the auditor's JSON | engineer-protocol §Q3 |
| `audit/waivers.md` | Project main branch | John | engineer-protocol §Q3 |
| `trials/<id>/result.json` | VM state dir | Supervisor | engineer-feasibility C19, C53 |
| `/etc/claude-code/managed-settings.json` | VM, root-owned | `setup-root.sh` | engineer-human-loop E148 |
| Kill-switch file `/var/lib/engineer/STOP` (path is a builder default) | VM, directory owned by `supervisor`, not writable by `engineer` | John (`sudo touch`) or supervisor; the PreToolUse hook and the supervisor stop when it exists | engineer-human-loop E158 |

## Enforcement: who owns it
The engineer must not be able to rewrite its own checks (engineer-protocol E11, E15). Deny rules are "not a security boundary" (engineer-human-loop E142-E145), so the real boundaries are file ownership, the sandbox, the broker and the server.
- Managed settings: `/etc/claude-code/managed-settings.json`, root-owned, read at the highest precedence; holds deny rules and `disableBypassPermissionsMode`, and no level including CLI flags overrides it (engineer-human-loop E148, §Q9).
- Hooks: `plugin/hooks/` in the template is the only source. `setup-root.sh --install` copies the scripts to root-owned `/opt/engineer/plugin/hooks/` (updated 2026-10-16, stage-1 plan); `--lock` registers them in the managed-settings file, so the guards are installed last (setup.md, Root vs builder). Whether managed settings accept hook entries is not in the findings: untested default, confirmed by SP10; if not, `--lock` registers them in the root-owned plugin's `hooks.json` under `/opt/engineer/plugin/` (loaded by every session, see Plugin loading) and records the mechanism in `docs/versions.md`. Command hooks run outside the sandbox with full access (engineer-human-loop §Q9), so hook scripts only read.
- Supervisor, `audit.sh`, reply parser, state dir `/var/lib/engineer/`: owned by and run as `supervisor`; `engineer` cannot write them.
- Unix users and sudoers (builder defaults, installed by `setup-root.sh`; findings name only `engineer` and `secretbroker`, engineer-human-loop setup 1):

| User | Runs | Sudoers line |
| --- | --- | --- |
| `engineer` | Interactive and builder sessions; every `claude -p`; holds the Max `/login` | `engineer ALL=(secretbroker) NOPASSWD: /opt/engineer/bin/agent-run` |
| `egress` (updated 2026-10-16, stage-1 plan) | `engineer-egress-proxy.service` (mitmproxy); system user, no login; nftables lets `engineer` and `supervisor` reach only its port | none |
| `supervisor` | `engineer-supervisor.service`; rootless Podman for trial containers (subuid/subgid, engineer-feasibility setup 2) and trial worktrees under `/var/lib/engineer/trials/`; reads project clones through a read-only ACL; talks to Telegram only through broker jobs | `supervisor ALL=(engineer) NOPASSWD: /opt/engineer/bin/run-task` and `supervisor ALL=(secretbroker) NOPASSWD: /opt/engineer/bin/agent-run` |
| John (his own sudo) | `sudo -u secretbroker /opt/engineer/bin/seed <NAME>` and `.../oauth-capture`, from his SSH terminal; `seed` and `oauth-capture` are root-owned, outside the `agent-run` allowlist, and run only through John's own sudo (which asks for his password); `engineer` and `supervisor` may sudo only to `agent-run`, so the model can neither overwrite a secret nor start a consent capture | his normal admin sudo |
| `secretbroker` | `agent-run` jobs: `push-branch`, `open-pr`, `automerge` (Tier 1 now; Tier 2 only once John's own approving review exists) (updated 2026-10-16, John's decision), `api-call`, `tg-send`, `tg-poll`, `hc-ping`; `mint-child` is a later stage (updated 2026-10-16, stage-1 plan) | none |

`run-task <project> <task-id> <profile>` is a root-owned wrapper run as `engineer`. It creates or reuses the task's worktree, then execs `claude -p --plugin-dir /opt/engineer/plugin` with the profile's agent, model, tools, `--max-turns`, `--max-budget-usd` and timeout from `templates/run-defaults.yaml`, so the supervisor cannot pass arbitrary commands. Profiles: `implementer`, `auditor` (started by the supervisor after the implementer exits and the Stop gate passes; `--output-format json --json-schema` for the verdict), `plan-reviewer`, `planner`, `mapper`. How the profile selects the agent definition is a builder default confirmed by SP83. It uses `engineer`'s `/login` (Path A for every run; no API key in v1, and it refuses to start if `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set) (updated 2026-10-16, John's decision).
- Files on the VM (builder defaults): project clones at `/home/engineer/projects/<name>/`, task worktrees at `/home/engineer/projects/<name>.wt/<task-id>/`, both owned by `engineer`; `supervisor` has read-only ACL access to compute `ready` from `tasks.json`. Nobody is in the `docker` group.
- Plugin loading (builder default, confirmed by SP83): every session, interactive or `claude -p`, loads the engineer plugin from root-owned `/opt/engineer/plugin/` with `--plugin-dir`; nothing is installed at user scope, so `engineer` cannot change skills, agents or hooks. `--install` copies `plugin/` there from the reviewed checkout, Superpowers subset included, with `hooks/hooks.json` replaced by an empty stub, so no hook is active before `--lock`; `--lock` installs the real hooks (managed settings or the plugin's `hooks.json`, per SP10). The vendor MCP servers (MCP server configs) are in that plugin's root-owned `.mcp.json`. **One exception:** the Channels Telegram plugin is installed at user scope for `engineer`, because the preview accepts only allowlisted marketplace plugins (engineer-runtime H37); only the daytime Channels session uses it, `run-task` starts sessions with it disabled (builder default, SP83 confirms how), and it carries no approvals (ruling 3).
- CLIs the broker runs (wrangler, the Clay CLI, `gh`, `gcloud`, `cloudflared`) are root-installed (`/opt/engineer/node_modules/.bin` or `/usr/bin`); `agent-run` uses a fixed `PATH` of `/opt/engineer/bin:/usr/bin:/bin`, so `engineer` cannot swap a binary the broker executes. CLI session stores (Clay, `gh`, `gcloud`) live in `secretbroker`'s home.
- Secrets: only `secretbroker` reads them; `engineer` calls `sudo agent-run <job>` (engineer-human-loop E58-E60).
- Git: `engineer` has no push credential; branches go up through an `agent-run` job that never pushes to the default branch, and server-side branch protection refuses it anyway (engineer-protocol E41, E77; SP18).

## Records (builder default)
The supervisor never writes into `engineer`'s clones, and `engineer` never writes `audit/` (F23). Instead the supervisor owns a records clone per project at `/var/lib/engineer/records/<project>/`, checked out on a branch `engineer-records`. It writes `audit/AUDIT-<id>.md`, `docs/runs/<date>-MORNING.md` and appends `decisions/approvals.jsonl` there, commits with the bot's name and email, and pushes with the `push-branch` broker job (bot PAT); `push-branch` refuses the `engineer-records` branch unless the caller is `supervisor`, and only `supervisor` and root can read the records clone (builder defaults). Branch protection on `engineer-records` allows pushes only from the bot and never merges it into main; the auditor verdict is also written into the task PR description through `open-pr`. Trial worktrees come from a supervisor-owned clone under `/var/lib/engineer/trials/`, made from the read-only project clone.

## MCP server configs
| Server | Where configured | Transport | Notes |
| --- | --- | --- | --- |
| Playwright, DeepWiki, Firecrawl | `plugin/.mcp.json` (existing) | stdio / HTTP | Pinned version plus `tools/list` hash (engineer-security E117, E119) |
| Attio MCP | `/opt/engineer/plugin/.mcp.json` (root-owned), never a project `.mcp.json`, because `-p` shows no MCP trust prompt (engineer-security E110) | Hosted (engineer-existing-systems S-table) | Reads only; writes go through REST scripts (engineer-browser A11) |
| n8n instance MCP | `/opt/engineer/plugin/.mcp.json` | Served by John's n8n 2.13+ instance (engineer-deploy E51) | Only workflows flagged "Available in MCP" |
| Outreach MCP | `/opt/engineer/plugin/.mcp.json`, once the app exists | Not stated in the findings | engineer-browser A43 |
| Vercel MCP | `/opt/engineer/plugin/.mcp.json`, only if Vercel is used | OAuth remote (engineer-deploy E38) | Read-only |
URLs and auth for the four vendor servers are not in the findings: the builder takes them from vendor docs, records them with the `tools/list` hash in `docs/versions.md`, and SP55 and SP56 run first.

## Schemas (builder starting defaults)
Field lists cited where the findings give them; everything else is "builder decides and records in the schema file under `templates/schemas/`".
- `tasks.json` item: `id`, `title`, `status` (`todo|ready|running|done|blocked|needs_john`), `depends_on`, `requirement_ids`, `files`, `files_to_read`, `check` (the evidence command), `evidence_result`, `passes`, `attempts`, `blocked_note` (engineer-planning setup 2; engineer-context §Q7.2; `attempts` and `blocked_note` builder-added).
- `events.jsonl` line: `ts`, `project`, `task_id`, `session_id`, `event` (`task_start|task_end|gate|audit|denial|limit|reset_wait|resume|approval_ask|approval_answer|crash|reconcile`), `exit_code`, `cost_usd`, `head_sha`, `detail` (builder default).
- `RUN_STATUS.json`: `state` (`done|blocked|stopped_by_bound|crashed|waiting_for_reset`), `reason`, `reset_at`, `last_task`, `counts`, `started`, `ended` (states from engineer-context §Q7.5 and engineer-protocol E115; other fields builder default).
- `profile.yaml`: `hard_gates` (default the three), `t2_extra`, `promote` (`hold`), `self_merge` (`true`, R16 on from day one (updated 2026-10-16, John's decision)), `data_classes` per path (`public|internal|customer|health`, engineer-models §Q7), `allowed_processors`, `adopted_rules` (quote plus `path:line`, ruling 8), `unattended` (`true|false`).
- `integrations.yaml` service: `id` (same as `architecture.yaml`), `purpose`, `auth`, `env_vars` (names), `price` with date, `owner_action`, `fallback` (engineer-planning §Q1), plus the 12 checklist fields of engineer-feasibility §Q7: auth type, token lifetime and rotation, scopes and grantor, rate limit and 429, pagination, webhook signature, webhook retries and reconciliation, idempotency, sandbox vs production, API version, plan or role gating, residency and terms; and `edges` (from, to, data, direction) for the generated map.

## Plan set and what John signs
The plan set is 8 entries (engineer-planning §Q1), mapped to this blueprint's paths: `docs/plan/brief.md`, `docs/plan/requirements.md` (EARS with fit criteria: the acceptance criteria), `docs/plan/architecture.yaml` (the system model; planning's `architecture.md` becomes its generated `architecture.mmd`), `docs/plan/integrations.yaml` (services, auth, each price with date and the monthly total: the costs), `docs/plan/contracts/`, `docs/plan/tasks.json`, `tests/acceptance/`, and decision records in `docs/adr/` (ruling 10). `docs/plan/profile.yaml` (gates, privacy) is a blueprint addition.
- John signs: `brief.md` (goal, scope, non-goals, risks, costs summary), `requirements.md` (acceptance criteria), `integrations.yaml` (integrations and costs), `profile.yaml` (gates). He does not sign architecture, contracts, tasks or acceptance test code; the `plan-reviewer` checks those against the signed files (engineer-planning §Q2).
- `approval.json` = `{approved_by, date, files: {path: sha256}, scope_version, gates}` (engineer-planning §Q2 step 3). `files` holds exactly those four paths; planning's own list is brief, requirements and integrations (§Q2 step 4), and `profile.yaml` is added because the gates live there. The hook recomputes those four hashes (F20, SP17).

## Project skeleton (written into each project repo)
```
CLAUDE.md               under 200 lines, "# Compact instructions"; no generated overview
.env.example            names only
docs/plan/              brief.md (3 pages, signed), brief-after.md, requirements.md (EARS),
                        architecture.yaml + generated architecture.mmd, integrations.yaml (the one
                        integration map), contracts/, tasks.json, approval.json (records copy), plan.approved.vN,
                        changes/NNNN-<slug>.md, profile.yaml (gates, privacy, data classes, adopted rules)
docs/adr/NNNN-*.md      MADR, the one decision-record path (ruling 10)
docs/map/               as-is pack, notes/<module>.md, snapshots/<tool>.json
docs/DEPENDENTS.md      doc-change manifest
docs/setup.md           the project's ordered setup list
docs/runs/              copied MORNING.md files (engineer-records branch)
tests/acceptance/       frozen acceptance checks
flows/<app>/<task>.spec.ts   recorded browser flows with pre- and postconditions
security/               ASVS checklist, findings.json, allowlist.md, REPORT.md, BRIEF.md
audit/                  AUDIT-<id>.md (engineer-records branch), waivers.md
decisions/approvals.jsonl   (engineer-records branch)
dead-ends.md  PROGRESS.md
model-routing.json, reviews/   only if a second model is enabled
```
Sources: engineer-planning §Q1-Q3; engineer-existing-systems §Repo composition; engineer-browser §Implications 3; engineer-security §Implications 2; engineer-models §Q6.

## MCP servers, connectors, browser tooling
- MCP in `.mcp.json`: Playwright (the driver, `--browser chrome` with an explicit non-default `--user-data-dir` (updated 2026-10-16, John's decision)), DeepWiki, Firecrawl, all pinned with a `tools/list` hash (engineer-security E117, E119). Attio MCP is read-mostly: its writes ask for confirmation (engineer-browser A11), so writes go through REST scripts. n8n instance MCP for workflow edits (engineer-deploy E51). Outreach MCP once an app exists (engineer-browser A43). Vercel MCP stays read-only (engineer-deploy E38).
- claude.ai connectors (Exa, Parallel Search, Context7, Mermaid Chart): usable in interactive `/login` sessions, and kept by unattended runs because every run is Path A (updated 2026-10-16, John's decision) (engineer-human-loop E186; whether `-p` runs see them is SP02); where one is missing, research falls back to the bundled MCP servers (blueprint inference).
- Browser: Playwright MCP primary on branded Chrome (`--browser chrome`), Playwright CLI skill alternate, Playwright Test Agents for record and heal, headed Chrome on Xvfb, noVNC behind Cloudflare Access for John (engineer-browser T4, T1, T39, S38; engineer-host E12) (updated 2026-10-16, John's decision). Claude in Chrome only on John's machine, attended (engineer-browser T17).

## Superpowers, Beads, Ralph and others
| Source | Kept | Dropped | Evidence |
| --- | --- | --- | --- |
| Superpowers pinned at commit bb92a77 (version label unverified) | Brainstorming hard gate; "decide nothing" plan hygiene; writing-plans; ledger; fresh subagent per task; verification-before-completion; two-part task review; worktree skill; vendored into the plugin | TDD iron law; its task sizing (no numeric cap); local merge to main and the finishing menu (replaced by always-PR) | engineer-planning E21, E25, E81, E82; engineer-context §Q7.1; engineer-protocol E14, E19, E20, E40, E41; engineer-runtime P17 |
| Beads | Upgrade path above about 50 tasks or several agents; `--with-beads` flag | Not in v1; `bd remember` overlaps auto memory; 2026-08-11 data-loss incident | engineer-context §Q1, §Q7 Alternatives; engineer-planning E105; engineer-runtime P19 |
| Ralph | One task per loop, fresh context, one commit per iteration, bash-loop shape under the supervisor | The in-session plugin and unbounded loop (6,239 iterations, about 11.7 hours, issue 1699) | engineer-planning E86; engineer-context §Q7 Rejected; engineer-human-loop E179, E180 |
| cwc-long-running-agents | Read-only evaluator, default FAIL, kill-switch hook idea | As a dependency (README seen only as an excerpt) | engineer-protocol E32-E34; engineer-human-loop E163 |
| spec-kit | NEEDS CLARIFICATION marker, read-only checklist gate, [P] marker, `/clarify` shape | Wholesale install | engineer-planning E3, E5; engineer-intake E23, A12 |
| BMAD | correct-course change tiers | The framework | engineer-planning E37, E38 |
| Spec Guard | sha256 approval binding (idea only) | As a dependency | engineer-planning E29, E61 |
| frankbria | Breaker thresholds (no diff in 3, same failure in 5) | Code | engineer-context §Q7.4 |

How Superpowers arrives and how the dropped parts are switched off: the template vendors a subset of https://github.com/obra/superpowers at commit `bb92a77` (the pin John's GTM repo records, /home/user/attio-project/CLAUDE.md; MIT) as plain files into `plugin/skills/`, the way John's GTM repo vendors it (engineer-existing-systems J3), and `--install` copies it into `/opt/engineer/plugin/` with the rest of the plugin. The subset leaves out the `test-driven-development` and `finishing-a-development-branch` skill folders (TDD iron law; finishing menu and local merge). Its task sizing is overridden by a CLAUDE.md line that the `plan` skill's task contract wins; Superpowers' own `using-superpowers` skill says CLAUDE.md instructions take precedence over skills (Superpowers `using-superpowers/SKILL.md`, "User Instructions", as vendored in `/home/user/attio-project/.claude/skills/`, read 2026-10-16). Local merge to main is blocked by the missing push credential and branch protection, not by prose.
