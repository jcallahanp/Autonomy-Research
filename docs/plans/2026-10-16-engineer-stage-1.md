# Engineer Stage 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the blueprint's Phase A, the engineer's template code with no VM and no secrets, under `engineer/` in this repo, update the blueprint to John's six decisions, and write the setup-day checklist, all as one PR John reviews.

**Architecture:** `engineer/` holds everything that later lands in `/opt/engineer/` on the droplet: the `engineer` plugin (skills, agents, hooks, MCP config), sudo-target wrappers (`bin/`), the supervisor, the broker jobs, the checks, egress and root setup scripts, and templates (schemas, run defaults, systemd units, project skeleton). Every script finds its root from its own path and reads its settings from `<root>/etc/engineer.conf`, so tests copy `engineer/` into a temp dir, rewrite that file, drop stub commands in, and run everything without root, systemd, a VM or the network.

**Tech Stack:** Bash, Python 3.12 (stdlib plus PyYAML from `python3-yaml`), jq, git, age; Markdown skills and agents; JSON Schema files checked by a small stdlib validator; Mermaid.

**Spec:** `research/blueprint/` (README, decisions, setup Phase A, repo-composition, stack, flow, spikes, open-questions, requirements-trace) and `research/findings/engineer-host.md` (Recommendation, Q1-Q6), overridden by John's decisions below.

## Where the code lives
Top-level `engineer/` in this repo. A separate `engineer-template` repo is not essential: `setup-root.sh` copies from the checkout it runs in, so the droplet can clone this repo read-only; splitting it out later is Open decision 1.

## John's decisions (override the blueprint)
| # | Decision | Effect on stage 1 |
| --- | --- | --- |
| 1 | Auth Path A: Claude Max via `/login`, unattended runs included; no API key in v1 | Supervisor and `run-task` are built now; Path B rows go; wrappers refuse to start if `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set |
| 2 | GitHub Pro bought; self-merge (R16) on from day one; no shadow or trial weeks | `profile.yaml` default `self_merge: true`; `automerge` broker job; SP18 is a setup-day test that must pass before `--lock`; SP19 dropped |
| 3 | No 1Password: SOPS+age behind `secretbroker` | All `op` rows go; TOTP via a pyotp wrapper later |
| 4 | DigitalOcean US-East, Ubuntu 24.04 LTS, 4 vCPU / 8 GB; headed branded Chrome via Playwright (`channel chrome`), persistent non-default profile, Xvfb, noVNC behind Cloudflare Access; John signs in by hand once; APIs first; stop and notify on any bot challenge; no stealth, proxy rotation or CAPTCHA solvers. Fallbacks only if the setup-day sign-in test fails: a Tailscale exit node at home for the browser's traffic, or the same setup on a home Mac mini | `doctor.sh` checks the size; browser route, challenge check and units built; fallbacks documented in setup-day.md only |
| 5 | Chat control: Remote Control (server mode) plus a Telegram channel/bot; no NanoClaw or OpenClaw in v1; Slack bridge on an API key is a later option | `engineer-remote-control` and `engineer-channels` units; supervisor Telegram bot jobs |
| 6 | First project after setup: the GTM framework over Attio, Clay, n8n; the focus is the framework for automating such projects | Framework code only; vendor snapshot exporters wait for that project's as-is stage |

## Global Constraints
- All new code lives under `engineer/`; tests under `tests/engineer/<area>/`; nothing in `plugin/` (the research-agent plugin) changes.
- Python code runs on Python 3.12 (Ubuntu 24.04) with the stdlib and PyYAML only; no `jsonschema`, no `requests`.
- Bash files start `#!/bin/bash` and `set -euo pipefail` and pass `bash -n`; there is no shellcheck here.
- Each code file is at most 200 lines; each SKILL.md at most 300 lines; each doc at most 250 lines; one concern per file.
- Tests run offline: no network except `127.0.0.1`, no root, no systemd, no VM, no sops, no podman; the whole `tests/engineer/run.sh` finishes in under 60 s.
- No secret values, health data or John's personal data anywhere. Fixture tokens are visibly fake (`TEST-TOKEN-...`, Telegram ids `111111`, `222222`).
- A sudo-target or root-run script never takes a secret, a secret path or a command to run from its caller; it reads root-owned config next to itself (`<root>/etc/`) or under `ETC_DIR`.
- No git command runs as `supervisor`, `secretbroker` or root inside a repo `engineer` can write; they fetch from it (`git fetch file://...`, which only runs `upload-pack`) into a clone they own.
- Every pinned version is recorded in `engineer/docs/versions.md`; user-level pins live in `engineer/templates/bootstrap-packages.txt`. Pins are taken with `npm view <pkg> version` (or the vendor's release page) on build day, with the date.
- Timestamps are ISO-8601 UTC; the night window is in `America/New_York`.
- Behaviour statements are EARS ("When X, the engineer shall Y").
- Blueprint edits carry the marker `(updated 2026-10-16, John's decision)`; plan-made changes carry `(updated 2026-10-16, stage-1 plan)`.
- Unix users: `engineer`, `supervisor`, `secretbroker`, plus `egress` (new, runs the proxy). Paths: `/opt/engineer`, `/etc/engineer`, `/var/lib/engineer`, `/etc/claude-code/managed-settings.json`.
- Implementers do not commit or push; the lead commits each task.

## Conventions every task uses
- **Root:** a `bin/` script uses `root=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)`; a script in `scripts/<area>/` uses two levels up; Python uses `Path(__file__).resolve().parents[N]`. `root` is `engineer/` in the repo and `/opt/engineer` on the droplet.
- **Config:** `<root>/etc/engineer.conf`, `KEY=VALUE` or `KEY="VALUE"`, `#` comments, no `$` expansion, sourced by bash and parsed by `eng.conf.load(root)`. Keys (Task 2 writes the droplet defaults): `STATE_DIR=/var/lib/engineer`, `SPOOL_DIR=/var/lib/engineer/spool`, `RECORDS_DIR=/var/lib/engineer/records`, `KILL_SWITCH=/var/lib/engineer/STOP`, `MIRROR_DIR=/var/lib/engineer/mirrors` (updated 2026-10-16, integration), `PROJECTS_DIR=/home/engineer/projects`, `ETC_DIR=/etc/engineer`, `MANAGED_SETTINGS=/etc/claude-code/managed-settings.json`, `CHROME_PROFILE=/home/engineer/.engineer/chrome-profile`, `DISPLAY=:99`, `NOVNC_PORT=6080`, `PROXY_PORT=3128`, `BROKER_USER=secretbroker`, `SECRETS_FILE=/home/secretbroker/secrets.enc.json`, `AGE_KEY_FILE=/home/secretbroker/.config/sops/age/keys.txt`, `AGE_RECIPIENT_FILE=/home/secretbroker/.config/sops/age/recipient.txt`, `BROKER_STATE_DIR=/home/secretbroker/state`, `TZ_NAME=America/New_York`, `BOT_EMAIL=engineer-bot@users.noreply.github.com`, `TELEGRAM_API=https://api.telegram.org`, `GITHUB_URL=https://github.com`, `RUN_TASK="sudo -n -u engineer /opt/engineer/bin/run-task"`, `AGENT_RUN="sudo -n -u secretbroker /opt/engineer/bin/agent-run"`, `AUDIT_CMD=/opt/engineer/scripts/checks/audit.sh`.
- **Droplet config under `ETC_DIR`** (written on setup day, never in git): `projects.txt` lines `name owner/repo default_branch self_merge=on|off scratch=yes|no owner_login=<github-login>`; `egress.txt` (active allowlist); `egress-added.txt`.
- **Temp-root testing:** `tests/engineer/lib.sh` `mk_root DIR` and `tests/engineer/testlib.py` `make_root(tmp) -> Path` copy `engineer/` to `DIR/opt`, rewrite `etc/engineer.conf` so every path points inside `DIR`, set `BROKER_USER` to the current user, and return the root. Stubs are executables written into `<root>/bin/` (first on every fixed `PATH`) or over a script inside the copy. Stubs log their argv to `DIR/argv.log`.
- **Run tests:** `bash tests/engineer/run.sh [area ...]` runs every `tests/engineer/<area>/test_*.sh` and `python3 -m unittest discover -s tests/engineer/<area> -p 'test_*.py'`; prints `FAIL engineer/<area>: <file>` per failure; exits 1 on any. Python tests import with `sys.path.insert(0, str(REPO / "engineer" / "scripts"))` where `REPO = Path(__file__).resolve().parents[3]`.

## Task graph
| Task | Group | Depends on |
| --- | --- | --- |
| 1 Blueprint, ADRs and diagrams | A | none |
| 2 Scaffold, shared libs, schemas, run defaults | A | none |
| 3 Root setup | B | 2 |
| 4 Host tools and egress | B | 2 |
| 5 Privilege wrappers and broker jobs | B | 2 |
| 6 Supervisor | B | 2 |
| 7 Approvals and chat control | B | 2 |
| 8 Hooks | B | 2 |
| 9 Checks | B | 2 |
| 10 Browser route | B | 2 |
| 11 Skills, agents, Superpowers subset, project skeleton | B | 2 |
| 12 Setup-day guide | C | 1-11 |

Group A runs in parallel. Group B tasks run in parallel with each other (and with Task 1) once Task 2 is in; their file sets are disjoint and cross-task calls go through the interfaces named below, stubbed in tests. Task 12 runs last.

## Review Focus
1. **Engineer-controlled git config.** A project clone whose `.git/config` sets `core.fsmonitor`, `core.hooksPath` or a hook that writes a marker file. Expected: the broker's `push-branch` and the supervisor's `audit.sh` never execute it. Tests: Task 5 `test_push_branch_ignores_repo_config`, Task 9 `test_audit_ignores_repo_config`.
2. **Secret values in argv, logs or stdout.** `seed`, `push-branch`, `api-call`, `tg-send` must never put a value on a command line, in `agent-run.log` or in output. Tests: Task 5 `test_seed_value_not_in_argv`, `test_push_branch_token_not_in_argv`, `test_api_call_output_has_no_secret`; Task 7 `test_tg_send_token_not_logged`.
3. **Adversarial Telegram replies.** A reply from another user id, `all y` while a T2 is open, `CONFIRM` with the wrong phrase or wrong case, an edited message, lookalike Unicode digits. Expected: nothing approves. Tests: Task 7 `test_reply_*`, `test_tg_poll_drops_other_senders`.
4. **Torn state after a crash.** A half-written last line in `events.jsonl`, a `RUN_STATUS.json` interrupted mid-write, a `tasks.json` with a cycle or an unknown dependency. Expected: reconcile skips the torn line, the status file is always whole, the DAG error is a `blocked` night with a reason. Tests: Task 6 `test_events_skip_torn_line`, `test_run_status_atomic`, `test_dag_cycle_blocks_night`.
5. **Path tricks against the guards.** `../` and absolute paths into another project, a symlink into `tests/acceptance/`, `git -C . push`, `/usr/bin/git push`, `env git push`, `bash -c "git push"`, `sh -c`. Expected: denied. Tests: Task 8 `test_protected_*`, `test_git_push_variants`.

---

### Task 1: Blueprint, ADRs and diagrams

**Files:**
- Modify: `research/blueprint/README.md`, `decisions.md`, `setup.md`, `stack.md`, `repo-composition.md`, `flow.md`, `spikes.md`, `open-questions.md`, `requirements-trace.md`
- Modify: `docs/diagrams/engineer-context.mmd`, `engineer-runtime.mmd`, `engineer-approvals.mmd`, `docs/diagrams/index.md`
- Create: `docs/diagrams/engineer-supervisor-loop.mmd`, `docs/diagrams/engineer-browser-route.mmd`
- Create: `engineer/docs/adr/0001-claude-max-login.md`, `0002-self-merge-on.md`, `0003-sops-age-secrets.md`, `0004-digitalocean-chrome-host.md`, `0005-chat-control.md`, `0006-first-project-gtm-framework.md`
- Test: `tests/engineer/blueprint/test_blueprint.sh`

**Interfaces:**
- Produces: the updated blueprint that Tasks 3-12 and the setup-day guide cite; the two new diagram files linked from the index.

Changes to make (each changed ruling or row gets the John's-decision marker; replaced text is rewritten, not struck):
- README: "Decisions John still owes" becomes "Decisions John made" with the six decisions; rows 1, 2, 3, 5 answered; row 4 stays open. Glossary: drop "Shadow mode"; Path A/B entry says Path A chosen; add "Server mode (Remote Control)".
- decisions.md: ruling 1 = Path A for every run, quote of the legal page and the Help Center line kept as the recorded risk (engineer-host Q6 Contradictions), SP01 re-read on setup day; ruling 2 = R16 on from day one under GitHub Pro, enforced by branch protection plus CODEOWNERS, SP18 on setup day, no shadow weeks; ruling 3 = Remote Control server mode as the phone cockpit plus the Telegram channel, supervisor bot for digest and T2 prompts, NanoClaw and OpenClaw not in v1, Slack bridge on an API key later; ruling 6 = SOPS+age only; area 6 = branded Chrome via Playwright `channel chrome`, noVNC behind Cloudflare Access (SSH tunnel as fallback), challenge rule; area 14 = DigitalOcean US-East droplet, fallbacks (Tailscale exit node at home for browser traffic, or home Mac mini), "Persistent Chromium profile" becomes branded Chrome; NanoClaw moves from Kept to "later option".
- setup.md: Phase A step 1 becomes "stage the code under `engineer/` in Autonomy-Research" (Open decision 1); step 3 becomes "ADRs 0001-0006"; step 4 names the droplet; step 5 clones this repo; step 7 says `/login` (`claude auth login`), never `setup-token`; step 14 is done; a new row after step 24: John creates the Cloudflare Tunnel and an Access app for `novnc.<domain>` by hand; step 25 (Path B) deleted; step 30 uses the Access URL, SSH tunnel as fallback; step 32 pyotp only; steps 15-17, 26, 28, 29, 31 move to "Per-project rows" (Open decision 2); step 41 deleted, SP18 runs before step 34; new Phase E row: enable `engineer-remote-control` and `engineer-channels` units. "Verifies all": delete the `ANTHROPIC_API_KEY` row. Add a row per the plan-made changes listed under "Builder changes" below, with the stage-1 marker.
- stack.md: VM row = DigitalOcean Basic 4 vCPU/8 GiB, $48/month, snapshots $0.06/GB-month (engineer-host E64); delete 1Password rows and the API-key secret row; Chrome row = branded Chrome; add Remote Control server mode, Tailscale (fallback, free Personal) and Mac mini M6 ($899, fallback) rows; "Max monthly API credits" row only for a later Slack bridge.
- repo-composition.md: template tree lives under `engineer/`; hooks installed at `/opt/engineer/plugin/hooks/`; approval file location (below); `egress` user; `profile.yaml` `self_merge` default `true`.
- flow.md: F28 self-merge for Tier 1 now; add F41 (challenge rule) and F42 (auth rule) from engineer-host Implications, both EARS.
- spikes.md: SP19 dropped; SP63 reduced to a setup-day sign-in test; SP18 marked setup-day gate for `--lock`; add SP85 Google and Attio sign-in from the droplet IP, SP86 logins survive a snapshot restore, SP87 Remote Control and the Telegram channel on one host at once, SP88 memory with real tabs on 8 GB, SP89 DigitalOcean acceptable-use policy (engineer-host setup-day spikes 1-5).
- open-questions.md: rows 1, 2, 3, 7, 21 answered with the marker; row 13 unchanged.
- requirements-trace.md: R15 met (pending SP04-SP08), R16 met pending SP18, constraint "John is on Max" met.
- Diagrams: `engineer-context.mmd` "Max plan or API key" becomes "Max plan via /login"; `engineer-runtime.mmd` noVNC reached "through Cloudflare Access" and adds the Remote Control server node; `engineer-approvals.mmd` T0 node says Tier 1 self-merges. New `engineer-supervisor-loop.mmd` (flowchart: kill switch, night window, reconcile, pick ready, implementer, check, audit.sh, auditor, PR, tier 1 auto-merge or T1 line, breaker, terminal states). New `engineer-browser-route.mmd` (flowchart: John's phone or computer, Cloudflare Access, cloudflared, noVNC 127.0.0.1:6080, Xvfb :99, branded Chrome profile, Playwright MCP `channel chrome`, egress proxy, challenge check, stop and notify). Index rows for both.
- ADRs: MADR shape (Context, Decision, Consequences, Status: accepted 2026-10-16), each under 40 lines, citing the blueprint and engineer-host evidence ids.

**Builder changes the plan makes (record in setup.md and repo-composition.md with the stage-1 marker):**
- The live plan approval is `$STATE_DIR/approvals/<project>.json`, written by the supervisor; the copy in `docs/plan/approval.json` lives on the `engineer-records` branch. Reason: `engineer` could forge a file in its own clone.
- Hooks live in `/opt/engineer/plugin/hooks/`; `--lock` registers them in managed settings (SP10), else in the plugin's `hooks.json`.
- `chrome-xvfb.service` runs Xvfb and a window manager; Chrome starts on demand (Playwright MCP, or `browser-login` for John's hand sign-in, which launches Chrome with no automation flags).
- Tier 2 PRs merge only after John's own approving review on GitHub; the broker enables auto-merge for them only once that review exists.
- The trial runner, vendor snapshot exporters, changed research skills, `oauth-capture`, `mint-child` and the TOTP wrapper move to later stages (see "Phase A items not in stage 1").

- [ ] **Step 1: Write the failing test** `tests/engineer/blueprint/test_blueprint.sh`:
```bash
m="updated 2026-10-16, John's decision"
for f in README decisions setup stack repo-composition flow spikes open-questions requirements-trace; do
  grep -qF "$m" "research/blueprint/$f.md" || fail "$f.md lacks marker"; done
! grep -q 'Path B only' research/blueprint/setup.md || fail "Path B row still in setup.md"
grep -q 'DigitalOcean' research/blueprint/stack.md && grep -q '\$48' research/blueprint/stack.md || fail "host row"
! grep -qi '1Password `op`' research/blueprint/stack.md || fail "1Password install row"
! grep -q 'or API key' docs/diagrams/engineer-context.mmd || fail "context diagram"
grep -q 'Cloudflare Access' docs/diagrams/engineer-runtime.mmd || fail "runtime diagram"
for d in engineer-supervisor-loop engineer-browser-route; do grep -qF "($d.mmd)" docs/diagrams/index.md || fail "$d not indexed"; done
grep -q 'F41' research/blueprint/flow.md && grep -q 'F42' research/blueprint/flow.md || fail "F41/F42"
for n in 1 2 3 4 5 6; do ls engineer/docs/adr/000$n-*.md >/dev/null 2>&1 || fail "ADR $n"; done
MERMAID_SKIP_RENDER=1 bash tests/check-mermaid.sh >/dev/null || fail "mermaid static checks"
```
(`fail` and the exit code come from `tests/engineer/lib.sh`; if Task 2 has not landed yet, run the file with a local `fail() { echo "FAIL $*"; exit 1; }`.)
- [ ] **Step 2: Run it; expect FAIL** `bash tests/engineer/blueprint/test_blueprint.sh` → `FAIL README.md lacks marker`.
- [ ] **Step 3: Make the edits and write the diagrams and ADRs** listed above.
- [ ] **Step 4: Run; expect PASS** `bash tests/engineer/blueprint/test_blueprint.sh && bash tests/check-mermaid.sh` (the second renders with npx; if npx cannot reach the registry, `MERMAID_SKIP_RENDER=1` and say so).
- [ ] **Step 5: Hand back** the file list; the lead commits.

---

### Task 2: Scaffold, shared libs, schemas, run defaults

**Files:**
- Create: `engineer/README.md`, `engineer/plugin/.claude-plugin/plugin.json`, `engineer/etc/engineer.conf`, `engineer/docs/versions.md`
- Create: `engineer/scripts/eng/__init__.py`, `conf.py`, `schema.py`, `approval.py`, `paths.py`, `hosts.py`, `brokerlib.py`
- Create: `engineer/templates/schemas/{tasks,event,run-status,profile,integrations,approval,approval-record,audit-verdict,run-result}.schema.json`
- Create: `engineer/templates/run-defaults.yaml`, `engineer/templates/protected-paths.txt`, `engineer/templates/bootstrap-packages.txt`
- Create: `tests/engineer/run.sh`, `tests/engineer/lib.sh`, `tests/engineer/testlib.py`, `tests/rules/engineer.sh`
- Test: `tests/engineer/eng/test_conf.py`, `test_schema.py`, `test_approval.py`, `test_paths.py`, `test_hosts.py`, `test_brokerlib.py`, `tests/engineer/eng/test_static.sh`
- Modify: `.github/workflows/validate.yml` (two steps), `CLAUDE.md` (one repo-map line)

**Interfaces (Produces):**
- `eng.conf.load(root: Path) -> dict[str, str]`; raises `ValueError` on a line that is not `KEY=VALUE`.
- `eng.schema.load(root: Path, name: str) -> dict` (reads `templates/schemas/<name>.schema.json`); `eng.schema.validate(instance, schema) -> list[str]` (empty = valid). Supports `type` (string or list), `required`, `properties`, `additionalProperties: false`, `enum`, `items`, `minimum`, `minLength`, `maxLength`, `maxItems`, `pattern`. No `$ref`.
- `eng.approval.SIGNED = ("docs/plan/brief.md", "docs/plan/requirements.md", "docs/plan/integrations.yaml", "docs/plan/profile.yaml")`; `hashes(repo: Path) -> dict[str, str]`; `make(repo, approved_by, source, record_id, scope_version, gates, date) -> dict`; `check(repo: Path, approval: dict | None) -> list[str]` (`["no approval"]` when None; one line per mismatched or missing file).
- `eng.paths.load(path: Path) -> dict` with keys `always`, `existing` (sections `[always]`, `[existing]` in `protected-paths.txt`); `eng.paths.match(rel: str, pattern: str) -> bool` (`**` spans directories, `*` does not); `eng.paths.protected(rel: str, rules: dict, exists: bool) -> str | None` (the matching pattern). `rel` is normalised first: reject absolute or `..`-escaping paths by returning `"outside project"`.
- `eng.hosts.load(path: Path) -> list[str]`; `eng.hosts.allowed(host: str, patterns: list[str]) -> bool` (exact match, or `*.suffix` matching any deeper subdomain but not the bare suffix; case-insensitive; trailing dot stripped; a bare `*` pattern is rejected by `load`).
- `eng.brokerlib.caller() -> str` (`SUDO_USER` when the effective user is `BROKER_USER`, else `getpass.getuser()`); `secret(conf, name) -> str` (runs `sops -d --extract '["NAME"]' SECRETS_FILE` with `SOPS_AGE_KEY_FILE` in the environment; name must match `^[A-Z][A-Z0-9_]*$`); `http(method, url, headers: dict, body: bytes | None, timeout=30) -> tuple[int, bytes]` (urllib, honours `HTTPS_PROXY`); `log(conf, job, exit_code)` appends `ts caller job exit` to `BROKER_STATE_DIR/agent-run.log`.
- Schemas, with the fields in repo-composition.md §Schemas plus: `tasks` top level `{version: 1, tasks: [...]}`, item adds `type` (enum `feat fix docs test chore refactor style perf`); `event` enum adds `check night_start night_end pr_open merge challenge heartbeat`, `detail` is an object; `approval` = `{approved_by, date, files: {path: sha256}, scope_version, gates, source: telegram|pr, record_id}`; `approval-record` = `{ts, item, tier: T1|T2, kind: merge|plan|promote|relogin|deadend|denial|other, ask, answer: yes|no|default|expired, from_id, raw, source: telegram|pr|timeout}`; `audit-verdict` = `{verdict: PASS|FAIL|NEEDS-JOHN, head_sha: ^[0-9a-f]{40}$, lines: maxItems 15}`; `run-result` = `{profile, exit_code, timed_out, session_id, cost_usd, num_turns, subtype, is_error, head_sha, output_tail, permission_denials}`; `profile` `self_merge` default documented as `true`, `hard_gates` enum `money delete_data store_submission`; `integrations` checklist keys `auth_type token_lifetime scopes rate_limit pagination webhook_signature webhook_retries idempotency sandbox api_version plan_gating residency_terms`.
- `run-defaults.yaml` (values from flow.md Run defaults; numbers are untested defaults):
```yaml
night: {start: "22:00", end: "07:00", tz: America/New_York, digest_at: "07:30"}
task: {attempts: 2}
breaker: {no_diff_sessions: 3, same_failure_repeats: 5}
denials_per_kind_per_night: 5
t1: {timeout_hours: 24, reminder_hours: 12, max_open: 5}
heartbeat_minutes: 15
self_merge_cooldown_seconds: 60
cleanup_period_days: 7
profiles:
  implementer:   {agent: implementer,   model: sonnet, max_turns: 60, max_budget_usd: 5, timeout_minutes: 45}
  auditor:       {agent: auditor,       model: sonnet, max_turns: 30, max_budget_usd: 2, timeout_minutes: 15, json_schema: audit-verdict}
  plan-reviewer: {agent: plan-reviewer, model: sonnet, max_turns: 40, max_budget_usd: 3, timeout_minutes: 30}
  planner:       {agent: planner,       model: opus,   max_turns: 60, max_budget_usd: 8, timeout_minutes: 45}
  mapper:        {agent: mapper,        model: sonnet, max_turns: 40, max_budget_usd: 3, timeout_minutes: 30}
  check:         {timeout_minutes: 20}
```
- `protected-paths.txt`: `[always]` `tests/acceptance/**`, `.github/**`, `.claude/**`, `audit/**`, `CODEOWNERS`, `.github/CODEOWNERS`, `docs/plan/approval.json`, `docs/plan/plan.approved.*`, `**/conftest.py`, `pytest.ini`, `tox.ini`, `jest.config.*`, `vitest.config.*`, `.mocharc*`, `CLAUDE.md`; `[existing]` `tests/**`, `**/test_*.py`, `**/*.test.*`, `**/*.spec.*`.
- `bootstrap-packages.txt`: `name<TAB>method<TAB>pin` rows for `@anthropic-ai/claude-code` (2.1.301, the CI pin; at least 2.1.234), `@playwright/mcp`, `@playwright/cli`, `@mermaid-js/mermaid-cli` (11.12.0), `mermaid-lint`, `gitleaks`, `osv-scanner`, `semgrep`; pins from `npm view` or the release page today.
- `engineer.conf` with the keys in Conventions. `plugin.json`: name `engineer`, version `0.1.0`, MIT, author `jcallahanp`, description one sentence.
- `tests/rules/engineer.sh`: runs `bash tests/engineer/run.sh` into a temp file; on failure `fail engineer "<first 3 FAIL lines>"`.
- CI: add `sudo apt-get install -y python3-yaml` before "Structure checks", and `claude plugin validate engineer/plugin --strict` after "Validate plugin".

- [ ] **Step 1: Write the failing tests.** Key cases:
  - `test_conf.py`: `test_parses_quoted_and_plain`, `test_rejects_dollar_expansion_line` (`A=$HOME` raises), `test_bash_and_python_agree` (source the real `engineer/etc/engineer.conf` in bash, print each key, compare to `load`).
  - `test_schema.py`: `test_required_missing`, `test_enum_violation`, `test_additional_properties_false`, `test_pattern`, and `test_every_schema_file_is_valid_json_with_type_object`.
  - `test_approval.py`: write the four signed files in a temp repo; `make(...)["files"]` has 4 sha256 values; `check(repo, a) == []`; edit `brief.md` → one line naming it; `check(repo, None) == ["no approval"]`.
  - `test_paths.py`: `protected("tests/acceptance/a.py", r, False) == "tests/acceptance/**"`; `protected("tests/unit/new_test.py", r, False) is None`; `protected("tests/unit/old.py", r, True) == "tests/**"`; `protected("../other/x", r, False) == "outside project"`; `protected("/etc/passwd", r, False) == "outside project"`; `protected("pkg/conftest.py", r, False) == "**/conftest.py"`.
  - `test_hosts.py`: `allowed("app.attio.com", ["*.attio.com"])`; not `allowed("attio.com", ["*.attio.com"])`; not `allowed("evilattio.com", ["*.attio.com"])`; `allowed("API.Telegram.org.", ["api.telegram.org"])`; `load` raises on a `*` line.
  - `test_brokerlib.py`: with a temp root whose `bin/sops` stub prints `TEST-TOKEN-1`, `secret(conf, "GH_BOT_PAT") == "TEST-TOKEN-1"`; `secret(conf, "bad-name")` raises; `http` against a `http.server` thread on 127.0.0.1 returns `(200, b"ok")`.
  - `test_static.sh`: for every `engineer/**/*.sh` and extensionless file in `engineer/bin/` with a bash shebang: `bash -n` passes and line 2 or 3 is `set -euo pipefail`; every `engineer/**/*.py` passes `python3 -m py_compile`; every code file is at most 200 lines; no file under `engineer/` matches `(sk-ant-|ghp_[A-Za-z0-9]{20,}|github_pat_|xox[baprs]-|AKIA[0-9A-Z]{16}|[0-9]{8,10}:[A-Za-z0-9_-]{35}|BEGIN [A-Z ]*PRIVATE KEY)`.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh eng` → import errors.
- [ ] **Step 3: Implement** the files above. `run.sh` takes optional area names; with none it runs every subdirectory.
- [ ] **Step 4: Run; expect PASS** `bash tests/engineer/run.sh eng && bash tests/check.sh && claude plugin validate engineer/plugin --strict` → `check.sh: all rules pass`.
- [ ] **Step 5: Hand back.**

---

### Task 3: Root setup

**Files:**
- Create: `engineer/scripts/setup-root.sh` (argument parsing and dispatch), `engineer/scripts/setup-root.d/{common.sh,users.sh,packages.sh,tree.sh,managed.sh,units.sh,egress.sh,lock.sh,allow.sh}`
- Create: `engineer/templates/managed-settings.json`, `engineer/templates/sudoers/engineer`, `engineer/templates/apparmor/bwrap`, `engineer/templates/apt-packages.txt`, `engineer/templates/apt-repos.txt`, `engineer/templates/release-pins.txt`
- Create: `engineer/templates/systemd/{engineer-supervisor,chrome-xvfb,novnc,engineer-remote-control,engineer-channels,engineer-egress-proxy}.service`
- Test: `tests/engineer/setup-root/test_install.sh`, `test_lock.sh`, `test_allow.sh`, `test_templates.py`

**Interfaces:**
- Consumes: `templates/managed-hooks.json` (Task 8; tests use a fixture), `scripts/egress/render-nft.py` (Task 4; called as `python3 <root>/scripts/egress/render-nft.py --uid engineer=<n> --uid supervisor=<n>`; in dry run only printed), `templates/egress-install.txt` and `egress-allowlist.txt` (Task 4; tests use fixtures), the unit `ExecStart` targets `bin/xvfb-session`, `bin/novnc-session` (Task 10), `bin/remote-control-session`, `bin/channels-session` (Task 7), `scripts/supervisor/loop.py` (Task 6), `scripts/egress/mitm_addon.py` (Task 4).
- Produces: `setup-root.sh MODE [--dry-run] [--prefix DIR] [--src DIR] [--research-plugin DIR]`, MODE one of `--install`, `--lock`, `--unlock`, `--allow HOST`. `--prefix` (default `/`) is prepended to every path written; `--src` (default the script's `engineer/` dir); `--research-plugin` (default `<src>/../plugin`). In `--dry-run`, every privileged command (`apt-get`, `useradd`, `usermod`, `chown`, `setfacl`, `systemctl`, `nft`, `apparmor_parser`, `git clone` as another user) is printed as `RUN: <cmd>` instead of run; file writes still go under `--prefix`. Without `--dry-run` the script requires EUID 0 and `--prefix /`.

Behaviour (EARS):
- When run with `--install`, setup-root shall create the users `engineer` (login shell), `supervisor`, `secretbroker`, `egress` (system, no login); install `apt-packages.txt` and the repos in `apt-repos.txt`; refuse to install any `release-pins.txt` or `apt-repos.txt` row whose checksum or key fingerprint is `TO-PIN`; copy `--src` to `/opt/engineer` owned by root, with `plugin/hooks/hooks.json` replaced by `{"hooks": {}}` and the research-agent skills `interview research tool-scan repo-triage spike system-map setup` and agents `researcher synthesizer verifier spike-worker` copied from `<repo>/plugin/` into `/opt/engineer/plugin/`; write `/opt/engineer/SOURCE_SHA`; write managed settings without a `hooks` key; install the sudoers file (mode 0440) and units (enable and start `chrome-xvfb`, `novnc`, `engineer-egress-proxy`; install `engineer-supervisor`, `engineer-remote-control`, `engineer-channels` disabled); create `/var/lib/engineer/{spool,records,approvals,checks,audit-clones}` (owner `supervisor`, `spool` group `engineer` mode 1770), `/var/lib/engineer/mirrors` (owner `secretbroker`, group `engineer`, mode 2750: the broker's `sync-mirror` job writes it, `run-task` as `engineer` reads it; updated 2026-10-16, integration), `/etc/engineer/`, the Chrome profile dir (owner `engineer`, 0700) and `/var/log/engineer/`; give `supervisor` read-only ACLs on `/home/engineer/projects`; copy `egress-install.txt` to `/etc/engineer/egress.txt`; load the nft rules and the AppArmor profile.
- When run with `--lock`, setup-root shall merge `templates/managed-hooks.json` into the managed settings `hooks` key, write `/opt/engineer/LOCKED` with the source SHA, write `egress-allowlist.txt` plus `egress-added.txt` to `/etc/engineer/egress.txt`, restart the proxy and enable and start `engineer-supervisor`.
- When run with `--unlock`, setup-root shall remove the `hooks` key and `LOCKED`, stop and disable `engineer-supervisor` and restore the install egress list.
- When run with `--allow HOST`, setup-root shall accept only `^(\*\.)?([a-z0-9-]+\.)+[a-z]{2,}$`, append it once to `egress.txt` and `egress-added.txt`, and restart the proxy.
- If run twice with the same mode, then setup-root shall leave the same files (idempotent).

Template contents:
- `managed-settings.json` (key names to be checked against https://code.claude.com/docs/en/settings and https://code.claude.com/docs/en/permissions while writing, recorded in `engineer/docs/versions.md` notes; SP10 confirms on the droplet): `permissions.disableBypassPermissionsMode: "disable"`; `permissions.deny`: `Read(//home/engineer/.engineer/chrome-profile/**)`, `Read(//home/secretbroker/**)`, `Read(//var/lib/engineer/**)`, `Read(**/.env)`, `Read(**/.env.local)`, `Read(**/.env.production)`, `Bash(git push:*)`, `Bash(git -C * push:*)`; `sandbox: {enabled: true, allowUnsandboxedCommands: false}`; `cleanupPeriodDays: 7`; `autoContinueAtUsageLimit: true`; `env: {HTTPS_PROXY: "http://127.0.0.1:3128", HTTP_PROXY: "http://127.0.0.1:3128", NO_PROXY: "127.0.0.1,localhost"}`.
- `sudoers/engineer`, exactly three rules: `engineer ALL=(secretbroker) NOPASSWD: /opt/engineer/bin/agent-run`, `supervisor ALL=(engineer) NOPASSWD: /opt/engineer/bin/run-task`, `supervisor ALL=(secretbroker) NOPASSWD: /opt/engineer/bin/agent-run`, plus `Defaults:engineer,supervisor env_reset`.
- `apparmor/bwrap`: `abi <abi/4.0>,` `include <tunables/global>` `profile bwrap /usr/bin/bwrap flags=(unconfined) { userns, include if exists <local/bwrap> }` (SP09).
- Units: `engineer-supervisor` `User=supervisor`, `ExecStart=/usr/bin/python3 /opt/engineer/scripts/supervisor/loop.py --projects /etc/engineer/projects.txt`, `Restart=on-failure`, `RestartSec=30`, `ExecStopPost=/usr/bin/sudo -n -u secretbroker /opt/engineer/bin/agent-run hc-ping fail`, `Environment=TZ=America/New_York`, no `NoNewPrivileges` (sudo needs it); `chrome-xvfb` `User=engineer`, `ExecStart=/opt/engineer/bin/xvfb-session`; `novnc` `User=engineer`, `After=chrome-xvfb.service`, `ExecStart=/opt/engineer/bin/novnc-session`; `engineer-remote-control` `User=engineer`, `ExecStart=/opt/engineer/bin/remote-control-session`, `Restart=always`, `RestartSec=30` (it exits after about 10 minutes offline, engineer-host E104); `engineer-channels` `User=engineer`, `Type=forking`, `ExecStart=/usr/bin/tmux new-session -d -s channels /opt/engineer/bin/channels-session`; `engineer-egress-proxy` `User=egress`, `ExecStart=/usr/bin/mitmdump --listen-host 127.0.0.1 --listen-port 3128 --ignore-hosts '.*' -s /opt/engineer/scripts/egress/mitm_addon.py --set engineer_allowlist=/etc/engineer/egress.txt`.
- `apt-packages.txt`: `ca-certificates curl git jq python3 python3-yaml age tmux xvfb fluxbox x11vnc novnc websockify nftables apparmor-utils bubblewrap acl mitmproxy google-chrome-stable nodejs gh cloudflared`. `apt-repos.txt`: Google Chrome, NodeSource 22.x, GitHub CLI, Cloudflare, each `name<TAB>key-url<TAB>fingerprint<TAB>deb-line`. `release-pins.txt`: `sops<TAB>url<TAB>sha256`. Fill fingerprints and checksums from the vendor pages today if reachable; otherwise `TO-PIN` (setup-day item).

- [ ] **Step 1: Write the failing tests.**
  - `test_install.sh`: in the `mk_root` copy, replace `templates/release-pins.txt` and `apt-repos.txt` with fixtures holding fake 64-hex checksums and 40-hex fingerprints; `setup-root.sh --install --dry-run --prefix $T --src <copy> --research-plugin <repo>/plugin` exits 0; `$T/opt/engineer/plugin/hooks/hooks.json` equals `{"hooks":{}}`; `$T/opt/engineer/plugin/skills/research/SKILL.md` exists; `$T/etc/claude-code/managed-settings.json` has no `hooks` key; `RUN: useradd` lines name the four users; `RUN: systemctl enable --now chrome-xvfb.service` present and no `enable` for `engineer-supervisor`; a second run produces the same file tree (`find | sort | sha256sum` equal); `--install` without `--dry-run` as non-root → exit 1 "must run as root"; `--install --dry-run` with a fixture `release-pins.txt` holding a `TO-PIN` row → exit 1 naming that row (the pin check runs in both modes).
  - `test_lock.sh`: after a dry-run install, `--lock --dry-run` adds a `hooks` key equal to the fixture `managed-hooks.json`, writes `LOCKED`, writes the runtime list to `$T/etc/engineer/egress.txt`, prints `RUN: systemctl enable --now engineer-supervisor.service`; `--unlock --dry-run` reverses all three.
  - `test_allow.sh`: `--allow api.attio.com` appends once (twice → one line); `--allow 'evil.com;rm'` → exit 2; `--allow '*'` → exit 2.
  - `test_templates.py`: sudoers non-comment lines equal the three rules plus the Defaults line; no other `NOPASSWD`; managed settings parse as JSON and carry `disableBypassPermissionsMode` and `allowUnsandboxedCommands: false`; each unit has `[Unit]`, `[Service]`, `[Install]`, the `User=` above, and `ExecStart` paths under `/opt/engineer/` or `/usr/bin/`.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh setup-root`.
- [ ] **Step 3: Implement.** `setup-root.sh` sources `setup-root.d/common.sh` (`run()` prints or executes, `write_file prefix-relative`), then the mode files.
- [ ] **Step 4: Run; expect PASS** `bash tests/engineer/run.sh setup-root eng`.
- [ ] **Step 5: Hand back.**

---

### Task 4: Host tools and egress

**Files:**
- Create: `engineer/scripts/bootstrap.sh`, `engineer/scripts/doctor.sh`
- Create: `engineer/scripts/egress/allowlist.py`, `mitm_addon.py`, `render-nft.py`
- Create: `engineer/templates/egress-install.txt`, `engineer/templates/egress-allowlist.txt`
- Test: `tests/engineer/host/test_bootstrap.sh`, `test_doctor.sh`; `tests/engineer/egress/test_allowlist.py`, `test_render_nft.py`, `test_lists.py`

**Interfaces:**
- Consumes: `eng.hosts`, `eng.conf`, `templates/bootstrap-packages.txt`, `docs/versions.md` (Task 2).
- Produces: `render-nft.py --uid NAME=UID ... [--table engineer_egress]` prints the ruleset; `allowlist.py check FILE HOST` exits 0 allowed, 1 denied; `mitm_addon.py` defines `addons = [Allowlist()]` reading option `engineer_allowlist`, answering 403 to a CONNECT or request whose host is not allowed and appending `ts host` to `/var/log/engineer/egress-denied.log`; it imports `mitmproxy` only inside functions so it compiles without it. `bootstrap.sh [--dry-run]`; `doctor.sh [--skip units]` prints `OK <check>` or `FAIL <check>: <detail>` and exits 1 on any FAIL.

Behaviour (EARS):
- When `bootstrap.sh` runs as root, it shall exit 1 ("run as engineer").
- When a `bootstrap-packages.txt` row has pin `latest`, empty or `TO-PIN`, bootstrap shall exit 1 naming the row.
- When `bootstrap.sh` runs, it shall install npm rows with `npm install -g --prefix "$HOME/.local" <pkg>@<pin>` and release rows to `$HOME/.local/bin` after a sha256 check, and install the Channels Telegram plugin at user scope (the one exception, repo-composition.md); with `--dry-run` it prints each command.
- When `doctor.sh` runs, it shall check: Ubuntu 24.04 (`/etc/os-release`), at least 4 CPUs, at least 7.5 GiB RAM, at least 75 GB disk on `/`, no `ANTHROPIC_API_KEY` and no `CLAUDE_CODE_OAUTH_TOKEN` in the environment (Path A; Remote Control refuses setup-token, engineer-host E105), `claude --version` at least the pin, `google-chrome-stable --version` present, the kill switch absent, managed settings present, and (unless `--skip units`) `chrome-xvfb`, `novnc`, `engineer-egress-proxy` active, plus `engineer-supervisor` when `/opt/engineer/LOCKED` exists. Inputs are overridable for tests by `DOCTOR_OS_RELEASE`, `DOCTOR_MEMINFO`, `DOCTOR_NPROC`, `DOCTOR_DISK_GB` (doctor is unprivileged and read-only, so overrides are harmless).
- The nft ruleset shall accept loopback output for the listed uids and log-and-drop all other output for them; every other uid is untouched.
- `egress-install.txt` = runtime list plus `registry.npmjs.org`, `github.com`, `objects.githubusercontent.com`, `codeload.github.com`, `pypi.org`, `files.pythonhosted.org`, `accounts.google.com`, `dash.cloudflare.com`. `egress-allowlist.txt` = `api.anthropic.com`, `claude.ai`, `*.claude.ai`, `github.com`, `api.github.com`, `api.telegram.org`, `hc-ping.com`, `api.uptimerobot.com`, `api.attio.com`, `app.attio.com`, `*.attio.com`, `app.clay.com`, `*.clay.com`, `accounts.google.com`, `api.osv.dev`, `api.deps.dev`, `api.securityscorecards.dev`, `registry.modelcontextprotocol.io`. Header comment in both: provisional; the builder rewrites them from the hosts logged during the sitting (stack.md, Egress). n8n hosts are added on setup day once John says where n8n runs (Open decision 8).

- [ ] **Step 1: Write the failing tests.**
  - `test_render_nft.py`: output for `--uid engineer=1001 --uid supervisor=1002` contains `table inet engineer_egress`, `meta skuid { 1001, 1002 } oif "lo" accept`, `meta skuid { 1001, 1002 } log prefix "engineer-egress-drop " drop`, in that order; `--uid engineer=abc` exits 2.
  - `test_allowlist.py`: `check` exit codes for allowed and denied hosts; the addon's pure function `decide(host, patterns) -> bool` matches `eng.hosts.allowed`; `mitm_addon.py` compiles with `py_compile`.
  - `test_lists.py`: both lists load with `eng.hosts.load`; every runtime host is in the install list; no `*` line; no duplicates.
  - `test_bootstrap.sh`: as the test user with a `mk_root` copy, `--dry-run` prints `npm install -g --prefix` with each npm pin; a fixture with `latest` → exit 1; when `id -u` is stubbed to 0 → exit 1.
  - `test_doctor.sh`: with fixture files for a good host and `--skip units`, and stub `claude`/`google-chrome-stable` in PATH, exit 0 and 8 `OK` lines; with `ANTHROPIC_API_KEY=x` → `FAIL no_api_key`; with `DOCTOR_NPROC=2` → `FAIL cpu`; with an `/etc/os-release` fixture of 22.04 → `FAIL os`.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh host egress`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run; expect PASS** same command.
- [ ] **Step 5: Hand back.**

---

### Task 5: Privilege wrappers and broker jobs

**Files:**
- Create: `engineer/bin/agent-run`, `engineer/bin/seed`, `engineer/bin/run-task`
- Create: `engineer/etc/broker-jobs.txt`, `engineer/etc/broker-services.json`
- Create: `engineer/scripts/broker/jobs/{push-branch,open-pr,automerge,api-call,hc-ping}`, `engineer/scripts/broker/mirror.sh`
- Create: `engineer/templates/prompts/{implementer,auditor,plan-reviewer,planner,mapper}.md`, `engineer/templates/projects.txt.example`
- Test: `tests/engineer/broker/test_agent_run.sh`, `test_seed.sh`, `test_push_branch.sh`, `test_open_pr.sh`, `test_automerge.sh`, `test_api_call.py`, `test_hc_ping.sh`; `tests/engineer/run-task/test_run_task.sh`

**Interfaces:**
- Consumes: `eng.brokerlib`, `eng.conf`, `run-defaults.yaml`, `tasks.schema.json` (Task 2); `scripts/checks/merge-tier.py` (Task 9: stdin `{"title", "files": [{"path","additions","deletions"}]}`, stdout `{"tier": 1|2, "reasons": [...]}`; tests replace it in the temp root with a stub).
- Produces:
  - `agent-run JOB [ARGS...]`: fixed `PATH=<root>/bin:/usr/bin:/bin`; refuses unless the effective user is `BROKER_USER` (exit 77); `JOB` must match `^[a-z][a-z0-9-]*$`, be listed in `<root>/etc/broker-jobs.txt` as `job<TAB>callers` and exist under `<root>/scripts/broker/jobs/` (else exit 64 "job not allowed"); the caller from `eng.brokerlib.caller()` must be in that row (else exit 77); exports `AGENT_RUN_CALLER`; execs the job with stdin passed through; logs via `brokerlib.log`. Rows: `push-branch engineer,supervisor`, `open-pr engineer,supervisor`, `automerge supervisor`, `api-call engineer,supervisor`, `hc-ping supervisor`, `tg-send supervisor`, `tg-poll supervisor` (the last two are Task 7's job files).
  - `seed NAME` (run by John only, through his own sudo; not in `broker-jobs.txt`): reads the value from the terminal with echo off (or stdin when not a tty), refuses empty, decrypts the SOPS file into memory, merges `NAME` in Python reading the value from a pipe, re-encrypts with `sops -e --age "$(cat AGE_RECIPIENT_FILE)" --input-type json --output-type json /dev/stdin` to a temp file in `BROKER_STATE_DIR` and renames it. The value never appears in argv.
  - `push-branch REPO_DIR BRANCH [--tag plan-approved-N]`: `REPO_DIR` must be `PROJECTS_DIR/<name>` or a worktree `PROJECTS_DIR/<name>.wt/<id>` (callers engineer or supervisor) or `RECORDS_DIR/<name>` (supervisor only); `<name>` must be in `ETC_DIR/projects.txt`. Refuses the project's default branch, `main`, `master`, anything containing `..` or starting with `-`, and `engineer-records` unless the caller is supervisor; tags only for supervisor and only `^plan-approved-[0-9]+$`. Fetches the branch with `git -c safe.directory=REPO_DIR fetch --no-tags file://REPO_DIR +refs/heads/B:refs/heads/B` into a broker-owned bare mirror `BROKER_STATE_DIR/mirrors/<name>.git` (`mirror.sh`), then pushes from the mirror to `GITHUB_URL/<owner/repo>.git` (no `--force`), with the token passed as `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.<GITHUB_URL>/.extraheader GIT_CONFIG_VALUE_0="AUTHORIZATION: basic <base64(x-access-token:PAT)>"` in the environment. In tests `GITHUB_URL=file://$T/remotes`.
  - `open-pr PROJECT BRANCH TITLE` (body on stdin): title must match `^(feat|fix|docs|test|chore|style|refactor|perf|build|ci)(\([a-z0-9-]+\))?!?: .{1,72}$`; runs `gh pr create --repo owner/repo --head BRANCH --base DEFAULT --title TITLE --body-file -` with `GH_TOKEN` in the environment; prints `{"number": N, "url": "..."}`.
  - `automerge PROJECT PR`: requires `self_merge=on` for the project in `projects.txt`; reads `gh pr view PR --json title,files,reviews,headRefOid`; pipes title and files to `merge-tier.py`; tier 1 → `gh pr merge PR --auto --squash` and prints `{"tier":1,"auto_merge":true}`; tier 2 → enables auto-merge only if `reviews` holds an `APPROVED` review by `owner_login` on `headRefOid`, else prints `{"tier":2,"auto_merge":false,"reasons":[...]}` and exits 3.
  - `api-call SERVICE METHOD PATH` (body on stdin): service from `etc/broker-services.json`, e.g. `{"attio": {"base": "https://api.attio.com/v2", "secret": "ATTIO_API_KEY", "header": "Authorization", "format": "Bearer {}", "methods": ["GET"]}, "n8n": {"base_secret": "N8N_BASE_URL", "suffix": "/api/v1", "secret": "N8N_API_KEY", "header": "X-N8N-API-KEY", "format": "{}", "methods": ["GET"]}, "github": {"base": "https://api.github.com", "secret": "GH_BOT_PAT", "header": "Authorization", "format": "Bearer {}", "methods": ["GET"]}}` (base URLs and header names checked against vendor docs on setup day, SP60, SP66); `PATH` must start with `/`, contain no `..`, `//` or scheme; `METHOD` must be in `methods`; prints the status line to stderr and the body to stdout, with any occurrence of the secret replaced by `[REDACTED]`.
  - `hc-ping [start|fail|ok]`: GET `HC_PING_URL` plus `/start` or `/fail`.
  - `run-task PROJECT TASK_ID PROFILE [--resume SESSION_ID] [--dry-run]`: runs as `engineer`; `--resume` is accepted only for `implementer` and only with `^[0-9a-f-]{36}$`, and adds `--resume SESSION_ID` to the `claude` argv; `PROJECT` matches `^[a-z0-9][a-z0-9-]{0,39}$` and is in `projects.txt`; `TASK_ID` matches the tasks schema pattern and exists in the project's `docs/plan/tasks.json`; `PROFILE` is a key of `profiles` in run-defaults; refuses when the kill switch exists (exit 75), when `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set (exit 78), and for any profile but `check` when `<root>/LOCKED` is absent unless the project row has `scratch=yes` (exit 75). Creates or reuses the worktree `PROJECTS_DIR/<p>.wt/<id>` on branch `task/<id>` from the default branch. Sets `ENGINEER_TASK_ID`, `ENGINEER_PROJECT`, `ENGINEER_UNATTENDED=1`. Profile `check` runs the task's `check` with `timeout` in the worktree. Other profiles run `timeout --kill-after=30s <m>m claude -p <prompt> --plugin-dir <root>/plugin --agent <agent> --model <model> --max-turns <n> --max-budget-usd <b> --permission-mode auto --permission-prompts none --output-format json` plus `--json-schema <root>/templates/schemas/<s>.schema.json` when the profile names one; the prompt is `templates/prompts/<profile>.md` with `{{TASK_ID}}` and `{{PROJECT}}` replaced. Prints one `run-result` JSON line (last 200 output lines in `output_tail`, `head_sha` of the worktree). `--dry-run` prints `{"argv": [...], "cwd": "...", "env": {...}}` instead of running. `--agent` and plugin loading are confirmed by SP83.

- [ ] **Step 1: Write the failing tests** (all against a `mk_root` copy; `sops`, `gh`, `claude` are stubs in `<root>/bin`; GitHub is a local bare repo under `$T/remotes`).
  - `test_agent_run.sh`: unknown job → 64; listed job, caller `engineer` for `tg-send` → 77; effective user not `BROKER_USER` → 77; `PATH` seen by a stub job is `<root>/bin:/usr/bin:/bin`; a log line is written with no args.
  - `test_seed.sh`: `printf 'TEST-SECRET-9\n' | seed ATTIO_API_KEY` → stub sops decrypt shows the key; `grep -r TEST-SECRET-9 $T/argv.log` finds nothing (`test_seed_value_not_in_argv`); empty input → exit 1; `seed bad-name` → exit 2.
  - `test_push_branch.sh`: pushes `task/t1` to the bare remote; `main` → exit 65; caller engineer with `engineer-records` → exit 77; `--tag v1` → exit 65; REPO_DIR outside `PROJECTS_DIR` → exit 65; `test_push_branch_ignores_repo_config`: the source clone sets `core.fsmonitor = touch $T/pwned` and a `pre-push` hook doing the same → after the push, `$T/pwned` does not exist; `test_push_branch_token_not_in_argv`: `TEST-TOKEN-PAT` absent from `argv.log` and from `ps`-style capture (stub `git` wrapper logging argv).
  - `test_open_pr.sh`: good title → stub `gh` argv has `--base main --head task/t1`; `"update stuff"` → exit 65.
  - `test_automerge.sh`: stub merge-tier tier 1 → `gh pr merge 7 --auto --squash` called; tier 2 without review → exit 3 and no merge call; tier 2 with `APPROVED` by `owner_login` on head → merge called; `self_merge=off` → exit 3.
  - `test_api_call.py`: a local `http.server` stands in for Attio (services file in the temp root points `base` at it); GET `/self` returns the body with the bearer header received; POST → exit 65; `PATH` `/../x` and `http://evil` → exit 65; `test_api_call_output_has_no_secret`: server echoes the auth header in its body → stdout shows `[REDACTED]`.
  - `test_hc_ping.sh`: stub `curl`/local server receives `/fail`.
  - `test_run_task.sh`: `--dry-run` implementer argv contains `--permission-mode auto --permission-prompts none --max-turns 60 --max-budget-usd 5 --plugin-dir <root>/plugin --agent implementer` and `env.ENGINEER_UNATTENDED == "1"`; worktree created on `task/t1`; kill switch → 75; `ANTHROPIC_API_KEY=x` → 78; project `Bad_Name` → 65; unknown task id → 65; no `LOCKED` and `scratch=no` → 75; `check` profile runs the task check and prints `run-result` with `exit_code` 0.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh broker run-task`.
- [ ] **Step 3: Implement.** Python for `api-call`; bash for the rest.
- [ ] **Step 4: Run; expect PASS** same command.
- [ ] **Step 5: Hand back.**

---

### Task 6: Supervisor

**Files:**
- Create: `engineer/scripts/supervisor/{dag.py,events.py,run_status.py,breaker.py,limits.py,nightwin.py,morning.py,spool.py,records.py,steps.py,loop.py}`
- Test: `tests/engineer/supervisor/test_dag.py`, `test_events.py`, `test_run_status.py`, `test_breaker.py`, `test_limits.py`, `test_nightwin.py`, `test_morning.py`, `test_spool.py`, `test_loop.py`

**Interfaces:**
- Consumes: `eng.*` (Task 2); commands from `engineer.conf`: `RUN_TASK`, `AGENT_RUN`, `AUDIT_CMD`; `python3 <root>/scripts/approvals/digest.py` and `apply-replies.py` and `<root>/bin/approve-plan` (Task 7, CLI contracts below). Tests stub every one in the temp root.
- Produces:
  - `dag.load(path) -> list[dict]` (validates with the tasks schema; raises `ValueError` listing errors); `dag.find_cycle(tasks) -> list[str] | None`; `dag.ready(tasks, done: set, blocked: set, running: set) -> list[str]` in file order; unknown `depends_on` ids raise.
  - `events.append(path, event: dict) -> dict` (adds `ts`, validates, writes one line with `flush` and `fsync`); `events.read(path) -> list[dict]` (skips a torn or invalid line, counting it); `events.state(events) -> {"done": set, "blocked": set, "needs_john": set, "running": set, "attempts": dict}`; `events.reconcile(path) -> list[str]` (tasks `running` without `task_end`; appends a `crash` then a `reconcile` event for each and counts the attempt).
  - `run_status.write(path, state, **fields)` writes a temp file then `os.replace`; validates the run-status schema.
  - `breaker.task_blocked(attempts, max_attempts=2) -> bool`; `breaker.night_stop(sessions: list[dict], no_diff=3, same_failure=5) -> str | None` (`sessions` items `{"diff": bool, "failure_sig": str | None}`; three consecutive no-diff sessions, or one failure signature five times in the night).
  - `limits.classify(text: str) -> {"kind": "session"|"weekly"|None, "reset_at": iso | None}`; patterns are provisional and replaced by the real text from SP07; fixtures say so.
  - `nightwin.in_window(now_utc, start, end, tz) -> bool` (window crosses midnight); `nightwin.digest_due(now_utc, last_digest_date, digest_at, tz) -> bool`.
  - `morning.render(events, run_status) -> str` (Markdown: state line, done, blocked with notes, needs-John, PRs, denials, cost total, open T1 count).
  - `spool.ingest(spool_dir, events_path, project) -> int` moves hook-tap lines (`event_tap.py`, Task 8) into `events.jsonl` as `denial`/`limit`/`gate` events with `detail.source = "hook"`, then deletes the ingested file; invalid lines are dropped and counted. (updated 2026-10-16, integration) Each file is first renamed to a private `<name>.ingesting.<pid>` and only that name is read and unlinked, so a hook append during a pass lands in a fresh file; leftover `.ingesting.*` files from a crashed pass are ingested on the next pass.
  - `records.write_and_push(records_dir, project, relpath, content, message, run)` writes inside the supervisor-owned records clone on `engineer-records`, commits as the bot (name `engineer-bot`, email from conf `BOT_EMAIL`) and calls `AGENT_RUN push-branch <records_dir> engineer-records`.
  - `steps.run_task(conf, project, task_id, profile) -> dict` (parses the `run-result` line; a non-JSON reply becomes `{"exit_code": n, "is_error": true}`), `steps.audit(conf, project, task_id) -> dict` (runs `AUDIT_CMD`; JSON `{verdict, head_sha, lines}`), `steps.open_pr(...)`, `steps.automerge(...)`, `steps.digest(...)`, `steps.poll_replies(...)`.
  - `loop.py [--projects FILE] [--project NAME] [--once] [--now ISO]`; `--once` runs a single iteration for tests.
- Task 7 CLIs used (updated 2026-10-16, integration): `digest.py --events E --records R --now ISO [--max-open N] [--json-object]` prints a JSON list of message strings (each open T2 item first, then the T1 digest); the supervisor passes `--json-object` and reads `{"messages": [...], "shown": [item, ...]}`, where `shown` is the T1 items the digest lists (the ones `all y` may cover); `apply-replies.py --events E --records R --now ISO [--timeout-hours H]` reads `tg-poll` JSON lines on stdin, appends `approval-record` lines to R and prints the applied decisions as JSON lines `{item, kind, answer, ref}`; `approve-plan PROJECT --record-id ID --item N --by NAME --source telegram|pr` (the supervisor calls it with `--record-id item-N --item N --by john --source telegram`).

Behaviour (EARS; F22-F29, F39, F40):
- While the kill switch file exists, the supervisor shall start no task and shall write `RUN_STATUS.json` `stopped_by_bound` with reason `kill switch`.
- When outside the night window, the supervisor shall run no `implementer` session but shall still poll replies and send the digest when due.
- When an iteration starts, the supervisor shall ingest the spool, reconcile, ping `hc-ping`, then pick the first ready task.
- When a task is ready, the supervisor shall append `task_start`, run `RUN_TASK <p> <id> implementer`, append `task_end` with `exit_code`, `cost_usd`, `session_id`; then run the `check` profile (store its result as `STATE_DIR/checks/<p>/<id>.json`), `AUDIT_CMD`, and on a script PASS the `auditor` profile; it shall accept the auditor verdict only if it validates against the schema and its `head_sha` equals the script's `head_sha`.
- When the verdict is PASS, the supervisor shall write `audit/AUDIT-<id>.md` through `records`, open the PR (title `<type>: <task title>` cut to 72 characters), call `automerge`, record `done`, and on a tier-2 answer add a T1 `merge` ask with the PR URL.
- If a task fails twice, then the supervisor shall record it `blocked` with the last reason; if the same FAIL repeats, `needs_john`; if `breaker.night_stop` fires or the denial limit per kind is reached, then the supervisor shall end the night `stopped_by_bound`.
- When `limits.classify` reports a session limit, the supervisor shall write `waiting_for_reset` with `reset_at` and wait (`autoContinueAtUsageLimit` is on in managed settings); when the run ended anyway it shall resume with `RUN_TASK <p> <id> implementer --resume <session_id>`; a weekly limit ends the night `stopped_by_bound`.
- When the night reaches a terminal state, the supervisor shall write `RUN_STATUS.json`, render `MORNING.md` into `STATE_DIR/<p>/`, push a copy to `docs/runs/<date>-MORNING.md` on `engineer-records`, and send the digest messages through `tg-send`.
- If the loop gets SIGTERM, then it shall write `stopped_by_bound` reason `stopped by systemd`; if it raises, then it shall write `crashed` with the exception type.
- If `tasks.json` is invalid or has a cycle, then the supervisor shall write `blocked` with the error and start no task.


- [ ] **Step 1: Write the failing tests.** Key cases: `test_dag_ready_respects_depends_on`, `test_dag_cycle_detected`, `test_dag_unknown_dependency_raises`; `test_events_skip_torn_line` (append two, write `{"ts": "2026` with no newline, `read` returns 2), `test_reconcile_marks_running_as_crash`; `test_run_status_atomic` (patch `os.replace` to raise, the old file is unchanged and still valid JSON); `test_breaker_three_no_diff`, `test_breaker_same_failure_five`; `test_limits_session_and_weekly` (fixtures marked synthetic); `test_window_crosses_midnight` (03:00 ET in, 12:00 ET out, DST date included); `test_morning_lists_blocked_note`; `test_spool_ingest_drops_invalid`; in `test_loop.py`, a temp root with stub `RUN_TASK` returning scripted `run-result` lines, stub `AUDIT_CMD` returning PASS with a fixed SHA, stub auditor verdict, stub `AGENT_RUN` logging calls: `test_happy_path_opens_pr_and_automerges`, `test_auditor_sha_mismatch_is_fail`, `test_two_failures_block_task`, `test_kill_switch_stops`, `test_weekly_limit_stops_night`, `test_dag_cycle_blocks_night`, `test_sigterm_writes_status`.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh supervisor`.
- [ ] **Step 3: Implement** the modules in the order listed; `loop.py` stays under 200 lines by delegating to `steps.py`.
- [ ] **Step 4: Run; expect PASS** same command.
- [ ] **Step 5: Hand back.**

---

### Task 7: Approvals and chat control

**Files:**
- Create: `engineer/scripts/approvals/{items.py,digest.py,replies.py,apply-replies.py}`, `engineer/bin/approve-plan`
- Create: `engineer/scripts/broker/jobs/tg-send`, `engineer/scripts/broker/jobs/tg-poll`
- Create: `engineer/bin/remote-control-session`, `engineer/bin/channels-session`
- Test: `tests/engineer/approvals/test_items.py`, `test_digest.py`, `test_replies.py`, `test_apply_replies.py`, `test_approve_plan.sh`, `test_tg_jobs.py`, `test_chat_sessions.sh`

**Interfaces:**
- Consumes: `eng.schema`, `eng.approval`, `eng.brokerlib`, `run-defaults.yaml` (Task 2); `AGENT_RUN push-branch ... --tag plan-approved-N` (Task 5, stubbed).
- Produces:
  - `items.open_items(events, records, now) -> dict[int, dict]`: every `approval_ask` event (`detail`: `item`, `tier`, `kind`, `text`, `default`, `reversible`, `phrase` for T2, `ref`) without a record; `items.apply_timeouts(open, now, timeout_h=24) -> list[record]` (only reversible T1 items older than the timeout, `answer: default`, `source: timeout`; never T2); `items.reminders(open, now, reminder_h=12) -> list[int]`.
  - `digest.py --events E --records R --now ISO [--max-open N] [--json-object]` (updated 2026-10-16, integration): prints a JSON list of message strings, each open T2 item (`render_t2`) first, then the T1 digest (`render`); `--max-open` defaults to `t1.max_open` in `run-defaults.yaml` (5); with `--json-object` it prints `{"messages": [...], "shown": [item, ...]}`, the T1 items the digest lists.
  - `digest.render(open_items, max_open=5) -> list[str]`: one line per T1 item `N. <text> (default: <default>). Reply "N y" or "N n".`, oldest first, at most `max_open` with `+K more in MORNING.md`, messages of at most 4096 characters; `digest.render_t2(item) -> str`: `HARD GATE N: <text>` / `To approve, reply exactly: CONFIRM N <PHRASE>` / `No reply means no.`
  - `replies.parse(text, open_items) -> {"decisions": [{"item", "answer"}], "errors": [str]}`. Grammar: tokens split on whitespace; `<n> y|n` pairs (ASCII digits only), `all y` / `all n` for every open T1 item, `CONFIRM <n> <PHRASE...>` matching the item's phrase exactly (case-sensitive, whole rest of the message). A T2 item answered by anything but its exact CONFIRM is an error; `all` never touches T2; an unknown item number, an unknown token or an empty message is an error and approves nothing in that message.
  - `apply-replies.py` CLI as in Task 6; only messages whose `from_id` is in the tg-poll output (tg-poll already filters) are parsed; edited messages (`edited: true`) are ignored.
  - `approve-plan PROJECT --record-id ID --item N --by NAME --source telegram|pr` (updated 2026-10-16, integration): runs as supervisor; copies the four signed files out of the project clone (regular files only, no symlinks) and refuses (exit 65) unless each still has the sha256 that plan ask N carried in `STATE_DIR/<p>/events.jsonl`; with `--source telegram` it also needs John's `yes` for N in the records clone; writes `STATE_DIR/approvals/<p>.json` (approval schema; `scope_version` = previous + 1); writes the same JSON to `docs/plan/approval.json` and creates tag `plan-approved-N` in the records clone; pushes with `AGENT_RUN push-branch RECORDS_DIR/<p> engineer-records --tag plan-approved-N`.
  - `tg-send` (stdin text): splits on line boundaries into chunks of at most 4096 characters; POSTs `TELEGRAM_API/bot<TG_SUPERVISOR_TOKEN>/sendMessage` with `chat_id` = secret `TG_JOHN_CHAT_ID`; prints `{"sent": n}`; the token never reaches argv, logs or stdout.
  - `tg-poll`: GET `getUpdates?offset=<stored+1>&timeout=0`; keeps only `message` updates whose `from.id` equals secret `TG_JOHN_USER_ID`; marks `edited_message` updates `edited: true`; stores the last `update_id` in `BROKER_STATE_DIR/tg-offset`; prints JSON lines `{update_id, from_id, date, text, edited}`; prints the dropped count to stderr.
  - `remote-control-session`: refuses (exit 78) if `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set; `cd PROJECTS_DIR`; `exec claude remote-control` (server mode, engineer-host E103; exact flags confirmed on setup day). `channels-session`: same refusal; `exec claude --channels plugin:telegram` (setup.md step 39).

Behaviour (EARS; ruling 3, F38, F39):
- When a T2 item is open, the engineer shall send it as its own message at once and shall never apply a default to it.
- When a reply is unparseable, the engineer shall approve nothing from that message and shall add one T1 line saying the reply was not understood.
- When John approves the plan item, the supervisor shall run `approve-plan`, and code edits shall be allowed only while the hashes match (hook, Task 8).

- [ ] **Step 1: Write the failing tests.**
  - `test_replies.py`: `parse("1 y 2 n", open{1:T1,2:T1})` → two decisions; `parse("all y", {1:T1, 4:T2})` → item 1 only; `parse("4 y", {4:T2})` → error, no decision; `parse("CONFIRM 4 SPEND $12", {4: T2 phrase "SPEND $12"})` → yes; `"confirm 4 spend $12"` → error; `"CONFIRM 4 SPEND $13"` → error; `"１ y"` (full-width digit) → error; `"1 y 9 y"` with 9 unknown → errors and no decisions; `""` → error; `"1 yes please"` → error.
  - `test_digest.py`: six open T1 items → five lines plus `+1 more in MORNING.md`; a 5,000-character item text → two messages each at most 4096; `render_t2` text equals the three lines above.
  - `test_items.py`: reversible T1 at 25 h gets `default`; non-reversible T1 at 25 h stays open; T2 at 100 h stays open; reminder at 12 h.
  - `test_apply_replies.py`: records appended validate against `approval-record`; an `edited: true` line is ignored.
  - `test_approve_plan.sh`: writes `STATE_DIR/approvals/demo.json` with four hashes and `scope_version` 1, then 2 on a second run; stub `AGENT_RUN` called with `--tag plan-approved-1`.
  - `test_tg_jobs.py`: local server as Telegram; `tg-send` with 5,000 characters → two POSTs; `test_tg_send_token_not_logged` (`TEST-TOKEN-TG` absent from stdout, stderr, `agent-run.log`); `test_tg_poll_drops_other_senders` (updates from `111111` and `222222`, secret user `111111` → one line out, stderr `dropped 1`); offset file advanced.
  - `test_chat_sessions.sh`: stub `claude` logs argv; `remote-control-session` → argv `remote-control`; with `CLAUDE_CODE_OAUTH_TOKEN=x` → exit 78; `channels-session` → `--channels plugin:telegram`.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh approvals`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run; expect PASS** same command.
- [ ] **Step 5: Hand back.**

---

### Task 8: Hooks

**Files:**
- Create: `engineer/plugin/hooks/hooks.json`, `engineer/templates/managed-hooks.json`
- Create: `engineer/plugin/hooks/{hookctx.py,session_start.py,pre_tool_use.py,post_tool_use.py,stop_gate.py,event_tap.py}`, `engineer/plugin/hooks/guards/{__init__.py,kill.py,protected.py,git.py,plan_hash.py,vendor.py,browser.py,deploy.py}`
- Create: `engineer/templates/vendor-cli-deny.txt`, `engineer/templates/deploy-deny.txt`
- Test: `tests/engineer/hooks/test_pre_tool_use.py`, `test_protected.py`, `test_git.py`, `test_plan_hash.py`, `test_browser_guard.py`, `test_stop_gate.py`, `test_session_start.py`, `test_post_tool_use.py`, `test_event_tap.py`, `test_registration.py`

**Interfaces:**
- Consumes: `eng.conf`, `eng.paths`, `eng.hosts`, `eng.approval`, `templates/protected-paths.txt` (Task 2); `templates/browser-allowlist.txt` (Task 10; tests use a fixture; a missing file means deny every navigation).
- Produces:
  - Hook input is the JSON on stdin (`tool_name`, `tool_input`, `cwd`, `session_id`, `hook_event_name`, `stop_hook_active`). `hookctx.load(event) -> Ctx` with `root` (`CLAUDE_PLUGIN_ROOT/..`), `conf`, `project_dir` (git top level of `cwd`), `project` (name of the main clone, so `<p>.wt/<id>` maps to `<p>`), `unattended` (`ENGINEER_UNATTENDED == "1"`).
  - Each guard is `check(event: dict, ctx: Ctx) -> str | None` (a deny reason). `pre_tool_use.py` runs `kill, protected, git, plan_hash, vendor, browser, deploy` in that order; the first reason goes to stderr and the hook exits 2; any exception exits 2 with `guard error: <type>` (fail closed).
  - `kill`: kill switch file exists → deny everything.
  - `protected`: for `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, resolve `file_path` (following symlinks) relative to `project_dir`; `eng.paths.protected(rel, rules, exists)` → deny. For `Bash`, if the command has a write form (`>`, `>>`, `tee`, `sed -i`, `mv`, `cp`, `rm`, `truncate`, `chmod`, `ln`) and any token resolves to an `[always]` path or an existing `[existing]` path → deny. Heuristic only (SP13); audit and CODEOWNERS are the real stops.
  - `git`: split the command on `;`, `&&`, `||`, `|`, newlines and `bash -c`/`sh -c` strings; deny any `git` invocation (any options before the subcommand; `git` called by path or through `env`, `command`, `exec`) whose subcommand is `push`, `filter-branch`, `filter-repo`, `update-ref`, `reflog`, `remote`, or `config` setting `core.hooksPath`, `core.fsmonitor`, `core.sshCommand`, `credential.*`, `http.*`; and `branch -D`/`tag -d`.
  - `plan_hash`: when `unattended` and the tool writes a file outside `docs/plan/`: load `STATE_DIR/approvals/<project>.json`; `eng.approval.check(project_dir, approval)` non-empty → deny with the first line.
  - `vendor`: deny a Bash command whose any segment's first word is in `vendor-cli-deny.txt` (`codex`, `gemini`, `agy`, `aider`, `openai`, `llm`).
  - `browser`: tool names matching `^mcp__.*playwright.*__browser_navigate$` (and `browser_tabs` with a `url`): host of `tool_input.url` must pass `eng.hosts.allowed` against `browser-allowlist.txt`; `file:`, `chrome:`, `data:`, `javascript:` schemes denied (SP64 confirms the tool names).
  - `deploy`: deny when any regex line of `deploy-deny.txt` matches (`\bvercel\b.*--prod\b`, `\bwrangler\b.*\bdeploy\b.*--env[= ]production\b`, `\bgcloud\b.*\bupdate-traffic\b`, `\bsupabase\b.*\bdb\b.*\bpush\b`); promotes go through the digest (ruling 9).
  - `session_start.py`: prints `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}` with up to 20 open tasks from `docs/plan/tasks.json`, the last `## ` section of `PROGRESS.md` (at most 40 lines), approval status (`approved`, `changed: <file>`, `none`), kill switch status, and one line: "superpowers:<name> means the local skill <name>; the plan skill's task contract wins over Superpowers task sizing". Always exits 0.
  - `post_tool_use.py`: on `Write`/`Edit`/`MultiEdit` of a `.mmd` file, the first non-comment line must start with `flowchart`, `graph` or `sequenceDiagram` and contain no `C4` keyword, else exit 2 with the reason.
  - `stop_gate.py` (for `Stop` and `TaskCompleted`): exit 0 when `ENGINEER_TASK_ID` is unset; else run the task's `check` (from `docs/plan/tasks.json`) with `bash -c` in `project_dir` and the `check` profile timeout; non-zero → exit 2 with the last 30 lines; then the DEPENDENTS check: rows `| <glob> | <doc> |` of `docs/DEPENDENTS.md`; changed files = `git diff --name-only <merge-base with default branch>...HEAD` plus the working tree; a changed file matching a glob without its doc changed → exit 2 naming both. Block count per session in `~/.cache/engineer/stop-<session_id>`; at the 8th block, exit 0 and write a `gate_gave_up` spool line (audit then fails the task). The check runs as `engineer` under the egress rules, never as root or supervisor.
  - `event_tap.py` (for `StopFailure`, `Notification`): appends `{ts, session_id, hook_event_name, project, task_id, detail}` to `SPOOL_DIR/<session_id>.jsonl`; always exits 0.
  - `hooks.json` registers: `SessionStart` matcher `startup|resume|compact`; `PreToolUse` matcher `*` timeout 10; `PostToolUse` matcher `Edit|Write|MultiEdit` timeout 10; `Stop` and `TaskCompleted` timeout 1200; `StopFailure` and `Notification` timeout 5; each command `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py"`. `managed-hooks.json` is the same object with `/opt/engineer/plugin` in place of `${CLAUDE_PLUGIN_ROOT}`.

- [ ] **Step 1: Write the failing tests** (each pipes an event JSON into the script with `subprocess.run`, against a temp git repo as the project and a `make_root` copy).
  - `test_protected.py`: Write new `tests/unit/test_new.py` → exit 0; Edit existing `tests/unit/test_old.py` → exit 2; Write `tests/acceptance/x.py` → exit 2; Write via symlink `link -> tests/acceptance` → exit 2; Write `../other/CLAUDE.md` → exit 2 ("outside project"); Bash `echo x > tests/acceptance/a.py` → exit 2; Bash `cat tests/acceptance/a.py` → exit 0.
  - `test_git.py` (`test_git_push_variants`): `git push`, `git -C . push origin x`, `/usr/bin/git push`, `git --git-dir=.git push`, `env git push`, `bash -c "git push"`, `sh -c 'cd x && git push'`, `git config core.hooksPath /tmp` → exit 2; `git status`, `git commit -m x`, `git diff` → exit 0.
  - `test_plan_hash.py`: approval matches → Edit `src/a.py` exit 0; brief changed → exit 2 naming `docs/plan/brief.md`; Edit `docs/plan/brief.md` itself → exit 0; not unattended → exit 0.
  - `test_pre_tool_use.py`: kill switch present → any tool exit 2; a guard raising → exit 2 with `guard error`; `codex exec x` → exit 2; `vercel --prod` → exit 2.
  - `test_browser_guard.py`: `mcp__plugin_engineer_playwright__browser_navigate` to `https://app.attio.com/x` → 0; to `https://evil.example` → 2; `file:///etc/passwd` → 2; missing allowlist → 2.
  - `test_stop_gate.py`: no task id → 0; check `exit 1` → 2 with output tail; check `true` and DEPENDENTS row `| src/** | docs/api.md |` with only `src/a.py` changed → 2; both changed → 0; 8th block → 0 and a spool line.
  - `test_session_start.py`: output JSON has `additionalContext` containing a task id, `approved`, and `superpowers:`.
  - `test_post_tool_use.py`: `.mmd` starting `C4Context` → 2; `flowchart LR` → 0; `.py` file → 0.
  - `test_event_tap.py`: one line appended to `SPOOL_DIR/<session>.jsonl`; unreadable spool dir → still exit 0.
  - `test_registration.py`: every command in `hooks.json` names an existing file; `managed-hooks.json` equals `hooks.json` after the path substitution; `claude plugin validate engineer/plugin --strict` passes when `claude` is on PATH (skip otherwise).
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh hooks`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run; expect PASS** `bash tests/engineer/run.sh hooks && claude plugin validate engineer/plugin --strict`.
- [ ] **Step 5: Hand back.**

---

### Task 9: Checks

**Files:**
- Create: `engineer/scripts/checks/{audit.sh,clone.sh,testcount.py,test-diff-guard.py,merge-tier.py,secret-scan.py,integrations-env.py,parity.py,verify-all.sh}`
- Create: `engineer/templates/tier2-paths.txt`, `engineer/templates/verify-all.tsv`
- Test: `tests/engineer/checks/test_audit.sh`, `test_testcount.py`, `test_test_diff_guard.py`, `test_merge_tier.py`, `test_secret_scan.py`, `test_integrations_env.py`, `test_parity.py`, `test_verify_all.sh`

**Interfaces:**
- Consumes: `eng.paths`, `eng.conf`, `eng.schema` (Task 2); `STATE_DIR/checks/<p>/<id>.json` (a `run-result` written by the supervisor, Task 6); `AGENT_RUN` (Task 5, stubbed).
- Produces:
  - `audit.sh PROJECT TASK_ID`: runs as supervisor; `clone.sh` fetches `refs/heads/task/<id>` and the default branch from `file://PROJECTS_DIR/<p>` into the supervisor-owned bare clone `STATE_DIR/audit-clones/<p>.git` (git run with `-c core.hooksPath=/dev/null -c core.fsmonitor=` and `GIT_CONFIG_NOSYSTEM=1`); base = merge-base; head = branch tip. Lines: FAIL if the check result's `head_sha` differs from head, if its `exit_code` is not 0, or if `testcount.parse(output_tail)` is `None` or 0 (F25); FAIL on any `[always]` protected path in the diff; FAIL on `test-diff-guard` findings; FAIL on `secret-scan` findings in added lines; FAIL on `integrations-env` or `parity` mismatches when those files changed. Prints `{"verdict": "PASS"|"FAIL", "head_sha": "<40 hex>", "lines": [...]}` (at most 15 lines); exit 0 PASS, 1 FAIL.
  - `testcount.parse(text) -> int | None`: explicit `TESTS_RUN=<n>`; pytest `<n> passed`; unittest `Ran <n> tests`; jest/vitest `Tests: ... <n> passed`/`Tests  <n> passed`; node test runner `# pass <n>`; bats/TAP `1..<n>`; else `None`.
  - `test-diff-guard.py --repo GITDIR --base SHA --head SHA`: JSON list of findings `{kind, path, detail}` for: a deleted test file (`[existing]` patterns), added skip markers (`@pytest.mark.skip`, `pytest.skip(`, `@unittest.skip`, `it.skip(`, `describe.skip(`, `test.skip(`, `xit(`, `xdescribe(`, `t.Skip(`), a drop in `assert`/`expect(` line count in a test file, any change under `tests/acceptance/`, any change to a test config file (`[always]` list); exit 1 when non-empty.
  - `merge-tier.py [--tier2 FILE] [--protected FILE]`: stdin `{"title", "files": [{"path", "additions", "deletions"}]}`; tier 1 only when: title type in `docs test chore style fix feat refactor`, no `!` and no `BREAKING`; at most 20 files; at most 1000 changed lines; no path in `tier2-paths.txt` or `[always]`; else tier 2 with one reason each (engineer-protocol §Q5). `tier2-paths.txt`: `**/migrations/**`, `migrations/**`, `**/auth/**`, `auth/**`, `.github/**`, `infra/**`, `**/*.tf`, `Dockerfile`, `docker-compose*.yml`, `wrangler.toml`, `vercel.json`, `CODEOWNERS`, `CLAUDE.md`, `.claude/**`, `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements*.txt`, `pyproject.toml`, `poetry.lock`, `uv.lock`, `go.mod`, `go.sum`, `Cargo.toml`, `Cargo.lock`, `docs/plan/**`, `security/**`, `.env.example` (lockfile bumps stay Tier 2: Open decision 6).
  - `secret-scan.py [FILES... | --diff GITDIR BASE HEAD]`: regexes as Task 2's static test plus `sk-[A-Za-z0-9]{20,}` and `Bearer [A-Za-z0-9._-]{20,}`; prints `path:line kind` with the match redacted; exit 1 on any. (gitleaks `--redact` replaces it on the droplet once installed; same output shape.)
  - `integrations-env.py --repo DIR`: names in `integrations.yaml` `env_vars` vs names in `.env.example`; prints `missing:`/`extra:` lines; exit 1 on any.
  - `parity.py --repo DIR`: node ids in `docs/plan/architecture.yaml` (`nodes[].id`) vs ids in `docs/plan/architecture.mmd` (`^\s*([A-Za-z0-9_]+)[\[\(\{]`); exit 1 on mismatch.
  - `verify-all.sh [--out FILE]`: rows of `verify-all.tsv` (`name<TAB>job args<TAB>check text`) for this sitting: `GH_BOT_PAT` (`api-call github GET /user`), `TG_SUPERVISOR_TOKEN` (`tg-send` with "setup test"), `HC_PING_URL` (`hc-ping ok`), `ATTIO_API_KEY` (`api-call attio GET /self`), `N8N_API_KEY` (`api-call n8n GET /workflows?limit=1`), and three manual rows (`UPTIMEROBOT_API_KEY`, whose API takes the key in the request body; the Clay CLI session; browser sessions) marked `manual`; calls `AGENT_RUN <job args>` per row; writes `Name | Broker job | Check | Result` to `--out` (default `docs/setup-verify.md` in the current directory); stops at the first failure, marking the rest `not run`; exit 1 then. The `github` service it calls is defined in Task 5's `broker-services.json`.

- [ ] **Step 1: Write the failing tests.**
  - `test_audit.sh` (temp project repo, `make_root`, check result JSON fixture): clean task branch with `TESTS_RUN=3` tail → PASS JSON and exit 0; check result SHA stale → FAIL; `tests_run` 0 → FAIL; a commit adding `@pytest.mark.skip` → FAIL; a commit adding `TEST-TOKEN` shaped like `ghp_` + 36 chars → FAIL; `test_audit_ignores_repo_config`: project `.git/config` with `core.fsmonitor = touch $T/pwned` → `$T/pwned` absent after the run.
  - `test_testcount.py`: one sample per runner format; unrelated text → `None`.
  - `test_test_diff_guard.py`: deleted `tests/test_a.py` → finding `deleted_test`; `assert` lines 5 → 3 → `fewer_asserts`; `conftest.py` changed → `test_config`; clean diff → `[]`.
  - `test_merge_tier.py`: `fix: x` with `src/a.py` 10 lines → tier 1; `feat!: x` → 2; `package-lock.json` → 2; 21 files → 2; 1001 lines → 2; `ci: x` → 2; `.github/workflows/a.yml` → 2.
  - `test_secret_scan.py`, `test_integrations_env.py`, `test_parity.py`: one positive and one negative each.
  - `test_verify_all.sh`: stub `AGENT_RUN` passes rows 1-2 and fails row 3 → output table has `pass`, `pass`, `FAIL`, then `not run`; exit 1.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh checks`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run; expect PASS** same command.
- [ ] **Step 5: Hand back.**

---

### Task 10: Browser route

**Files:**
- Create: `engineer/plugin/.mcp.json`, `engineer/plugin/scripts/playwright-mcp.sh`
- Create: `engineer/bin/browser-login`, `engineer/bin/xvfb-session`, `engineer/bin/novnc-session`
- Create: `engineer/scripts/browser/challenge-check.py`, `engineer/templates/challenge-patterns.txt`, `engineer/templates/browser-allowlist.txt`, `engineer/templates/cloudflared/config.yml.tmpl`
- Create: `engineer/plugin/skills/browser/SKILL.md`
- Test: `tests/engineer/browser/test_playwright_mcp.sh`, `test_browser_login.sh`, `test_sessions.sh`, `test_challenge.py`, `test_allowlist_file.py`, `test_mcp_json.sh`, `test_skill.sh`

**Interfaces:**
- Consumes: `eng.conf`, `eng.hosts`, `templates/bootstrap-packages.txt` (`@playwright/mcp` pin) (Task 2).
- Produces:
  - `.mcp.json`: `playwright` (`bash ${CLAUDE_PLUGIN_ROOT}/scripts/playwright-mcp.sh`), `deepwiki` and `firecrawl` (same keyless HTTP entries as `plugin/.mcp.json`). Vendor servers (Attio, n8n instance) are added on setup day after SP55 and SP56 (Open questions 35).
  - `playwright-mcp.sh`: `exec npx --no-install @playwright/mcp@<pin> --browser chrome --user-data-dir "$CHROME_PROFILE" --proxy-server "http://127.0.0.1:$PROXY_PORT"` with `DISPLAY` from conf; refuses (exit 2) if any argument passed in contains `--headless` or `--isolated`, or if `CHROME_PROFILE` is empty or ends in `.config/google-chrome` (the default profile, which Chrome 136+ will not open for automation, engineer-host E13).
  - `browser-login URL`: as `engineer`; refuses as root; refuses (exit 75) when `$CHROME_PROFILE/SingletonLock` points at a live pid; creates the profile dir 0700; `exec google-chrome-stable --user-data-dir="$CHROME_PROFILE" --no-first-run --proxy-server=http://127.0.0.1:$PROXY_PORT "$URL"` on `DISPLAY`; never adds `--headless`, `--remote-debugging-port`, `--remote-debugging-pipe` or `--enable-automation` (John's hand sign-in runs in a browser that is not automated, engineer-host Q1).
  - `xvfb-session`: `Xvfb $DISPLAY -screen 0 1920x1080x24 -nolisten tcp &` then `exec fluxbox` on that display. `novnc-session`: `x11vnc -display $DISPLAY -localhost -rfbport 5900 -forever -shared -nopw &` then `exec websockify --web /usr/share/novnc 127.0.0.1:$NOVNC_PORT 127.0.0.1:5900`.
  - `challenge-check.py`: stdin `{"url", "title", "text"}` (a Playwright snapshot); patterns `kind<TAB>field<TAB>regex` from `challenge-patterns.txt`: `google_blocked` text `This browser or app may not be secure|Couldn't sign you in`, `google_sorry` url `google\.[a-z.]+/sorry/`, `cloudflare` title `^Just a moment`, `cloudflare` text `Verify you are human`, `captcha` text `recaptcha|hcaptcha|turnstile`, `login_required` url `/(login|signin|sign-in)(\b|/|\?)`; prints `{"challenge": bool, "kind": str|null}`; exit 3 on a challenge.
  - `browser-allowlist.txt`: `accounts.google.com`, `app.attio.com`, `*.attio.com`, `app.clay.com`, `*.clay.com`, and a comment that John's n8n host is added on setup day (Open decision 8).
  - `cloudflared/config.yml.tmpl`: `tunnel: {{TUNNEL_ID}}`, `credentials-file: /etc/cloudflared/{{TUNNEL_ID}}.json`, `ingress:` `- hostname: novnc.{{DOMAIN}}` `service: http://127.0.0.1:6080`, `- service: http_status:404`. John creates the tunnel and the Access app (one-email policy) by hand on setup day.
  - `browser` skill: the ladder API or MCP, then a recorded flow (`flows/<app>/<task>.spec.ts`), then exploratory Playwright, then John; after every navigation run `challenge-check.py`; every write is followed by a separate read that confirms it; recorded flows carry pre- and postconditions.

Behaviour (EARS; F41):
- When a login page, CAPTCHA or bot challenge appears, the engineer shall stop the task, record a blocked note naming the host and kind, and add a T1 "re-login or clear the challenge on noVNC" line, and shall not attempt to bypass it.
- The engineer shall not use stealth plugins, user-agent spoofing, proxy rotation or CAPTCHA solvers.
- When an API or MCP route exists for an action, the engineer shall use it instead of the browser.

- [ ] **Step 1: Write the failing tests.**
  - `test_playwright_mcp.sh`: stub `npx` logs argv: contains `--browser chrome`, `--user-data-dir <profile>`, `--proxy-server`, the pin from `bootstrap-packages.txt`; no `--headless`; passing `--headless` → exit 2; `CHROME_PROFILE=$HOME/.config/google-chrome` → exit 2.
  - `test_browser_login.sh`: stub `google-chrome-stable` logs argv: no `--headless`, `--remote-debugging`, `--enable-automation`; profile dir mode 700; a `SingletonLock` symlink to `host-$$` (live pid) → exit 75; to a dead pid → runs.
  - `test_sessions.sh`: stubs for `Xvfb`, `fluxbox`, `x11vnc`, `websockify`: argv contains `-nolisten tcp`, `-localhost`, `127.0.0.1:6080`.
  - `test_challenge.py`: Google "This browser or app may not be secure" → `google_blocked`, exit 3; title "Just a moment..." → `cloudflare`; an Attio records page fixture → clean, exit 0; `https://app.attio.com/login` → `login_required`.
  - `test_allowlist_file.py`: loads with `eng.hosts.load`; `app.attio.com` allowed; `example.com` not.
  - `test_mcp_json.sh`: valid JSON; no `KEY|TOKEN|SECRET` strings; playwright command path exists.
  - `test_skill.sh`: frontmatter `name: browser`; mentions `challenge-check.py`, `noVNC`, "stealth", "read" after write.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh browser`.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run; expect PASS** same command.
- [ ] **Step 5: Hand back.**

---

### Task 11: Skills, agents, Superpowers subset, project skeleton

**Files:**
- Create: `engineer/plugin/skills/{as-is,plan,deploy,security-review,digest}/SKILL.md`
- Create: `engineer/plugin/agents/{planner,implementer,plan-reviewer,auditor,mapper,merger,triage-reader}.md`
- Create (copy): `engineer/plugin/skills/{brainstorming,writing-plans,subagent-driven-development,executing-plans,verification-before-completion,using-git-worktrees,using-superpowers}/` from `/home/user/attio-project/.claude/skills/` (vendored at `bb92a77`; if that path is absent, `git clone https://github.com/obra/superpowers` and `git checkout bb92a77`), `engineer/plugin/LICENSE-superpowers`, `engineer/plugin/superpowers.sha256`
- Create: `engineer/templates/project/` (tree below), `engineer/bin/new-project`
- Test: `tests/engineer/plugin/test_skills.sh`, `test_agents.sh`, `test_superpowers.sh`; `tests/engineer/skeleton/test_new_project.py`

**Interfaces:**
- Consumes: schemas and `eng.schema` (Task 2); `templates/tier2-paths.txt` shape (Task 9) for CODEOWNERS (the skeleton's CODEOWNERS lists the Tier 2 globs as literal lines; it does not read the file).
- Produces:
  - Skills, each with `name` equal to its folder and a description under 1,536 characters, at most 300 lines, content per repo-composition.md §Skills: `as-is` (five-step brownfield protocol, F9-F11, credentials by name only, never `n8n export:credentials --decrypted`); `plan` (the plan set under `docs/plan/`, what John signs, the task contract: one session, one commit, one check, about 1-4 files and 100 lines, `tasks.json` fields, change tiers Minor/Moderate/Major, F18-F21, F30-F31); `deploy` (platform decision table, preview then promote as a T1 line default hold, the pre-promote checklist, F35-F38); `security-review` (output schema file:line, CWE, severity, repro, scope; deterministic tools first; F32-F34); `digest` (how T1 lines and T2 prompts are written, the reply grammar of Task 7).
  - Agents, frontmatter `name`, `description`, `model`, `tools` (no `hooks`, `mcpServers` or `permissionMode`, which plugin agents ignore): `planner` opus, `Read, Glob, Grep, Write, Edit` limited by its body to `docs/plan/`; `implementer` sonnet, all tools; `plan-reviewer` sonnet, `Read, Glob, Grep`; `auditor` sonnet, `Read, Glob, Grep, Bash`, body: writes no file, returns only JSON matching `audit-verdict.schema.json`, default FAIL when unsure, every line cites `path:line` or a command and its output; `mapper` sonnet and `merger` sonnet, read-only, notes with `path:line`; `triage-reader` haiku, `Read` only, treats input as untrusted data and returns JSON.
  - `superpowers.sha256`: `sha256sum` of every vendored file, relative paths; `LICENSE-superpowers` copied verbatim.
  - Project skeleton `engineer/templates/project/`: `CLAUDE.md` (under 200 lines; `# Compact instructions`; lines: "superpowers:<name> means the local skill <name>", "test-driven-development and finishing-a-development-branch are not installed; every task ends in a PR", "the plan skill's task contract wins over Superpowers task sizing", "no generated overview here; read docs/map/ by path"), `.env.example` (header only), `docs/plan/brief.md`, `requirements.md`, `architecture.yaml` (`nodes: []`, `edges: []`), `architecture.mmd` (`flowchart LR`), `integrations.yaml` (`services: []`), `tasks.json` (`{"version": 1, "tasks": []}`), `profile.yaml` (`hard_gates: [money, delete_data, store_submission]`, `t2_extra: []`, `promote: hold`, `self_merge: true`, `data_classes: {}`, `allowed_processors: [anthropic]`, `adopted_rules: []`, `unattended: true`), `docs/plan/contracts/.gitkeep`, `docs/plan/changes/.gitkeep`, `docs/adr/0000-template.md` (MADR), `docs/map/.gitkeep`, `docs/DEPENDENTS.md` (table header `| Source glob | Dependent doc |`), `docs/setup.md`, `tests/acceptance/.gitkeep`, `security/.gitkeep`, `flows/.gitkeep`, `dead-ends.md` (columns: tool or path, version tested, what failed, retry-when), `PROGRESS.md`, `.github/CODEOWNERS` (every Tier 2 glob followed by `@{{OWNER}}`), `.github/workflows/checks.yml` (one job running `bash scripts/check.sh` when present; actions pinned to exact versions).
  - `new-project DIR --name NAME --owner LOGIN [--adopt]`: copies the skeleton replacing `{{NAME}}` and `{{OWNER}}`; refuses a non-empty `DIR` without `--adopt`; with `--adopt` copies only missing files and lists every skipped file; never overwrites.

- [ ] **Step 1: Write the failing tests.**
  - `test_skills.sh`: the six engineer skills (five here plus `browser` from Task 10 when present) and seven vendored folders exist; each SKILL.md has `name` matching its folder, a description under 1,536 characters, at most 300 lines (vendored files exempt from the line rule); `test-driven-development` and `finishing-a-development-branch` folders absent; `plan` mentions `tasks.json`, `approval`, `Minor`, `Major`; `as-is` mentions `--decrypted`.
  - `test_agents.sh`: seven agents, each with `name`, `description`, `model`, `tools`; none sets `hooks`, `mcpServers` or `permissionMode`; `auditor` tools exclude `Write` and `Edit` and its body names `audit-verdict`; `plan-reviewer` tools exclude `Write` and `Edit`.
  - `test_superpowers.sh`: `sha256sum -c engineer/plugin/superpowers.sha256` passes from `engineer/plugin/`; `LICENSE-superpowers` contains "MIT".
  - `test_new_project.py`: into an empty temp dir → `tasks.json` validates against the tasks schema, `profile.yaml` against the profile schema with `self_merge: True`, `integrations.yaml` against the integrations schema, CODEOWNERS lines end in `@octo-test`; non-empty dir without `--adopt` → exit 1; with `--adopt` an existing `CLAUDE.md` is untouched and reported.
  - Plus: `claude plugin validate engineer/plugin --strict` passes.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh plugin skeleton`.
- [ ] **Step 3: Copy the vendored skills, write the skills, agents, skeleton and `new-project`.**
- [ ] **Step 4: Run; expect PASS** `bash tests/engineer/run.sh plugin skeleton && claude plugin validate engineer/plugin --strict`.
- [ ] **Step 5: Hand back.**

---

### Task 12: Setup-day guide

**Files:**
- Create: `docs/engineer/setup-day.md`
- Modify: `engineer/README.md` (link to the guide; one line)
- Test: `tests/engineer/docs/test_setup_day.sh`

**Interfaces:**
- Consumes: the final names from Tasks 3-11 (commands, units, files, broker jobs, verify-all rows) and the "Deferred to setup day" table below.

Content (plain language for John, who is not deep on Docker or git; each technical word explained the first time; at most 250 lines):
1. **What you will have at the end** (five lines).
2. **Accounts and costs** table: DigitalOcean droplet, Basic 4 vCPU / 8 GiB, US East (New York region), Ubuntu 24.04 LTS, $48/month, snapshots $0.06/GB per month (engineer-host E64); Claude Max (already have; overnight runs use its limits); GitHub Pro (already bought) and a second free GitHub account for the bot; Cloudflare free plan, Tunnel and Access, plus a domain on Cloudflare (Open decision 3); Telegram (free) with two bots from @BotFather; healthchecks.io Hobbyist (free, 20 checks) and UptimeRobot Free (50 monitors); Attio, Clay, n8n (your current plans). Fallbacks, only if the sign-in test fails: Tailscale Personal (free) exit node on a small always-on device at home carrying only the browser's traffic; or a Mac mini M6 at home ($899 one-off) with the same setup.
3. **Before the day**: merge the stage-1 PR; decide the open decisions below; have your phone, your password manager and an hour and a half.
4. **The one sitting**, numbered, each step "You do" / "It checks": create the droplet with your SSH key; log in; make the read-only deploy key and clone the repo to `/srv/autonomy-research`; `sudo bash .../engineer/scripts/setup-root.sh --install`; switch to the engineer user and run `claude auth login` with your Max account (never `setup-token`); `bootstrap.sh`; `doctor.sh`; create the bot GitHub account and its fine-grained token (Contents, Pull requests, Metadata); branch protection from your own account (required checks, CODEOWNERS review, no bypass, no force push, allow auto-merge, `engineer-records` branch bot-only); Telegram bots and `/start`; healthchecks.io and UptimeRobot; Cloudflare tunnel (`cloudflared tunnel login`, `create`, route `novnc.<domain>`) and an Access app allowing only your email; seed each secret with `sudo -u secretbroker /opt/engineer/bin/seed <NAME>` (names listed; values typed, never pasted into chat); open `https://novnc.<domain>`, run `browser-login`, sign in to Google by hand, then Attio, Clay, n8n; Attio key, n8n key, Clay CLI sign-in as `secretbroker`; write `/etc/engineer/projects.txt`; `verify-all.sh`; the setup-day tests; snapshot the droplet; `setup-root.sh --lock`; enable `engineer-remote-control` and `engineer-channels`, pair your phone; first night on a scratch repo.
5. **Setup-day tests**: the table from "Deferred to setup day", each with what passing looks like and what to do if it fails (including the two fallbacks and `--unlock`).
6. **If something goes wrong**: kill switch `sudo touch /var/lib/engineer/STOP`; `--unlock`; where the morning report is.
7. **Words used here**: droplet, SSH key, deploy key, branch protection, PR, CODEOWNERS, systemd unit, noVNC, snapshot.

- [ ] **Step 1: Write the failing test** `test_setup_day.sh`: file exists, at most 250 lines; headings `## Accounts and costs`, `## The one sitting`, `## Setup-day tests`, `## If something goes wrong`; mentions `$48`, `claude auth login`, `setup-token`, `seed`, `--lock`, `novnc`, `Tailscale`, `Mac mini`; every spike id in the plan's "Deferred to setup day" table appears; no secret pattern (Task 2 regex); relative links resolve.
- [ ] **Step 2: Run; expect FAIL** `bash tests/engineer/run.sh docs`.
- [ ] **Step 3: Write the guide.**
- [ ] **Step 4: Run; expect PASS** `bash tests/engineer/run.sh && bash tests/check.sh && MERMAID_SKIP_RENDER=1 bash tests/check-mermaid.sh`.
- [ ] **Step 5: Hand back.**

---

## Phase A items not in stage 1
| Item (blueprint) | Why it waits | When |
| --- | --- | --- |
| Trial runner (`scripts/trial/`), rootless Podman, TLS-terminating proxy | Needs Podman and a container runtime; SP03, SP26-SP28 (incl. `/dev/kvm`, which may switch it to `sbx`) must run on the droplet first. The `run-result` schema is ready for it | Stage 2, after the setup day |
| Vendor snapshot exporters (`scripts/snapshot/` for Attio, Clay, n8n, Outreach, Slack) | API shapes are unverified (SP60, SP65, SP66); John's decision 6 puts the framework first | The GTM project's as-is stage |
| Changes to the research-agent skills (interview, research, tool-scan, repo-triage, spike, system-map, setup) | They sit under the research-agent's frozen exam and need `claude plugin eval` runs with a model; stage 1 installs them unchanged into `/opt/engineer/plugin/` | Stage 2 |
| `oauth-capture`, `mint-child`, TOTP wrapper | No OAuth consent, child token or TOTP is needed for Attio, Clay or n8n on day one; John creates the Cloudflare tunnel and Access app by hand | The first project that needs one |
| Checks: contrast, vet card, staleness, n8n export; PostToolUse `updatedToolOutput` redaction; dead-end reminder hook | Each depends on a spike (SP49, SP54, SP66, SP14, SP53) | When their spike passes |
| Plugin evals for the new skills; seeded-flaw fixtures | Need a model run | Stage 2 |

## Deferred to setup day
| Test on the droplet | Spike | Exercises |
| --- | --- | --- |
| Re-read the Agent SDK billing article and legal page; record the quotes in ADR 0001 | SP01 | Task 1 |
| `/login` keeps Remote Control, connectors and Chrome; `setup-token` is not used | SP02 | Tasks 4, 7 |
| `--permission-mode auto --permission-prompts none` on a task that triggers blocks | SP04 | Tasks 5, 6 |
| `--max-turns`, `--max-budget-usd` exit codes and `result.subtype` | SP05 | Tasks 5, 6 |
| Stop and TaskCompleted hooks block with exit 2 under `-p` | SP06 | Task 8 |
| Real usage-limit text replaces the synthetic `limits.py` fixtures | SP07 | Task 6 |
| Overnight run with restart on stall; Channels relay under tmux | SP08 | Tasks 3, 6, 7 |
| Bash sandbox with the AppArmor bwrap profile on 24.04 | SP09 | Task 3 |
| Managed settings honoured for a non-root user; hooks accepted there | SP10 | Tasks 3, 8 |
| `engineer` cannot read a secret (`sudo -l`, `/proc/*/environ`) | SP11 | Tasks 3, 5 |
| A seeded canary never appears in transcripts or logs | SP12 | Task 5 |
| Deny-rule bypass attempts (`git -C . push`, `sh -c`, Bash writes to tests) | SP13 | Tasks 3, 8 |
| One or two Telegram bots | SP16 | Task 7 |
| Approval-hash hook blocks a live edit | SP17 | Tasks 7, 8 |
| Branch protection, CODEOWNERS, bot push refused, `gh pr merge --auto` at zero approvals; must pass before `--lock` | SP18 | Tasks 5, 9, 11 |
| Branded Chrome and Playwright MCP launch on Xvfb; mermaid-cli renders | SP22 | Tasks 4, 10 |
| PreToolUse fires on Playwright MCP tools with usable `tool_input` | SP64 | Tasks 8, 10 |
| Cloudflare Access app for noVNC, login from the phone | SP71 | Task 10 |
| healthchecks.io alert reaches the phone | SP72 | Task 5 |
| Plugin loads from `/opt/engineer/plugin` with `--plugin-dir`; `--agent` picks the profile's agent | SP83 | Tasks 5, 11 |
| Google and Attio sign-in from the droplet IP through noVNC; any challenge noted | SP85 | Task 10 |
| Logins survive a snapshot restore | SP86 | Task 10 |
| Remote Control and the Telegram channel on the host at the same time | SP87 | Task 7 |
| Memory with real Attio, Clay, n8n tabs on 8 GB | SP88 | Task 4 |
| DigitalOcean acceptable-use policy read | SP89 | Task 12 |
| `nft -c` loads the ruleset; the proxy sees CONNECT hosts with `--ignore-hosts`; `claude -p` works on the runtime list; the egress lists rewritten from the logged hosts | SP09, SP13, SP26 | Tasks 3, 4 |
| `visudo -c` accepts the sudoers file; units start | none (doctor.sh) | Task 3 |
| Pins marked `TO-PIN` filled and checked | none | Tasks 2, 3 |

## Open decisions (stage 1 does not decide; default assumed)
1. **Repo home.** Keep the engine in Autonomy-Research under `engineer/`, or split it into its own `engineer-template` repo. Default: keep it here; the droplet clones this repo read-only.
2. **Which accounts join the one sitting.** Default: the engine's own accounts plus Attio, Clay, n8n and the Google sign-in; Outreach, Slack, Google OAuth apps, WHOOP, Withings, GCP, Vercel and Supabase wait for the project that needs them (each project gets its own setup list, F21).
3. **Domain for Cloudflare Access.** Default: a domain John already has on Cloudflare; buying one is a money decision he makes himself.
4. **One or two Telegram bots.** Default: two (supervisor bot and Channels bot) until SP16 says one can be shared.
5. **Night window and digest time.** Default: 22:00-07:00 US Eastern, digest at 07:30.
6. **Gates.** Default: hard gates are exactly money, deleting data and app-store submission; production promotes are T1 lines with default "hold"; lockfile and dependency bumps are Tier 2 (John reviews); Moderate changes are FYI; health data stays Claude-only.
7. **Claude data-retention setting (30 days or 5 years).** Default: nothing in stage 1 depends on it; John chooses at the sitting; local transcripts kept 7 days.
8. **Where n8n runs (Cloud or self-hosted) and its host name.** Default: it stays where it is; the n8n API is treated as unavailable until SP66.
9. **Droplet backups.** Default: snapshots only (after the hand sign-in); weekly backups (+20%, about $9.60/month) off.

## Blueprint conflicts with John's decisions, and how the plan resolves them
| Blueprint said | John decided | Resolution |
| --- | --- | --- |
| Ruling 1: auth unresolved; unattended runs not built until he chooses; Path B rows in setup and verify-all | Path A, unattended included, no API key | Supervisor and `run-task` built now; Path B rows deleted; wrappers and `doctor.sh` refuse `ANTHROPIC_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN`; the legal-page risk stays recorded in ADR 0001 and SP01 is re-read on setup day |
| Ruling 2: self-merge off; on only after a GitHub route and two weeks of shadow mode (SP19) | GitHub Pro; self-merge on from day one; no shadow weeks | `self_merge: true` default; `automerge` job for Tier 1; Tier 2 waits for John's GitHub review; SP18 must pass before `--lock`; SP19 and setup step 41 dropped |
| Ruling 6: 1Password `op` pipe if he has it | No 1Password | SOPS+age only; `op` rows removed; TOTP via pyotp later |
| VPS or home box open; size an untested default; "Persistent Chromium profile"; noVNC over an SSH tunnel | DigitalOcean US-East 24.04, 4 vCPU/8 GB; branded Chrome via Playwright `channel chrome`; noVNC behind Cloudflare Access | Host, size and price fixed in stack.md and `doctor.sh`; Chrome is branded; Access app for noVNC moves into the sitting before the browser logins; SSH tunnel kept as a fallback; Tailscale exit node and home Mac mini recorded as fallbacks only |
| Ruling 3 and area 14: Channels daytime relay, Remote Control as a view; NanoClaw kept as an alternative | Remote Control server mode plus Telegram; no NanoClaw or OpenClaw in v1 | `engineer-remote-control` unit with restart (E104) and `engineer-channels` unit; NanoClaw moved to "later option"; Slack bridge on an API key noted as later |
| Setup sitting includes Outreach, Google OAuth, WHOOP, Withings, Slack, GCP, Vercel, Supabase rows | First project is the GTM framework over Attio, Clay, n8n | Those rows move to per-project setup lists (Open decision 2) |
| Phase A step 1: John creates a separate `engineer-template` repo first | Stage 1 is one PR in this repo | Code staged under `engineer/` (Open decision 1) |
| SP63: profile kept 2-3 weeks to measure session life | No trial weeks | Replaced by setup-day SP85 and SP86; session life is watched afterwards by the daily logged-in line, not gating |
