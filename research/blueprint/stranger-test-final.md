# Stranger test, final check

Date: 2026-10-16. Reader: a fresh session with no prior knowledge of the project.

Read only: `stranger-test.md`, `stranger-test-2.md`, `stranger-test-3.md` (the 26 gaps in their section 4(b)), then the
current blueprint: `README.md`, `decisions.md`, `stack.md`, `setup.md`, `repo-composition.md`, `flow.md`,
`gtm-scenario.md`, `spikes.md`, `requirements-trace.md`, `open-questions.md` in this folder, and
`docs/diagrams/engineer-{approvals,context,project-flow,runtime}.mmd`. Not read: `digests/`, `hand-check.md`,
`verification.md`, findings files, anything on the web. References are `file:line` in the current files.

## 1. The 26 gaps

ST1 = `stranger-test.md` 4(b), ST2 = `stranger-test-2.md` 4(b), ST3 = `stranger-test-3.md` 4(b).

| # | Gap | Status | Where the blueprint now answers it |
| --- | --- | --- | --- |
| ST1-1 | Bring-up order cannot run; nobody writes the scripts or clones the template; who builds | CLOSED | Builder session defined (setup.md:7); phase A writes the scripts in a cloud session before any VM (setup.md:14-16); clone and `setup-root.sh` (setup.md:22-23); SP02 moved after the VM exists (setup.md:36); SP09 at step 9, SP10 after lock (setup.md:31, 68) |
| ST1-2 | Phase 2 checks run before their inputs are seeded; push refusal before branch protection | CLOSED | Each credential is seeded and checked in the same row (setup.md:39); bot PAT at step 19, branch protection and the refused-push check at step 20 (setup.md:48-49); canary for broker tests before the sitting (setup.md:9, 32) |
| ST1-3 | No way for John to reach noVNC; `cloudflared` and Cloudflare account missing | CLOSED | noVNC on 127.0.0.1:6080 via `ssh -L` (setup.md:59; engineer-runtime.mmd:30); `cloudflared` root-installed (stack.md:72); Cloudflare account and domain at step 24 (setup.md:53) |
| ST1-4 | Install list and pins incomplete; egress hosts never listed | CLOSED | Install list with installer per row, incl. `gh`, sops, age, wrangler, `gcloud`, `cloudflared`, Clay CLI, pyotp, n8n not installed (stack.md:63-85); pin rule and Claude Code floor (stack.md:64, 76); egress host classes, exact names from logged requests (stack.md:88-91) |
| ST1-5 | Channels plugin and its bot never installed; vendor MCP servers have no config | CLOSED | Channels plugin (stack.md:83; setup.md:35); two bots (setup.md:51); vendor MCP at user scope, URLs from vendor docs after SP55/SP56 (repo-composition.md:126-130; open-questions.md:147) |
| ST1-6 | Template tree omits `tests/`, CI, `.claude/`; kill-switch path missing | CLOSED | repo-composition.md:34-42; kill switch `/var/lib/engineer/STOP` (repo-composition.md:99) |
| ST1-7 | Enforcement layer has no owner; Superpowers' dropped parts have no off switch | CLOSED | Root-owned managed settings and `/opt/engineer/hooks/`, registered at `--lock` (repo-composition.md:101-105); subset vendored without the TDD and finishing skills (repo-composition.md:13-15, 185) |
| ST1-8 | Numbers, schemas and VM size missing | CLOSED | Run defaults incl. F29 denials, turns, budget, timeout, `cleanupPeriodDays` (flow.md:7-21); schemas (repo-composition.md:132-138); VM size and `doctor.sh` floor (stack.md:60-61) |
| ST1-9 | n8n hosting contradiction; diagram stage numbers; undefined terms | CLOSED | n8n open everywhere (stack.md:54, 85; decisions.md:99; open-questions.md:124); diagram stages 0-11 match flow.md (engineer-project-flow.mmd:2-13); glossary for D0-D2, capability card, `ROW:`, ledger, pass^3, `setup-token` (README.md:59, 68-70, 74-75) |
| ST2-1 | Root work assigned to an unprivileged builder | CLOSED | All root work in `setup-root.sh` run by John, with modes (setup.md:9); root vs bootstrap split per tool (stack.md:64-85); bootstrap is user-level only (setup.md:30) |
| ST2-2 | Builder bound by the guards it is building | CLOSED | Guards installed last; hooks unregistered until `--lock` at step 34; builder tests hooks in a scratch project; after lock, changes go by PR (setup.md:9, 31, 63, 68) |
| ST2-3 | Git plumbing for the template repo missing | CLOSED | Repo created and seeded (setup.md:14); read-only deploy key and `/srv` clone (setup.md:22); commits local until the bot exists, then `push-branch` and John merges (setup.md:27, 50; repo-composition.md:8) |
| ST2-4 | Supervisor user's privileges unspecified | CLOSED | Users and sudoers table and the `run-task` wrapper (repo-composition.md:108-115) |
| ST2-5 | Egress allowlist would block bootstrap; no enforcement mechanism | CLOSED | nftables plus mitmproxy, root traffic unrestricted, install-mode list with package hosts, `--allow` by John (stack.md:88-91) |
| ST2-6 | Branch protection needs admin rights nobody has | CLOSED | John sets it from his admin account at step 20 (setup.md:49) |
| ST2-7 | Alerting accounts and dead-man route never set up | CLOSED | Sign-up row (setup.md:47); healthchecks.io chosen with reason (decisions.md:36; stack.md:24); pings via `hc-ping` job (stack.md:102); diagram (engineer-approvals.mmd:12, 24; engineer-runtime.mmd:26-27) |
| ST2-8 | No source for Superpowers or backcheck | CLOSED | https://github.com/obra/superpowers at `bb92a77` (stack.md:26; repo-composition.md:185); backcheck URL (stack.md:29, 82) |
| ST2-9 | `run-defaults.yaml`, `schemas/` not in tree; hooks location conflict; "Verifies all" table missing | CLOSED | Tree (repo-composition.md:30-33); hooks only in `plugin/hooks/` (repo-composition.md:18, 104); table (setup.md:75-88) |
| ST3-1 | Auditor launch path and write rights contradict | CLOSED | Auditor writes no file, returns JSON (repo-composition.md:69; decisions.md:35); started by `run-task` with the `auditor` profile (repo-composition.md:115; flow.md:64); SP83 (spikes.md:27). See new contradiction N1 for who writes the file |
| ST3-2 | How unattended runs load the plugin and Superpowers | CLOSED | `--plugin-dir /opt/engineer/plugin` for every session (repo-composition.md:115, 117); Superpowers inside that plugin, not bootstrap (decisions.md:104; stack.md:74; repo-composition.md:185) |
| ST3-3 | OAuth consent has no token capture or redirect route | CLOSED | `oauth-capture` loopback route plus tunnel fallback, tunnel before consents (setup.md:41, 53, 60); SP84 (spikes.md:28) |
| ST3-4 | Broker-run CLIs editable by `engineer`; Clay session location | CLOSED | Root-installed CLIs and fixed `PATH` (repo-composition.md:118; stack.md:72, 79); sign-in as `secretbroker` (setup.md:56; stack.md:103) |
| ST3-5 | Browser logins: login hosts not allowed; noVNC units not running | CLOSED | Login and consent hosts in both lists (stack.md:89-90); `chrome-xvfb` and `novnc` enabled at `--install` (setup.md:9, 35) |
| ST3-6 | Template starts empty but assumes "existing" files and findings | CLOSED | Seeded from a full copy of Autonomy-Research, findings included (setup.md:14; repo-composition.md:8) |
| ST3-7 | Supervisor container and worktree rights missing | CLOSED | Rootless Podman as `supervisor`, no `docker` group (decisions.md:25; stack.md:68; repo-composition.md:111, 116); clones and worktrees owned by `engineer` (repo-composition.md:116) |
| ST3-8 | 8-file plan set not listed; signed files do not map to the skeleton | CLOSED | Plan set, the four signed files and `approval.json` (repo-composition.md:140-143; flow.md:55); skeleton matches (repo-composition.md:149-158) |

CLOSED: 26. OPEN: 0.

## 2. New contradictions introduced by the fixes

### Counted (would stop or mislead a builder)
- **N1. The supervisor must write into project repos it can only read.** The ST3-7 fix gives `supervisor` read-only
  ACL access to project clones (repo-composition.md:111, 116). The ST3-1 fix and older rows make the supervisor write
  `audit/AUDIT-<id>.md` (repo-composition.md:69, 96; flow.md:64; decisions.md:35), copy `MORNING.md` into `docs/runs/`
  (repo-composition.md:88) and append `decisions/approvals.jsonl` (repo-composition.md:90), all in the project repo.
  `engineer` cannot write `audit/` either (repo-composition.md:78; flow.md:62). No file says who writes, commits and
  pushes these files, so F25 cannot be built as written. Supervisor-owned trial worktrees from a read-only clone
  (repo-composition.md:111) have the same problem.
- **N2. "Nothing is installed at user scope" vs user-scope installs.** repo-composition.md:117 says nothing is
  installed at user scope, so `engineer` cannot change skills, agents or hooks. But the four vendor MCP servers go in
  with `claude mcp add --scope user` (repo-composition.md:126-129), and bootstrap installs the Channels plugin with
  `claude plugin install` as `engineer` (stack.md:83; setup.md:35). The builder cannot tell which rule wins, or
  whether `engineer` may edit user-level plugin and MCP config.

### Noted, not counted (a builder can decide and record)
- `--install` copies the whole `plugin/`, including `hooks/hooks.json`, into `/opt/engineer/plugin/`, which every
  session loads (repo-composition.md:18, 117). That could register hooks before `--lock` (setup.md:9). The fallback
  wording (repo-composition.md:104) implies hook entries are written only at `--lock`, so the builder can ship the
  copy without them.
- `oauth-capture` is both a command John runs by hand and an `agent-run` job that `engineer` may call
  (repo-composition.md:112-113). The model could then rewrite a refresh token, which is the reason given for keeping
  `seed` out of `agent-run`.
- stack.md:114 lets the supervisor read the ntfy and Twilio credentials. stack.md:101 and repo-composition.md:119
  say only `secretbroker` reads secrets. Both channels are optional and off.
- Step 27 opens the Clay sign-in in the noVNC Chrome (setup.md:56), but the SSH tunnel is first described at step 30
  (setup.md:59).
- The loopback redirect to 127.0.0.1:8765 (setup.md:41) comes from Chrome, which runs as `engineer`. The nftables
  rule lets that UID reach only the proxy (stack.md:88), so it needs a loopback exception.
- The gate scanners are bootstrap-installed in `engineer`'s venv (stack.md:81), while `audit.sh` is described as
  something `engineer` cannot alter (repo-composition.md:105).
- stack.md:103 names `gh` and `gcloud` session stores created at step 27, but step 27 has only the Clay sign-in.

## 3. Verdict
**FAIL: 26 of 26 gaps CLOSED, 0 OPEN; 2 new contradictions that would mislead a builder (N1, N2), plus 7 minor
items a builder can decide and record.**

## Re-check after fixes

Date: 2026-10-16. I re-read the same set of files, plus `brief-for-john.md`, which is new in this folder. I checked
only the four items below and looked for new contradictions in paths, users, sudo rights, branches and step numbers.

| Item | Status | Where |
| --- | --- | --- |
| N1: the supervisor writes into project repos it can only read | CLOSED | The supervisor now has its own records clone `/var/lib/engineer/records/<project>/` on branch `engineer-records`, pushed with `push-branch`, and never writes into `engineer`'s clones (repo-composition.md:123-124). The same rule appears in repo-composition.md:88, 90, 96, 161, 165-166, flow.md:64, decisions.md:35 and setup.md:49 (step 20 protects `engineer-records`). Trial clones come from a supervisor-owned copy (repo-composition.md:124) |
| N2: "nothing at user scope" vs user-scope installs | CLOSED | The vendor MCP servers are now in the root-owned `/opt/engineer/plugin/.mcp.json` (repo-composition.md:118, 126-133). The Channels plugin is the one stated exception, disabled in `run-task` sessions, and stack.md:83, setup.md:35 and repo-composition.md:118 all agree |
| Minor: plugin `hooks.json` active before `--lock` | CLOSED | `--install` replaces `hooks/hooks.json` with an empty stub, and `--lock` installs the real hooks (repo-composition.md:118, 105; setup.md:9) |
| Minor: `oauth-capture` callable by `engineer` | CLOSED | It has been removed from the `agent-run` job list (repo-composition.md:114). It runs only through John's own password sudo (repo-composition.md:113; setup.md:41) |

New contradictions from these fixes that would stop or mislead a builder: **none**.

Noted, not counted (a builder can decide and record):
- `engineer` can also call `agent-run push-branch`, and it uses the same bot PAT. So "only the bot may push to
  `engineer-records`" (repo-composition.md:124; setup.md:49) does not stop the model from pushing a fake record. The
  job should allow `engineer-records` only when the caller (`SUDO_USER`) is `supervisor`.
- `push-branch` runs as `secretbroker`, so it needs read access to the supervisor's records clone. The records clone
  also needs a credentialed fetch of `engineer-records` before each push. Neither is stated (repo-composition.md:124).
- brief-for-john.md:102 calls the step 21 merge "the builder's first pull request". The first pull request is the
  phase A one (setup.md:15; brief-for-john.md:139).
- The other minor items in section 2 were not part of this re-check and still stand as noted.

### Updated verdict
**PASS: 26 of 26 gaps CLOSED; N1 and N2 CLOSED; both security items CLOSED; 0 new contradictions that would stop or
mislead a builder. 3 new minor items are noted above.**
