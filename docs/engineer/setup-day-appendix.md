# Setup day: builder appendix

For the builder session, not for John. [setup-day.md](setup-day.md) is John's guide; this file holds the
technical checks behind it, in the order of `research/blueprint/setup.md` phases B-E. The builder never holds
root: anything below that needs root is a command the builder writes out for John to paste. Record each
result (pass, fail, quote) in `engineer/docs/versions.md` or the ADR the row names, through a PR.

## A. Before the day (cloud session, one small PR)
- `engineer/templates/release-pins.txt`: the `sops` and `bun` rows are `TO-PIN`; `setup-root.sh --install`
  refuses until both carry a sha256. Take each from the vendor's checksum file on the release page
  (`sops-v3.13.3.checksums.txt`, bun `SHASUMS256.txt` for bun-v1.4.3); record the date in `versions.md`.
  Bun is needed by the Claude Code Channels plugins.
- `engineer/templates/apt-repos.txt`: the nodesource and cloudflare fingerprints were read from the key
  files themselves (trust on first use). Re-check both against the vendors' own pages; fix the row if they
  differ.
- Give John GitHub's published SSH host-key fingerprints for step 3, so his first `yes` is checked.

## B. Phase C: on the droplet as `engineer`, before the guards (blueprint steps 8-13)
- `bootstrap.sh` done: `claude --version` matches `engineer/docs/versions.md`; the Telegram channel plugin is
  installed at user scope (needs Bun from part A).
- SP22: branded Chrome and Playwright MCP start on Xvfb (`DISPLAY=:99`); mermaid-cli renders one diagram.
- Hooks from a scratch project's `.claude/settings.json` (guards not registered yet): SP06 (Stop and
  TaskCompleted block with exit 2 under `-p`), SP09 (bwrap sandbox with the AppArmor profile), SP13 (bypass
  attempts: `git -C . push`, `sh -c`, Bash writes into `tests/acceptance/`), SP17 (approval-hash block).
- Broker: John seeds a made-up `CANARY` (`setup-root.sh` does not seed one). SP11: `sudo -l` as engineer,
  `/proc/*/environ` and the SOPS file give the engineer no value. SP12: the canary never appears in
  transcripts, `agent-run.log` or job output.
- Supervisor on `engineer-scratch` (`scratch=yes`, so `run-task` starts sessions before `--lock`): SP04,
  SP05 (exit codes and `result.subtype`), SP08 (stall and restart; the Channels relay under tmux).
- SP07: the usage-limit patterns in `scripts/supervisor/limits.py` are synthetic. Replace them from the
  first real limit message; until then a night that hits a limit may end as an unknown stop.
- SP16 and SP87: whether one bot can serve both jobs, and whether Channels and Remote Control share a
  session or run side by side. Also check the Channels plugin stays out of `run-task` sessions (it is
  installed at user scope, so confirm `claude -p` there does not load it).
- SP64 and SP83: PreToolUse fires on Playwright MCP tools with a usable `tool_input`; record the exact
  Playwright tool names; check whether a server-level MCP name in an agent's `tools` grants that server's
  tools, and that `--plugin-dir /opt/engineer/plugin` with `--agent` picks the profile's agent.
- SP88: memory with real Attio, Clay and n8n tabs open, on 8 GB.
- For John: the healthchecks.io period and grace (from the supervisor loop's ping cadence and the longest
  run timeout in `templates/run-defaults.yaml`), and the branch-protection checklist for step 11, with the
  required check name (`checks` job in the project skeleton's workflow). Check whether a repo owned by a
  personal account can limit pushes on `engineer-records` to the bot; if not, record the fallback.

## C. Projects, mirrors and records (after John's step 17)
- The supervisor's `sync-mirror` broker job fetches each project's default branch into the broker's bare
  mirror under `MIRROR_DIR` (`/var/lib/engineer/mirrors`); `run-task` fetches from there over `file://`.
  The first sync, for John (root) to paste:
  `sudo -u supervisor sudo -n -u secretbroker /opt/engineer/bin/agent-run sync-mirror engineer-scratch`.
- The engineer's clone: `git clone /var/lib/engineer/mirrors/engineer-scratch.git ~/projects/engineer-scratch`
  as `engineer`, then `/opt/engineer/bin/new-project ~/projects/engineer-scratch --name engineer-scratch
  --owner jcallahanp --adopt` if the repo lacks the skeleton (it adds missing files only).
- The records clone must exist at `RECORDS_DIR/<project>` (`/var/lib/engineer/records/<project>`), owned by
  `supervisor`, before the supervisor starts; otherwise `records.ensure` starts an empty `engineer-records`
  history there. The mirror holds only the default branch, so work out the route (a supervisor clone from
  the mirror, then the `engineer-records` branch) and record it.
- `approve-plan PROJECT --record-id ID --item N --by NAME --source telegram|pr` is run by the supervisor; with
  `--source telegram` it reads John's `yes` from the records clone, so test it once on the scratch project.

## D. Checks only the real droplet can answer
- git on Ubuntu 24.04 refuses repos owned by another user: `mirror.sh` and `scripts/checks/clone.sh` add a
  one-shot `safe.directory` for the source. Confirm broker and supervisor fetches from engineer-owned repos
  work and that no global trust is left behind.
- SP18, before `--lock`: `push-branch` passes the bot token only as `http.<url>.extraheader` through
  `GIT_CONFIG_COUNT`. Push a branch to real GitHub over HTTPS with John's classic `repo` token (a
  fine-grained token cannot act as a collaborator on a personal-account repo); bot push to main and force
  push refused; `gh pr merge --auto` merges at zero approvals once checks pass.
- Egress: `nft -c` loads the ruleset; the mitmproxy `http_connect` hook still fires under
  `--ignore-hosts '.*'`; the proxy refuses CONNECT to any port but 443; `claude -p` works on the runtime
  list; rewrite the lists from the logged hosts (SP09, SP13, SP26).
- Scanners on the bare audit clone: gitleaks 8.30.1, osv-scanner 2.7.0, semgrep 1.181.0; semgrep
  `p/owasp-top-ten` with `--metrics=off` runs without a login.
- `verify-all.sh` runs as supervisor: `sudo -u supervisor /opt/engineer/scripts/checks/verify-all.sh --out
  /var/lib/engineer/setup-verify.md` (its default `--out` is relative to the working directory).
- Cloudflare: fill `templates/cloudflared/config.yml.tmpl` (tunnel ID, domain, credentials file under
  `/etc/cloudflared/`), confirm against Cloudflare's docs how to run it as a service, and write John the
  commands. SP71: noVNC through Access from his phone.
- Clay CLI: find its sign-in command in Clay's docs; John runs it as `secretbroker`. Telegram channel: its
  token and pairing commands from the Channels docs, for John's step 21.
- SP85 and SP86: Google and Attio sign-in from the droplet IP; logins after restoring the snapshot to a new
  droplet (then destroy it). If sign-in fails: fallback 1, a Tailscale exit node on an always-on device at
  John's home carrying the browser's traffic only; fallback 2, the same setup on a home Mac mini.
- SP01 (re-read the Agent SDK billing article and legal page, quotes into ADR 0001), SP02, SP10, SP89.

## E. Phase E: under the guards (after `--lock`)
- Rerun SP06, SP10, SP13 on scratch repos. On a failure John runs `--unlock`; the fix goes through a PR,
  then `--install` and `--lock`.
- `verify-all.sh` again; report the first failing row in the digest.
- UptimeRobot monitors for any further web service on the tunnel.
- `doctor.sh` all OK, including `unit_engineer-supervisor`; first night on `engineer-scratch` ends in a known
  state with a digest.

## F. Gaps found while writing the guide
- `setup-root.sh --install` makes no age key and no `recipient.txt`; John's step 5 does it by hand.
- It seeds no `CANARY`; part B asks John to.
- Fine-grained token limit (GitHub, "Managing your personal access tokens", read 2026-10-16); the plan and
  blueprint step 19 still say fine-grained.
