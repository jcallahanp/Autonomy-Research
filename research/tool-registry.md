# Tool registry

Every tool evaluated for this project. Verdicts as of the verified date; details and the
evidence behind each verdict are in `research/findings/` (tool-routing.md, methodology.md,
packaging.md, architecture.md, engineer-intake.md, engineer-existing-systems.md).

## Research tools in use

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Parallel Search MCP | https://docs.parallel.ai/search/search-mcp | Keyless web search with answer-ready excerpts; fetch up to 20 URLs with objective-focused excerpts | claude.ai connector | 2026-10-16 | **Primary** for discovery and page reading; web_fetch returned "Too Many Requests" repeatedly in the engineer-context run, fall back to Exa (engineer-context.md) |
| Exa MCP (web_search_exa, web_fetch_exa) | https://exa.ai/docs/reference/exa-mcp | Semantic search with highlights; fetch with repo metadata (stars, contributors) | claude.ai connector ($10/month free credit) | 2026-10-16 | Second opinion for discovery; fetch when repo metadata wanted |
| Exa agent_run | https://exa.ai/pricing | Multi-step metered research agent | claude.ai connector | 2026-10-16 | Subagent only, always with `budget.maxCostDollars` |
| WebFetch (built-in) | https://code.claude.com/docs/en/tools-reference | Fetch up to 100k chars and answer a pointed prompt | Claude Code | 2026-10-16 | **Primary** for verify-and-cite |
| WebSearch (built-in) | https://code.claude.com/docs/en/tools-reference | Titles and URLs only, US-only | Claude Code | 2026-10-16 | Fallback only; missed the canonical repo in testing |
| DeepWiki MCP | https://docs.devin.ai/work-with-devin/deepwiki-mcp | Q&A and wiki over public GitHub repos, no auth | `.mcp.json` (http) | 2026-10-16 | **Primary** for understanding repos; `read_wiki_contents` subagent-only (905k chars seen) |
| git clone --depth 1 + grep | (local) | Exact source for verification | Bash | 2026-10-16 | **Primary** verification of DeepWiki claims |
| Context7 MCP | https://context7.com/plans | Versioned library docs snippets; 1,000 calls/month free | claude.ai connector | 2026-10-16 | Keep, for API syntax of a known library only |
| Playwright MCP | https://github.com/microsoft/playwright-mcp | Headless Chromium via accessibility snapshots | `.mcp.json` (stdio, `plugin/scripts/playwright-mcp.sh`) | 2026-10-16 | Last resort, subagent only; blocked by Cloudflare/Vercel bot checks; 45-95 KB snapshots |
| Mermaid Chart MCP | https://mermaid.ai/docs/ai/mcp-server | Validate and render Mermaid (free account) | claude.ai connector | 2026-10-16 | Keep for validation via subagent; 60k-char output per render |
| GitHub MCP | https://github.com/github/github-mcp-server | Repo/file/PR tools | claude.ai connector | 2026-10-16 | Own-repo reads only; search returns 403 in cloud sessions |
| Superpowers | https://github.com/obra/superpowers | Engineering methodology skills; manifest version 7.0.0 at commit bb92a77; spec/plan/ledger files, fresh-subagent execution, SessionStart bootstrap on `startup|clear|compact` | plugin, via `scripts/cloud-setup.sh` | 2026-10-16 | In use; brainstorming flow reused for the interview skill; pin the version in the bootstrap (engineer-runtime.md); process layer for the engineer, watch issues #2481, #2493, #2510 (engineer-context.md) |

## Free additions recommended

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Official MCP registry API | https://github.com/modelcontextprotocol/registry | Keyless `/v0.1/servers?search=` listing of MCP servers; name-substring search only; unvetted listings (pay-per-call and token-gated servers returned) | curl | 2026-10-16 | **Add** for MCP-server discovery, always followed by a URL/repo verification step (engineer-intake.md) |
| Sourcegraph stream API | https://sourcegraph.com/docs/api/stream_api | Keyless cross-repo code search on sourcegraph.com | curl | 2026-10-16 | **Add** for "where does code do X" |
| Firecrawl keyless MCP | https://docs.firecrawl.dev/mcp-server/keyless | Search/scrape/parse with no key, rate limited; live `tools/list` shows `firecrawl_scrape`, `firecrawl_search`, `firecrawl_parse` | Bundled keyless MCP in `plugin/.mcp.json` (`https://mcp.firecrawl.dev/v2/mcp`) | 2026-10-16 | **Installed**: fallback fetcher before Playwright |
| OpenSSF Scorecard | https://github.com/ossf/scorecard | Per-repo security heuristics 0-10, viewer + REST API | hosted, read-only | 2026-10-16 | **Add** as lookup in repo triage |

## Plugin build and test tooling

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code subagents | https://code.claude.com/docs/en/sub-agents | Isolated-context workers with per-agent model/tools/memory | plugin `agents/` | 2026-10-16 | Core primitive for workers |
| Claude Code dynamic workflows (`/deep-research`) | https://code.claude.com/docs/en/workflows | Scripted fan-out with schema returns, cross-check and vote | plugin `workflows/` | 2026-10-16 | Phase 2 target for the verifier pipeline |
| Claude Code agent teams | https://code.claude.com/docs/en/agent-teams | Peer sessions with shared task list and messaging | experimental | 2026-10-16 | Rejected for v1; roughly 7x tokens |
| `claude plugin validate --strict` | https://code.claude.com/docs/en/plugins-reference | Checks manifest, frontmatter, `.mcp.json` | shell, CI | 2026-10-16 | Use in CI |
| `claude plugin eval` | https://code.claude.com/docs/en/plugin-evals | Runs cases with/without plugin; free regex/tool_used/tool_order/file_exists graders, paid llm/baseline; `--runs` (default 3), `--threshold`, `--judge-model`, `--ablation none`, `--max-cost-usd` | CLI v2.1.269+, session auth | 2026-10-16 | Adopt for `/self-test`; for improvement rounds add dev/holdout/regression tags, a pinned `--judge-model`, 5 runs for accept decisions, `--ablation none` for version-vs-version |
| `/skill-doctor`, `/doctor prompt-audit` | https://code.claude.com/docs/en/skills | Per-skill context cost; CLAUDE.md conflict audit | interactive terminal | 2026-10-16 | Use to prune skills and CLAUDE.md |
| GitHub template repository | https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository | "Use this template" copies the repo | GitHub web | 2026-10-16 | Use for clone-and-go |
| Cloud network secrets | https://code.claude.com/docs/en/cloud-environments | Proxy attaches API key; key never enters the VM | cloud only | 2026-10-16 | Use for any paid API in cloud |
| Claude Code plan mode + AskUserQuestion | https://code.claude.com/docs/en/best-practices | Read-only plan, 1-4 questions with 2-4 options, plan file, ExitPlanMode gate; AskUserQuestion not available in subagents | local CLI / SDK | 2026-10-16 | Use as intake engine in the main session; do not rely on ExitPlanMode as sole approval record (issues #50176, #30090) |

## Engineer runtime and packaging (engineer-runtime.md)

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code cloud sessions | https://code.claude.com/docs/en/claude-code-on-the-web | Anthropic-hosted VM sessions, no VM charge, plan usage | cloud | 2026-10-16 | Use as the unattended repo worker; no browser logins |
| Routines | https://code.claude.com/docs/en/routines | Schedule (>=1 h), API `/fire`, GitHub triggers; no approval prompts; research preview | cloud | 2026-10-16 | Use for overnight GitHub-only runs; spike duration |
| Cloud environments (setup script, network levels) | https://code.claude.com/docs/en/cloud-environments | Network levels, env vars, cached setup script | cloud | 2026-10-16 | Use; Full network for installs, network secrets for keys |
| Remote Control | https://code.claude.com/docs/en/remote-control | Drive local sessions from phone/web; push notifications; server mode; outbound-only; subscription login only | John's machine/VM | 2026-10-16 | Use for browser logins, monitoring and live approvals; gives up after about 10 min offline; API keys and setup-token unsupported |
| Claude in Chrome | https://code.claude.com/docs/en/chrome | Uses logged-in Chrome; visible window; local only; off under API-key/setup-token auth | John's machine | 2026-10-16 | Fallback; not unattended-safe per docs |
| Channels (Telegram/Discord/iMessage) | https://code.claude.com/docs/en/channels | Push events and permission relay into a running local session; sender allowlist; research preview | John's machine/VM | 2026-10-16 | Use for live approvals; needs always-on local process |
| /loop and scheduled tasks | https://code.claude.com/docs/en/scheduled-tasks | In-session cron, 7-day expiry; Desktop tasks run on your machine | local session | 2026-10-16 | Skip /loop for overnight; Desktop tasks are an alternative on a spare machine |
| Claude Code GitHub Actions | https://code.claude.com/docs/en/github-actions | Action with cron, uses subscription via OAuth token | GitHub runners | 2026-10-16 | Alternative to routines for CI-bound jobs |
| claude -p / Agent SDK CLI | https://code.claude.com/docs/en/headless | Official non-interactive Claude Code | VPS/VM/own machine | 2026-10-16 | Use: core of unattended runs; add `--bare` only with API key |
| claude setup-token | https://code.claude.com/docs/en/authentication | One-year OAuth token from a Max plan for headless auth | any server | 2026-10-16 | Avoid as the VM's primary auth (breaks Remote Control, connectors, Chrome); fine for CI |
| Claude Agent SDK | https://code.claude.com/docs/en/agent-sdk/overview | Embed Claude Code loop, hooks, MCP in own daemon | local/VM | 2026-10-16 | Use for a custom always-on service if needed; third-party login rules apply |
| browser-use/bux | https://github.com/browser-use/bux | Claude Code on a $5 Ubuntu VPS with persistent real Chromium, Telegram, hand-off on login walls | VPS | 2026-10-16 | Reference pattern only; not installed; page contains instructions addressed to agents, not followed. Spike before trust |
| thereisno-tomorrow/claude-vps | https://github.com/thereisno-tomorrow/claude-vps | Hetzner + Tailscale + tmux bootstrap scripts | Hetzner VPS | not opened (search excerpt only) | Reference only; not verified |
| amineorion/claude-mini-setup | https://github.com/amineorion/claude-mini-setup | Spare Mac, tmux, Tailscale, ntfy hooks | Mac mini | not opened (search excerpt only) | Reference only; not verified |
| nurkert/claude-systemd | https://github.com/nurkert/claude-systemd | systemd service for Claude Code with Remote Control | Linux | not opened (search excerpt only) | Reference only; not verified |
| 1Password for Claude | https://1password.com/blog/1password-for-claude | Vault fill without exposing secrets to the model | Mac desktop | 2026-10-16 | Paid; Mac-only; defer; favours a spare Mac if wanted |
| Dev Container + Claude Code Feature | https://github.com/anthropics/devcontainer-features/tree/main/src/claude-code | 4-line devcontainer.json installs Claude Code; needs Docker or Codespaces (facts from https://code.claude.com/docs/en/devcontainer) | local Docker / Codespaces | 2026-10-16 | Second route; hides Docker only inside Codespaces |
| Anthropic reference devcontainer | https://github.com/anthropics/claude-code/tree/main/.devcontainer | Dockerfile + iptables firewall + volumes, example only (facts from https://code.claude.com/docs/en/devcontainer) | Docker | 2026-10-16 | Copy as a starting point; not a maintained base |
| Self-hosted environments | https://code.claude.com/docs/en/self-hosted-environments | Run cloud sessions on own runners | own infra, Team/Enterprise beta | 2026-10-16 | Skip for one Max user |
| sandbox-runtime | https://github.com/anthropics/sandbox-runtime | Wraps whole Claude process in bubblewrap/Seatbelt, no Docker (facts from https://code.claude.com/docs/en/sandbox-environments) | Linux/macOS | 2026-10-16 | Option for isolation without Docker; beta |
| Nix flake / Home Manager | https://devopsboys.com/blog/nix-reproducible-devops-environments-guide-2026 | Declarative env | any | not opened (search excerpt only) | Reject for v1 (worker inference; not researched from an opened page) |
| Ansible | https://docs.ansible.com/ansible/latest/getting_started/introduction.html | Idempotent agentless playbooks | SSH to VM | 2026-10-16 | Later, if multiple hosts |
| cloud-init | https://docs.cloud-init.io/en/latest | First-boot VPS config | VPS | not opened (search excerpt only) | Optional wrapper that calls bootstrap.sh; unverified |
| Packer | (no page opened) | Machine images | - | not opened | Reject; not researched beyond name |
| NanoClaw | https://github.com/nanocoai/nanoclaw | Small TS assistant, Docker container per agent, credential gateway; install via nanoclaw.sh | local/VM, Docker | 2026-10-16 (clone of qwibitai/nanoclaw) | Spike first if a Slack/WhatsApp daemon is needed; Agent SDK claim unverified |
| Hermes Agent | https://github.com/NousResearch/hermes-agent | MIT Python agent with memory, cron, gateway, 7 execution backends; model-agnostic | local/VPS/serverless | 2026-10-16 | Skip as Claude Code host; not Claude-centric |

## Reference designs (not installed)

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Anthropic deep-research skill | local synced skill | Coordinator + file-note researchers + single writer | claude.ai synced skill | 2026-10-16 | Template for our research skill and note schema |
| langchain-ai/open_deep_research | https://github.com/langchain-ai/open_deep_research | Supervisor/researcher with compression node, 5 concurrent | Python | 2026-10-16 | Reference design |
| assafelovic/gpt-researcher | https://github.com/assafelovic/gpt-researcher | Recursive breadth/depth research with citations | Python | 2026-10-16 | Reference design |
| stanford-oval/storm | https://github.com/stanford-oval/storm | Perspective-driven conversations to cited article | Python | 2026-10-16 | Reference for perspective decomposition |
| bytedance/deer-flow | https://github.com/bytedance/deer-flow | Lead with `task()` subagents and citation rules | Python | 2026-10-16 | Reference design |
| Anthropic skill-creator | https://github.com/anthropics/skills/tree/main/skills/skill-creator | Content loop, grader/comparator/analyzer agents, description optimiser with 60/40 split and 5-iteration cap via `claude -p` | local, session auth, no extra key | 2026-10-16 | Use as template for the self-improvement loop; copy patterns into plugin agents |
| agentskills.io skill-eval guide | https://agentskills.io/skill-creation/evaluating-skills | Eval-driven iteration loop; previous-version baseline; assertion pruning; stop rule | docs | 2026-10-16 | Use as the loop template; it has no holdout rule |
| GEPA (DSPy optimizer, optimize_anything) | https://dspy.ai/api/optimizers/GEPA/overview/index.md | Reflective, Pareto-based prompt and text evolution with minibatch-then-validation gating; learned coding-agent skills in a Feb 2026 post | Python; needs a reflection LM | 2026-10-16 | Reference design only; copy the loop, do not install |
| DeepResearch Bench (RACE/FACT) | https://github.com/Ayanami0730/deep_research_bench | 100-task report-quality (RACE) and citation (FACT) benchmark; judge GPT-5.5 / GPT-5.4-mini since 11 May 2026 | local Python; OpenRouter/OpenAI key plus Jina key | 2026-10-16 | Skip as a per-round gate; reuse the FACT claim-to-URL design as a deterministic grader |
| DeepResearch Bench II | https://github.com/imlrz/DeepResearch-Bench-II | 132 tasks, about 9,430 binary expert rubrics, public `tasks_and_rubrics.jsonl`; judge GPT-5.5 | local Python (uv); paid judge key | 2026-10-16 | Fallback: borrow a few rubrics as grader text; skip the full run |
| GitHub spec-kit (/specify, /clarify templates) | https://github.com/github/spec-kit | /specify (max 3 clarification markers, informed defaults), /clarify (one question at a time, max 5, recommended option, coverage scan, writes answers into spec), /plan, /tasks | agent slash commands, Python CLI install; template read only | 2026-10-16 | Copy the clarify/specify prompt patterns as the intake gap-closing phase; do not adopt wholesale (verbosity per Fowler) |
| AWS Kiro specs (requirements-first, Quick Spec) | https://kiro.dev/docs/specs/feature-specs/requirements-first/ | requirements.md (user stories + EARS), design.md, tasks.md; Quick Spec asks questions up front | proprietary IDE/CLI (separate product) | 2026-10-16 | Borrow the EARS output format and size-gating; do not adopt the IDE (Claude Code is the engine) |
| EARS | https://alistairmavin.com/EARS | Five-pattern requirement syntax | notation, no install | 2026-10-16 | Use as intake output layer; model drafts, John confirms |
| Volere fit criterion / snow card | https://www.reqview.com/blog/2019-02-27-news-volere-requirements-specification-template | Per-requirement shell with fit criterion; SCOPE/REQS/ISSUES/DEFS split | template | 2026-10-16 | Use fit criterion and glossary ideas only |
| OntoAgent | https://arxiv.org/html/2605.05828 | Ontology-guided interview agent, IRE 0.69 | research prototype (not run) | 2026-10-16 | Reference design; slot pruning and coverage-plus-cap stop worth copying |
| LLMREI | https://arxiv.org/html/2507.02564v1 | GPT-4o interviewer chatbot prompts | research prototype (not run) | 2026-10-16 | Reference for prompt rules (one question at a time, final summary); fine-tuning rejected |
| OpenSpec | https://github.com/Fission-AI/OpenSpec | proposal/specs/design/tasks per change, delta specs, archive | npm CLI + slash commands; licence not checked | 2026-10-16 | Fallback if a ready-made spec framework is wanted; lighter than spec-kit |
| Gemini Deep Research (Interactions API) | https://ai.google.dev/gemini-api/docs/deep-research | Research agent with optional collaborative plan review, MCP tool support; preview | Google API, paid | 2026-10-16 | Reference design for plan-approval loop only; skip as engine |
| urlhealth | https://arxiv.org/abs/2604.03173v1 | Open-source URL liveness and stale-vs-hallucinated checker | pip / agent skill (not installed) | 2026-10-16 | Reference: copy the idea as the candidate verify step in intake |

## Brownfield mapping and SaaS configuration reads (engineer-existing-systems.md)

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code Explore/Plan subagents | https://code.claude.com/docs/en/sub-agents | Read-only exploration in separate context; model overridable to Haiku | Claude Code | 2026-10-16 | Use: the mapping workers |
| Aider repo map | https://aider.chat/docs/repomap.html | Tree-sitter definitions ranked by file-dependency graph, 1k-token default budget | Aider CLI (not installed) | 2026-10-16 | Reference design; do not adopt Aider as engine |
| SCIP / scip-python / scip-typescript | https://docs.sourcegraph.com/code_intelligence/explanations/precise_code_intelligence | Exact symbol index per language | CLI, CI | 2026-10-16 | Fallback: add if reference lookups prove unreliable |
| Sourcegraph (hosted) | https://sourcegraph.com/docs/code-navigation | Search-based and precise navigation | hosted / self-hosted | 2026-10-16 | Skip for private repos; the stream API row above covers public search |
| CodeQL | https://codeql.github.com/docs/codeql-overview/about-codeql/ | AST, data-flow and control-flow database; build-free for Python and JS/TS | CLI, local | 2026-10-16 | Fallback for targeted queries; licence unchecked |
| Semgrep (pattern syntax) | https://semgrep.dev/docs/writing-rules/pattern-syntax | Structural pattern matching with ellipsis and metavariables | CLI, local | 2026-10-16 | Use for credential and external-call inventory; spike |
| pydeps | https://pythonhosted.org/pydeps/index.html | Python import graph, external dependency JSON | pip, local | 2026-10-16 | Use for Python module graph (spike on dynamic imports) |
| dependency-cruiser | https://github.com/sverweij/dependency-cruiser | JS/TS dependency graph and rule checks, MIT | npx, local | 2026-10-16 | Use for TS module graph |
| madge | https://github.com/pahen/madge | JS/TS module graph, circular dependency finder | npm, local | 2026-10-16 | Alternative to dependency-cruiser |
| DeepWiki (docs) / CodeWiki benchmark | https://docs.devin.ai/work-with-devin/deepwiki ; https://arxiv.org/abs/2510.24428 | Generated wiki, 30-page cap, public basic tier; benchmarked 64% / 69% | hosted / local | 2026-10-16 | Skip for private code; navigation aid only, not source of truth |
| universal-ctags | https://docs.ctags.io/en/latest/man/ctags.1.html | Symbol tag index | local | 2026-10-16 (one man-page excerpt only) | Skip; Aider dropped it for tree-sitter |
| FastContext | https://arxiv.org/html/2606.14066v1 | Trained small explorer subagent (research) | research, not run | 2026-10-16 | Reference only: design of read/glob/grep explorer returning file:line |
| DocAgent | https://aclanthology.org/2025.acl-demo.44.pdf | Dependency-ordered multi-agent docstring generation | research code (not run) | 2026-10-16 | Reference: topological order, verifier role |
| SWE-Explore | https://arxiv.org/pdf/2606.07297 | Benchmark of repo exploration | dataset, not run | 2026-10-16 | Evidence source; possible test harness |
| ArchAgent | https://arxiv.org/html/2601.13007v1 | Static analysis + LLM architecture recovery (paper) | research, not run | 2026-10-16 | Reference design: add dependency graph before LLM |
| Claude Code OpenTelemetry | https://code.claude.com/docs/en/monitoring-usage | Export traces/metrics of agent runs | Claude Code | 2026-10-16 | Use to measure mapping token cost |
| Attio REST API + OpenAPI | https://docs.attio.com/rest-api/overview | Reads objects, attributes, lists, entries, view titles, webhooks, read-only SQL | hosted, API key or OAuth | 2026-10-16 | Use for Attio inventory; views and workflows incomplete |
| Attio MCP (official) | https://docs.attio.com/mcp/overview | OAuth-hosted MCP, 40+ tools, reads auto-approved | hosted remote MCP | 2026-10-16 | Use for interactive reads; no view or workflow tool |
| Clay developer platform + CLI | https://developers.clay.com/ | Searches, Routines, Workflows (Alpha), Enterprise table query | hosted API, CLI/plugin | 2026-10-16 | Use for Workflows reads; tables Enterprise only |
| claycast internal Clay API reference | https://github.com/TenSpy-ai/claycast | Reverse-engineered session-cookie API, table get/export | local Python (not run) | 2026-10-16 | Skip except as a spike; unofficial |
| n8n public API (incl. credentials/audit scopes) | https://docs.n8n.io/connect/n8n-api | Workflows, executions, credential metadata (secrets write-only), security audit | self-hosted or cloud | 2026-10-16 | Use for workflow and credential inventory; availability on free trial unverified (snippet only) |
| n8n CLI export | https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line | Workflow/credential export to JSON | self-hosted server | 2026-10-16 | Use workflow export; never `--decrypted` by default |
| Outreach REST API | https://developers.outreach.io/api/reference | Sequences, steps, templates, mailboxes via OAuth or S2S | hosted | 2026-10-16 | Use if app creation is permitted; needs company approval |
| Slack app manifest API | https://docs.slack.dev/reference/methods/apps.manifest.export | Exports scopes, events, features per app | hosted, config token | 2026-10-16 | Use |
| Claude Code CLI inspectors | https://code.claude.com/docs/en/debug-your-config | `claude mcp list/get`, `claude doctor`, /context, /mcp | local | 2026-10-16 | Use |
| Claude Compliance API artifacts | https://platform.claude.com/docs/en/api/compliance/code/artifacts | List and download artifact versions org-wide | hosted, compliance key | 2026-10-16 | Fallback; likely org-admin only |
| C4 model | https://c4model.com/diagrams | Context/container/component/code diagram notation | notation, no install | 2026-10-16 | Use context + container levels for the as-is map |
| gitleaks | https://github.com/gitleaks/gitleaks | Secret scanner for git/dir/stdin; `--redact`, json/csv/sarif reports | local binary (not installed) | 2026-10-16 | Use, free; spike that report files are redacted |
| TruffleHog | https://github.com/trufflesecurity/trufflehog | Secret scanner, filesystem mode, live-verification of finds | local binary (not installed) | 2026-10-16 | Fallback; only with `--no-verification` |
| Claude Code permissions.deny + sandbox | https://code.claude.com/docs/en/settings-example | Blocks reads of secret files; sandbox covers grep -r | Claude Code | 2026-10-16 | Use as hard gate; spike enforcement (issue #24846) |
| Attio Dedupe app | https://attio.com/apps/dedupe | Weighted match rules, gated merge, audit log, 30-day undo | Attio app, pricing not checked | 2026-10-16 | Fallback; check price first |
| attio-dedup-audit-skill | https://github.com/gmaramigin/attio-dedup-audit-skill | Claude skill: detect, report, approve, merge | Claude / Attio MCP; not run | 2026-10-16 | Reference for approval-gated flow; unvetted, do not install |
| Clay Attio integration | https://university.clay.com/docs/attio-integration | Lookup/upsert/update into Attio | Clay (paid plan) | 2026-10-16 | Existing system; follow lookup-first rule |

## Evaluated and deferred or skipped

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Beads | https://github.com/steveyegge/beads | Dolt-backed dependency-graph issue tracker for agents; CLI installed once (`bd setup claude`); checksum-verified installer now under gastownhall org; `bd prime`/`bd remember`, ready/claim, SessionStart hook; 446 open issues, 2026-08-11 data-loss incident documented (commit d274841) | not installed (clone read only) | 2026-10-16 | Phase 2; git files suffice for one researcher; install by bootstrap flag only (engineer-runtime.md); for the engineer, alternative to `tasks.json` only when dependency ordering or multi-agent claims bite (engineer-context.md) |
| Ralph Loop (official plugin, anthropics/claude-code plugins/ralph-wiggum) | https://claude.com/plugins/ralph-loop ; https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum | Stop hook re-feeds the same prompt in the current session until `<promise>` text or `--max-iterations`; default unlimited; no no-op detection (claude-plugins-official issue #1699, 6,239 iterations) | not installed (clone read only, commit 03b5892) | 2026-10-16 | Skip as shipped; fallback only with both `--max-iterations` and `--completion-promise` set and an outer supervisor owning the real bounds (engineer-context.md) |
| Trail of Bits skills | https://github.com/trailofbits/skills | ~40 security plugins | not installed | 2026-10-16 | Only two relevant (below) |
| supply-chain-risk-auditor (Trail of Bits) | https://github.com/trailofbits/skills/blob/main/plugins/supply-chain-risk-auditor/README.md | OSV advisories, archived upstreams, install scripts, Scorecard for deps | plugin + `uv run` | 2026-10-16 | Later; adopt when a lockfile needs checking |
| gh-cli (Trail of Bits) | https://github.com/trailofbits/skills/blob/main/plugins/gh-cli/README.md | PreToolUse hooks redirect GitHub fetches to `gh` | plugin hooks | 2026-10-16 | Skip; would deny Exa fetch on github.com, and `gh` is unauthenticated in cloud |
| Semgrep plugin | https://claude.com/plugins/semgrep | Post-edit SAST scan | not installed | 2026-10-16 | Not useful for a researcher |
| Tavily MCP | https://docs.tavily.com/documentation/mcp | Search + extract, 1,000 free credits/month with key | not installed | 2026-10-16 | Later |
| Octocode MCP | https://github.com/bgauryy/octocode-mcp | GitHub code research tools, needs token | not installed | 2026-10-16 | Later (cloud token blocked) |
| Jina Reader | https://jina.ai/reader/ | URL to markdown; 20 RPM keyless | curl (401 from cloud IP) | 2026-10-16 | Later, needs free key |
| arXiv MCP server | https://github.com/blazickjp/arxiv-mcp-server | Paper tools via uvx | not installed | 2026-10-16 | Later; academic focus |
| Semantic Scholar API | https://www.semanticscholar.org/product/api | Scholarly graph | curl | 2026-10-16 | Later |
| gh CLI | https://cli.github.com/manual/gh_search_repos | GitHub search from shell | preinstalled; token invalid in cloud | 2026-10-16 | Skip in cloud; fine locally |
| Sequential Thinking MCP | https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking | Numbered thought log | not installed | 2026-10-16 | Skip |
| grep.app | https://grep.app/ | Code search; 429 to all fetchers | - | 2026-10-16 | Skip |
| Perplexity Sonar | https://docs.perplexity.ai/getting-started/pricing | Paid search-grounded LLM | not installed | 2026-10-16 | Skip, no free tier |
| Brave Search MCP | https://brave.com/search/api/ | Search API, card required | not installed | 2026-10-16 | Skip |
| Glama / Smithery / mcpservers.org | https://glama.ai/mcp/servers | MCP directories; key or bot-blocked | - | 2026-10-16 | Skip as tools; the official registry API covers discovery |
| OpenClaw | https://github.com/openclaw/openclaw | MIT Node gateway daemon, 20+ chat channels, drives Claude Code via claude-cli backend or ACP; install via curl script/npm/Docker; sandbox off by default; 255+ advisories | not installed (clone read only) | 2026-10-16 | Reject as host; fallback only if channel breadth is needed, in a dedicated VM, sandbox `all`, no ClawHub skills (engineer-runtime.md) |
| BrowseComp | https://arxiv.org/abs/2504.12516 | 1,266 short-answer questions testing persistent browsing | dataset | 2026-10-16 | Skip; measures answers, not reports or citations |
| DSPy MIPROv2 | https://dspy.ai/api/optimizers/MIPROv2/ | Bootstrapped demos, proposed instructions, Bayesian search | Python; needs LM key | 2026-10-16 | Skip; many calls, little value for markdown skills |
| TextGrad | https://github.com/zou-group/textgrad | Textual-gradient critique and rewrite, PyTorch-style API | Python; needs OpenAI/Anthropic key | 2026-10-16 | Skip |
| promptfoo optimize | https://www.promptfoo.dev/docs/usage/prompt-optimization/ | Baseline eval, LLM-proposed rewrites from failures, optional `--validation-split` | Node CLI; needs provider credential | 2026-10-16 | Fallback; built for prompt/provider pairs, not markdown skills |
| ReqElicitGym | https://arxiv.org/abs/2602.18306v1 | Benchmark with oracle user for LLM interviewers | local Python (not run) | 2026-10-16 | Possible later test harness for the intake skill; website domain only |
| tau-Elicitation | https://arxiv.org/html/2609.13602v1 | Voice entity capture benchmark | research (not run) | 2026-10-16 | Evidence only, for the dictated-name glossary playback |
| BMAD Method | https://github.com/bmad-code-org/BMAD-METHOD | Skill pipeline brief, PRD, spec, architecture, tickets, build, build-auto | skills in coding tool; needs uv; v7 alpha | 2026-10-16 | Skip for one user; heavy; reference for right-sizing |
| Aider modes | https://aider.chat/docs/usage/modes.html | ask / architect / code modes, no plan file (page seen in search excerpt only, not opened) | local CLI | 2026-10-16 (search excerpt only) | Skip; different engine, no artifact; description unverified |
| Devin interactive planning | https://docs.devin.ai/work-with-devin/interactive-planning | Initial assessment, cited plan, 30 s auto-proceed | hosted, paid | 2026-10-16 | Skip; paid, hosted; borrow code-cited plan idea |
| Cursor plan mode | https://cursor.com/blog/plan-mode | Clarifying questions then editable Markdown plan with to-dos | proprietary IDE | 2026-10-16 | Skip; different engine |
| Claude research feature | https://support.claude.com/en/articles/11088861-use-research-on-claude | Multi-search research in claude.ai, paid plans (page seen in search excerpt only, not opened) | claude.ai web/desktop | 2026-10-16 (search excerpt only) | Skip for the engineer; cannot be driven from Claude Code; description unverified |
| TrailLM / Sensecape | https://arxiv.org/html/2607.11810v1 | Research prototypes for exploratory search with LLMs | academic | 2026-10-16 | Skip; design ideas only (visible goal trail, option map) |

## Engineer context, memory, loops and model tiers (engineer-context.md)

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| frankbria/ralph-claude-code | https://github.com/frankbria/ralph-claude-code | Bash Ralph with circuit breaker (3 no-file-change loops, 5 error loops, 30 min cooldown), dual-condition exit gate | local shell | 2026-10-16 (`lib/circuit_breaker.sh` opened; not cloned, not run) | Reference design for the breaker; copy thresholds, do not adopt wholesale |
| /goal | https://code.claude.com/docs/en/goal | Session-scoped Stop hook with an evaluator that cannot run tools; clears on met, impossible or unrecoverable error; stalls stop the loop | Claude Code, interactive or `-p` | 2026-10-16 | Use inside one task when the end state is demonstrable in output, with a turn clause in the condition; not a bound on its own |
| claude -p --max-turns / --max-budget-usd (Agent SDK maxTurns / maxBudgetUsd) | https://code.claude.com/docs/en/cli-reference ; https://code.claude.com/docs/en/agent-sdk/agent-loop | Per-run turn and estimated-spend caps; `error_max_turns` / `error_max_budget_usd` result subtypes; default none | Claude Code CLI / SDK | 2026-10-16 | Use on every unattended call; caps are per run, so the supervisor owns per-task and per-night bounds; exit-code values are a spike |
| PreToolUse output-filter hook | https://code.claude.com/docs/en/costs | Rewrites test/log commands to show failures only | Claude Code hooks | 2026-10-16 | Use; A/B test for quality before making default |
| Prompt cache TTL controls (`promptCacheTtl`) | https://code.claude.com/docs/en/prompt-caching | 5 m or 1 h cache for the main conversation; 1 h only on subscription within plan usage unless set | Claude Code | 2026-10-16 | Set `1h` when API-key runs have gaps over 5 min |
| TaskCompleted / Stop command hooks | https://code.claude.com/docs/en/hooks | Block completion or the turn on exit 2; eight-block override; `stop_hook_active` guard | Claude Code | 2026-10-16 | Use: core done-gate and doc-manifest gate; spike exit 2 vs JSON block |
| SessionStart hook (startup/resume/compact) | https://code.claude.com/docs/en/hooks-guide | Re-inject state from files after startup, resume and compaction | Claude Code | 2026-10-16 | Use |
| Claude Code task list (TaskCreate/TaskUpdate, `CLAUDE_CODE_TASK_LIST_ID`) | https://code.claude.com/docs/en/tools-reference | In-session checklist with dependencies; named-dir sharing; default only on Opus 4.7 / Sonnet 4.6 / Haiku 4.5 and earlier | Claude Code | 2026-10-16 | In-session view only; never the plan |
| Claude Haiku 5.5 | https://www.anthropic.com/claude-haiku-5-5 | Cheap subagent model; vendor says pairs with Opus 5.5 / Sonnet 5.5 as a coding subagent, not for complex agentic coding | Claude API / Claude Code alias `haiku` | 2026-10-16 | Narrow checkable roles only (fixed-command test run, search, log summary, citation check); not implementer; paired test first |
| anthropics/cwc-long-running-agents | https://github.com/anthropics/cwc-long-running-agents | Hooks plus fresh-context evaluator subagent, default-FAIL contract, progress hand-off | Claude Code / Agent SDK | not opened (Exa search excerpt only) | Template candidate; open README and spike before copying |
| Scrouting / SuperScout | https://arxiv.org/html/2608.04804v1 | Small scout hands off to a frontier fixer; research prototype | research (not run) | 2026-10-16 | Reference; cheap-scout, strong-fixer idea |
| Agent-as-a-Router / CodeRouterBench | https://www.alphaxiv.org/abs/2606.22902 | Routing benchmark for coding tasks | research | not opened (search excerpt only) | Reference only; unverified |
| eng-skills (viditparashar96) | https://github.com/viditparashar96/eng-skills | Stop gate blocking a turn that changed code without docs; ADR commands; 0 stars | Claude Code hooks (npm) | 2026-10-16 (page only, not installed) | Reference only; copy the idea, do not install |
| doc-sentinel (dgalarza/claude-code-workflows PR #36) | https://github.com/dgalarza/claude-code-workflows/pull/36 | Stop hook auto-dispatching a drift resolver; found JSON block ineffective, exit 2 worked | Claude Code plugin | 2026-10-16 (PR page only) | Reference only; useful pitfalls |
| DevSquad spec amendment | https://microsoft.github.io/devsquad-copilot/concepts/spec-amendment/ | Drift flag, propagation checklist, blocks resume until artifacts updated or waived | Copilot framework | 2026-10-16 | Borrow the checklist idea; skip the tool |
| Cline Memory Bank | https://docs.cline.bot/features/memory-bank | Markdown memory files re-read each session, split by role | Cline | 2026-10-16 | Idea only (activeContext/progress split) |
| Aider repo map | https://aider.chat/docs/repomap.html | Graph-ranked repo map, 1k-token default budget | Aider | 2026-10-16 | Idea only |
| Devin Knowledge | https://docs.devin.ai/product-guides/knowledge | Trigger-recalled tips | hosted, paid | 2026-10-16 | Idea only (trigger descriptions) |
| OpenHands skills (microagents) | https://docs.openhands.dev/openhands/usage/microagents/microagents-overview | Always-on repo context plus keyword-triggered skills | OpenHands | 2026-10-16 | Idea only |
| OpenReview PDF (ContextRotBench) | https://openreview.net/pdf?id=DiZ67nkfay | ContextRotBench host | web | 2026-10-16 | Blocked (browser check, 429); find an arXiv copy |

## Engineer browser and computer control (engineer-browser/tool-landscape.md)

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Playwright CLI (@playwright/cli) | https://github.com/microsoft/playwright-cli | Token-efficient CLI + skills for coding agents; ref snapshots on disk; codegen; Apache-2.0, 14.2k stars; `npm i -g @playwright/cli`, `playwright-cli install --skills` | local | 2026-10-16 | **Use**: primary driver for the engineer; spike on real Attio/Clay tasks |
| Playwright MCP (engineer use) | https://github.com/microsoft/playwright-mcp | Accessibility-snapshot MCP, `browser_drag`, persistent login; Apache-2.0, 38.2k stars | local stdio MCP | 2026-10-16 | **Use** as alternate; widens the research-tools row (which said last resort); MCP and CLI token gap closed by mid-2026 per a third-party re-benchmark |
| Playwright Test Agents | https://playwright.dev/docs/test-agents | planner/generator/healer produce .spec.ts; `npx playwright init-agents --loop=claude` | local | 2026-10-16 | **Use**: record once, replay free; spike healer on drag/drop |
| Puppeteer | https://github.com/puppeteer/puppeteer | Chrome/Firefox JS API, Apache-2.0, 95.7k stars; README points to chrome-devtools-mcp | local | 2026-10-16 | Skip; subsumed by Playwright |
| Chrome DevTools MCP | https://github.com/ChromeDevTools/chrome-devtools-mcp | Google MCP + CLI over Puppeteer; traces, network, console; Apache-2.0, 53.6k stars | local | 2026-10-16 | Fallback for network/console inspection of app requests |
| agent-browser (Vercel Labs) | https://github.com/vercel-labs/agent-browser | Rust CLI, accessibility refs; Apache-2.0, 44k stars, created 2026-01 | local npm/brew/cargo | 2026-10-16 | Fallback; spike vs Playwright CLI |
| Stagehand | https://github.com/browserbase/stagehand | MIT TS SDK, act/extract/observe, selfHeal, local `cacheDir` replay; 25.7k stars | local or Browserbase | 2026-10-16 | Fallback replay layer; needs own LLM key; John-named, adopted only as an option |
| browser-use | https://github.com/browser-use/browser-use | MIT Python agent + CLI skill, cloud $0.02/browser-hour; 118k stars; page contains agent-addressed install prompts, not followed | local or cloud | 2026-10-16 | Skip as primary (second LLM loop) |
| browser-harness | https://github.com/browser-use/browser-harness | MIT; Claude Code drives real Chrome over CDP, MCP stdio; agent writes helpers; page contains agent-addressed install prompt, not followed | local | 2026-10-16 | Fallback; unvetted, spike first |
| workflow-use | https://github.com/browser-use/workflow-use/ | Record-to-JSON workflows with agent fallback | local | 2026-10-16 | Skip; maintainers say not production-ready |
| Skyvern | https://github.com/Skyvern-AI/skyvern | Vision-LLM agent + Playwright SDK, explore/replay code-gen; AGPL-3.0; cloud Free/$29/$149 | local server or cloud | 2026-10-16 | Skip for now; AGPL, own server and LLM |
| Magnitude browser agent | https://github.com/magnitudedev/browser-agent | Vision-first TS agent, Apache-2.0, 4.1k stars; magnitudedev/magnitude is now an inference engine | local | 2026-10-16 | Reject: stale, self-reported benchmark only |
| Anthropic browser use tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool | API toolset with accessibility refs + coordinate drag; you write the executor | Claude API | 2026-10-16 | Reference design only |
| Anthropic computer use tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | Desktop screenshot/mouse toolset `computer_toolset_20260801` | Claude API + your VM | 2026-10-16 | Fallback for desktop (other facet) |
| Claude in Chrome (engineer use) | https://code.claude.com/docs/en/chrome | Logged-in visible Chrome via extension; off with API key/setup-token | John's machine | 2026-10-16 | Fallback for supervised one-offs (existing row above) |
| ComponentBench | https://arxiv.org/html/2608.18307 | 2,910 component-level tasks; AX-tree vs pixel vs browser-use; drag/drop findings | dataset (not run) | 2026-10-16 | Evidence; possible harness for the drag-drop spike |
| Online-Mind2Web leaderboards (Steel, HAL) | https://leaderboard.steel.dev/leaderboards/online-mind2web/ | Live-web benchmark boards; judges differ, many self-reports | web | 2026-10-16 | Evidence only; do not plan from vendor scores |
| Claude Code computer use (CLI `computer-use` MCP) | https://code.claude.com/docs/en/computer-use | Built-in screen control of approved apps; macOS only, Pro/Max, interactive only (not `-p`); real desktop | John's Mac | 2026-10-16 | Not for the unattended engineer; native-app tests on a Mac only (computer-control.md) |
| Claude Desktop computer use | https://code.claude.com/docs/en/desktop | Same engine, macOS and Windows; app must run; browsers view-only; Dispatch approvals 30 min | John's Mac/Windows | 2026-10-16 | Alternative on a spare machine; not unattended-safe |
| OpenClaw computer/browser tools | https://github.com/openclaw/openclaw | Peekaboo/CUA `computer` tool, managed Chrome; `openclaw mcp serve` exposes only channel conversations (commit 58d7e878) | local/VM | 2026-10-16 | Reject as controller; cannot hand its hands to Claude Code |
| Cua (Driver, Lume, SDK, Spaces) | https://github.com/trycua/cua | Driver MIT, MCP for Claude Code, macOS/Windows/Linux; Spaces FSL-1.1-MIT; 29.9k stars; old npm `cuabot` flagged "Do not run it" | Mac/Win/Linux, VMs | 2026-10-16 | Spike first as optional desktop add-on in a throwaway VM |
| E2B Desktop | https://github.com/e2b-dev/desktop | Apache-2.0 Linux Xfce sandbox SDK for LLM computer use | E2B cloud (paid, price unverified) | 2026-10-16 | Alternative sandbox |
| Bytebot | https://github.com/bytebot-ai/bytebot | Self-hosted Docker desktop agent with MCP | Docker | 2026-10-16 | Reject: archived 2026-03-07 |
| UI-TARS Desktop / Agent TARS | https://github.com/bytedance/UI-TARS-desktop | Apache-2.0 GUI agent app with own models | local | 2026-10-16 | Reject: separate agent, last news 2025-11-05 |
| Agent S (Simular) | https://github.com/simular-ai/Agent-S | Apache-2.0 research GUI agent; 72.6% OSWorld self-report | local | 2026-10-16 (search result only) | Reference only |
| OpenAI ChatGPT agent / Operator | https://help.openai.com/en/articles/11752874-agent | Closed hosted agent; help page says no longer available | OpenAI | 2026-10-16 (search result only) | Reject: not drivable from Claude Code |
| Playwright MCP persistent profile / --extension (sessions-and-hosting.md) | https://github.com/microsoft/playwright-mcp | Persistent on-disk profile by default; isolated mode + storage-state; extension mode attaches to running Chrome/Edge; headed by default | VM / local | 2026-10-16 | Use persistent profile on the VM; extension mode fallback on John's machine |
| Playwright storageState | https://playwright.dev/docs/auth | Cookie/localStorage/IndexedDB/passkey snapshot file; no sessionStorage; delete when expired | local | 2026-10-16 | Fallback only; the file is a credential |
| noVNC + websockify | https://github.com/novnc/noVNC | Browser VNC client (MPL 2.0) for a virtual desktop | VM | 2026-10-16 | Use behind Tailscale/SSH for the one-time login and live view; spike |
| 1Password CLI service accounts | https://www.1password.dev/service-accounts/use-with-1password-cli | Vault-scoped reads incl. OTP attribute; hourly/daily request limits | VM | 2026-10-16 | Use if John has 1Password; else local seed + pyotp; spike |
| Bitwarden Secrets Manager CLI | https://bitwarden.com/help/secrets-manager-cli/ | Machine-account token CLI; no TOTP documented | VM | 2026-10-16 | Fallback for static secrets only |
| Browserbase | https://www.browserbase.com/pricing | Hosted browsers; Free 15-min sessions; $20/$99 plans; $0.12/$0.10 per extra hour | hosted | 2026-10-16 | Skip for logged-in work; vendor would hold cookies and health data |
| Steel / Anchor Browser | https://llms.anchorbrowser.io/anchor-browser-vs-steel | Hosted browsers with credential stores (vendor-authored comparison); Steel is Apache-2.0 self-hostable | hosted / Docker | 2026-10-16 | Skip; reference only; primary pages not opened |
| Hyperbrowser / Browserless | https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/ | Hosted browsers; stealth/CAPTCHA are headline features | hosted | 2026-10-16 (third-party page only) | Reject (evasion focus) |
| Stealth plugins, CAPTCHA solvers, residential proxies | https://github.com/blhutchings/google-login-service | Bot-detection evasion | n/a | 2026-10-16 (search highlights only) | Rejected as evasion; not evaluated |
| Claude Code computer use | https://code.claude.com/docs/en/computer-use | GUI control; macOS CLI; Desktop macOS/Windows; interactive only | John's machine | 2026-10-16 | Not a login path for the VM |
| Playwright actionability + trace viewer + retries (reliability-and-guardrails.md) | https://playwright.dev/docs/trace-viewer-intro | Auto-wait before actions; `trace: 'on-first-retry'`; trace.zip with per-step DOM, network, console | local | 2026-10-16 | **Use** as the deterministic reliability layer |
| Claude in Chrome safety features (reliability-and-guardrails.md) | https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely | Injection probes, per-action classifier, site blocklists, confirmations, Manually-approve mode, separate-profile advice | John's machine | 2026-10-16 | Use for attended work; vendor says risk is not zero |
| Claude Code PreToolUse hooks + MCP deny rules (browser guard) | https://code.claude.com/docs/en/hooks | Deny/ask `mcp__<server>__.*` browser calls in any mode; deny beats hook allow; timed-out hook does not block unless `onFailure: "block"` | Claude Code | 2026-10-16 | **Build point** for destructive-click and domain guard; spike `tool_input` fields; incident anthropics/claude-code#65563 (reporter claim) shows need |
| Checkly Playwright monitors | https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/ | Hosted scheduled Playwright checks, golden-image diff on production | hosted, paid (price not checked) | 2026-10-16 | Fallback; self-host a cron smoke run first |
| Attio REST API views/workflows finding (api-vs-browser.md) | https://api.attio.com/openapi/api | Spec has 53 paths; views are GET-only (id/title), no workflow routes; attributes, options, statuses, lists writable | hosted | 2026-10-16 | Use API for data model; browser only for views and Workflows |
| Clay agent plugin + CLI (clay-run/agent-plugins) | https://github.com/clay-run/agent-plugins | Skills + clay CLI: searches, routines, Workflows (Alpha), signals, campaigns; cannot create tables (SKILL.md:96, commit b9952b6) | Claude Code with shell | 2026-10-16 | Use for Workflows and reads; table/column building stays UI |
| Outreach MCP server | https://developers.outreach.io/mcp-server | 32 tools, OAuth 2.1 DCR, RBAC inherited; sequence_create, no template or mailbox tools | hosted | 2026-10-16 | Use for sequences; REST for templates and mailboxes |
| WHOOP developer API | https://developer.whoop.com/docs/developing/getting-started | OAuth2, dashboard app creation (human), offline scope refresh, 100 req/min | hosted | 2026-10-16 | Use after one-time human registration and consent |
| Withings Public API | https://developer.withings.com/developer-guide/v3/get-access/sign-up-for-a-developer-account | OAuth2 web flow; Withings+ required for new accounts on free plan from 2026-10-12 | hosted | 2026-10-16 | Use; check plan terms (plans page unreadable) |
| n8n public API handlers (master) | https://github.com/n8n-io/n8n | Routes for community packages, credentials, variables, tags, projects, SSO settings (commit 21221ad) | self-hosted/cloud | 2026-10-16 | Use; confirm release and Cloud availability |
| Fasten OnPrem (patient-portals.md) | https://github.com/fastenhealth/fasten-onprem/ | GPL-3.0 self-hosted FHIR viewer; archived; cannot import from providers, FHIR Bundle upload only | Docker | 2026-10-16 | Reject as puller; archived |
| Fasten Connect | https://docs.connect.fastenhealth.com/quickstart | Commercial patient-authorized records API; free sandbox; TEFCA live fees; live price unpublished | hosted | 2026-10-16 | Fallback; ask whether an individual may open a live account |
| Flexpa | https://www.flexpa.com/pricing | Patient-consented FHIR API with MCP add-on; $20,000/year minimum, no free live mode | hosted | 2026-10-16 | Reject: price |
| 1upHealth / Metriport / Health Gorilla / Particle | https://docs.1up.health/docs/get-started/third-party-apps | Sales- or vetting-gated record aggregators (search highlights only) | hosted | 2026-10-16 (search highlight) | Reject for solo use |
| Epic on FHIR patient-facing SMART app | https://open.epic.com/DeveloperResources | Self-service client IDs; per-health-system patient OAuth; sandbox forbids real PHI | Epic customers | 2026-10-16 | Fallback for MyChart labs; John does consent |
| Android Health Connect Medical Records | https://developer.android.com/health-and-fitness/health-connect/medical-records | On-phone FHIR store with lab read permission; experimental | Android 16 | 2026-10-16 | Skip |
| Apple Health clinical-records export | https://www.johngoldin.com/blog/apple-health-export/2020-02-apple-health-export1/index.en.html | export.zip with FHIR JSON clinical records (2020 blog) | iPhone then local parse | 2026-10-16 | Use if John has iPhone; spike |
| Labcorp User Agreement (portal automation) | https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement | Bans robots/scrapers without written permission; allows personal downloads | n/a | 2026-10-16 | No unattended portal login; John downloads PDF |

## Engineer feasibility and trials

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| MADR | https://adr.github.io/madr/ | Markdown ADR template: decision drivers, considered options, pros/cons, confirmation | notation, no install | 2026-10-16 | Use as the path-decision record (mapping-and-rubric.md) |
| mermaid-lint | https://github.com/jasonworden/mermaid-lint | MIT Mermaid validator using official parser; npx, Node 22+; exit 0/1/2 | local, CI, hook (not installed) | 2026-10-16 | Use as diagram gate; spike on generated diagrams |
| Mermaid C4 diagram type | https://mermaid.js.org/syntax/c4.html | C4 in Mermaid, labelled experimental | Mermaid renderers | 2026-10-16 | Skip as default; plain flowchart instead; GitHub rendering contested |
| Structurizr DSL | https://docs.structurizr.com/dsl | Text C4 model; exports PlantUML/Mermaid | local | 2026-10-16 | Fallback for multi-view models |
| Pugh matrix / weighted scoring / mini-ATAM | https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/ | Datum-based non-numeric comparison; frozen-weight scoring; SEI utility tree with High/Medium/Low | notation | 2026-10-16 | Use gates + Pugh/H-M-L ratings + tie rule; no summed decimals; full ATAM rejected |
| rune-kit ADR criteria | https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md | Gate for when to write an ADR; 1-5 reversibility scale | reference (not installed) | 2026-10-16 | Reference: copy gate and counter-test |
| Claude Code worktrees (`--worktree`, `isolation: worktree`) | https://code.claude.com/docs/en/worktrees | Isolated checkout and branch per session or subagent; `-p` runs are not cleaned up | Claude Code, local | 2026-10-16 | Use: one per trial; supervisor sweeps leftovers (trial-sandboxes.md) |
| Claude Code agent view (`claude agents`) | https://code.claude.com/docs/en/agents | Background-session dispatcher, research preview | Claude Code | 2026-10-16 | Skip for trials; results only to the user |
| Claude Code Bash sandbox (bubblewrap) | https://code.claude.com/docs/en/sandboxing | Shell-only OS sandbox, empty domain allowlist, credential mask; Ubuntu 24.04 needs AppArmor profile | Linux/macOS/WSL2 | 2026-10-16 | Inner layer only; Anthropic: not sufficient unattended |
| Hardened container + credential-injecting proxy | https://code.claude.com/docs/en/agent-sdk/secure-deployment | `--network none` container, host proxy allowlists and injects credentials | local Docker / rootless Podman | 2026-10-16 | Recommended trial boundary; spike |
| Rootless Podman | https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md | Rootless containers; needs subuid/subgid and pasta | local | 2026-10-16 | Fallback to Docker; limits unverified |
| gVisor / Firecracker | https://code.claude.com/docs/en/agent-sdk/secure-deployment | Userspace kernel (slow I/O) / microVM (vsock proxy) | local | 2026-10-16 (Anthropic page only) | Skip for v1 |
| Docker Sandboxes (sbx) | https://docs.docker.com/ai/sandboxes/ | MicroVM per agent, host credential proxy, deny-by-default egress; Ubuntu 24.04+ with KVM; Docker login; curl-script install (not run) | local or Docker cloud | 2026-10-16 | Strong alternative if `/dev/kvm` exists; spike |
| E2B | https://e2b.dev/pricing | Hosted sandbox, prebuilt `claude` template, $100 one-time credit, 1 h Hobby session, open egress default | hosted | 2026-10-16 | Fallback for public-code probes |
| Daytona | https://www.daytona.io/pricing | Hosted sandbox, $200 free compute, sub-90ms create claim | hosted | 2026-10-16 | Fallback; limits not seen |
| Vercel Sandbox | https://vercel.com/docs/vercel-sandbox/pricing | Firecracker microVMs; Hobby 10 concurrent/45 min, Pro 24 h; $0.11 for a 30-min 4-vCPU build | hosted | 2026-10-16 | Fallback; cheapest hosted for 30-minute trials |
| Modal Sandboxes | https://modal.com/pricing | Sandbox rate about 3x container; $30 monthly free credit | hosted | 2026-10-16 | Skip |
| Cloudflare Sandbox SDK | https://developers.cloudflare.com/sandbox/ | Per-task Linux sandbox on Containers; Workers Paid | hosted | 2026-10-16 | Skip unless on Cloudflare; price not opened |
| epitaph 0.2.0 | https://pypi.org/project/epitaph/ | Repo-scoped JSON ledger of rejected agent attempts with `retry_when`; `check_nogo` lookup via CLI/MCP; pipx install | local, Python >=3.10 | 2026-10-16 (PyPI page only, not installed) | Reference only; copy the record shape, v0.x unvetted (spike-practice.md) |
| dsh-negative-ledger | https://github.com/akslcw/dsh-negative-ledger | Negative-fact ledger from failed tool calls with fingerprint, TTL, warn/block | local plugin | not opened (search excerpt only) | Reference only; unverified |
| vexjoy-agent what-didnt-work.md | https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md | Dated negative-results registry: expectation / what happened / evidence / decision | repo markdown | 2026-10-16 | Copy the four-field format for dead-ends.md |
| Cursor /best-of-n | https://cursor.com/docs/configuration/worktrees | Same task across several models, one worktree each, picker not merger | Cursor IDE | 2026-10-16 | Skip, different engine; idea only |
| Claude Code worktrees, /batch, isolation: worktree | https://code.claude.com/docs/en/best-practices | Parallel isolated sessions and subagents (5 to 30 for /batch) | Claude Code | 2026-10-16 | Use for parallel candidate runs |
| MADR | https://adr.github.io/madr/decisions/adr-template.html | ADR template with Considered Options and Bad-because per option | markdown | 2026-10-16 | Use for decisions; not for trial logs |
| Slack apps.manifest.create | https://docs.slack.dev/reference/methods/apps.manifest.create | Create a Slack app from a manifest using an app configuration token | hosted | 2026-10-16 | Use for app registration; workspace install still needs an admin click (edge-cases-and-setup-list.md) |
| Stripe webhook + idempotency docs | https://docs.stripe.com/webhooks | Reference rules: raw-body signature, 5-minute replay tolerance, dedupe by event ID, no ordering, 24 h idempotency keys | docs | 2026-10-16 | Reference pattern for the integration edge-case checklist |
| Google AIP-194 | https://google.aip.dev/194 | Retry guidance (UNAVAILABLE retryable; no blind retry of state changes) | docs | 2026-10-16 | Reference; thin on backoff |
| Cloudflare Terraform provider | https://developers.cloudflare.com/api/terraform/ | IaC for Cloudflare with API token auth | local | not opened (search excerpt only) | Candidate; spike before relying |

## Engineer deployment

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Gradle wrapper (Android CLI build) | https://developer.android.com/build/building-cmdline | Headless build and sign of APK/AAB, no Android Studio | Linux VM | 2026-10-16 | Use; spike SDK setup (mobile.md) |
| Bubblewrap / Trusted Web Activity | https://developer.chrome.com/docs/android/trusted-web-activity/overview | Node CLI wraps a PWA as an Android app; page dated 2020 | Linux VM | 2026-10-16 | Fallback for Play-listing a PWA; README not opened |
| Capacitor (Android) | https://capacitorjs.com/docs/android | Web app in Android WebView; Android Studio centred, CLI allowed | Linux VM | 2026-10-16 | Use when native plugins needed; spike headless |
| Expo EAS Build / Submit | https://docs.expo.dev/submit/android/ | 15 free Android + 15 iOS builds/month; `eas build --local` on Linux; Submit uploads .aab to internal track, no listing | Expo cloud / VM | 2026-10-16 | Fallback if React Native chosen; first-upload claim conflicts with fastlane |
| fastlane supply | https://docs.fastlane.tools/actions/upload_to_play_store/ | Uploads binaries, listing, screenshots; promotes tracks; first build uploaded manually | Linux VM | 2026-10-16 | Use for non-Expo |
| Firebase App Distribution | https://firebase.google.com/docs/app-distribution | Tester distribution via CLI/Gradle/fastlane; price not seen | Google cloud | 2026-10-16 | Fallback to `adb install` |
| Codemagic | https://codemagic.io/pricing/ | Cloud macOS builds, 500 free M2 min/month then $0.095/min | cloud | 2026-10-16 | Use for iOS later |
| Health Connect SDK | https://developer.android.com/health-and-fitness/health-connect/get-started | Native Android health API; no web API on page | Android | 2026-10-16 | Needs wrapper/native app, not PWA |
| n8n self-hosted (Community) licence/limits (automation-surfaces.md) | https://github.com/n8n-io/n8n/blob/master/LICENSE.md | Sustainable Use Licence: internal business use; no git/environments in Community; API on by default | VM | 2026-10-16 | Keep for John's visual flows; Postgres, pruning, nightly export to git |
| n8n Cloud pricing | https://n8n.io/pricing/ | Starter 20 EUR/mo annual, 2.5K executions; API not on free trial | cloud | 2026-10-16 | Fallback; small quota |
| n8n instance-level MCP | https://docs.n8n.io/advanced-ai/mcp/accessing-n8n-mcp-server/ | Create/edit workflows (2.13.0+) on flagged workflows | n8n | 2026-10-16 | Use after spike on throwaway instance |
| Cloudflare Workers cron + webhook receiver | https://developers.cloudflare.com/workers/platform/limits/ | Free 100k req/day, 5 cron triggers, 10 ms CPU; wrangler cron + local scheduled route | cloud | 2026-10-16 | Use for webhook receivers and light cron |
| Cloudflare Tunnel | https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ | Outbound-only tunnel; price not on page | VM | 2026-10-16 | Option; price unverified |
| GitHub Actions schedule | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows | Cron >=5 min, delays, auto-disable after 60 days inactivity (public repos) | GitHub | 2026-10-16 | Fallback for repo-bound jobs |
| Supabase pg_cron + edge functions | https://supabase.com/docs/guides/cron | SQL cron calling edge functions; free 150 s wall clock | cloud | 2026-10-16 | Only if data is in Supabase |
| systemd timers | https://man7.org/linux/man-pages/man5/systemd.timer.5.html | Persistent= catch-up of missed runs | VM | 2026-10-16 | Use: default VM scheduler |
| Trigger.dev | https://trigger.dev/pricing | Durable tasks, Apache 2.0, $5 credit, 10 schedules free | cloud/self-host | 2026-10-16 | Fallback if durable retries needed |
| Inngest | https://www.inngest.com/pricing | Durable functions; 50k executions/mo free | cloud | 2026-10-16 | Fallback |
| Windmill | https://www.windmill.dev/pricing | Scripts/flows; free self-host unlimited executions; licence not stated on page | self-host | 2026-10-16 | Fallback; licence unverified |
| Temporal | (not opened) | Durable workflow engine | - | not opened | Reject for one user; not researched |
