# Tool registry

Every tool evaluated for this project. Verdicts as of the verified date; details and the
evidence behind each verdict are in `research/findings/` (tool-routing.md, methodology.md,
packaging.md, architecture.md, engineer-intake.md).

## Research tools in use

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Parallel Search MCP | https://docs.parallel.ai/search/search-mcp | Keyless web search with answer-ready excerpts; fetch up to 20 URLs with objective-focused excerpts | claude.ai connector | 2026-10-16 | **Primary** for discovery and page reading |
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
| Superpowers | https://github.com/obra/superpowers | Engineering methodology skills; manifest version 7.0.0 at commit bb92a77 | plugin, via `scripts/cloud-setup.sh` | 2026-10-16 | In use; brainstorming flow reused for the interview skill; pin the version in the bootstrap (engineer-runtime.md) |

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

## Evaluated and deferred or skipped

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Beads | https://github.com/steveyegge/beads | Dolt-backed dependency-graph issue tracker for agents; CLI installed once (`bd setup claude`); checksum-verified installer now under gastownhall org | not installed | 2026-10-16 | Phase 2; git files suffice for one researcher; install by bootstrap flag only (engineer-runtime.md) |
| Ralph Loop | https://claude.com/plugins/ralph-loop | Stop hook re-feeds one prompt until `<promise>` text or iteration cap | not installed | 2026-10-16 | Phase 2; only with script-checked completion and max-iterations |
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
