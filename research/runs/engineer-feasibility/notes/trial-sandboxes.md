# Sandboxes for parallel trials and growing the spike skill

Brief: Choose how an autonomous Claude Code engineer runs several candidate paths in parallel safely (isolation, credentials, network, result capture, cleanup) on John's Ubuntu VM, and how the spike skill should grow for build-time trials.
Run: research/runs/engineer-feasibility/PLAN.md

All pages opened 2026-10-16 (WebFetch; Parallel fetch returned "Too Many Requests"). Claude Code docs pages cite versions up to about v2.1.295.

## What Claude Code offers today for parallel isolated work

### Takeaway
Claude Code now covers file isolation well (worktrees, worktree-isolated subagents, agent view background sessions, /batch) and shell isolation partly (bubblewrap Bash sandbox with an empty-by-default domain allowlist). It does not isolate MCP servers, hooks or file tools, does not enforce per-trial credentials except through the sandbox credential mask, and its own docs say the Bash sandbox alone is "not sufficient" for fully unattended runs. Trials that need network plus credentials need a container or VM boundary around the whole process. Confidence: high.

### Cited findings
- Worktrees are the first-party parallel-edit primitive; one flag creates an isolated checkout and branch — https://code.claude.com/docs/en/worktrees, opened 2026-10-16, WebFetch — Quote: "Pass `--worktree` or `-w` with a name to create an isolated worktree and start Claude in it."
- Subagents can be pinned to a worktree in frontmatter and are removed when they finish without changes — same page — Quote: "Each subagent gets a temporary worktree that Claude Code removes automatically when the subagent finishes without changes"
- Headless `-p` worktrees are not cleaned up automatically, so the engineer's supervisor must sweep them — same page — Quote: "Non-interactive runs with `-p` have no exit prompt, so Claude doesn't clean up their worktrees"
- Worktree checks guard git and edit targets only, not arbitrary writes — same page — Quote: "None of them tracks which files a shell command writes"
- A worktree does not carry gitignored files such as `.env` unless `.worktreeinclude` lists them; that file is the one place a trial would receive local secrets, so it must stay empty or hold test values only — same page — Quote: "To carry gitignored files such as `.env` into every new worktree automatically, add a [`.worktreeinclude` file]"
- Five parallel approaches exist; worktrees isolate files; agent teams do not — https://code.claude.com/docs/en/agents, opened 2026-10-16, WebFetch — Quote: "Agent teams don't isolate teammates in worktrees"
- Agent view dispatches background sessions (research preview) — same page — Quote: "One screen to dispatch and monitor sessions running in the background, opened with `claude agents`. Research preview"
- `/batch` is a packaged worktree fan-out of 5 to 30 subagents — same page — Quote: "has Claude split one large change into 5 to 30 worktree-isolated subagents"
- Parallel runs multiply token use — same page — Quote: "Running several sessions or subagents at once multiplies token usage."
- The Bash sandbox covers shell commands only — https://code.claude.com/docs/en/sandboxing, opened 2026-10-16, WebFetch — Quote: "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it."
- Network default is deny with an empty allowlist — same page — Quote: "No direct route out. Connections go through a proxy on your machine that checks each host against your allowed domains, which start empty."
- Linux needs bubblewrap and socat; Ubuntu 24.04+ needs an AppArmor profile for bwrap (a one-off sudo step on John's VM) — same page — Quote: "On Ubuntu 24.04 and later, the default AppArmor policy prevents bubblewrap from creating the user namespaces it needs for isolation."
- Credentials can be masked: the sandboxed command sees a placeholder and the proxy substitutes the real value (needs TLS termination, which is experimental) — same page — Quote: "Claude Code shows sandboxed commands a per-session placeholder called the sentinel" and "the proxy substitutes the real value inside request contents, so it has to see them."
- Built-in credential deny list is empty — same page — Quote: "There is no built-in credential deny list, so only the files and variables you list are restricted."
- Allowlist is by hostname, so a leaky allowed domain defeats it — https://code.claude.com/docs/en/agent-sdk/secure-deployment, opened 2026-10-16, WebFetch — Quote: "The proxy allowlists domains based on the client-supplied hostname and does not terminate or inspect encrypted traffic."
- Anthropic's own verdict on the Bash sandbox for unattended work — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "on its own constrains only shell commands, so it is not sufficient for fully unattended runs in either mode."
- Skip-permissions needs a non-root user — same page — Quote: "On Linux and macOS, Claude Code refuses to start with this flag when running as root, so run the container, VM, or sandbox runtime as a non-root user."
- Sandbox runtime wraps the whole process (file tools, MCP, hooks), beta — same page — Quote: "The runtime is a beta research preview, and its configuration format may change as the package evolves."
- Headless: structured result, cost and exit code per run — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "With `--output-format json`, the response payload includes `total_cost_usd` and a per-model cost breakdown"
- `--bare` is recommended for scripts but cannot use the subscription login — same page — Quote: "In bare mode, Claude Code never reads OAuth credentials or the system keychain."
- Without `--bare`, a `-p` run in a trial directory executes that directory's hooks and MCP servers — same page — Quote: "Without `--bare`, a `-p` session runs the hooks in a project's `.claude/settings.json` and connects the servers in its `.mcp.json`, even in a folder you've never trusted."
- Kill behaviour: SIGTERM gives exit 143 and no result for the in-flight turn — same page — Quote: "Claude Code exits with code 143."

### Contradictions
- None found. (Note the tension, not a source conflict: `--bare` is "the recommended mode for scripted and SDK calls" but bare mode reads no OAuth login, while engineer-runtime.md recommends subscription login on the VM. Settle by spiking trials with `ANTHROPIC_API_KEY` only for trials, or without `--bare`.)

### Inferences
- Parallel trial = one worktree (or throwaway dir) + one `claude -p` process per path, supervised by the engineer; the built-in Bash sandbox is a second layer, not the boundary (rests on sandbox-environments and sandboxing quotes above).
- Agent teams and agent view are the wrong fit for trials: no worktree isolation (teams), research preview and results go "only to you" (agent view), versus `-p` with JSON results the supervisor can read.

### Gaps
- Whether a subagent's `isolation: worktree` frontmatter can also carry a per-agent sandbox or credential scope: not found on the pages opened.
- Whether `claude -p` under subscription login can run `--max-budget-usd` cleanly with the sandbox on: not tested (spike).

## Local isolation on the Ubuntu VM

### Takeaway
Cheapest adequate boundary on one Ubuntu VM: the Claude Code process for each trial runs as a non-root user inside a hardened rootless container (Docker or Podman) with no direct network, reaching an allowlisting, credential-injecting proxy on the host. Anthropic documents exactly this pattern. gVisor and Firecracker add kernel isolation at real cost and are worth it only for untrusted code. Docker Sandboxes (sbx microVM) is the lowest-effort strong option if the VM exposes KVM, which is unknown. Confidence: medium (KVM availability and Podman specifics unverified).

### Cited findings
- Hardened container recipe with no network and a proxy socket is documented by Anthropic — https://code.claude.com/docs/en/agent-sdk/secure-deployment, opened 2026-10-16, WebFetch — Quote: "Removes all network interfaces; the agent communicates through the mounted Unix socket below"
- Credentials stay outside the boundary — same page — Quote: "The recommended approach is to run a proxy outside the agent's security boundary that injects credentials into outgoing requests."
- Mounted code can leak secrets even read-only — same page — Quote: "Even read-only access to a code directory can expose credentials."
- Tools that ignore proxy variables exist — same page — Quote: "Node.js `fetch()` ignores these variables by default; in Node 24+ you can set `NODE_USE_ENV_PROXY=1` to enable support."
- gVisor: strong isolation, I/O cost — same page — Quote: "Up to 10-200× slower for heavy open/close patterns"
- Firecracker microVM numbers — same page — Quote: "It can boot VMs in under 125ms with less than 5 MiB memory overhead"
- Anthropic's isolation table lists effort: dev container medium, custom container medium to high, VM high — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "| [Virtual machine](#virtual-machine) | Full operating system | No | High |"
- Reference devcontainer has a default-deny firewall and is meant for unattended runs — same page — Quote: "Because the firewall blocks unapproved egress, a configuration like this supports running Claude Code with `--dangerously-skip-permissions` for unattended work."
- Unprivileged containers break nested bubblewrap — same page — Quote: "Unprivileged containers need `enableWeakerNestedSandbox`"
- Docker Sandboxes (`sbx`) runs agents in microVMs with host-side credential injection and deny-by-default egress — https://docs.docker.com/ai/sandboxes/security/, opened 2026-10-16, WebFetch — Quote: "The raw credential values never enter the VM."
- sbx Linux requirements — https://docs.docker.com/ai/sandboxes/install/, opened 2026-10-16, WebFetch — Quote: "KVM hardware virtualization supported and turned on by the CPU, and your user account in the `kvm` group."
- sbx Ubuntu support is 24.04+ and its documented install is a `curl | sh` (page text, not an instruction to this agent; not run) — same page — Quote: "Ubuntu 24.04 or later."
- sbx teardown and Claude Code launch — https://docs.docker.com/ai/sandboxes/get-started/ and https://docs.docker.com/ai/sandboxes/agents/claude-code/, opened 2026-10-16, WebFetch — Quote: "Removing a sandbox deletes everything inside it." and "Launch Claude Code in a sandbox by pointing it at a project directory:"
- sbx does not import host Claude config — same Claude page — Quote: "Sandboxes don't pick up user-level configuration from your host, such as `~/.claude`."
- sbx clone mode keeps the host tree read-only — https://docs.docker.com/ai/sandboxes/security/ — Quote: "Clone mode: Your repository is mounted read-only, and the agent works on a private clone."
- Rootless Podman prerequisites are small but real — https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md, opened 2026-10-16, WebFetch — Quote: "Rootless Podman requires the user running it to have a range of UIDs listed in the files /etc/subuid and /etc/subgid."

### Contradictions
- None found.

### Inferences
- Per-trial network scope = a per-trial allowlist file given to the host proxy (Envoy, mitmproxy or Squid are named by Anthropic); per-trial credential = a short-lived or test-account token the proxy injects for that trial's container only, never an env var (rests on the proxy-pattern quotes).
- Cost to set up: Docker plus a proxy and a firewall-less `--network none` container is roughly a day of one-off work with Anthropic's reference devcontainer as the starting point; gVisor adds a runtime install; Firecracker needs KVM and is rejected for one VM (inference; Anthropic rates VM effort High).
- If John's VM is itself a cloud VM, nested KVM may be missing, which would rule out sbx and Firecracker (inference; not checked on his VM).

### Gaps
- Whether John's VM exposes `/dev/kvm`: unknown; a one-line check `ls /dev/kvm` decides sbx and Firecracker.
- Podman rootless limits (ports, cgroup delegation, performance): the tutorial opened did not cover them; not verified. Firejail, LXD, devcontainers beyond Anthropic's reference: not researched.
- Docker Sandboxes pricing: the fetch summary said the CLI and local compute are free and cloud is pay-as-you-go, but not as a verbatim quote, so it is not cited.
- sbx on non-KVM hosts, and whether its network policy can be set per sandbox: not seen.

## Hosted sandboxes

### Takeaway
Hosted sandboxes are not worth it for John's trials by default: the VM already exists, and trials that hold credentials or customer data would leave it. Use hosted only when the VM cannot give strong isolation (no KVM, untrusted code) or when concurrency or public URLs outweigh data-leaving risk. If one is needed, Vercel Sandbox (Firecracker microVMs, free Hobby tier, 24-hour Pro sessions) or E2B (prebuilt `claude` template, $100 one-time credit) are the most direct. Confidence: medium (Fly, Northflank and Runloop not opened; Cloudflare price not opened).

### Cited findings
- E2B: ready-made Claude Code template, headless flags, open internet by default — https://docs.e2b.dev/agents/claude-code, opened 2026-10-16, WebFetch — Quote: "E2B provides a pre-built `claude` template with Claude Code already installed."
- E2B egress is open unless set — same page — Quote: "The sandbox isolates the agent from your host machine, but sandboxes can reach the open internet by default."
- E2B passes the API key as a sandbox env var, so the credential is inside the boundary — same page — Quote: "Use `-p` for non-interactive mode and `--dangerously-skip-permissions` to auto-approve all tool calls."
- E2B price and limits — https://e2b.dev/pricing, opened 2026-10-16, WebFetch — Quote: "One-time $100 in usage credits." / "Up to 1 hour per sandbox session." / "Up to 20 concurrently running sandboxes." / "$150 monthly plan fee, plus usage"
- Daytona: free credit and startup claim — https://www.daytona.io/pricing, opened 2026-10-16, WebFetch — Quote: "$200 in free compute included." / "Sub 90ms sandbox creation from code to execution."
- Vercel Sandbox quotas (page last_updated 2026-09-10) — https://vercel.com/docs/vercel-sandbox/pricing (served as /docs/sandbox/pricing), opened 2026-10-16, WebFetch — Quote: "| Max Session Duration | 45 minutes | 24 hours | 24 hours |" and "| Concurrent Sandboxes | 10 | 10,000 | 10,000 |"
- Vercel Hobby hard-stops rather than bills — same page — Quote: "Once you exceed the quotas, sandbox creation is paused until 30 days have passed since you first used the feature."
- Vercel cost example for a 30-minute 4 vCPU build and test — same page — Quote: "| Build and test | 30 min | 4 | 8 GB | $0.0256 | $0.0848 | $0.1104 |"
- Vercel egress cost, downloads free — same page — Quote: "Data your sandbox downloads from the internet, such as packages, Git repositories, artifacts, and datasets, is free."
- Vercel persistence: snapshots expire by default — same page — Quote: "Snapshots expire **30 days after their last use by default**."
- Modal sandbox price is about 3x container price; Starter has monthly credit — https://modal.com/pricing, opened 2026-10-16, WebFetch — Quote: "$30 / month free credits" and "$0.00003942 / core / sec"
- Cloudflare Sandbox SDK runs coding agents per task, needs a paid Workers plan — https://developers.cloudflare.com/sandbox/, opened 2026-10-16, WebFetch — Quote: "Run coding agents such as Claude Code, Codex, and Devin in a sandbox that belongs to one task."
- Cloudflare plan gate — same page — Quote: "Available on Workers Paid plan"
- Anthropic itself says managed services can host the container — https://code.claude.com/docs/en/sandbox-environments — Quote: "Several managed sandbox and remote execution services can host the container for you."

### Contradictions
- None found.

### Inferences
- Hosted data handling: every hosted option puts the repo and any injected token on a third party; E2B's own example passes the key as an env var inside the box. Only the proxy pattern keeps credentials out, and no hosted page opened documents a credential-injecting egress proxy (Docker sbx does, locally).
- Break-even: 10 trials of 30 minutes on Vercel Pro cost about $1.10 in total (10 x $0.1104), far below John's effort to build a local proxy; but Hobby caps at 45 minutes and 5 CPU-hours a month, so Hobby serves occasional probes only. Hosted wins on effort for one-off public-code probes; local wins on credentials and data (inference).
- Claude Code drives hosted boxes through each vendor's SDK or CLI from a Bash/MCP call; no source opened shows an official first-party MCP for any of them (not checked).

### Gaps
- Fly Machines, Northflank, Runloop: no page opened.
- Startup times for E2B, Vercel, Modal, Cloudflare: not stated on pages opened (Daytona claim is vendor marketing).
- Cloudflare Containers price, Daytona per-sandbox limits and egress rules: not stated in the fetch results.
- Data retention and training terms for each vendor: not opened.

## Result capture and cleanup

### Takeaway
Use `claude -p --output-format json --json-schema` for the trial agent, so each trial returns one machine-readable record, and have the supervisor (not the agent) write `result.json` with exit code, duration, cost, artifacts and teardown status. Teardown is guaranteed by the container/VM lifecycle (`--rm`, `sbx rm`, hosted timeout), not by the agent's own `rm -rf`. Confidence: medium; the record schema is my design.

### Cited findings
- JSON output carries result, session id and metadata, and a schema can force a structured field — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "`json`: structured JSON with result, session ID, and metadata"
- Schema-validated output — same page — Quote: "The response includes metadata about the request (session ID, usage, etc.) with the structured output in the `structured_output` field."
- Cost figures are estimates — same page — Quote: "Both figures are [client-side estimates](/docs/en/agent-sdk/cost-tracking) and can differ from your actual bill."
- Exit status — same page — Quote: "Claude Code exits with code 0 on success and a non-zero code when the run fails, so your scripts can branch on the exit status."
- Permission denials are reported in the final stream message — same page — Quote: "the final result message lists them in `permission_denials`."
- Background work can hold a run open for 10 minutes — same page — Quote: "Claude Code stops whatever is still running after 10 minutes of continuous idle waiting by default and drops its partial result."
- Budget cap stops background work — same page — Quote: "If the run reaches its [`--max-budget-usd`](/docs/en/cli-reference#cli-flags) cap, Claude Code stops the remaining background work instead of waiting."
- Ephemeral writable locations and review before persist — https://code.claude.com/docs/en/agent-sdk/secure-deployment — Quote: "an overlay filesystem lets the agent write without modifying underlying files."
- Container tmpfs clears on stop — same page — Quote: "Provides a writable temporary directory that's cleared when the container stops"
- Sandbox runtime review step after unattended runs — https://code.claude.com/docs/en/sandbox-environments — Quote: "Review the paths you kept writable. On Linux and WSL2, also review anything the session created."
- Vercel cost control: stop promptly, spend management — https://vercel.com/docs/vercel-sandbox/pricing — Quote: "Stop sandboxes promptly: Call `sandbox.stop()` when done rather than waiting for timeout"
- Pro tier spend alerts — same page — Quote: "configure [Spend Management](/docs/spend-management) to receive alerts or pause projects when you reach a specified amount."

### Contradictions
- None found.

### Inferences
- Proposed trial result record (mine): `{trial_id, path, question, probe, verdict, exit_code, duration_s, cost_usd (from total_cost_usd), network_hosts_denied, creds_used (names only), artifacts[], log_path, teardown: ok|failed, started, ended}`. Teardown failure is itself a verdict-blocking field.
- Cost caps are three layers: `--max-budget-usd` and `--max-turns` per run (already in the registry), a wall-clock `timeout` wrapper whose SIGTERM yields exit 143, and a per-night total owned by the supervisor. Hosted adds the vendor's spend limit.
- Sweep job: `git worktree list`, `docker ps -a --filter label=trial`, and tmp dirs older than a threshold, run at engineer start (worktree locks from killed sessions are released by Claude Code's own sweep, per the worktrees page).

### Gaps
- Whether `--max-budget-usd` exit codes are distinguishable: already open in the registry; not re-tested.
- Log redaction of injected tokens in trial transcripts: not researched.

## Spike skill gaps for build-time trials

### Takeaway
The spike skill is built for short, no-credential, no-account, three-path, user-named read-only feasibility probes inside a prompt-enforced temp dir; every one of the five build-time needs breaks a written rule. It needs a second mode ("trial") rather than loosened rules: a supervisor-owned boundary, a trial-scoped credential and network manifest, a machine-readable result record, and a pre-authorised path list. Confidence: high on the gaps, since they are read directly from the files.

### Cited findings
- Path count cap — /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:16, read 2026-10-16, Read — Quote: "The skill shall run at most three workers in parallel, each testing exactly one path."
- User must name paths; skill adds none — SKILL.md:14 — Quote: "The skill shall test only paths the user named, and shall not add a path of its own."
- No credentials — SKILL.md:28 — Quote: "The skill shall give a worker no credentials beyond read-only search keys."
- Account needs equal blocked — SKILL.md:28-29 — Quote: "If a path needs an account, a write token or a payment, the worker shall stop and report it as blocked."
- Isolation is a shell recipe, not an enforced boundary — spike-worker.md:26-27 — Quote: "Every install, clone or run of the candidate happens in a fresh temp dir outside the project"
- Recipe passes proxy variables but allows any host — SKILL.md:40-44 — Quote: "passing only the proxy variables (`HTTPS_PROXY`,"
- Install limits — spike-worker.md:52-53 — Quote: "No `sudo`, no global installs (`npm -g`, `pip` without a venv in `$T`), no `curl | sh`"
- Worker has Bash and Write but no sandbox setting, and Read/Write are not bound to `$T` — spike-worker.md:8 — Quote: "tools: Read, Write, Grep, Glob, Bash, ToolSearch, WebFetch"
- Turn and call caps sized for short probes — spike-worker.md:6 and :79 — Quote: "maxTurns: 40" and "Stop at about 15 tool calls."
- Worker may never retry — spike-worker.md:79-80 — Quote: "A path that fails is a result: do not retry with changed flags to make it pass."
- Cleanup is the worker's own last step — spike-worker.md:79 — Quote: "When done, `rm -rf` the literal temp path."
- Step 1 needs the user in the loop — SKILL.md:52 — Quote: "Confirm the question, the named paths (one to three) and the probe with the user in one message."
- Overrides need the user's own message — SKILL.md:34-35 — Quote: "If an isolation rule is to be relaxed, then the lead shall quote the user's own message in the brief."
- Output location and writer — SKILL.md:64 and :68 — Quote: "Spawn one `synthesizer` to read the spike notes and write `research/spikes/<slug>.md`"
- Result format is prose headings — spike-worker.md:87-93 — Quote: "`Verdict: works | fails | blocked` (keep one word)"
- Worker model and omitted context — spike-worker.md:7-9 — Quote: "omitClaudeMd: true"

### Contradictions
- None found.

### Inferences
Concrete gaps and the change each implies (do not edit the files; this is a list for the plan):
1. Path cap and path source: the 3-worker and user-named rules block "more than three paths" and engineer-proposed paths. Add a trial mode with a configurable cap (supervisor reads John's cost/quota, not a fixed 3) and a pre-authorised path list written at intake.
2. Credentials: "no credentials beyond read-only search keys" makes any account-bound trial `blocked`. Add a per-trial credential manifest (names, scope, expiry, test account only) injected by a host proxy or Claude Code's sandbox credential mask, never an env var in the worker.
3. Network: `env -i` only passes proxy variables; it neither limits hosts nor stops a tool ignoring them. Replace the recipe with a boundary (container `--network none` plus allowlisting proxy, or the Claude sandbox allowlist) and a per-trial domain list.
4. Isolation is advisory: Read/Write/Grep are not bound to `$T`, and the clean-env recipe runs on the engineer's own VM as the same user. For the VM, run each trial worker as `claude -p` in a rootless container or dedicated OS user, not as an in-session subagent.
5. Longer probes: `maxTurns: 40` and "about 15 tool calls" cap a 30-minute build/test trial. Add a wall-clock timeout, `--max-budget-usd`, and a rule on what counts as progress; the kill rules themselves belong to the spike-practice facet.
6. Retry rule: "do not retry" is right for feasibility, wrong for a build-time trial where fixing configuration is the work; trial mode needs bounded retries.
7. Install rules: `--ignore-scripts`, no global installs and no `curl | sh` block real build steps. Inside a container these can be relaxed per trial with the boundary as the control, recorded in the result record.
8. Result capture: free-text note plus a synthesizer-written spike file is heavy and not machine-checkable. Add a JSON result record per trial (see schema above) that the supervisor reads; keep the prose note for negative results.
9. Cleanup: one `rm -rf` by the worker is not a guarantee. Move teardown to the supervisor (container `--rm`, `git worktree remove`, sbx rm) with a startup sweep, and record `teardown` in the result.
10. Human gate: step 1 requires confirming with the user; for unattended runs that must become a written authorisation record, or a Channels/Remote Control approval.
11. Registry and outputs: the synthesizer writing `tool-registry.md` rows and `research/spikes/<slug>.md` suits research, not build-time trials living in the engineer's repo; decide where trial records live.
12. `claude -p` auth: if trials are separate `claude -p` processes, `--bare` needs an API key (cost) and non-bare runs execute the trial directory's hooks and `.mcp.json`; use `--bare` with a trial-only key and `--max-budget-usd`, or run non-bare in a directory with a clean settings file (rests on the headless quotes).
13. Parallel resource contention: no port, disk or CPU allocation per trial; add a per-trial CPU/memory/pids limit (container flags) and a concurrency cap tied to quota.

### Gaps
- Whether a plugin subagent can declare `isolation: worktree` together with a sandbox config: not found.
- Whether the spike kill rules interact with these changes: other facet.

## Recommendation, alternatives, rejected, spikes (facet-level)

Recommendation: a layered local design on John's VM. (1) One git worktree per trial, created by the supervisor with `claude --worktree` or `git worktree add`. (2) Each trial runs as its own `claude -p --output-format json --json-schema ... --max-budget-usd N` process as a non-root user inside a hardened rootless container (Anthropic's `docker run` flags, `--network none`, `--rm`, pids/memory limits), with a host-side allowlisting proxy that injects the trial's scoped test credential (Envoy `credential_injector` or mitmproxy). (3) Inside it, keep the built-in Bash sandbox on. (4) The supervisor, not the agent, writes `result.json` and tears down. Hosted is the exception path.
Alternatives: Docker Sandboxes `sbx` (microVM, built-in credential proxy and deny-by-default egress) if `/dev/kvm` exists; sandbox-runtime (no Docker, beta) for low-risk trials; Anthropic's reference devcontainer firewall as the starting file; hosted Vercel Sandbox or E2B for public-code probes.
Rejected: agent teams (no worktree isolation, experimental); agent view as the trial runner (research preview, results only to you); Hobby tiers as a production path (E2B 1 hour, Vercel 45 minutes and creation paused when quota is used); Firecracker self-hosted and gVisor for v1 (cost and no untrusted code in scope, inference); the Bash sandbox alone (Anthropic: not sufficient unattended).
Spike before building: (a) `ls /dev/kvm` and sbx on the VM; (b) a hardened container running `claude -p` with subscription login and with API key, proving `--bare`, exit codes 0/143 and budget-stop exits; (c) the proxy injecting a test token with TLS termination, and a tool that ignores `HTTP_PROXY` failing closed; (d) the AppArmor bwrap profile on Ubuntu 24.04; (e) three trials in parallel with leaked-secret and orphan-worktree checks after a forced kill.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code worktrees (`--worktree`, `isolation: worktree`) | https://code.claude.com/docs/en/worktrees | Isolated checkout and branch per session or subagent; no cleanup under `-p` | Claude Code, local | 2026-10-16 | Use: one per trial; supervisor sweeps leftovers |
| Claude Code agent view / `claude agents` | https://code.claude.com/docs/en/agents | Background session dispatcher, research preview | Claude Code | 2026-10-16 | Skip for trials; results only to the user |
| Claude Code Bash sandbox (bubblewrap) | https://code.claude.com/docs/en/sandboxing | OS sandbox for shell commands, empty domain allowlist, credential mask | Linux/macOS/WSL2 | 2026-10-16 | Use as inner layer; not a boundary alone |
| Hardened Docker/Podman container + proxy | https://code.claude.com/docs/en/agent-sdk/secure-deployment | `--network none` plus host proxy that injects credentials | local Docker or rootless Podman | 2026-10-16 | Use: trial boundary (recommended) |
| Rootless Podman | https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md | Daemonless rootless containers; needs subuid/subgid and pasta | local | 2026-10-16 | Fallback to Docker; limits unverified |
| gVisor (runsc) | https://code.claude.com/docs/en/agent-sdk/secure-deployment | Userspace kernel; slower I/O | local | 2026-10-16 (via Anthropic page) | Skip for v1 |
| Firecracker | https://code.claude.com/docs/en/agent-sdk/secure-deployment | MicroVMs, vsock proxy | local, KVM | 2026-10-16 (via Anthropic page) | Skip for v1 |
| Docker Sandboxes (sbx) | https://docs.docker.com/ai/sandboxes/ | MicroVM per agent, host credential proxy, deny-by-default egress; Ubuntu 24.04+, KVM; Docker login; install via curl script (not run) | local or Docker cloud | 2026-10-16 | Strong alternative if KVM exists; spike |
| E2B | https://e2b.dev/pricing | Hosted sandbox, prebuilt `claude` template, $100 one-time credit, 1 h Hobby session | hosted | 2026-10-16 | Fallback for public-code probes; open egress and key inside box |
| Daytona | https://www.daytona.io/pricing | Hosted sandbox, $200 free compute, sub-90ms create claim | hosted | 2026-10-16 | Fallback; limits not seen |
| Vercel Sandbox | https://vercel.com/docs/vercel-sandbox/pricing | Firecracker microVMs, Hobby 10 concurrent / 45 min, Pro 24 h, $20 monthly Pro credit | hosted | 2026-10-16 | Fallback; cheapest hosted for 30-minute trials |
| Modal Sandboxes | https://modal.com/pricing | Sandbox compute about 3x container price; $30 monthly free credit | hosted | 2026-10-16 | Skip; no advantage seen |
| Cloudflare Sandbox SDK | https://developers.cloudflare.com/sandbox/ | Per-task Linux sandbox on Containers, Workers Paid | hosted | 2026-10-16 | Skip unless already on Cloudflare; price not opened |
| Fly Machines, Northflank, Runloop | (no page opened) | Hosted sandboxes | hosted | not opened | Not researched |
