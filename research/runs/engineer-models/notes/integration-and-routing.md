# Integration patterns, routing criteria and risks

Brief: Find how a Claude Code engineer would call a non-Claude model when it helps, what each mechanism costs to keep working, and how to route and fall back safely.
Run: research/runs/engineer-models/PLAN.md

Repo facts below come from `git clone --depth 1` into a mktemp dir on 2026-10-16 (read only, nothing run). Parallel Search returned "Too Many Requests"; Exa and WebFetch were used instead. Opened pages were read through WebFetch (summarising model), so quotes are limited to text it returned in quotation marks or as page text.

## Mechanisms (MCP wrapper, CLI subprocess, routing proxy, Agent SDK tool)

### Takeaway
Cheapest-to-keep-working is a CLI subprocess wrapped as a plugin/skill (official `openai/codex-plugin-cc` for Codex; an `agy`/Antigravity or paid-key Gemini CLI wrapper for Gemini), with an in-process Agent SDK tool or a thin MCP as the place to enforce data-class rules. Routing proxies are the worst fit: Anthropic says it does not support non-Claude models through any gateway, and setting a gateway credential drops the Max subscription. Confidence: medium-high.

### Cited findings
- Anthropic: gateways work if they speak a supported API format, but "doesn't support routing Claude Code to non-Claude models through any gateway"; the gateway operator must keep up with each Claude Code release. — https://code.claude.com/docs/en/llm-gateway, opened 2026-10-16, WebFetch — Quote: "doesn't support routing Claude Code to non-Claude models through any gateway"
- With a gateway credential variable or apiKeyHelper active, the Max login is not used and traffic is billed per token; setting only ANTHROPIC_BASE_URL keeps the subscription login. — https://code.claude.com/docs/en/llm-gateway, opened 2026-10-16, WebFetch — Quote: "requests carry that credential in place of a developer's claude.ai subscription login, and the subscription's usage limits don't apply to them."
- Gateways that strip headers or rewrite bodies break features: beta header and body field pairs cause 400s; prompt caching silently bills uncached; `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` removes tool search among others. — https://code.claude.com/docs/en/llm-gateway-protocol, opened 2026-10-16, WebFetch — Quote: "A gateway that strips the header while passing the body, or forwards an Anthropic-format body to an upstream with a different schema, produces hard `400` errors"
- Sessions through a gateway are outside the HIPAA configuration. — https://code.claude.com/docs/en/llm-gateway-protocol, opened 2026-10-16, WebFetch — Quote: "Sessions that go through a gateway aren't eligible for the HIPAA configuration."
- OpenRouter's own Claude Code guide: non-Anthropic models are not guaranteed to work. — https://openrouter.ai/docs/guides/guides/claude-code-integration, opened 2026-10-16, WebFetch — Quote: "Claude Code is optimized for Anthropic models and may not work correctly with other providers."
- Terms: OAuth subscription credentials are for ordinary use of Claude Code; developers building on the Agent SDK should use API keys; routing requests through Pro/Max credentials on behalf of others is barred. — https://code.claude.com/docs/en/legal-and-compliance, opened 2026-10-16, WebFetch — Quote: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- Agent SDK custom tools: in-process MCP server via `createSdkMcpServer`/`tool()`; tools named `mcp__{server}__{tool}`; handler errors can return `isError: true` so Claude can retry or explain. — https://code.claude.com/docs/en/agent-sdk/custom-tools, opened 2026-10-16, WebFetch — Quote: "The server runs in-process inside your application, not as a separate process."
- claude-code-router (CCR): MIT licence, last commit 2026-10-10 (057abaa); local gateway with retries, key rotation and ordered fallback models, supports Gemini, OpenAI, OpenRouter, others. — https://github.com/musistudio/claude-code-router README.md:36 (commit 057abaa), read 2026-10-16, git clone — Quote: "**Keep requests running** with retries, credential pools, key rotation, and ordered fallback models."
- LiteLLM: repo active (last commit 2026-10-16, f81e657); MIT outside enterprise/ directory. PyPI releases 1.82.7 and 1.82.8 were malicious on 2026-03-24 (credential stealer), official Docker image not affected. — https://docs.litellm.ai/blog/security-update-march-2026, opened 2026-10-16, Exa search highlights (page text) — Quote: "The compromised PyPI packages were litellm==1.82.7 and litellm==1.82.8."
- Same incident confirmed independently, with the stolen-secret list and persistence. — https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/, opened 2026-10-16, Exa search highlights — Quote: "Defenders should treat any host or CI job that installed `litellm``1.82.7` or `1.82.8`"
- PAL MCP (formerly Zen MCP): Apache-2.0; last commit in clone 2025-12-15 (7afc7c1), 10 months before today; providers Gemini, OpenAI, Azure, X.AI, OpenRouter, DIAL, Ollama; keys read from `.env` or the MCP `env` block; `clink` bridges to other CLIs. — https://github.com/BeehiveInnovations/pal-mcp-server README.md:26 (commit 7afc7c1), read 2026-10-16, git clone — Quote: "connects external AI CLIs directly into your workflow"
- PAL tools beyond the core carry per-tool context cost and are off by default. — https://github.com/BeehiveInnovations/pal-mcp-server README.md:207 (commit 7afc7c1), read 2026-10-16, git clone — Quote: "Each tool comes with its own multi-step workflow, parameters, and descriptions that consume valuable context window space even when not in use."
- Codex CLI: Apache-2.0, active (last commit 2026-10-16, b5115cd). `codex exec` is the headless mode: read-only sandbox by default, `--json`, `--output-schema`, `-o`; CI key via `CODEX_API_KEY` for one invocation only. — https://learn.chatgpt.com/docs/non-interactive-mode, opened 2026-10-16, WebFetch — Quote: "By default, `codex exec` runs in a read-only sandbox."
- Official Codex plugin for Claude Code: `/codex:review`, `/codex:adversarial-review`, `/codex:rescue`; works with a ChatGPT subscription (including Free) or an OpenAI API key; Apache-2.0, last commit 2026-07-07 (db52e28). — https://github.com/openai/codex-plugin-cc README.md (commit db52e28), read 2026-10-16, git clone — Quote: "ChatGPT subscription (incl. Free) or OpenAI API key."
- Gemini CLI moved: Apache-2.0, active, but consumer free/Pro/Ultra serving ended 2026-06-18 in favour of Antigravity CLI; still reachable via paid API keys. — https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli, opened 2026-10-16, WebFetch — Quote: "Gemini CLI will remain accessible via paid Gemini and Gemini Enterprise Agent Platform API keys."
- Gemini CLI README banner confirms the cutover and that Gemini 4 Argon needs Antigravity. — https://github.com/google-gemini/gemini-cli README.md:3 (commit b25669d), read 2026-10-16, git clone — Quote: "Gemini CLI has not been optimized for Gemini 4 Argon. To use Gemini 4 Argon, please use Antigravity."
- Gemini CLI terms: using its OAuth through third-party tools is a violation. — https://github.com/google-gemini/gemini-cli docs/resources/tos-privacy.md:9 (commit b25669d), read 2026-10-16, git clone — Quote: "using OpenClaw with Gemini CLI OAuth) is a violation of applicable terms and policies."
- Gemini CLI headless: `-p`, `--output-format` json or stream-json. — https://github.com/google-gemini/gemini-cli docs/cli/headless.md:6 (commit b25669d), read 2026-10-16, git clone — Quote: "Headless mode is triggered when the CLI is run in a non-TTY environment or when providing a query with the `-p` (or `--prompt`) flag."

### Contradictions
- None found on mechanisms. Note the tension (not a contradiction): CCR and OpenRouter advertise non-Claude models behind Claude Code, Anthropic says it does not support that.

### Inferences
- Rank (mine): (1) CLI subprocess plugin/skill, (2) own Agent SDK / small MCP tool "ask_other_model" that holds the data-class gate, (3) PAL MCP only as a reference or fallback (stale since Dec 2025), (4) CCR only for a separate non-Max experiment, (5) LiteLLM rejected (supply-chain incident, plus subscription loss). Rests on the llm-gateway, legal, PAL and LiteLLM findings.
- Keys: CLIs hold their own login on disk (`codex login`, `agy` sign-in); API keys belong in the process env of the wrapper only, or the cloud "network secrets" proxy from the registry, never in the repo.

### Gaps
- Antigravity CLI (`agy`) headless flags, quota and terms not opened first-hand; only third-party plugin pages (Idun Group blog, LovelaceLoom README) seen in search excerpts, so no cited claim about `agy` internals.
- Whether a Max-subscribed Claude Code session may spawn `codex`/`agy` subprocesses is not a Claude auth question (they use their own credentials); no Anthropic page addresses it. Treated as allowed by inference.
- OpenRouter ZDR/data-policy routing not on the page opened.

## What others have built

### Takeaway
Many small plugins exist for second-opinion review and delegation; none I opened carries measured results. Pattern is consistent: Claude drives, other model is read-only reviewer or large-context reader, output written to a file or stdout. Confidence: medium (anecdotal evidence only).

### Cited findings
- Gemini plugin for Claude Code with `/gemini:review` (diff sent via stdin, findings by severity) and `/gemini:task` read-only unless `--write`. — https://github.com/tokenpower/gemini-claude-plugin, opened 2026-10-16, Exa search highlights — Quote: "This command is read-only and will not make any code changes."
- Second Opinion MCP bundles session files, dependencies and branch diff, sends to Gemini and GPT in parallel, writes reviews to `second-opinions/`; API keys passed as env. — https://github.com/noelweichbrodt/second-opinion, opened 2026-10-16, Exa search highlights — Quote: "Smart fallback: if only one API key is configured, uses that single provider"
- Antigravity plugin, adversarial-review mode, a stop-time review gate that fails open by default. — https://github.com/LovelaceLoom/gemini-plugin-cc, opened 2026-10-16, Exa search highlights — Quote: "By default the stop hook **fails open** on infrastructure errors"
- Silent-failure case: `agy --print` returned exit 0 with empty stdout when preview quota ran out (agy 1.0.3). — https://idun-group.com/blog/antigravity-plugin-claude-code, opened 2026-10-16, Exa search highlights — Quote: "When the per-account preview quota runs out, `agy --print` exits `0` with completely empty stdout."
- Single-developer write-up: Gemini CLI used as "external peer" after a Claude fix; it reported three missed items (one old init pattern, a possible leak, missing error boundaries). Anecdote, undated in excerpt. — https://byjos.dev/claude-gemini-workflow/, opened 2026-10-16, Exa search highlights — Quote: "Gemini CLI, acting as an external peer reviewer, caught a few things we missed"

### Contradictions
- None found.

### Inferences
- The silent-empty-output case means the wrapper must treat empty stdout as failure, not success (mine, from the Idun finding).
- Plugins above are 0-to-few-star single-author repos (unvetted); copy the shape (stdin diff, read-only, background job, timeouts, fail-open gate), prefer the official `openai/codex-plugin-cc`.

### Gaps
- No measured quality, cost or defect-catch rate for cross-model review found; all evidence is anecdote. Needs a spike on John's own repos.
- Dates of the blog and plugin pages not shown in excerpts.

## Routing criteria and fallback

### Takeaway
Default every task to Claude; call another model only for (a) an independent review of a finished diff or plan, (b) a read that will not fit in Claude's context or is cheaper elsewhere, (c) a modality Claude lacks. Gate by data class first, then size, then cost. If the other vendor fails, skip it and continue with Claude plus a logged note. Confidence: medium (mostly design, resting on cited mechanics).

### Cited findings
- Codex exec prints only the final message to stdout and streams progress to stderr, and `-o` writes the last message to a file: suitable for "result goes to a file in the repo". — https://learn.chatgpt.com/docs/non-interactive-mode, opened 2026-10-16, WebFetch — Quote: "Codex streams progress to stderr and prints only the final agent message to stdout"
- Timeout exit code 124 and fail-open gate show a usable fallback contract. — https://github.com/LovelaceLoom/gemini-plugin-cc, opened 2026-10-16, Exa search highlights — Quote: "Exit code on timeout is **124** (matches `timeout(1)`)"
- CCR gives ordered fallback models and retries when a provider is down (relevant only if a router is used). — https://github.com/musistudio/claude-code-router README.md:36 (commit 057abaa), read 2026-10-16, git clone — Quote: "retries, credential pools, key rotation, and ordered fallback models."
- Gemini CLI free quota by auth: API key unpaid 250 requests/day (page predates the consumer cutover for Google-login rows). — https://github.com/google-gemini/gemini-cli docs/resources/quota-and-pricing.md (commit b25669d), read 2026-10-16, git clone — Quote: "Free tier (Unpaid)              | 250 requests"

### Contradictions
- quota-and-pricing.md in the Gemini CLI clone still lists Google-account tiers (1,000 to 2,000 requests/day) although the README and Google blog say consumer serving stopped 2026-06-18. Treat the table as stale for those rows.

### Inferences
Routing table (mine; thresholds are spike items, not findings):
| Signal | Route |
| --- | --- |
| Data class health or personal | Claude only (or a paid-tier, no-training endpoint after John approves per vendor) |
| Data class GTM/customer PII | Claude, or paid-tier API only |
| Public/repo code, plans, research notes | Any |
| Input over what Claude holds comfortably (size set by the long-context facet) | Gemini paid key read-only, summary to a file |
| Review of finished diff/plan | Codex or Gemini, adversarial prompt, read-only |
| Cost-sensitive bulk summarising | Cheaper model, or Haiku 5.5 per registry |
Fallback: wrapper returns `{status: ok|empty|timeout|auth|quota}`; on anything but ok, Claude proceeds alone and writes "second opinion unavailable: <status>" into the PR/plan file; no retry loop beyond one. One source of truth: the other model never edits files (read-only/sandbox default, no `--write`/yolo); its output lands as a file under e.g. `reviews/` and Claude folds accepted points into the plan or code.

### Gaps
- No source on latency or relative cost per task type; model-fact facets cover that.
- Antigravity free-tier limits not opened.

## Risks and data-class marking

### Takeaway
Free Gemini API quota trains on and human-reviews prompts, so health data must never reach it; paid Gemini and the OpenAI API do not train by default. Each extra vendor adds a key, a terms set and a failure mode, and Gateways take sessions out of Anthropic's HIPAA configuration. Mark data classes in the repo and enforce with a hook and a wrapper that only holds paid keys. Confidence: high on the terms, medium on the enforcement design.

### Cited findings
- Gemini API unpaid services: content used to improve products; human review; warned off sensitive data. — https://ai.google.dev/gemini-api/terms, opened 2026-10-16, WebFetch — Quote: "Do not submit sensitive, confidential, or personal information to the Unpaid Services."
- Gemini API paid services: not used to improve products; limited logging for abuse and legal reasons. — https://ai.google.dev/gemini-api/terms, opened 2026-10-16, WebFetch — Quote: "human reviewers may read, annotate, and process your API input and output."  (this quote is the unpaid-tier review clause; paid-tier "does not use prompts to improve products" is the page summary, not a verbatim quote)
- OpenAI API: no training by default, 30-day abuse logs. — https://developers.openai.com/api/docs/guides/your-data, opened 2026-10-16, WebFetch — Quote: "data sent to the OpenAI API is not used to train or improve OpenAI models,"
- Same page: retention. — https://developers.openai.com/api/docs/guides/your-data, opened 2026-10-16, WebFetch — Quote: "By default, abuse monitoring logs are generated for all API feature usage and retained for up to 30 days."
- Codex CI hygiene: keys not job-wide in workflows that run repo-controlled code. — https://learn.chatgpt.com/docs/non-interactive-mode, opened 2026-10-16, WebFetch — Quote: "Don't set `OPENAI_API_KEY` or `CODEX_API_KEY` as a job-level environment variable"
- Gemini CLI auth table maps each login to different terms (Google account, unpaid key, paid key, Vertex), so the tier in use decides the data rules. — https://github.com/google-gemini/gemini-cli docs/resources/tos-privacy.md:34 (commit b25669d), read 2026-10-16, git clone — Quote: "Gemini Developer API Key | Gemini API - Unpaid Services"
- Supply-chain: LiteLLM compromise stole env vars, SSH keys, cloud credentials. — https://docs.litellm.ai/blog/security-update-march-2026, opened 2026-10-16, Exa search highlights — Quote: "Harvest secrets by scanning for:"
- Anthropic BAA scope excludes gateway-routed sessions. — https://code.claude.com/docs/en/legal-and-compliance, opened 2026-10-16, WebFetch — Quote: "Claude Code routed through a third-party cloud provider or a gateway aren't covered."

### Contradictions
- None found. (Code Assist for individuals privacy notice, which would cover the old free Google-login tier, was fetched but the page did not contain the training terms.)

### Inferences
Marking scheme (mine):
1. Every data directory or file carries a class: `public`, `internal`, `customer` (GTM PII), `health`. Store as a `DATA_CLASS.md` or frontmatter, and a small allow-list `model-routing.json` mapping class to permitted endpoints (e.g. `health: [anthropic]`, `customer: [anthropic, openai-api, gemini-paid]`, `public: all`).
2. The only route to another model is one wrapper (SDK tool or script). It takes file paths, looks up the class of each, refuses if any path is not allowed for that endpoint, and refuses unlabelled paths (default deny).
3. A PreToolUse hook denies direct `gemini`/`codex`/`agy`/`curl` to model hosts from Bash so the wrapper cannot be bypassed (hooks doc is in the registry; enforcement spike needed).
4. Free-tier keys are never put in the environment; use paid Gemini key only, so the unpaid-terms path does not exist.
5. Secrets: one key per vendor, in the wrapper's env or cloud network-secrets proxy; log vendor, class, bytes sent; rotate on a calendar.
6. Inconsistent outputs and debugging: store each external answer as a dated file with model id and prompt hash; treat as advice, never as a gate except review-with-fail-open.

### Gaps
- Whether a BAA or ZDR exists for OpenAI/Google endpoints for health data: not researched. Safest rule until John decides: health stays Claude-only.
- Gemini paid-tier "no training" is from the WebFetch summary of the terms page, not a clean verbatim quote.

## Recommendation, alternatives, rejections, spikes

Recommendation: keep Claude Code on its Max login with no gateway. Add `openai/codex-plugin-cc` for Codex reviews and a small own wrapper (Agent SDK in-process tool or a script) for Gemini via a paid key and for the data-class gate. Output to files only, read-only, one retry, fail-open.
Alternatives: PAL MCP `clink` (if a multi-model Swiss-army tool is wanted; stale since 2025-12-15); second-opinion MCP (single author); CCR for a separate API-key-billed experiment.
Rejected: LiteLLM as the front proxy (March 2026 compromise; also drops Max login; Anthropic unsupported for non-Claude); OpenRouter in front of Claude Code (vendor says non-Anthropic not guaranteed); Gemini CLI with free Google login (consumer serving ended 2026-06-18; free tier trains); OAuth-token reuse via third-party tools (Google terms and Anthropic terms).
Spike before building: (1) codex-plugin-cc review on a real John repo diff, compare against Claude's own review for 5 diffs; (2) the wrapper's refusal on an unlabelled path and a `health` path; (3) PreToolUse deny of direct vendor CLIs; (4) `agy --print` empty-output behaviour and paid-key Gemini CLI headless; (5) whether a hook-launched subprocess inherits only the intended env.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| openai/codex-plugin-cc | https://github.com/openai/codex-plugin-cc | Official Claude Code plugin: /codex:review, adversarial-review, rescue; Apache-2.0; commit db52e28 (2026-07-07); needs ChatGPT login or OpenAI key, Node 18.18+ | local, Claude Code plugin | 2026-10-16 | **Use** (Codex second opinion); spike on real diffs |
| Codex CLI (`codex exec`) | https://github.com/openai/codex | Headless agent, read-only sandbox default, --json/--output-schema; Apache-2.0; active 2026-10-16 | local | 2026-10-16 | Use via plugin or wrapper; API key per call only |
| Gemini CLI | https://github.com/google-gemini/gemini-cli | Apache-2.0 CLI, `-p` headless; consumer free/Pro/Ultra serving ended 2026-06-18, paid API keys still work; not optimised for Gemini 4 Argon | local | 2026-10-16 | Fallback, paid key only; never free tier |
| Antigravity CLI (agy) | https://antigravity.google/product/antigravity-cli | Gemini successor CLI (page not opened; from README banner and third-party plugins) | local | 2026-10-16 (README only) | Spike first; headless and terms unverified |
| PAL MCP (ex Zen) | https://github.com/BeehiveInnovations/pal-mcp-server | Apache-2.0 multi-model MCP with clink CLI bridge; last commit 2025-12-15 | local MCP | 2026-10-16 | Fallback/reference; stale 10 months, key in .env |
| claude-code-router | https://github.com/musistudio/claude-code-router | MIT local gateway for coding agents with fallback models; active 2026-10-10 | local | 2026-10-16 | Skip as front door (Anthropic does not support non-Claude via gateway; API billing); optional experiment |
| LiteLLM | https://github.com/BerriAI/litellm | LLM proxy; MIT outside enterprise/; active; PyPI 1.82.7/1.82.8 malicious 2026-03-24 | self-host | 2026-10-16 | Reject as front proxy; if ever used, official Docker image pinned |
| OpenRouter + Claude Code | https://openrouter.ai/docs/guides/guides/claude-code-integration | Env-var routing; vendor says only Anthropic 1P guaranteed | hosted | 2026-10-16 | Reject for non-Claude brains |
| Claude Agent SDK custom tools | https://code.claude.com/docs/en/agent-sdk/custom-tools | In-process MCP tool wrapper where the data-class gate lives | local/VM | 2026-10-16 | Use for the gate wrapper |
| noelweichbrodt/second-opinion | https://github.com/noelweichbrodt/second-opinion | MCP sending session context to Gemini/GPT, consensus mode | local MCP | 2026-10-16 (search excerpt) | Reference only; sends session files, unvetted |
| tokenpower/gemini-claude-plugin, LovelaceLoom/gemini-plugin-cc, Idun antigravity-plugin-cc | https://github.com/LovelaceLoom/gemini-plugin-cc | Third-party Gemini/agy review plugins | local | 2026-10-16 (search excerpt) | Reference for wrapper design; do not install unvetted |
