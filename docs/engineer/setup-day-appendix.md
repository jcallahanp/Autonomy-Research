# Setup day: builder appendix

For the builder session, not for John. [setup-day.md](setup-day.md) is John's guide; this file holds the
technical checks behind it, in the order of `research/blueprint/setup.md` phases B-E. The builder never holds
root: anything below that needs root is a command the builder writes out for John to paste. Record each
result (pass, fail, quote) in `engineer/docs/versions.md` or the ADR the row names, through a PR.

**Where repo changes are made.** The builder on the droplet runs as `engineer`, reads `/opt/engineer` and
`/srv/autonomy-research` (root's read-only clone), and has no checkout it can push from: stage 1 builds no
`~engineer/autonomy-research` and no push route for this repo. Every change to Autonomy-Research is made in
a claude.ai/code cloud session on the repo (as in phase A), as a PR John merges; John then runs
`git -C /srv/autonomy-research pull` and `setup-root.sh --install` (and `--lock` once locked). The on-VM
builder writes down what to change and why; John pastes that into the cloud session.

## A. Before the day (cloud session, one small PR)
- Done 2026-10-17: the `sops` and `bun` checksums in `engineer/templates/release-pins.txt` are filled, so
  no `TO-PIN` row is left (vendor checksum files, matched by download), and the nodesource and cloudflare key fingerprints in
  `engineer/templates/apt-repos.txt` were re-checked against each repo's signed index and the Ubuntu
  keyserver (the vendors do not print them).
- Done 2026-10-17: GitHub's published SSH host-key fingerprints are in the guide's step 3.
- Help John make `engineer-scratch` from the skeleton (guide, before-the-day step 4) if he asks: it must
  hold the skeleton, `.github/workflows/checks.yml` included, before SP18 can test auto-merge.

## B. Phase C: on the droplet as `engineer`, before the guards (blueprint steps 8-13)
- `bootstrap.sh` done (it exports `HTTPS_PROXY` from `PROXY_PORT`, since nft lets `engineer` reach only the
  proxy): `claude --version` matches `engineer/docs/versions.md`; the Telegram channel plugin is installed
  at user scope (needs Bun from part A).
- SP22: branded Chrome and Playwright MCP start on Xvfb (`DISPLAY=:99`); mermaid-cli renders one diagram.
- Hooks from a scratch project's `.claude/settings.json` (guards not registered yet): SP06 (Stop and
  TaskCompleted block with exit 2 under `-p`), SP09 (bwrap sandbox with the AppArmor profile), SP13 (bypass
  attempts: `git -C . push`, `sh -c`, Bash writes into `tests/acceptance/`), SP17 (approval-hash block).
  Hooks run as `/usr/bin/python3 -I`, so nothing in `~/.local/bin` can stand in for the interpreter.
- User namespaces for bwrap (SP09): Ubuntu 24.04 restricts unprivileged user namespaces through AppArmor
  (`kernel.apparmor_restrict_unprivileged_userns=1`). `bubblewrap` is in `apt-packages.txt`, and
  `--install` loads `templates/apparmor/bwrap`, an unconfined profile for `/usr/bin/bwrap` that grants
  `userns`. Check as `engineer`: `bwrap --unshare-user --ro-bind / / true` exits 0, and `/sandbox` in a
  session shows no missing dependency. If it fails, `apparmor_parser -r /etc/apparmor.d/bwrap` (root).
- Plan approval signs five files (`brief.md`, `requirements.md`, `integrations.yaml`, `profile.yaml`,
  `tasks.json` under `docs/plan/`); the audit fails any task diff that touches `docs/plan/`, and a task is
  done only after its PR merges. Check both once on the scratch project.
- Sandbox and the broker (SP09, SP11): bwrap sets no_new_privs, so `sudo` cannot work inside the Bash
  sandbox. Managed settings list `sandbox.excludedCommands: ["sudo -n -u secretbroker
  /opt/engineer/bin/agent-run *"]` (key and pattern syntax: code.claude.com/docs/en/settings-reference,
  read 2026-10-16). The same page says "Claude Code keeps a Bash call sandboxed when it has one of these
  shapes ... A command starting with `sudo`". Test it: from a session, Bash `sudo -n -u secretbroker
  /opt/engineer/bin/agent-run hc-ping ok`. If it stays sandboxed and fails, record it in
  `research/open-questions.md`; the fallback is an excluded root-owned wrapper whose name does not start
  with `sudo` (a code change, by PR).
- Sandbox network: `sandbox.network.httpProxyPort` is 3128, so the sandbox's host-side relay goes to the
  egress proxy (nft drops engineer's loopback connections to any port but 3128 and x11vnc's 5900, and all
  port-53 DNS). Check a sandboxed `curl https://api.github.com` works and `dig @127.0.0.53 example.com`
  fails. SOCKS through the sandbox is dead by design; local dev servers outside the sandbox and the
  brainstorming companion's localhost port are blocked for `engineer` too: record what breaks.
- Broker: John seeds a made-up `CANARY` (`setup-root.sh` does not seed one; deferred). SP11: `sudo -l` as
  engineer, `/proc/*/environ` and the SOPS file give the engineer no value. SP12: the canary never appears
  in transcripts, `agent-run.log` or job output.
- Supervisor on `engineer-scratch` (`scratch=yes`, so `run-task` starts sessions before `--lock`): SP04,
  SP05 (exit codes and `result.subtype`), SP08 (stall and restart; the Channels relay under tmux). The
  supervisor runs no planner or mapper profile in stage 1: planning and the as-is scan are interactive.
- SP07: the usage-limit patterns in `scripts/supervisor/limits.py` are synthetic. Replace them from the
  first real limit message; until then a night that hits a limit may end as an unknown stop. Also record
  what `autoContinueAtUsageLimit` does to a `claude -p` run with JSON output (open-questions).
- SP16 and SP87: whether one bot can serve both jobs, and whether Channels and Remote Control share a
  session or run side by side. Also check the Channels plugin stays out of `run-task` sessions (it is
  installed at user scope, so confirm `claude -p` there does not load it).
- SP64 and SP83: PreToolUse fires on Playwright MCP tools with a usable `tool_input`; record the exact
  Playwright tool names; check whether a server-level MCP name in an agent's `tools` grants that server's
  tools, and that `--plugin-dir /opt/engineer/plugin` with `--agent` picks the profile's agent.
- SP88: memory with real Attio, Clay and n8n tabs open, on 8 GB.
- For John: the healthchecks.io period and grace (from the supervisor loop's ping cadence and the longest
  run timeout in `templates/run-defaults.yaml`), and the branch-protection checklist for step 11, with the
  required check name (`checks` job in the project skeleton's workflow), "Dismiss stale pull request
  approvals" and "Require approval of the most recent reviewable push". "Restrict who can push to matching
  branches" exists only for organization repos (GitHub, "About protected branches", read 2026-10-16), so
  `engineer-records` cannot be limited to the bot on John's personal repos: record the fallback.
- Take John's n8n host (guide step 15) into `engineer/templates/browser-allowlist.txt` in the cloud PR.

## C. Projects, mirrors and records (after John's step 18)
- The supervisor's `sync-mirror` broker job fetches each project's default branch into the broker's bare
  mirror under `MIRROR_DIR` (`/var/lib/engineer/mirrors`); `run-task` fetches from there over `file://`.
  The first sync, for John (root) to paste:
  `sudo -u supervisor sudo -n -u secretbroker /opt/engineer/bin/agent-run sync-mirror engineer-scratch`.
- The engineer's clone: `git clone /var/lib/engineer/mirrors/engineer-scratch.git ~/projects/engineer-scratch`
  as `engineer`. The repo already holds the skeleton (John made it from `new-project`); for a repo that
  lacks it, `/opt/engineer/bin/new-project <dir> --name <name> --owner jcallahanp --adopt` adds missing
  files only.
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
  `GIT_CONFIG_COUNT`. Push a branch to real GitHub over HTTPS with the bot's classic `repo` token
  (`GH_BOT_PAT`; GitHub lists collaborator repos among fine-grained tokens' gaps, "Managing your personal
  access tokens", read 2026-10-16); bot push to main and force push refused; `gh pr merge --auto` merges at
  zero approvals once checks pass.
- Egress: `nft -c` loads the ruleset (the renderer's output passes `nft -c` in the tests); the mitmproxy
  `http_connect` hook still fires under `--ignore-hosts '.*'`; the proxy refuses CONNECT to any port but
  443; `claude -p` works on the runtime list; the supervisor's scanners reach their hosts through the
  proxy (its unit sets `HTTPS_PROXY`); rewrite the lists from the logged hosts (SP09, SP13, SP26).
- Scanners on the bare audit clone: gitleaks 8.30.1, osv-scanner 2.7.0, semgrep 1.181.0; semgrep
  `p/owasp-top-ten` with `--metrics=off` runs without a login (rules from `semgrep.dev`, on both lists).
- `verify-all.sh` runs as supervisor: `sudo -u supervisor /opt/engineer/scripts/checks/verify-all.sh --out
  /var/lib/engineer/setup-verify.md` (its default `--out` is relative to the working directory).
- Cloudflare: John's step 13 writes `/etc/cloudflared/config.yml` from the template (credentials copied to
  `/etc/cloudflared/<ID>.json`) and installs the service with `cloudflared --config ... service install`
  (developers.cloudflare.com, Tunnel local management, "As a service: Linux", read 2026-10-16). Check it; SP71: noVNC through
  Access from his phone.
- Clay CLI: deferred; stage 1 installs none. The Clay row of
  `verify-all.tsv` is n/a until a later stage installs it for `secretbroker`. Telegram channel: its token
  and pairing commands from the Channels docs, for John's step 23.
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

## F. Not in stage 1 (deferred), so not on the day
- Rootless Podman and the trial runner, a seeded `CANARY`, the builder's own checkout and push route,
  `gcloud`, Lynis, wrangler and the Clay CLI: none is installed by `setup-root.sh --install` or
  `bootstrap.sh`. Blueprint `stack.md` marks each row deferred.
- Bot-only pushes to `engineer-records` (organization repos only) and the usage-limit behaviour with
  JSON output are in `research/open-questions.md`.
