# Browser-automation tool landscape and benchmarks

Brief: Rank the current browser-automation options an autonomous Claude Code engineer could use to configure real web apps (Attio's builders, drag and drop, modals, Clay tables) with no human clicks.
Run: research/runs/engineer-browser/PLAN.md

Method note: Parallel Search was rate-limited ("Too Many Requests"); all reads used Exa (search + web_fetch_exa) and WebFetch. The GitHub API was blocked in this session ("GitHub access to this repository is not enabled"), so star counts, licences and contributors come from Exa's repo-metadata fetch, and release/last-commit dates were not obtained (see Gaps). Nothing was installed or run. Today is 2026-10-16.

## Q1 Tool comparison: what each is, DOM vs vision, licence, maturity, Claude Code hookup

### Takeaway
For a Claude Code engineer the strongest free, self-hosted stack is Playwright (library plus `@playwright/cli` skill or `@playwright/mcp`) as the DOM/accessibility-tree driver, with Claude's own vision (screenshot/coordinate actions) as a fallback for drag and drop. Stagehand, browser-use and Skyvern add an LLM-in-the-loop layer that Claude Code already is, so they matter mainly for caching/replay (Q3). Magnitude's browser agent is discontinued under that name. Claude in Chrome is fine for supervised use but is off under API-key/setup-token auth and needs a visible Chrome. Confidence: medium-high (maturity dates missing).

### Cited findings
- Playwright MCP (Microsoft): accessibility-snapshot driven, Apache-2.0, 38,194 stars, drives Claude Code via a standard MCP stdio config — https://github.com/microsoft/playwright-mcp, opened 2026-10-16, Exa web_fetch — Quote: "This server enables LLMs to interact with web pages through structured accessibility snapshots, bypassing the need for screenshots or visually-tuned models."
- Playwright MCP tool list includes native drag and drop, JS evaluate and a "run Playwright code" tool — https://playwright.dev/mcp/introduction, opened 2026-10-16, Exa search highlights of the page — Quote: "`browser_drag` | Drag and drop between elements"
- Playwright MCP keeps login state by default — same page — Quote: "Persistent sessions — login state and cookies preserved between sessions by default"
- Playwright CLI (`@playwright/cli`, Apache-2.0, 14,220 stars on the metadata page): installs skills that Claude Code uses; Microsoft itself recommends it over MCP for coding agents — https://github.com/microsoft/playwright-cli, opened 2026-10-16, Exa web_fetch — Quote: "Claude Code, GitHub Copilot and others will use the locally installed skills." and "playwright-cli install --skills"
- Microsoft's own framing of CLI vs MCP — https://github.com/microsoft/playwright-mcp — Quote: "MCP remains relevant for specialized agentic loops that benefit from persistent state, rich introspection, and iterative reasoning over page structure"
- Puppeteer: Apache-2.0 JS library, 95,697 stars, and its README now points to chrome-devtools-mcp as the MCP route — https://github.com/puppeteer/puppeteer, opened 2026-10-16, Exa web_fetch — Quote: "Install `chrome-devtools-mcp`, a Puppeteer-based MCP server for browser automation and debugging."
- Chrome DevTools MCP: Google-maintained, Apache-2.0, 53,561 stars, created 2025-09-11, Puppeteer-based, debugging/perf focus, CLI also provided, officially Chrome/Chrome for Testing only — https://github.com/ChromeDevTools/chrome-devtools-mcp, opened 2026-10-16, Exa web_fetch — Quote: "Uses puppeteer to automate actions in Chrome and automatically wait for action results."
- agent-browser (Vercel Labs): Apache-2.0, 44,026 stars, created 2026-01-11, native Rust CLI, accessibility snapshot with refs, installs Chrome for Testing, Linux deps flag — https://github.com/vercel-labs/agent-browser, opened 2026-10-16, Exa web_fetch — Quote: "agent-browser snapshot                    # Get accessibility tree with refs"
- browser-use: MIT, 118,157 stars, Python (and TypeScript) agent library plus paid Browser Use Cloud; offers a CLI skill installable into Claude Code — https://github.com/browser-use/browser-use, opened 2026-10-16, Exa web_fetch — Quote: "Install or upgrade browser-use to the latest stable version with uv using Python 3.12, run `browser-use skill install` to register the skill"
  - Page contains instructions addressed to agents; not followed. Quoted as data: "AI agents and crawlers: read browser-use.com/llms.txt for the product map" and the install prompt above.
- browser-harness (browser-use): MIT, lets Claude Code drive the user's real Chrome over CDP, exposes MCP over stdio — https://github.com/browser-use/browser-harness, opened 2026-10-16, Exa search page content — Quote: "`browser-harness-mcp` exposes the browser control helpers as MCP tools over stdio, so any MCP client (Claude Code, Devin, Cursor, etc.) can drive the browser"
  - Page contains instructions addressed to agents ("Paste one prompt into your coding agent to set it up"); not followed.
- Stagehand (Browserbase): MIT, 25,669 stars, TypeScript SDK (Python port also), `act/extract/observe`, `selfHeal` default true, local or Browserbase env — https://github.com/browserbase/stagehand, opened 2026-10-16, Exa web_fetch — Quote: "act() self-heals when the site redesigns its form"
- Stagehand options: `env: "LOCAL" | "BROWSERBASE"`, `selfHeal`, `cacheDir`, `serverCache` — https://docs.stagehand.dev/v3/references/stagehand, opened 2026-10-16, Exa search page content — Quote: "Enable self-healing mode where actions can recover from failures. Default: `true`"
- Skyvern: vision-LLM + Playwright SDK, 23,208 stars, licence is AGPL-3.0 (strong copyleft; matters only if hosted for others) — https://github.com/Skyvern-AI/skyvern, opened 2026-10-16, Exa web_fetch — Quote: "Skyvern relies on Vision LLMs to learn and interact with the websites."
- Skyvern cloud pricing: Free 5,000 credits, Hobby $29/mo, Pro $149/mo — https://www.skyvern.com/pricing/, opened 2026-10-16, Exa search page content — Quote: "Free (5,000 credits), Hobby ($29/mo), Pro ($ 149/mo), and Enterprise plans."
- Magnitude browser agent (vision-first, Apache-2.0, 4,134 stars) lives at magnitudedev/browser-agent; the name magnitudedev/magnitude is now an unrelated local-model inference engine created 2026-06-12 — https://github.com/magnitudedev/browser-agent and https://github.com/magnitudedev/magnitude, opened 2026-10-16, Exa web_fetch — Quote: "Magnitude is an open source inference engine that tunes its kernels on your hardware to find the fastest way to run each model."
- Magnitude's own claim and drag example (self-reported) — https://github.com/magnitudedev/browser-agent — Quote: "Magnitude is state-of-the-art, scoring 94% on WebVoyager!"
- Claude in Chrome: extension plus `claude --chrome`; visible Chrome, shares logins, pauses on login/CAPTCHA, needs a direct Anthropic plan, off with API key or setup-token — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "If you authenticate with an API key or a long-lived token from `claude setup-token`, Claude Code keeps Chrome integration off"
- Claude in Chrome pauses for humans — same page — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- Claude in Chrome blocked by JS dialogs — same page — Quote: "JavaScript dialogs block browser events and prevent Claude from receiving commands."
- New 2026 Anthropic API primitive: `browser_toolset_20260801` with accessibility-tree refs plus coordinates, `left_click_drag`, `left_mouse_down/up`, `zoom`; you supply the executor (not a ready tool for Claude Code) — https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool, opened 2026-10-16, Exa web_fetch — Quote: "Claude works with the page both through its structure (the accessibility tree, elements, forms, and tabs) and through screenshots and viewport coordinates."
- Same page: executor model — Quote: "Your application runs every call against its own browser automation; nothing runs on Anthropic's side."
- Computer use (desktop) toolset also exists and Anthropic points web-only tasks to the browser tool — https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool, opened 2026-10-16, Exa web_fetch — Quote: "For tasks that stay inside webpages, the browser use tool is the closer fit"

### Contradictions
- None found among the sources on tool capabilities. (Star counts are single-day snapshots from Exa metadata; GitHub API was unavailable to cross-check.)

### Inferences
- Claude Code is already the planning LLM, so a second LLM layer (Stagehand `act`, Skyvern, browser-use Agent) doubles model cost and adds a second decision-maker; use them only as replay/caching layers. (Mine; rests on the Stagehand, Skyvern and browser-use findings above.)
- The Anthropic `browser_toolset_20260801` shows the vendor's own design is hybrid (ref-addressed accessibility tree plus coordinate drag). That is the pattern to copy: refs by default, coordinates for drag. (Mine.)
- Ranking for this job: 1) Playwright via `@playwright/cli` skill (or MCP) with persistent profile; 2) Playwright MCP when snapshots in context help debugging; 3) Chrome DevTools MCP / agent-browser as alternates (agent-browser has fewer tools but is Rust-fast); 4) Claude in Chrome for supervised, logged-in one-offs; 5) Stagehand/Skyvern for replay; 6) browser-use for hosted stealth; Puppeteer subsumed by Chrome DevTools MCP; Magnitude rejected.

### Gaps
- Release cadence and last-commit dates per repo not obtained: GitHub API returned "GitHub access to this repository is not enabled for this session"; clone not attempted because the Exa metadata gave stars/licence and the verdict does not hinge on commit dates. Spike item.
- Whether Claude in Chrome can run on John's controlled environment unattended (headless, no display) is a session-persistence facet question; docs only say it uses a visible Chrome window.
- Magnitude: the sagekit/magnitude redirect surfaced only via a LibHunt snippet ("Discontinued ... Moved to"), not an opened page; treat browser-agent repo as stale pending check.

## Q2 Benchmarks and which approach wins on complex builders and drag and drop

### Takeaway
Headline benchmark scores are inflated and judge-dependent; on a component-level benchmark, accessibility-tree observation beats pixel-only by up to 34 points for the same model, but drag and drop is the one family where pixel/coordinate control beats DOM-level actions and every approach stays below about 60%. Complex multi-step enterprise workflows fall to roughly 10-20% for pixel agents in 2025 data. Plan for DOM/ref-first, coordinate drag as fallback, and a verify step after every drag. Confidence: medium (benchmarks are consumer sites or mock components, not Attio/Clay).

### Cited findings
- Online-Mind2Web showed over-optimism in earlier numbers — https://arxiv.org/html/2504.01382v4, opened 2026-10-16, Exa search page content — Quote: "Frontier web agents show a drastic drop in success rate when evaluated on Online-Mind2Web (human evaluation) compared with those reported on WebVoyager"
- Human-eval figures in that paper: Claude Computer Use 3.7 56.3%, Operator 61.3%, browser-use with GPT-4o 30.0% — same page — Quote: "Browser Use | $30.0$"; "Claude Computer Use 3.7 | $56.3$"
- Current Online-Mind2Web board (updated 2026-10-11) has self-reported 90%+ entries but warns about judges — https://leaderboard.steel.dev/leaderboards/online-mind2web/, opened 2026-10-16, Exa web_fetch — Quote: "Browser Use Cloud (bu-max)"; "97.0%"; "OpenAI's score uses a different screenshot-based judge — not directly comparable."
- Same board: harness result with generated browser code reaching 89.4% — Quote: "GPT-5.5 uses a terminal/filesystem harness and generated browser code, so this is a harness result rather than a GUI-only model score."
- Same board: Stagehand with Sonnet 4.5 scored 55.0% (Browserbase-reported, Mar 2026) — Quote: "Stagehand (Sonnet 4.5)"; "55.0%"
- HAL independent board: Browser-Use with Claude Sonnet 4 40.00%; SeeAct with GPT-5 42.33%; costs flagged as overstated 2x for some rows (Oct 5, 2026) — https://hal.cs.princeton.edu/online_mind2web, opened 2026-10-16, Exa search page content — Quote: "Nested trace spans counted the same API response twice, so affected models are inflated by exactly 2×."
- ComponentBench (Amazon AGI SF Lab/Duke, 2026): observation space changes success by 30+ points for the same model — https://arxiv.org/html/2608.18307, opened 2026-10-16, Exa web_fetch — Quote: "GPT-5 mini falls from 83.1% with accessibility-tree observations to 48.9% with coordinate-only Pixel control."
- ComponentBench on drag and drop: DOM-level browser-use actions lose, pixel wins — same page — Quote: "Browser-Use's DOM-level action surface cannot replicate genuine spatial drag operations on tasks like Kanban boards"
- ComponentBench: spatial manipulations stay hard for every agent — same page — Quote: "sliders, drag-and-drop lists, and splitters—remain below 60% mean pass rate across all agents tested."
- ComponentBench: drag/drop favours pixel, editors favour browser-use — same page — Quote: "Drag/Drop favors Pixel over Browser-Use, while Advanced Editors strongly favor Browser-Use."
- UI-CUBE (UiPath, 2025): pixel computer-use agents collapse on complex enterprise workflows — https://arxiv.org/html/2511.17131, opened 2026-10-16, Exa search page content — Quote: "Simple UI interactions achieve 67-85% success rates (compared to 97.9% human performance), but complex workflows drop precipitously to 9-19%."
- WebPageBench (Sep 2026): DOM harnesses beat screenshot-only on the same tasks; declared-done vs verified gap up to 41 points — https://arxiv.org/html/2609.35026, opened 2026-10-16, Exa search page content — Quote: "Qwen3.8-27B scores 0.737–0.763 through DOM harnesses and 0.480 through screenshots."
- Same page: agents over-report success — Quote: "the gap between what agents declare finished and what the log confirms reaches 41 points"
- Pixels vs structure disagreement: models trust stale structure over pixels — https://arxiv.org/html/2607.04334, opened 2026-10-16, Exa search page content — Quote: "on unedited stale snapshots from live pages the same models follow the outdated structure on up to $0.88$ of probes."
- Browser Use's own BU Bench V1 (100 hard tasks incl. iframes, drag-and-drop): LLM judge, claude-fable-5 80.0% at $580.87 per 100-task run, Claude Opus 4.6 62.0%, Sonnet 4.6 59.0% — https://browser-use.com/posts/ai-browser-agent-benchmark, opened 2026-10-16, Exa search page content — Quote: "Anthropic's claude-fable-5 set a new high score of 80.0% running on the open-source library"
- WebArena-Verified (812 tasks, self-hosted sites): top self-reported Pass@1 about 71% as of Sep 2026 — https://benchmarklist.com/benchmarks/webarena_verified/, opened 2026-10-16, Exa search page content — Quote: "A manually re-audited 812-task WebArena release covering six self-hosted web environments"; "Claude Opus 4.8 | 71.2% | Self-reported"

### Contradictions
- Online-Mind2Web 2025 paper says most agents get about 30% — https://arxiv.org/html/2504.01382v4; the Steel board lists 2026 self-reports of 88-97% — https://leaderboard.steel.dev/leaderboards/online-mind2web/. Different eras, models and judges (human vs custom agentic judge); the board itself says scores are not comparable. Settle by running a task set on John's own Attio/Clay with a state check.
- Browser Use's own board puts its cloud at 78% on its hard set; HAL's independent run of Browser-Use with Sonnet 4 is 40% on Online-Mind2Web — different benchmarks and models, not a direct conflict, but vendor numbers should not be trusted for planning.

### Inferences
- No benchmark covers Attio-style view/column builders or Clay tables; the closest are ComponentBench (component libraries incl. drag lists) and UI-CUBE (enterprise forms/modals). Combined message (mine): DOM/ref actions for everything except spatial gestures; use coordinate drag or Playwright `dragTo`/mouse steps for those and verify state afterwards.
- A frontier Claude in a ref-based Playwright loop is a reasonable choice; the vendor-reported leaderboards are not evidence that it beats alternatives on John's apps. A spike on 5-10 real Attio/Clay tasks is the only valid benchmark.

### Gaps
- No source found comparing tools specifically on Attio or Clay UIs.
- WebArena-Verified numbers are from third-party aggregators quoting model cards, not the paper; not independently verified.
- Mind2Web (original), BrowserGym/WorkArena leaderboards were not opened.

## Q3 Record once, replay deterministically

### Takeaway
Three routes exist: (a) Playwright's own Test Agents (planner, generator, healer) produce plain `.spec.ts` files from Claude Code, free and the most fit for this engineer; (b) Stagehand `cacheDir` replays cached `act`/agent actions with no LLM calls; (c) Skyvern explore/replay compiles runs to Playwright, and browser-use workflow-use records to JSON but is self-described early. Best fit: Claude Code explores once, writes a Playwright script with locators and a post-condition assertion, and reruns that script for free, calling Claude only on failure. Confidence: medium-high.

### Cited findings
- Playwright Test Agents; `init-agents --loop=claude` generates Claude Code agent definitions — https://playwright.dev/docs/test-agents, opened 2026-10-16, Exa web_fetch — Quote: "planner explores the app and produces a Markdown test plan"; "generator transforms the Markdown plan into the Playwright Test files"
- Healer repairs failures — same page — Quote: "Suggests a patch (e.g., locator update, wait adjustment, data fix)"
- Playwright CLI README: "Record and generate Playwright code" (repo description) — https://github.com/microsoft/playwright-cli, opened 2026-10-16, Exa web_fetch — Quote: "CLI for common Playwright actions. Record and generate Playwright code, inspect selectors and take screenshots."
- Stagehand local cache: first run uses LLM, later runs replay, committed cache is portable — https://docs.stagehand.dev/v3/best-practices/caching, opened 2026-10-16, Exa web_fetch / search highlights — Quote: "Stagehand saves every action and agent step to a local file on first run, then replays those cached actions on subsequent runs with no LLM calls"
- Stagehand cache clearing on site change; vendor speed claim — https://docs.stagehand.dev/v3/best-practices/deterministic-agent, opened 2026-10-16, Exa search page content — Quote: "If the website structure changes, clear the cache to force fresh exploration"; "Cached agent workflows run 10-100x faster"
- Stagehand server cache is Browserbase-hosted only, project-scoped, 48 hours — https://browserbase.com/blog/stagehand-caching/, opened 2026-10-16, Exa search page content — Quote: "cache entries are project-scoped (by Project ID), stored server-side on Browserbase, and valid for 48 hours."
- Skyvern explore/replay compiles to Playwright with LLM fallback; cost 0.11 to 0.04 per run, 2.7x cheaper — https://www.skyvern.com/blog/asking-ai-to-build-scrapers-should-be-easy-right/, opened 2026-10-16, Exa search page content — Quote: "Replay mode, it compiles those learnings into deterministic Playwright and runs fast and cheap, only falling back to the agent when something new or weird happens"
- Skyvern code-gen currently needs its server — same page — Quote: "It currently requires a Skyvern server running, but soon it will be the default behaviour."
- browser-use workflow-use: record, generate JSON workflow, run with no AI; fallback to agent; maintainers say not production-ready — https://github.com/browser-use/workflow-use/, opened 2026-10-16, Exa search page content — Quote: "This project is in very early development so we don't recommend using this in production."
- Self-healing in workflow-use still on its to-do list — same page — Quote: "Self healing, if it fails automatically agent kicks in and updates the workflow file"
- Browser Harness lets the agent write and keep its own helpers — https://browser-use.com/browser-harness, opened 2026-10-16, Exa search page content — Quote: "The agent adds what a site needs, uses it, and keeps it for next time."

### Contradictions
- None found. (Stagehand's "10-100x faster" and Skyvern's "2.7x cheaper" are vendor claims on their own examples and differ by an order of magnitude; not comparable.)

### Inferences
- For a one-user engineer, the generated Playwright script is the better artefact than a framework-specific cache: it is plain code, version-controlled, and needs no vendor server. Stagehand's local `cacheDir` is the nearest "no-code" equivalent but adds a second LLM (Stagehand model key) on cache misses. (Mine.)
- Caching works best on stable flows (create view with filters X) with variables for names; drag operations replay as the recorded mouse coordinates or `dragTo` locators and must be asserted after each run. (Mine.)

### Gaps
- Not verified: Playwright healer's reliability on drag/drop or canvas-like table UIs; needs a spike.
- Stagehand local-cache behaviour with `LOCAL` env and Claude model not tested; the docs snippets default to Browserbase.

## Q4 Token and speed cost: accessibility tree vs screenshots in Claude Code

### Takeaway
Accessibility-tree approaches are the text-cheap default, and in 2026 Playwright MCP and CLI converge because MCP now writes snapshots to disk; the real costs are fixed tool-schema overhead (MCP) versus extra tool calls (CLI). Dollar cost was roughly equal in one benchmark and MCP was twice as fast. No source with measured screenshot token cost per step was opened. Confidence: medium (small third-party benchmarks, one self-corrected).

### Cited findings
- Microsoft's own docs rate CLI cheaper — https://playwright.dev/agent-cli/introduction, opened 2026-10-16, Exa search page content — Quote: "Token cost | Lower — concise CLI output, skills loaded on demand | Higher — tool schemas + snapshots in context"
- A July 2026 re-benchmark found parity after MCP began writing snapshots to disk — https://dev.to/aswani25/playwright-cli-vs-playwright-mcp-which-should-you-use-with-claude-code-1olh, opened 2026-10-16, Exa search page content — Quote: "The ~4× token gap has essentially closed."
- Same page, fixed overhead — Quote: "MCP keeps its ~24 tool definitions (~18k characters) in the session's tool list the whole time, while the CLI reads a skill file once (~12.6k characters)"
- Earlier Feb 2026 figure now historical — https://www.test-lab.ai/blog/playwright-mcp-vs-cli-agentic-testing, opened 2026-10-16, Exa search page content — Quote: "One published comparison measured roughly 114,000 tokens with MCP versus 27,000 with CLI on the same flow."
- April 2026 benchmark: CLIs use half the context but MCP is faster and not costlier — https://outpost.ranger.net/post/the-hidden-cost-of-fewer-tokens/, opened 2026-10-16, Exa search page content — Quote: "The MCP case consistently took about half the time as the CLI. It also doesn't necessarily correlate to cost, and the MCP ended up slightly cheaper."
- Same page, mechanism — Quote: "the agents used dramatically more tool calls (2-3x) to accomplish the same goal with the CLIs."
- Same page, numbers — Quote: "the Playwright CLI and agent-browser average about 22k-24k tokens to complete scenario 1. The MCP requires 50k."
- Pixel observation also costs steps: pixel drops accuracy and efficiency — https://arxiv.org/html/2608.18307 — Quote: "GPT-5 mini Pixel passes 48.9% but only 19.0% within human steps"
- Claude in Chrome adds context when always on — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Enabling Chrome by default increases context usage since the browser tools and their instructions are always loaded."

### Contradictions
- Test-lab.ai (Feb 2026) says CLI wins by "4 to 10x fewer tokens" — https://www.test-lab.ai/blog/playwright-mcp-vs-cli-agentic-testing; the DEV post (updated 24 Jul 2026) says the gap closed after MCP moved snapshots to disk — https://dev.to/aswani25/playwright-cli-vs-playwright-mcp-which-should-you-use-with-claude-code-1olh; Outpost (Apr 2026) says CLI context is half but cost equal and speed worse. Different dates and versions (`@playwright/mcp@0.0.78`); settle by measuring on John's Attio flow with the installed versions.

### Inferences
- Pick on workflow: for a long unattended engineer, scoped `find`/ref reads (not full snapshots) matter more than transport; Attio tables and Clay grids are large trees, so cap with depth/ref reads. (Mine, from the 97,000-character page example and the 50,000-character cap in Anthropic's `read_page` spec.)

### Gaps
- No opened source gives screenshot token cost per step in Claude Code, or latency per step for Claude in Chrome. Anthropic image-token pricing page not opened.
- All token benchmarks are small, third-party, and on simple flows, not Attio/Clay.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Playwright CLI (@playwright/cli) | https://github.com/microsoft/playwright-cli | Token-efficient CLI plus skills for coding agents; ref-based snapshots to disk; codegen; Apache-2.0, 14.2k stars | local, npm global | 2026-10-16 | Use: primary driver for Claude Code |
| Playwright MCP (@playwright/mcp) | https://github.com/microsoft/playwright-mcp | Accessibility-snapshot MCP, 70+ tools incl. drag, persistent profile; Apache-2.0, 38.2k stars | local stdio MCP | 2026-10-16 | Use: alternate when in-context snapshots help; registry row exists, scope widened from "last resort research" to engineer driver |
| Playwright Test Agents | https://playwright.dev/docs/test-agents | planner/generator/healer producing .spec.ts; `init-agents --loop=claude` | local | 2026-10-16 | Use: record-once replay path |
| Puppeteer | https://github.com/puppeteer/puppeteer | Chrome/Firefox JS API, Apache-2.0, 95.7k stars | local | 2026-10-16 | Skip: subsumed by Playwright; reachable via chrome-devtools-mcp |
| Chrome DevTools MCP | https://github.com/ChromeDevTools/chrome-devtools-mcp | Google MCP + CLI over Puppeteer, traces, network, console; Apache-2.0, 53.6k stars | local | 2026-10-16 | Fallback: debugging/network inspection of Attio/Clay requests |
| agent-browser (Vercel Labs) | https://github.com/vercel-labs/agent-browser | Rust CLI, accessibility refs, Apache-2.0, 44k stars, created 2026-01 | local, npm/brew/cargo | 2026-10-16 | Fallback: alternate lightweight CLI; spike vs Playwright CLI |
| Stagehand | https://github.com/browserbase/stagehand | MIT TS SDK; act/extract/observe, self-heal, local `cacheDir` replay; 25.7k stars | local or Browserbase | 2026-10-16 | Fallback: replay cache if Playwright scripts prove brittle; needs its own LLM key |
| browser-use | https://github.com/browser-use/browser-use | MIT Python agent + CLI skill; paid cloud $0.02/browser-hour; 118k stars | local or cloud | 2026-10-16 | Skip as primary: second LLM loop; page has agent-addressed instructions (not followed) |
| browser-harness | https://github.com/browser-use/browser-harness | MIT; drives user's real Chrome over CDP, MCP over stdio, agent writes helpers | local | 2026-10-16 | Fallback: logged-in real-Chrome control; unvetted, spike first |
| workflow-use | https://github.com/browser-use/workflow-use/ | Record-to-JSON deterministic workflows with agent fallback; self-described early | local | 2026-10-16 | Skip: not production-ready per maintainers |
| Skyvern | https://github.com/Skyvern-AI/skyvern | Vision-LLM agent + Playwright SDK, explore/replay code-gen; AGPL-3.0; cloud Free/$29/$149 | local server or cloud | 2026-10-16 | Skip for now: AGPL, needs its server and own LLM; revisit for replay |
| Magnitude browser agent | https://github.com/magnitudedev/browser-agent | Vision-first TS agent, Apache-2.0, 4.1k stars; name now reused by an inference engine | local | 2026-10-16 | Reject: stale/redirected, self-reported 94% WebVoyager only |
| Claude in Chrome | https://code.claude.com/docs/en/chrome | Extension + `claude --chrome`, real logged-in visible Chrome, pauses on login/CAPTCHA | John's machine | 2026-10-16 | Fallback: supervised and one-off; unattended-safe not shown |
| Anthropic browser use tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool | API toolset `browser_toolset_20260801`, refs + coordinates, you write executor | Claude API | 2026-10-16 | Reference design only: copy hybrid ref/coordinate pattern |
| Anthropic computer use tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | `computer_toolset_20260801` desktop screenshots/mouse | Claude API, your VM | 2026-10-16 | Fallback for desktop (other facet) |
