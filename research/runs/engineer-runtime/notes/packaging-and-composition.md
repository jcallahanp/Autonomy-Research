# Packaging and composition of the engineer

Brief: How should the engineer be packaged so a non-Docker user can set up the same environment every time, and how does it bundle its pieces (research-agent plugin, Superpowers, Beads, Ralph, MCP servers, connectors, browser tooling)?
Run: research/runs/engineer-runtime/PLAN.md

Builds on /home/user/Autonomy-Research/research/findings/packaging.md (plugin anatomy, load matrix, secrets, setup flow); that is not repeated except where cited.

## Q1 Packaging routes compared

### Takeaway
Ranked for a non-Docker user: (1) a natural-language setup skill plus a pinned bootstrap script on a plain VM or his own machine, optionally driven by Remote Control; (2) a devcontainer in a cloud host (Codespaces), where Docker is hidden; (3) a cloud-init file for a VPS. Nix, Ansible and Packer are more reproducible but demand more of John than the gain justifies for one user. Docker-based routes are the only ones Anthropic documents for unattended `--dangerously-skip-permissions`; a VM also qualifies. Confidence: medium (docs read; no route was run).

### Cited findings
- Anthropic's own comparison table lists Docker required: no for sandbox runtime, VM and cloud sessions; yes for dev container and custom container; VM setup effort "High", cloud sessions "None" — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "Virtual machine | Full operating system | No | High"
- Cloud sessions need no setup but need a Claude subscription and GitHub (or `--cloud` upload) — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "None; requires a Claude subscription, and a connected GitHub account unless you launch with `claude --cloud`"
- Unattended runs must sit inside a container, VM or sandbox runtime — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "Always run `--dangerously-skip-permissions` sessions inside a container, a VM, or the sandbox runtime"
- Devcontainer minimum is a 4-line devcontainer.json using the Claude Code Feature; the feature version tag pins the install script, not Claude Code — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "The version tag at the end, such as `:1.0`, pins the feature's install script, not the Claude Code release."
- Exact Claude Code pinning needs a Dockerfile npm install plus autoupdate off — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "To pin a specific Claude Code version for reproducible builds, install it from your Dockerfile with `npm install -g @anthropic-ai/claude-code@X.Y.Z`"
- Devcontainer needs an editor plus Docker (or Codespaces) on the user side — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "A dev container runs as a Docker container, either on your machine or on a cloud host such as GitHub Codespaces."
- Anthropic calls its reference container an example, not a maintained base — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "It is provided as a working example rather than a maintained base image"
- The reference container needs NET_ADMIN for its firewall, and the firewall is optional — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "The firewall script and these capabilities are not required for Claude Code itself"
- The devcontainer is a convention, not enforcement — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "This is a convention rather than an enforcement boundary, because Claude Code does not require a container."
- Remote Control lets an always-on machine be driven from phone or browser with local MCP, tools and files; needs a claude.ai subscription login, API keys unsupported — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch (persisted output, grep) — Quote: "available on Pro, Max, Team, and Enterprise plans. API keys are not supported."
- Self-hosted cloud-session environments exist but are Team/Enterprise public beta and mean you "build and maintain the runner image" — https://code.claude.com/docs/en/self-hosted-environments, opened 2026-10-16, WebFetch — Quote: "Self-hosted environments are in public beta on Team and Enterprise plans and are off by default."
- Ansible is agentless, SSH-based, idempotent — https://docs.ansible.com/ansible/latest/getting_started/introduction.html, opened 2026-10-16, Parallel web_fetch — Quote: "When the system is in the state your playbook describes, Ansible does not change anything, even if the playbook runs multiple times."
- Beads ships a devcontainer and a Nix flake in its own repo, showing both routes are used by agent tooling — https://github.com/steveyegge/beads .devcontainer/README.md:1 and flake.nix (commit d274841), read 2026-10-16, git clone — Quote: "This devcontainer configuration provides a fully-configured development environment for beads with:"

### Contradictions
- None found.

### Inferences
- (mine) For one non-Docker user the lowest-effort reproducible path is not a container: a plain Ubuntu VM or his own machine, a repo-committed `scripts/bootstrap.sh` that pins `@anthropic-ai/claude-code@X.Y.Z`, and the setup skill as verifier. Basis: sandbox-environments table (VM needs no Docker), devcontainer pinning text.
- (mine) Offer the devcontainer as the optional second route for Codespaces; the same `.devcontainer/` file then serves a later team. Basis: devcontainer page, Codespaces secrets text.
- (mine) Remote Control gives a phone-driven always-on engineer with no Docker, but forbids API-key auth and ties availability to a subscription; spike it before depending on it.
- (mine) Nix and Packer are over-spec for one user: Nix needs a new language; Packer images go stale. Reject for v1; revisit if a second person joins.

### Gaps
- I opened no official cloud-init, Packer, Nix or Codespaces pricing pages; Nix and cloud-init claims rest on search excerpts and are uncited here.
- No evidence on how a non-technical user fares with Nix or Ansible; no source found.
- Docker Sandboxes (microVM, free per Anthropic) not evaluated beyond the one sentence in sandbox-environments.

## Q2 Composing plugins and skill sets without conflicts

### Takeaway
Plugin skills are namespaced, so research-agent and Superpowers coexist; hooks are not namespaced, MCP tool names carry a plugin prefix, and cloud sessions install no plugins, so composition needs a bootstrap script in cloud and `claude plugin install` locally. Pin by manifest version (Superpowers is 7.0.0 at commit bb92a77); Beads and Ralph are not plugins to bundle but a CLI and a Stop-hook plugin. Confidence: high on mechanics (packaging.md plus clones), medium on pinning behaviour.

### Cited findings
- Existing local finding: skills namespaced, hooks run twice if in both settings and plugin; cloud never installs plugins — /home/user/Autonomy-Research/research/findings/packaging.md:122-125 — Quote: "hooks have no prefix, so a hook that is in both your settings file and `hooks/hooks.json` runs twice each time its event fires."
- Existing local finding: manifest `version` pins; omitting it tracks commits; auto-update off by default for third-party marketplaces — /home/user/Autonomy-Research/research/findings/packaging.md:71-75 — Quote: "Manifest `version` pins users to the cached copy until the string changes"
- Superpowers install paths are per-harness and it appears in two marketplaces — https://github.com/obra/superpowers README.md:52-81 (commit bb92a77), read 2026-10-16, git clone — Quote: "/plugin install superpowers@superpowers-marketplace"
- Superpowers manifest is a plain plugin with a version — https://github.com/obra/superpowers .claude-plugin/plugin.json (commit bb92a77), read 2026-10-16, git clone — Quote: "\"version\": \"7.0.0\","
- Repo's current cloud bootstrap installs Superpowers only when `CLAUDE_CODE_REMOTE` is true, unpinned — /home/user/Autonomy-Research/scripts/cloud-setup.sh:8-18 — Quote: "claude plugin install superpowers@superpowers-marketplace >/dev/null 2>&1"
- Ralph official plugin is a Stop hook that re-feeds the prompt, with `--max-iterations` and `--completion-promise` — https://github.com/anthropics/claude-code plugins/ralph-wiggum/README.md:13,38 (commit 03b5892), read 2026-10-16, git clone — Quote: "This plugin implements Ralph using a **Stop hook** that intercepts Claude's exit attempts:"
- Beads is a CLI installed once system-wide, not a plugin; `bd setup claude` writes hooks and settings; embedded Dolt by default — https://github.com/steveyegge/beads README.md:30-43,131 (commit d274841), read 2026-10-16, git clone — Quote: "Beads is a CLI tool you install once and use everywhere. You don't need to clone this repository into your project."
- Beads install notes: npm path suits cloud, and install scripts check checksums — https://github.com/steveyegge/beads README.md:99-121 (commit d274841) — Quote: "The install scripts verify release checksums before install."
- Beads README now points its installer at the `gastownhall` org, while the repo URL stays `steveyegge/beads` — https://github.com/steveyegge/beads README.md:31 (commit d274841) — Quote: "curl -fsSL https://raw.githubusercontent.com/gastownhall/beads/main/scripts/install.sh | bash"
- Plugin MCP servers are named with a plugin prefix, which the repo's setup skill already probes for both forms — /home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:13-17 — Quote: "Installed as a plugin, the bundled servers' tools are named `mcp__plugin_research-agent_<server>__<tool>`"

### Contradictions
- None found. (Note: the Ralph write-up by its originator reportedly says the Claude Code plugin "isn't it" (ghuntley.com/ralph excerpt) while Anthropic ships the plugin; both can be true. Not opened in full.)

### Inferences
- (mine) Compose as: one repo = engineer plugin (own skills) + `bootstrap.sh` that installs pinned third-party plugins (Superpowers) and CLIs (bd). Do not vendor Superpowers' files; install by marketplace and record the commit in a lockfile-like `docs/versions.md`.
- (mine) Collision risk is hooks: Superpowers SessionStart, Beads hooks via `bd setup claude`, Ralph Stop hook, plus this repo's SessionStart. Spike: install all four and count hook firings.
- (mine) Ralph/Beads should stay Phase 2 as the registry says; the packaging must leave a slot (`bootstrap.sh --with-beads`), not install by default.
- (mine) Beads' `bd init` edits AGENTS.md and project Claude settings, so it mutates the repo; run it in the engineer's work repos only.

### Gaps
- Marketplace-level version pinning (git ref/SHA in `marketplace add`) not verified in this session; packaging.md says versions come from manifest or SHA, but I did not test pinning a third-party marketplace to a tag.
- How Superpowers updates interact with a pinned manifest: untested.
- ghuntley.com/ralph and how-to-ralph-wiggum were search excerpts only, so the Ralph-origin claims (bash loop, fresh context) are uncited. Nix (devopsboys guide) and cloud-init run-once behaviour likewise only seen in search excerpts.

## Q3 Claude.ai connectors vs repo .mcp.json, cloud vs local/VPS

### Takeaway
Connectors are tied to the claude.ai login, not the repo, so they follow John to cloud sessions and any local install signed in with claude.ai, but not to API-key auth, headless GitHub Actions or a VPS authenticated by API key. A repeatable setup should put every essential server in `.mcp.json` (keyless where possible) and treat connectors as optional enhancements with a probe and a documented fallback, which is what the repo's setup skill already does. Confidence: high (builds on packaging.md Q3; Remote Control page adds the VPS case).

### Cited findings
- Connectors need a claude.ai login; cloud connector traffic goes via Anthropic servers; repo `.mcp.json` servers run in the VM — /home/user/Autonomy-Research/research/findings/packaging.md:169-175 — Quote: "are automatically available in Claude Code\" when \"your active authentication method is a claude.ai subscription login"
- Cloud sessions load `.mcp.json` without a prompt; local asks per-server approval — /home/user/Autonomy-Research/research/findings/packaging.md:151-155 — Quote: "it loads project-scoped servers without asking"
- Remote Control on a machine you control keeps MCP servers and tools available — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "your filesystem, [MCP servers](/docs/en/mcp), tools, and project configuration all stay available"
- Remote Control forbids API-key auth, so a VPS using an API key loses both Remote Control and connectors — https://code.claude.com/docs/en/remote-control, opened 2026-10-16, WebFetch — Quote: "API keys are not supported."
- Devcontainer doc: put MCP servers in project `.mcp.json`, install stdio binaries in the image, allowlist remote domains — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "define them at project scope in a `.mcp.json` file at the repository root so they are checked in alongside your dev container configuration."
- Bash sandbox does not cover MCP servers or hooks; they run on the host — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "MCP servers, command hooks, and plugin monitors are separate processes that run unconstrained on the host."
- Repo CLAUDE.md states the split — /home/user/Autonomy-Research/CLAUDE.md (attached context, tools section), read 2026-10-16 — Quote: "Exa, Context7, Parallel Search and Mermaid Chart come from claude.ai connectors, not this repo."

### Contradictions
- None found.

### Inferences
- (mine) Three install targets, three MCP strategies: cloud = `.mcp.json` plus connectors; local with claude.ai login = both; VPS with API key = `.mcp.json` only. Packaging must therefore make the research path work on keyless `.mcp.json` servers alone (Firecrawl keyless, DeepWiki, Playwright) and treat Exa/Parallel/Context7 as bonus.
- (mine) Browser tooling (Playwright MCP, Stagehand-style) must be in `.mcp.json` and needs Node plus browser binaries in the image; this is where a devcontainer or bootstrap script earns its keep.
- (mine) Spike: does `claude -p` on a VPS signed in via `claude setup-token` see connectors? Not answered by sources read.

### Gaps
- Whether long-lived `CLAUDE_CODE_OAUTH_TOKEN` auth exposes connectors: no source opened that states it.
- Per-conversation connector toggle vs cloud sessions: still open (packaging.md open question 6).

## Q4 Secrets and credentials without committing them

### Takeaway
Every route has a native slot: devcontainer `containerEnv`/`${localEnv:}` and Codespaces secrets; cloud environment network secrets; plugin `userConfig` (sensitive); a root-owned env file or secret manager on a VM. For John, the simplest uniform rule is "the repo holds names only; values live in the host's secret store". Confidence: medium (spec page has no secrets property; patterns assembled).

### Cited findings
- Codespaces secrets arrive as environment variables, and long-lived tokens come from `claude setup-token` — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "Codespaces exposes secrets as environment variables inside the container automatically."
- Do not mount host secrets into the container — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "Avoid mounting host secrets such as `~/.ssh` or cloud credential files into the container; prefer repository-scoped or short-lived tokens."
- Cloud providers: pass credentials as env vars, not mounted files — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "pass credentials into the container as environment variables through `containerEnv`, a Codespaces secret, or your cloud's workload identity"
- Devcontainer spec has `${localEnv:VAR}` and warns unset variables are blank; it has no dedicated secrets property — https://containers.dev/implementors/json_reference/, opened 2026-10-16, WebFetch (summarised by fetch model; not verbatim page) — Quote: "Unset variables are left blank."
- A bypass-permissions session can exfiltrate anything in the container including `~/.claude` credentials — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "dev containers do not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in"
- Persisting login across rebuilds needs a volume at `~/.claude` plus `CLAUDE_CONFIG_DIR` — https://code.claude.com/docs/en/devcontainer, opened 2026-10-16, WebFetch — Quote: "so mounting a volume at `~/.claude` alone doesn't keep you signed in."
- Cloud network secrets, `userConfig` sensitive, GitHub Actions secrets — /home/user/Autonomy-Research/research/findings/packaging.md:164-168,299-303 — Quote: "so \"the key itself stays outside the VM\""
- Self-hosted environments use an environment key shown once — https://code.claude.com/docs/en/self-hosted-environments, opened 2026-10-16, WebFetch — Quote: "Shown once at environment creation, labeled **environment key** in the admin UI."

### Contradictions
- None found.

### Inferences
- (mine) Rule for the repo: commit `.env.example` with names only, gitignore `.env`, and have the setup skill report "set / not set" per name without printing values.
- (mine) Vault CLIs (1Password `op`, Bitwarden) and cloud secret stores (cloud secret manager, systemd credentials) are not cited here; I opened no source on them. For one user, a 0600 env file on a VPS and Codespaces secrets suffice; revisit if a paid API key enters.
- (mine) Since the engineer runs with permissions skipped, any secret in the environment is reachable by prompt injection; prefer cloud network secrets (key never in VM) wherever the route allows.

### Gaps
- No source opened for Ansible Vault, SOPS, 1Password CLI, cloud-init secret handling, or Nix secret tooling (agenix/sops-nix).
- The containers.dev page fetch was summarised by the tool; quote above is the tool's relay of the page, treat as medium reliability.

## Q5 Health checks and probes

### Takeaway
The best pattern found is the repo's own: a setup skill that probes capabilities by tool name via ToolSearch, prints only what is missing with the fallback, and edits nothing; add a deterministic shell `doctor` for non-tool facts (Claude version, bd, node, env var names set) and `claude plugin validate`/`list`. Others use the same shape (ECC `doctor`, research-superpowers session-start notice). Confidence: medium.

### Cited findings
- The repo's setup skill probes seven tools by name, reports missing ones with fallbacks, and installs nothing — /home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:8-9,51-55 — Quote: "Do not edit settings, install anything, or add keys."
- Deferred tools mean absence from a list is not proof; use ToolSearch — /home/user/Autonomy-Research/plugin/skills/setup/SKILL.md:13-15 — Quote: "a tool absent from your list is not yet proof it is missing."
- Other plugins: ECC ships `doctor`/`repair`; research-superpowers uses a session-start notice as the install signal — /home/user/Autonomy-Research/research/findings/packaging.md:243,246 (DeepWiki-derived for ECC, flagged medium there) — Quote: "`node scripts/ecc.js doctor` / `repair`"
- `claude plugin validate --strict` and `claude plugin eval` give CI-time checks — /home/user/Autonomy-Research/research/tool-registry.md:40-41 — Quote: "Checks manifest, frontmatter, `.mcp.json`"
- Self-hosted runner has a CI smoke test and a health endpoint for verifying a runner image — https://code.claude.com/docs/en/self-hosted-environments, opened 2026-10-16, WebFetch — Quote: "a CI smoke test that verifies a runner image before you promote it"
- Beads' installer verifies release checksums and `bd version` / `bd hooks install` are documented upgrade checks — https://github.com/steveyegge/beads README.md:110,121 (commit d274841) — Quote: "The install scripts verify release checksums before install."
- Runtime-sandbox gotcha: a clean start is not proof config loaded — https://code.claude.com/docs/en/sandbox-environments, opened 2026-10-16, WebFetch — Quote: "Don't take a clean start as proof your settings loaded."

### Contradictions
- None found.

### Inferences
- (mine) Two-layer probe: `scripts/doctor.sh` (deterministic: claude version equals pinned, node, bd, git, env var names set, `claude plugin list` contains the plugins, `claude mcp list` status) then `/research-agent:setup` (tool-name probes). Plus a smoke task with a `file_exists` grader via `claude plugin eval` to prove the whole path.
- (mine) Run the probe at SessionStart in unattended mode and write a status file; fail closed (refuse bypass-permissions work) if the sandbox/egress check fails.

### Gaps
- Self-hosted health endpoint specifics not read (only linked from the overview).
- No source found on a standard "setup complete" marker convention beyond plugin-specific ones.

## Recommendation (facet)
One recommendation: ship the engineer as a single GitHub template repo that is also the plugin (as packaging.md lays out), plus a pinned `scripts/bootstrap.sh` (Claude Code version, Superpowers, optional `bd`, Node/Playwright), `.env.example`, a `scripts/doctor.sh`, and the `/setup` skill as the human-readable verifier. Run it on a plain Ubuntu VM or John's machine first; add `.devcontainer/` (Anthropic Feature plus the firewall example) as route two for Codespaces.
Alternatives: Remote Control on an always-on machine (subscription login only); Codespaces devcontainer; cloud-init user-data for a VPS; self-hosted environments (Team/Enterprise only).
Rejected: Nix (new language for one user), Packer images (go stale, extra pipeline), Ansible (agentless and idempotent but is a second tool to learn; fine later), Ralph/Beads as default installs (Phase 2 per registry).
Spike before building: (1) all-four-plugin hook collision count; (2) connector visibility under `setup-token` auth on a VPS; (3) Playwright browser download inside the chosen route; (4) whether Codespaces `~/.claude` persistence works with the `CLAUDE_CONFIG_DIR` mount; (5) pinning a third-party marketplace to a tag.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Dev Container + Claude Code Feature | https://github.com/anthropics/devcontainer-features/tree/main/src/claude-code | 4-line devcontainer.json installs Claude Code; needs Docker or Codespaces | local Docker / Codespaces | 2026-10-16 | Second route; hides Docker only inside Codespaces |
| Anthropic reference devcontainer | https://github.com/anthropics/claude-code/tree/main/.devcontainer | Dockerfile + iptables firewall + volumes, example only | Docker | 2026-10-16 | Copy as a starting point; not a maintained base |
| Remote Control | https://code.claude.com/docs/en/remote-control | Drive a local session from phone/browser; no API keys | own machine/VPS | 2026-10-16 | Spike; subscription login only |
| Self-hosted environments | https://code.claude.com/docs/en/self-hosted-environments | Run cloud sessions on own runners | own infra, Team/Enterprise beta | 2026-10-16 | Skip for one user |
| sandbox-runtime | https://github.com/anthropics/sandbox-runtime | Wraps whole Claude process in bubblewrap/Seatbelt, no Docker | Linux/macOS | 2026-10-16 | Option for isolation without Docker; beta |
| Beads (bd) | https://github.com/steveyegge/beads | CLI + Dolt tracker; `bd setup claude` | CLI install | 2026-10-16 | Phase 2; install by bootstrap flag; org moving to gastownhall |
| Ralph Loop plugin | https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum | Stop-hook loop, max-iterations | plugin | 2026-10-16 | Phase 2 with iteration cap |
| Nix flake / Home Manager | https://devopsboys.com/blog/nix-reproducible-devops-environments-guide-2026 | Declarative env | any | 2026-10-16 (excerpt only) | Reject for v1 |
| Ansible | https://docs.ansible.com/ansible/latest/getting_started/introduction.html | Idempotent agentless playbooks | SSH to VM | 2026-10-16 | Later, if multiple hosts |
| cloud-init | https://docs.cloud-init.io/en/latest | First-boot VPS config | VPS | 2026-10-16 (excerpt only) | Optional wrapper that calls bootstrap.sh |
| Packer | (no page opened) | Machine images | - | 2026-10-16 | Reject; not researched beyond name |
