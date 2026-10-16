# Claude Code permission posture for unattended runs

Brief: Decide the Claude Code permission configuration for an engineer that runs overnight with no one to click yes, balancing no stalls against safety, on one Ubuntu VM John controls.
Run: research/runs/engineer-human-loop/PLAN.md

All docs pages opened 2026-10-16 with WebFetch (code.claude.com, page text saved and grepped; quotes copied from the saved text). Docs version context: features cited need Claude Code v2.1.259+ (`--permission-prompts`), v2.1.285+ (sandbox `false` precedence).

## Permission modes and headless behaviour
### Takeaway
Use `--permission-mode auto --permission-prompts none` for unattended `-p` runs only inside an isolated, non-root, egress-limited VM; `dontAsk` plus an exact allowlist is the strictest stall-free alternative; `bypassPermissions` only as a fallback inside a real container/VM. In `-p`, auto mode does not halt on repeated blocks: the blocked action is denied and Claude keeps working. Confidence: high (primary docs).

### Cited findings
- Mode table: `dontAsk` denies anything that would prompt, aimed at CI; `bypassPermissions` is for isolated containers and VMs only — https://code.claude.com/docs/en/permission-modes, opened 2026-10-16, WebFetch — Quote: "Locked-down CI and scripts" / "Isolated containers and VMs only"
- Deny rules hold in every mode including bypass — https://code.claude.com/docs/en/permission-modes, opened 2026-10-16, WebFetch — Quote: "Deny rules block in every mode, including `bypassPermissions`."
- Auto mode in `-p`: thresholds 3 in a row / 20 total are fixed; with no prompt to fall back to, the action is not run and the run continues — https://code.claude.com/docs/en/permission-modes, opened 2026-10-16, WebFetch — Quote: "When repeated blocks reach a threshold, the action doesn't run and Claude keeps working. Claude Code doesn't stop the run."
- The block counters are not configurable — same page — Quote: "The thresholds of 3 blocks in a row and 20 blocks total are not configurable."
- Anthropic's own caveat on auto mode — same page — Quote: "Auto mode reduces permission prompts but does not guarantee safety."
- `--permission-prompts none` (v2.1.259+) denies anything that would prompt and tells Claude not to retry, so nothing waits on a human; denials are listed in `permission_denials` in stream-json — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "Anything that would prompt is denied unless a `PermissionRequest` hook allows it, Claude is told that nobody can approve the request and not to retry it"
- In `-p` a bare `Bash` allow entry is dropped in auto mode — https://code.claude.com/docs/en/headless — Quote: "Claude Code drops a bare `Bash` entry as a broad allow rule and auto mode evaluates each command instead."
- A `-p` run with nothing set takes the built-in start mode, which can be auto, so pass the mode explicitly — https://code.claude.com/docs/en/headless — Quote: "A run where nothing sets a permission mode takes the built-in starting permission mode, which can be `auto`, so pass the one you want"
- `auto` or `bypassPermissions` set in project `.claude/settings.json` or `settings.local.json` is ignored; use the CLI flag or user/managed settings — https://code.claude.com/docs/en/permission-modes — Quote: "If you set `\"bypassPermissions\"` in those two files, it doesn't take effect either, and the session starts in Manual mode."
- Bypass refuses to run as root; Anthropic's unattended recipe requires a container, VM or sandbox runtime and a non-root user — https://code.claude.com/docs/en/permission-modes — Quote: "Required: a container, VM, or the sandbox runtime; on Linux and macOS, run it as a non-root user"
- Bypass warning — same page — Quote: "`bypassPermissions` offers no protection against prompt injection or unintended actions."
- In bypass `-p`, the few things that still prompt are denied; critical-path `rm` prompts time out after 2 minutes and are denied so the session keeps going — same page — Quote: "Claude Code denies the command and tells Claude what to do instead, so an unattended session keeps working."
- Classifier blocks by default include force-push-type and exfil actions, pushing to a third-party repo, `git remote set-url`, and launching agent loops without a sandbox — same page — Quote: "Changing where pushes go with `git remote set-url` or `git remote add`, unless you named the new remote"
- Prose boundaries ("don't push") are read by the classifier but can be lost on compaction; use deny rules for hard guarantees — same page — Quote: "a boundary can be lost if context compaction removes the message that stated it. For a hard guarantee, add a deny rule instead."
- Auto mode needs a supported model (Opus 4.6+, Sonnet 4.6+, Haiku 5.5 on the Anthropic API) — same page — Quote: "Claude Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5"
- Dev-container page endorses bypass for unattended work only with non-root plus egress limits — https://code.claude.com/docs/en/devcontainer — Quote: "Pair this flag with the network egress restrictions above to limit what a bypassed session can reach."

### Contradictions
- None found. (Note: sandbox-environments says the classifier "is not an isolation boundary" yet isolation is "not required" for auto; devcontainer page suggests auto instead of bypass. Consistent: auto is optional-isolation, bypass is mandatory-isolation.)

### Inferences
- Because blocked actions are silently denied and the run continues, an overnight auto-mode run can burn its budget on retries or finish "successfully" with the blocked step undone. The supervisor must read `permission_denials` and stop/flag at a threshold (my inference from the two `-p` quotes).
- The 20-total counter persists for the session, so a long single `-p` session degrades into denying more; prefer many short `-p` sessions with fresh state (inference).

### Gaps
- Exact exit code / result subtype when auto mode hits the 20-block limit in `-p` — not stated; spike.
- Classifier token/latency cost per action — docs section on cost not read; spike with `--output-format json`.

## Allow/deny rules, precedence, managed settings
### Takeaway
Rules evaluate deny, then ask, then allow; a deny anywhere wins. Bash deny rules match the written command text and are explicitly not a security boundary (git push has three documented rewordings). Put hard stops in managed settings (root-owned `/etc/claude-code/managed-settings.json`), in the sandbox, in a PreToolUse hook, and on the server (branch protection). Confidence: high.

### Cited findings
- Order — https://code.claude.com/docs/en/permissions, opened 2026-10-16, WebFetch — Quote: "Rules are evaluated in order: deny, then ask, then allow. The first match in that order determines the outcome"
- Deny cannot be carved out by allow — same page — Quote: "An allow rule can't carve an exception out of a deny rule."
- Documented bypass of `git push` deny — same page — Quote: "`git push *` | `git push origin main` | `git -C . push origin main`, `git -c push.default=current push origin main`, `git 'push' origin main`" (table row)
- Same for `curl`/`rm` via full path or `sh -c` — same page — Quote: "`/usr/bin/curl https://example.com`, `sh -c 'curl https://example.com'`"
- Anthropic's stance — same page — Quote: "a deny or ask rule covers the invocation Claude usually produces and isn't a security boundary around the program."
- Remedy named by the docs — same page — Quote: "For filesystem and network enforcement that doesn't depend on the command text, use sandboxing."
- Compound commands are split and deny applies to any subcommand, including nested ones — same page — Quote: "Deny and ask rules apply when any subcommand matches them, including a command nested inside a subshell, a command substitution, or a control-flow body"
- Wrapper list is fixed; `npx`, `docker exec` are not stripped — same page — Quote: "Development environment runners such as `direnv exec`, `devbox run`, `mise exec`, `npx`, and `docker exec` are not in the list."
- Managed settings beat everything including CLI flags — same page — Quote: "no other level, including command line arguments, can override a managed permission rule."
- Deny at any level is final — same page — Quote: "a managed settings deny can't be overridden by `--allowedTools`"
- `disableBypassPermissionsMode`/`disableAutoMode` work from any scope; most useful in managed — same page — Quote: "These are most useful in managed settings where they can't be overridden."
- Linux managed file path — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "Claude Code reads `/etc/claude-code/managed-settings.json` on Linux and applies it at the highest precedence in the settings hierarchy"
- A PreToolUse deny cannot be overridden by allow, and exit 2 beats allow rules — https://code.claude.com/docs/en/permissions — Quote: "A hook that exits with code 2 stops the tool call before permission rules are evaluated, so the block applies even when an allow rule would otherwise let the call proceed."
- A hook "allow" cannot override deny/ask rules — same page — Quote: "Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns"
- A `-p` session runs the project's hooks and `.mcp.json` servers without any trust dialog unless `--bare` — https://code.claude.com/docs/en/headless — Quote: "A `-p` session shows no workspace trust dialog and no per-server approval prompt."

### Contradictions
- None found.

### Inferences
- Because of the `-p` trust gap, repos the engineer clones (hooks in `.claude/settings.json`) execute with the agent's rights; run `--bare` or pin `--settings` for runs on third-party code, or keep it to John's own repos (inference).
- The protocol-run claim (git push deny can be bypassed by rewording) is confirmed by the official table above; the real stop is server-side branch protection (git-and-merge.md lines 105 and 125).

### Gaps
- Whether `allowManagedPermissionRulesOnly` plus a file in `/etc/claude-code` is honoured when Claude runs as a non-root user without MDM — documented as supported on Linux but not spiked.

## Hooks as guardrails
### Takeaway
A PreToolUse hook is the best place for a custom guard that inspects the full command (exit 2 or JSON deny; blocks even over allow rules), but hooks fail open on timeout/error unless `onFailure: "block"` is set, hooks run outside the sandbox, and the doc itself says use the permission system for hard allow/deny. Confidence: medium-high (hooks page read to char 100k of 270k).

### Cited findings
- Exit 2 and JSON decisions — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch — Quote: "Exit code 0 with no output means the hook has no decision to report, so the tool call continues through the normal permission flow."
- PermissionRequest cannot use exit 2 — same page — Quote: "Exit code 2 isn't honored for this event and the permission flow proceeds unchanged. Deny through the `decision` object instead."
- MCP matchers need `.*` — same page — Quote: "The `.*` is required: a matcher like `mcp__memory` or `mcp__brave-search` contains only exact-match characters"
- Fail-open on timeout — same page — Quote: "A timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call"
- `if` filter best-effort — same page — Quote: "Because the `if` filter is best-effort, use the permission system rather than a hook to enforce a hard allow or deny."
- Defaults: command hook timeout 600 s — same page — Quote: "600s for `command`, `http`, and `mcp_tool`"
- Hooks run with full access outside the Bash sandbox — https://code.claude.com/docs/en/sandboxing, opened 2026-10-16 — Quote: "command hooks, local MCP servers, plugin monitors, LSP servers, and helper commands such as your status line command and `apiKeyHelper` run with your full access"
- `--permission-prompts none` still lets a PermissionRequest hook allow a call (route to a human, see human-loop facet) — https://code.claude.com/docs/en/headless — Quote: "Anything that would prompt is denied unless a `PermissionRequest` hook allows it"
- Anthropic's cwc example uses PreToolUse `*` kill-switch hook that blocks every call while a file exists — https://github.com/anthropics/cwc-long-running-agents claude-code-config/.claude/hooks/kill-switch.sh:3 (commit ad107a9), read 2026-10-16, git clone + sed — Quote: "# Halt every tool call while ./AGENT_STOP exists. `touch AGENT_STOP` to engage; `rm AGENT_STOP` to resume."
- That repo is explicitly an example, not maintained — https://github.com/anthropics/cwc-long-running-agents README.md (commit ad107a9), read 2026-10-16 — Quote: "These are example ingredients, not a turnkey harness. Event demo; not maintained and not accepting contributions."

### Contradictions
- None found.

### Inferences
- Hook guards should be small fast scripts with `onFailure: "block"` (v2.1.295+; version of the VM install must be checked) and be tested for fail-closed behaviour; a hook that cannot run must not mean "allowed" (inference).
- A kill-switch file hook is cheap, gives John a stop that works from his phone via SSH, and is already written by Anthropic (copy, do not install the repo).

### Gaps
- Whether PermissionRequest hooks fire in `-p` with `--permission-prompts none` for classifier-denied (auto) actions: docs say they resolve "requests that nothing else resolves"; not spiked. Remaining 170k chars of hooks page not read.
- Hook latency numbers: only the `if` spawn-overhead remark found; no benchmark.

## Sandboxing
### Takeaway
The built-in Bash sandbox (bubblewrap/socat on Linux) is OS-enforced but covers only shell commands. Anthropic states it is not sufficient for fully unattended runs in either auto or bypass; wrap the whole process (container, VM, sandbox-runtime) and limit egress. Confidence: high.

### Cited findings
- Not sufficient alone — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "The sandboxed Bash tool on its own constrains only shell commands, so it is not sufficient for fully unattended runs in either mode."
- Coverage — https://code.claude.com/docs/en/sandboxing — Quote: "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it."
- Network allowlist starts empty — same page — Quote: "Connections go through a proxy on your machine that checks each host against your allowed domains, which start empty."
- Escape hatch: disable it for unattended runs — same page — Quote: "You can disable the unsandboxed retry by setting `\"allowUnsandboxedCommands\": false`"
- A matching allow rule also approves unsandboxed retry — same page — Quote: "An allow rule that matches a command also approves an unsandboxed retry of it, so the command can run outside the sandbox with no prompt."
- Fails open if bubblewrap missing — same page — Quote: "By default, if the sandbox can't start because a dependency is missing or the platform is unsupported, Claude Code runs commands without sandboxing."
- Ubuntu 24.04 needs an AppArmor profile for bwrap — same page — Quote: "On Ubuntu 24.04 and later, the default AppArmor policy prevents bubblewrap from creating the user namespaces it needs for isolation."
- Exfiltration residual risk — same page — Quote: "Allowing broad domains such as `github.com` can create paths for data exfiltration."
- Limits — same page — Quote: "Sandboxing reduces risk but is not a complete isolation boundary."
- Whole-process options — https://code.claude.com/docs/en/sandbox-environments — Quote: "Every other approach in the table puts the whole Claude Code process inside the isolation boundary, so file tools, MCP servers, and hooks are restricted too."
- sandbox-runtime is beta — same page — Quote: "The runtime is a beta research preview, and its configuration format may change as the package evolves."
- Devcontainer caveat — https://code.claude.com/docs/en/devcontainer — Quote: "dev containers do not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in `~/.claude`."
- Firewall is example only; needs NET_ADMIN — same page — Quote: "It is provided as a working example rather than a maintained base image"
- VM is strongest isolation — sandbox-environments — Quote: "A dedicated virtual machine provides the strongest separation, with its own kernel"

### Contradictions
- None found.

### Inferences
- John's Ubuntu VM is already the "virtual machine" row; if it holds only the engineer's work (no John personal keys, no ~/.ssh with broad rights), VM + non-root user + Bash sandbox + host firewall egress allowlist meets Anthropic's own unattended recipe without Docker (inference from sandbox-environments + devcontainer pages).
- The Claude OAuth credential in `~/.claude` is exfiltratable by any bypassed session; use a dedicated account/token and treat it as burnable (inference from devcontainer warning).

### Gaps
- Whether the VM has KVM (Docker Sandboxes route) and whether AppArmor `kernel.apparmor_restrict_unprivileged_userns` is 1 — must be checked on the machine.

## What others do overnight
### Takeaway
Anthropic's own guidance and example repo rely on hooks, evaluator subagents, and outer loop scripts, not on permission magic; practitioners who ran with skip-permissions report destructive-command and credential-reach incidents, and fixes are containers, egress limits and auto mode. Confidence: medium (one practitioner blog and one open issue opened).

### Cited findings
- cwc README: unattended loop is an outer script with capped sessions — https://github.com/anthropics/cwc-long-running-agents README.md (commit ad107a9), read 2026-10-16 — Quote: "Cap session length and have an outer script start the next one (pick next feature, build, evaluate, reset)"
- cwc suggests pairing with ralph-loop or `claude -p "continue from PROGRESS.md"` — claude-code-config/README.md:29 (commit ad107a9) — Quote: "For unattended multi-session runs, pair this config with the [`ralph-loop`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop) plugin"
- cwc README contains an agent-addressed instruction: "In your project, run `claude` and paste: Clone github.com/anthropics/cwc-long-running-agents into /tmp, copy its `claude-code-config/.claude/` directory..." — page contains instructions addressed to agents; not followed.
- Incident (24 h, skip-permissions): empty-variable `rm -rf`, a typosquatted skill POST, a leaked key; cost ~$387 — https://kenimoto.dev/blog/autonomous-agent-24-hours-security-lessons/, opened 2026-10-16, WebFetch (summary; verbatim quote from page: "sandboxing, not vibes") — Quote: "sandboxing, not vibes"
- Incident, issue #99198 (open 2026-10): sub-agent in `bypassPermissions` ran `rm -rf C:/Users/<USER~1>` via 8.3 short name; kept running ~45 min after stop; no maintainer reply; page also has a commenter promoting their own interception layer (unrelated promotion, not followed) — https://github.com/anthropics/claude-code/issues/99198, opened 2026-10-16, WebFetch — Quote: "bypassPermissions"
- Classifier now blocks the unresolved-variable `rm -rf "$VAR"` case that bit the 24 h run — https://code.claude.com/docs/en/permission-modes — Quote: "A recursive forced delete such as `rm -rf \"$VAR\"`"
- Search also surfaced (titles only, not opened): issue #32938 "Claude deleted 11h of inference output without permission then restarted job", nope.net and Docker "rm -rf ~/" incident write-ups.

### Contradictions
- None found.

### Inferences
- Windows path-aliasing in #99198 does not transfer to Ubuntu, but the lesson does: deny/allow decisions made on command text are weak; the OS/VM boundary and server-side protections are what hold.

### Gaps
- Ralph-specific 2026 posts, Anthropic "harness-design-long-run" engineering post, and nope.net/Docker/#32938 pages not opened.

## Recommended posture
### Takeaway
Recommendation: dedicated non-root Linux user on John's VM, `claude -p` per task from a supervisor with `--permission-mode auto --permission-prompts none --max-turns N --max-budget-usd X`, Bash sandbox on with the retry hatch off and `failIfUnavailable`, a root-owned managed-settings file holding deny rules and `disableBypassPermissionsMode`, a fail-closed PreToolUse guard hook plus kill-switch file, host-level egress allowlist, and server-side GitHub protections. Fallback if auto's false positives stall work: `dontAsk` with an exact allowlist; second fallback: `bypassPermissions` inside a container with the firewall. Confidence: medium (design synthesised from docs; not spiked).

### Cited findings
(See the sections above; each element rests on a cited line there.)

### Contradictions
- None found.

### Inferences
- Mode: auto, because Anthropic positions it as the lower-risk hands-off mode (devcontainer page: "consider auto mode instead") and it needs no isolation to start, while the VM adds defence in depth. Set it by flag or user/managed settings, never project settings.
- Allow list (with `dontAsk`/auto): Read/Edit/Write in the work dir, specific `Bash(git status|diff|log|add|commit|checkout -b *)`, test/lint/build commands by exact prefix, `gh pr create`, `WebFetch(domain:...)` for docs. Do not put bare `Bash` or `Bash(npx *)`, `Bash(docker *)`, `Bash(bash *)` in allow (wrapper/interpreter holes).
- Deny list (managed): `Read(**/.env*)`, `Read(~/.ssh/**)`, `Read(~/.config/gh/**)`, `Bash(git push --force*)`, `Bash(git push *main*)`, `Bash(gh pr merge *)` except `--auto`, `Bash(rm -rf *)`, `Bash(curl *)`, `Bash(wget *)`, `Bash(sudo *)`, plus the PreToolUse hook which parses the whole command (catching `git -C . push`, `sh -c`, `/bin/rm`). Treat all as defence in depth.
- Hooks: PreToolUse `*` kill-switch (cwc pattern), PreToolUse Bash guard with `onFailure: "block"`, Stop hook for done-gate (other facet). Keep each under a second.
- OS limits: dedicated user, no sudo, no access to John's keys; systemd unit or `ulimit`/cgroup caps (MemoryMax, TasksMax, CPUQuota) and a wall-clock `timeout`; nftables/iptables egress allowlist (api.anthropic.com, github.com, package registries) matching the devcontainer init-firewall idea; disk quota on workdir; dedicated bot-account fine-grained PAT, branch protection on main.
- Supervisor: parse `permission_denials` and `result.subtype`; stop the night after N denials of the same kind (auto never halts itself); run short sessions to reset the 20-block counter.
- What still needs John: one-time install of the AppArmor bwrap profile and managed-settings file (root), creating the bot account/PAT and branch protection, choosing the egress allowlist, deciding what is a hard stop (actions routed to him via PermissionRequest hook/channel, see human-loop notes), and reviewing denials each morning.
- Spike before building: (1) auto + `--permission-prompts none` on a task that triggers a block; record exit code, `permission_denials`, behaviour past 20 blocks; (2) rewording bypasses (`git -C . push`) against deny rules + hook + server rule; (3) sandbox with `allowUnsandboxedCommands:false` on Ubuntu 24.04, confirm `failIfUnavailable`; (4) hook timeout fail-open vs `onFailure: block`; (5) managed-settings file read by non-root user; (6) classifier cost/latency per action.
- Alternatives considered: bypass in container (stronger stall-freedom, zero classifier cost, no protection from injection); Docker Sandboxes microVM (needs KVM, Docker login); sandbox-runtime wrap (beta); cloud sessions/routines (already in registry). Rejected: bypass directly on the host VM with John's own account; Bash-sandbox-only; relying on prose boundaries or deny rules alone; Ralph loop as shipped (unbounded, see registry).

### Gaps
- No spike run; all behaviour from documentation. Claude Code version on John's VM unknown, several features need v2.1.259 to v2.1.295.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Auto mode (`--permission-mode auto`) | https://code.claude.com/docs/en/permission-modes | Classifier reviews actions; 3-in-a-row/20-total blocks fall back to prompt, in `-p` denied and run continues | Claude Code | 2026-10-16 | Use as unattended mode inside VM; supervisor must watch denials |
| `--permission-prompts none` | https://code.claude.com/docs/en/headless | Denies anything that would prompt; tells Claude not to retry (v2.1.259+) | Claude Code `-p` | 2026-10-16 | Use with auto |
| dontAsk mode | https://code.claude.com/docs/en/permission-modes | Denies all non-allowlisted prompts | Claude Code | 2026-10-16 | Fallback: strictest stall-free mode |
| bypassPermissions | https://code.claude.com/docs/en/permission-modes | Skips all prompts; non-root and isolation required | Claude Code | 2026-10-16 | Fallback in container only |
| Managed settings file (/etc/claude-code/managed-settings.json) | https://code.claude.com/docs/en/devcontainer | Highest-precedence settings, not overridable by session/flags | Linux | 2026-10-16 | Use for deny rules and disableBypassPermissionsMode; spike non-root read |
| PreToolUse / PermissionRequest hooks | https://code.claude.com/docs/en/hooks | Custom deny/allow before permission rules; fail-open on timeout unless onFailure block | Claude Code | 2026-10-16 | Use for command-aware guard and kill switch |
| anthropics/cwc-long-running-agents | https://github.com/anthropics/cwc-long-running-agents | Kill-switch, steer, verify-gate, commit-on-stop hooks, evaluator subagent; event demo, unmaintained | local clone read only (commit ad107a9) | 2026-10-16 | Reference; copy kill-switch.sh and verify-gate idea, do not install |
