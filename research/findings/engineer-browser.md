# Engineer browser: which browser and computer-control tooling lets an autonomous Claude Code engineer configure web apps that have no API, reliably and safely, and where that browser runs

**Summary.** Use the API or MCP route wherever one exists, and keep the browser for the parts that have none.
Attio's OpenAPI spec has only GET routes for views ("Lists saved views for an object", "Lists saved views for a
list") and no Workflows routes, while objects, attributes, select options and lists can be written
(https://api.attio.com/openapi/api). Clay "cannot create tables programmatically"
(https://github.com/clay-run/agent-plugins clay/skills/clay/SKILL.md:96 (commit b9952b6)), but agents "can read
and edit Workflows" through the Clay plugin (https://developers.clay.com/routines/workflows-alpha.md). n8n's
public API and environment variables cover nearly all settings, leaving OAuth consent clicks
(https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service.md). So the browser's job is
Attio views, Kanban and Workflows, Clay tables, columns, custom functions and custom signals, OAuth consent and
one-time developer-app sign-ups.

For that job the notes rank Playwright first, driven from Claude Code through either of two routes:
- the `@playwright/cli` skill, which "Claude Code ... will use"
  (https://github.com/microsoft/playwright-cli);
- the Playwright MCP server, which works "through structured accessibility snapshots" and has `browser_drag`
  (https://github.com/microsoft/playwright-mcp, https://playwright.dev/mcp/introduction).

Act through page structure (references to elements) by default and fall back to screen coordinates for drag
and drop. On ComponentBench, "GPT-5 mini falls from 83.1% with accessibility-tree observations to 48.9% with
coordinate-only Pixel control", but "Drag/Drop favors Pixel" and drag-and-drop tasks "remain below 60% mean
pass rate across all agents tested" (https://arxiv.org/html/2608.18307). Agents also over-report success: in
WebPageBench the worst harness pair (gpt-5.6-luna with openmanus) reports 1.00 completion against 0.59 log-verified
(EMS), a 41-point gap (https://arxiv.org/html/2609.35026) (corrected after hand check, 2026-10-16). Every write must therefore be checked by a separate read afterwards.

Record once and replay: Claude Code explores a flow, Playwright's generator turns the plan "into the Playwright
Test files", and a healer "Suggests a patch" when a run fails (https://playwright.dev/docs/test-agents). The
script then reruns without model calls, and Claude is called only when it fails (worker inference).

Where the browser runs: John's own Ubuntu VM, with headed Chrome using a dedicated, persistent `--user-data-dir`
profile on a virtual desktop. John logs in once through noVNC, "a HTML VNC client"
(https://github.com/novnc/noVNC). Persistent-profile mode is preferred because a saved storage-state file
misses sessionStorage and "you need to delete the stored state when it expires" (https://playwright.dev/docs/auth).
- Two-factor: TOTP codes can be generated from a vault (https://www.1password.dev/cli/secret-references).
- Google: Google refuses sign-in from browsers "controlled through software automation"
  (https://support.google.com/accounts/answer/7675428), so John logs in to Google by hand and the engineer
  never drives Google's login page.
- Hosted browsers: rejected for these logins because "cookies, and persistent profiles all live on someone
  else's infrastructure" (https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/).
- Stealth tools and CAPTCHA solvers: rejected. Cloudflare says automation frameworks "are not supported for
  solving production challenges"
  (https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/).

Safety rests on Claude Code's deny and ask rules and PreToolUse hooks on browser MCP tools
(https://code.claude.com/docs/en/hooks, https://code.claude.com/docs/en/permissions). Changes are made only
after checking the object does not already exist, never with blind retries ("unsafe around mutations")
(https://dev.to/harshithvaddiparthy/designing-browser-agents-that-dont-double-post-state-idempotency-and-verification-3be),
and money, deletion, sends, publishing and permission changes go to John for approval. Playwright MCP's own
origin list "is not a security boundary" (https://github.com/microsoft/playwright-mcp), and an issue reports
a browser agent that clicked Delete while "Accept Edits was ON"
(https://github.com/anthropics/claude-code/issues/65563).

General desktop control is not needed in v1. Claude Code's built-in computer use "is not available on Linux or
Windows" (https://code.claude.com/docs/en/computer-use), and Cua Driver (https://github.com/trycua/cua) is
the spiked, optional add-on.

Blood work: John downloads the PDF and the engineer parses it locally. The engineer does not log in to the lab
portal unattended, because Labcorp's agreement bans "robots, spiders, or scrapers, without our prior written
permission"
(https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement).

All claims rest on pages or clones the notes list as opened on 2026-10-16. Inferences are marked. Claims the
notes read only through Exa search highlights are labelled with that tool in the Evidence section.

## Questions and answers

### Q1. Which browser tools exist, how does each plug into Claude Code, and how do they rank?

**Confidence: medium-high** on the facts about each tool; **medium** on the ranking (release dates were not
obtained and nothing was run).

- **Playwright CLI** (`@playwright/cli`) installs skills that "Claude Code, GitHub Copilot and others will use"
  ("playwright-cli install --skills") (https://github.com/microsoft/playwright-cli). Microsoft's own docs rate its
  token cost "Lower — concise CLI output, skills loaded on demand" (https://playwright.dev/agent-cli/introduction).
- **Playwright MCP** lets LLMs "interact with web pages through structured accessibility snapshots, bypassing
  the need for screenshots" (https://github.com/microsoft/playwright-mcp). It has "`browser_drag` | Drag and
  drop between elements" and "Persistent sessions — login state and cookies preserved between sessions by
  default" (https://playwright.dev/mcp/introduction). Microsoft says "MCP remains relevant for specialized
  agentic loops that benefit from persistent state, rich introspection, and iterative reasoning over page
  structure" (https://github.com/microsoft/playwright-mcp).
- **Chrome DevTools MCP** "Uses puppeteer to automate actions in Chrome and automatically wait for action
  results" (https://github.com/ChromeDevTools/chrome-devtools-mcp). Puppeteer's own README now says "Install
  `chrome-devtools-mcp`, a Puppeteer-based MCP server" (https://github.com/puppeteer/puppeteer), so Puppeteer is
  reached through it.
- **agent-browser** (Vercel Labs) is a native CLI with "accessibility tree with refs"
  (https://github.com/vercel-labs/agent-browser).
- **browser-use** registers a skill via "`browser-use skill install`" (https://github.com/browser-use/browser-use).
  **browser-harness** exposes "browser control helpers as MCP tools over stdio, so any MCP client (Claude Code,
  Devin, Cursor, etc.) can drive the browser" (https://github.com/browser-use/browser-harness). Both pages hold
  instructions addressed to agents; the worker quoted them as data and did not follow them.
- **Stagehand** says "act() self-heals when the site redesigns its form" (https://github.com/browserbase/stagehand)
  and its self-heal option is "Default: `true`" (https://docs.stagehand.dev/v3/references/stagehand).
- **Skyvern** "relies on Vision LLMs" (https://github.com/Skyvern-AI/skyvern). Its cloud has "Free (5,000
  credits), Hobby ($29/mo), Pro ($ 149/mo)" (https://www.skyvern.com/pricing/). Worker inference (not in the
  source): its licence is AGPL-3.0.
- **Magnitude's** name now belongs to "an open source inference engine"
  (https://github.com/magnitudedev/magnitude). Its browser agent's "94% on WebVoyager" is self-reported
  (https://github.com/magnitudedev/browser-agent).
- **Claude in Chrome** works through an extension plus `claude --chrome`. It "pauses and asks you to handle it
  manually" at login or CAPTCHA, "JavaScript dialogs block browser events", and with API-key or setup-token
  auth "Claude Code keeps Chrome integration off" (https://code.claude.com/docs/en/chrome).
- **Anthropic's API browser tool** (`browser_toolset_20260801`) works "through its structure (the accessibility
  tree, elements, forms, and tabs) and through screenshots and viewport coordinates"; "nothing runs on
  Anthropic's side" (https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool). Anthropic
  also says "For tasks that stay inside webpages, the browser use tool is the closer fit"
  (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).

**Ranking (worker inference, tool-landscape note):**
1. Playwright through the `@playwright/cli` skill (or MCP), with a persistent profile.
2. Playwright MCP, when having snapshots in context helps debugging.
3. Chrome DevTools MCP or agent-browser as alternates.
4. Claude in Chrome for supervised, logged-in one-offs.
5. Stagehand or Skyvern for replay.
6. browser-use for hosted stealth.

Puppeteer is subsumed by Chrome DevTools MCP, and Magnitude is rejected.

Worker inference: Claude Code is already the planning model, so a second LLM layer (Stagehand `act`, Skyvern,
the browser-use Agent) doubles model cost and adds a second decision-maker. Anthropic's toolset is hybrid
(references plus coordinate drag), and that is the pattern to copy.

The sessions note names Playwright MCP in persistent-profile mode as the driver on the VM. The tool-landscape
note puts the CLI first. These are emphasis, not fact. Synthesis inference: use the MCP or CLI for
exploration and logins, and generated Playwright scripts for replay.

**Contradictions.** Two sources disagree on whether Playwright MCP keeps a profile by default:
- The Playwright MCP intro page says sessions are persistent "by default" (https://playwright.dev/mcp/introduction,
  read from Exa search highlights).
- The README option text says "If not specified, a temporary directory will be created" for the user data
  directory (https://github.com/microsoft/playwright-mcp, WebFetch).

The sessions note also flags as untested whether the profile "survives restarts of the MCP process". This is
unresolved: always pass an explicit `--user-data-dir` (sessions-note inference) and spike restart survival.

### Q2. What do benchmarks say, and what are their limits for builders and drag and drop?

**Confidence: medium.** No benchmark covers Attio- or Clay-style builders. Many scores are self-reported.

- **Headline scores are inflated.** Frontier agents "show a drastic drop in success rate when evaluated on
  Online-Mind2Web (human evaluation) compared with those reported on WebVoyager". On that paper's human
  evaluation, Browser Use scored 30.0 and Claude Computer Use 3.7 scored 56.3 (https://arxiv.org/html/2504.01382v4).
- **The 2026 Steel board lists self-reports up to 97.0%** but warns that one score "uses a different
  screenshot-based judge — not directly comparable" (https://leaderboard.steel.dev/leaderboards/online-mind2web/).
  The same board lists Stagehand (Sonnet 4.5) at 55.0%, and one 89.4% row is "a harness result rather than a
  GUI-only model score".
- **The independent HAL board** notes some cost rows "are inflated by exactly 2×"
  (https://hal.cs.princeton.edu/online_mind2web).
- **Observation space matters more than the tool.** On ComponentBench, GPT-5 mini fell from 83.1% with the
  accessibility tree to 48.9% with pixels. But "Browser-Use's DOM-level action surface cannot replicate genuine
  spatial drag operations on tasks like Kanban boards", drag and drop favours pixel control, and drag-and-drop
  lists stay "below 60% mean pass rate across all agents tested" (https://arxiv.org/html/2608.18307).
- **Enterprise workflows collapse.** On UI-CUBE, "Simple UI interactions achieve 67-85% success rates ... but
  complex workflows drop precipitously to 9-19%" (https://arxiv.org/html/2511.17131).
- **Agents over-claim and trust stale structure.** WebPageBench reports Qwen3.8-27B at 0.737–0.763 through DOM
  harnesses against 0.480 through screenshots (one model, one run per pair), and a 41-point gap between one
  harness's completion rate and its log-verified EMS (gpt-5.6-luna with openmanus, 1.00 vs 0.59)
  (https://arxiv.org/html/2609.35026) (corrected after hand check, 2026-10-16). Models "follow the outdated structure on up to $0.88$ of probes" on
  stale snapshots (https://arxiv.org/html/2607.04334).
- **Vendor and aggregator boards.** Browser Use's own board reports "claude-fable-5 set a new high score of
  80.0%" (https://browser-use.com/posts/ai-browser-agent-benchmark). WebArena-Verified lists "Claude Opus 4.8 |
  71.2% | Self-reported" (https://benchmarklist.com/benchmarks/webarena_verified/).
- **Desktop.** On OSWorld-Verified, "Claude Sonnet 5 | 81.2%" is self-reported in the system card
  (https://leaderboard.steel.dev/leaderboards/osworld/). The fetch tool paraphrased that row, so treat it as
  medium confidence. Worker inference: that is roughly one failure in five, so every step needs an outside
  check.

Worker inference: use structure-based (reference) actions for everything except spatial gestures. Use
coordinate drag or Playwright `dragTo` for those, and verify state afterwards. A 5-10 task spike on John's own
Attio and Clay is the only valid benchmark.

**Contradictions.** The 2025 Online-Mind2Web paper reports large drops, with Browser Use at 30.0
(https://arxiv.org/html/2504.01382v4). The 2026 Steel board lists self-reports up to 97.0%
(https://leaderboard.steel.dev/leaderboards/online-mind2web/). The eras, models and judges differ, and the board
itself says its scores are not comparable. The evidence favours treating the 2026 numbers as vendor claims;
settle it by running John's tasks with a state check.

Browser Use's own board (https://browser-use.com/posts/ai-browser-agent-benchmark) and HAL's independent run
(https://hal.cs.princeton.edu/online_mind2web) use different benchmarks and models, so they do not directly
conflict. Do not plan from vendor numbers.

### Q3. Can the engineer record a flow once and replay it deterministically?

**Confidence: medium-high.**

- **Playwright Test Agents** (best fit, free). The "planner explores the app and produces a Markdown test plan",
  the "generator transforms the Markdown plan into the Playwright Test files", and the healer "Suggests a patch
  (e.g., locator update, wait adjustment, data fix)". `init-agents --loop=claude` targets Claude Code
  (https://playwright.dev/docs/test-agents). The Playwright CLI also does "Record and generate Playwright code"
  (https://github.com/microsoft/playwright-cli).
- **Stagehand local cache.** It "saves every action and agent step to a local file on first run, then replays
  those cached actions on subsequent runs with no LLM calls"
  (https://docs.stagehand.dev/v3/best-practices/caching). "If the website structure changes, clear the cache".
  Its claim "Cached agent workflows run 10-100x faster" is a vendor claim
  (https://docs.stagehand.dev/v3/best-practices/deterministic-agent).
- **Stagehand server cache.** Cache entries are "stored server-side on Browserbase, and valid for 48 hours"
  (https://browserbase.com/blog/stagehand-caching/).
- **Skyvern.** Replay "compiles those learnings into deterministic Playwright", but "It currently requires a
  Skyvern server running" (https://www.skyvern.com/blog/asking-ai-to-build-scrapers-should-be-easy-right/).
- **browser-use workflow-use.** The maintainers say: "we don't recommend using this in production". Self-healing
  is still a to-do (https://github.com/browser-use/workflow-use/).
- **Browser Harness** lets the agent keep its own site helpers "for next time"
  (https://browser-use.com/browser-harness).

Worker inference: a generated Playwright script is a better artefact than a framework cache. It is plain,
version-controlled code that needs no vendor server. Drag steps replay as `dragTo` locators or recorded mouse
steps and must be asserted after each run. The healer's reliability on drag and drop and on table UIs is
unverified (spike).

**Contradictions.** None on facts. The vendor speed and cost claims (Stagehand 10-100x, Skyvern's figure)
measure different things and are not comparable.

### Q4. What does each approach cost in tokens and speed inside Claude Code?

**Confidence: medium** (small third-party benchmarks).

- **Accessibility-tree tools are the text-cheap default.** Microsoft rates the CLI "Lower" and MCP "Higher —
  tool schemas + snapshots in context" (https://playwright.dev/agent-cli/introduction).
- **The gap may have closed.** A July 2026 re-benchmark says "The ~4× token gap has essentially closed". MCP
  still keeps "~24 tool definitions (~18k characters)" loaded the whole session
  (https://dev.to/aswani25/playwright-cli-vs-playwright-mcp-which-should-you-use-with-claude-code-1olh).
- **CLI uses less context but more calls.** An April 2026 benchmark found the CLI and agent-browser "average
  about 22k-24k tokens" against 50k for MCP. But MCP "took about half the time" and was "slightly cheaper",
  because CLI agents "used dramatically more tool calls (2-3x)"
  (https://outpost.ranger.net/post/the-hidden-cost-of-fewer-tokens/).
- **Screenshots.** Each screenshot costs "roughly 1,000–1,800 input tokens"
  (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool). Pixel control also passed
  "only 19.0% within human steps" (https://arxiv.org/html/2608.18307).
- **Claude in Chrome.** Turning Chrome on by default "increases context usage"
  (https://code.claude.com/docs/en/chrome).

Worker inference: Attio tables and Clay grids are large trees, so cap reads by depth or by element reference
rather than taking full snapshots.

**Contradictions.** The sources disagree on the size of the CLI's token advantage:
- February 2026: "roughly 114,000 tokens with MCP versus 27,000 with CLI"
  (https://www.test-lab.ai/blog/playwright-mcp-vs-cli-agentic-testing).
- July 2026: the gap "has essentially closed"
  (https://dev.to/aswani25/playwright-cli-vs-playwright-mcp-which-should-you-use-with-claude-code-1olh).
- April 2026: half the context but equal cost and slower
  (https://outpost.ranger.net/post/the-hidden-cost-of-fewer-tokens/).

The dates and versions differ, and the newer sources favour near-parity. This is unresolved for John's flows:
measure on the installed versions.

### Q5. Is full-machine control needed, and which option?

**Confidence: high** on the docs, **medium** on the task split.

**Not for the core job.**
- Anthropic's order of preference keeps screen control for "things nothing else can reach: native apps,
  simulators such as the iOS Simulator, and tools without an API"
  (https://code.claude.com/docs/en/computer-use).
- Built-in CLI computer use "is a research preview on macOS that requires a Pro or Max plan ... It requires an
  interactive session". It "is not available on Linux or Windows", runs "on your actual desktop", and gives
  "Per-app approval" (https://code.claude.com/docs/en/computer-use). It is also "not available in
  non-interactive mode with the `-p` flag" (https://code.claude.com/docs/en/computer-use).
- In the Desktop app, browsers are "View only" (https://code.claude.com/docs/en/desktop).
- The API toolset is generally available as `computer_toolset_20260801`
  (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool). Anthropic advises "a
  dedicated virtual machine or container with minimal privileges" and admits "Claude will follow commands found
  in content even when they conflict with your instructions" (same page).

**OpenClaw cannot lend its tools to Claude Code.** Its `computer` tool exists
(https://github.com/openclaw/openclaw docs/nodes/computer-use.md:11 (commit 58d7e878)), and Linux support is
"experimental" (docs/nodes/computer-use.md:21). But `openclaw mcp serve` only exposes "Gateway-backed
conversations" (docs/cli/mcp.md:25). Its security posture is already recorded in
research/findings/engineer-runtime.md (Q6, lines 340-390).

**Cua is the plug-in candidate.** It gives agents "tools to inspect and operate native desktop apps and
browsers on macOS, Windows, and Linux", installs "the cua MCP server into your AI coding agents (Claude Code
...)", and "Everything outside Cua Spaces and Cua Driver Bench is MIT-licensed". It warns against its own old
npm package: "Do not run it" (https://github.com/trycua/cua).

**Other options:**
- E2B Desktop is "an open source secure virtual desktop ready for Computer Use" (https://github.com/e2b-dev/desktop).
- Bytebot "was archived by the owner on Mar 7, 2026" (https://github.com/bytebot-ai/bytebot).
- UI-TARS Desktop is a separate Apache-2.0 agent (https://github.com/bytedance/UI-TARS-desktop).

Worker inference, task buckets:
- Desktop control: only for Withings or WHOOP phone pairing, Android emulator UI, operating-system prompts and
  native file dialogs.
- Android builds: Gradle and adb cover building and installing.

Recommendation (computer-control note): no general desktop control in v1; Cua Driver MCP is an optional,
spiked add-on in a disposable Linux VM with a protected-path hook. A Claude Code subagent ran `rm -rf` on a
home folder, and the issue says there is "no reliable way to stop it once started"
(https://github.com/anthropics/claude-code/issues/99198).

**Contradictions.** None among opened sources. A conflicting OSWorld figure for Sonnet 5.5 and Opus 5.5 was
seen only in a search result (see Open questions).

### Q6. How are logged-in sessions and two-factor kept for weeks?

**Confidence: medium-high** on the mechanics, **low** on session lifetimes.

**Persistent profile versus storage state:**
- Playwright MCP's `--storage-state` is a "path to the storage state file for isolated sessions"; extension
  mode can "Connect to a running browser instance (Edge/Chrome only)"; the headless idle timeout "Defaults to
  one hour for headless browsers, never for headed ones" (https://github.com/microsoft/playwright-mcp).
- Storage state "covers cookies, local storage, IndexedDB and passkey (WebAuthn) based authentication". "You
  need to delete the stored state when it expires", and Playwright "strongly discourage[s] checking them into
  private or public repositories" (https://playwright.dev/docs/auth).
- Playwright does not support automating Chrome's default profile: "automating the default Chrome user profile
  is not supported" (https://playwright.dev/docs/api/class-browsertype). Chrome ignores remote-debugging
  switches on the default data directory (https://developer.chrome.com/blog/remote-debugging-port). Worker
  inference (not in the source): this applies from Chrome 136.
- Claude in Chrome's "service worker can go idle during extended sessions, which breaks the connection"
  (https://code.claude.com/docs/en/chrome).

**Two-factor:**
- TOTP is the factor that can be automated. 1Password secret references can get a field `attribute` such as the
  OTP (https://www.1password.dev/cli/secret-references), and `op item get --otp` exists
  (https://1password.com/blog/1password-cli-2-0).
- Service accounts "have hourly and daily limits"
  (https://www.1password.dev/service-accounts/use-with-1password-cli).
- The Bitwarden Secrets Manager CLI page documents machine-account tokens, not TOTP
  (https://bitwarden.com/help/secrets-manager-cli/).
- The seed is "a long-lived credential"
  (https://github.com/feder-cr/invisible_playwright/wiki/automating-totp-2fa-login-playwright, third-party wiki).
  One Google-login project reports "Currently only TOTP works reliably"
  (https://github.com/blhutchings/google-login-service).

**Google:**
- Google refuses browsers that "Are being controlled through software automation rather than a human" or "Are
  embedded in a different application" (https://support.google.com/accounts/answer/7675428).
- A testing vendor advises "Do not automate personal Google accounts"
  (https://docs.stably.ai/use-cases/testing-google-auth-and-2fa).

Worker inference (sessions note), the design:
1. A headed persistent profile, logged in once by John, including Google with his own two-factor.
2. A per-site "logged-in" check at task start.
3. TOTP from a host-side wrapper that returns only the code, so the seed never reaches the model.
4. Email codes possibly through the Gmail connector (not independently sourced).
5. SMS and push codes go to John.

**Contradictions.** The two notes disagree on persistent profile versus storage state:
- The reliability note's inference suggests "a separate Playwright-driven profile with a saved storage state"
  for unattended runs.
- The sessions note prefers the persistent profile. Storage state misses sessionStorage and must be deleted
  when it expires (https://playwright.dev/docs/auth), and `--storage-state` applies only to isolated sessions
  (https://github.com/microsoft/playwright-mcp).

The evidence favours the persistent profile: both cited lines point that way, and the reliability note gave no
source for storage state.

### Q7. What about bot detection and the apps' terms?

**Confidence: medium.** These are vendor docs, not a measured test, and the legal reading is not advice.

**Bot detection:**
- Cloudflare's JavaScript detections catch "headless browsers (browsers controlled by software, with no
  visible window or human operator)" (https://developers.cloudflare.com/bots/concepts/bot-score/).
- Its ML engine uses "headers, session characteristics, and browser signals"
  (https://developers.cloudflare.com/bots/concepts/bot-detection-engines/).
- "Browser automation frameworks, such as Selenium, Puppeteer, Playwright, and Cypress, are not supported for
  solving production challenges"
  (https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/).
- Cloudflare's own browser signs requests with Web Bot Auth
  (https://developers.cloudflare.com/browser-run/reference/automatic-request-headers/).
- This project's registry already records headless Playwright MCP "blocked by Cloudflare/Vercel bot checks"
  (research/tool-registry.md, Playwright MCP row).
- Hosted vendors sell "Stealth mode, residential proxies, CAPTCHA solving"
  (https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/).

Worker inference: the legitimate posture is a real headed Chrome, a stable profile, a stable IP (move the VM
or its exit node to John's home network if challenged, unsourced), human logins, and stop-and-ask on any
CAPTCHA. Stealth plugins, fingerprint spoofing, CAPTCHA solvers and rotating proxies are rejected as evasion.

**Terms.** None of the opened terms bans a logged-in customer's own UI automation by name. All of them put
credentials on the customer:
- Attio: "responsible for ensuring the security and confidentiality of all log-on identifiers"; no
  "circumvent any express or implied limitations on use ... including ... the number of calls to the Attio
  API"; no "permit or facilitate any third party to access or use"
  (https://attio.com/legal/terms-and-conditions). Its acceptable-use policy bans circumventing "security or
  access controls" (https://attio.com/legal/acceptable-use).
- Clay: "solely responsible for ... username and password"; "not to license, sell, or transfer your account"
  (https://www.clay.com/terms-of-service, first 8,000 characters only). Clay's blog calls CAPTCHA solvers and
  IP rotation "not recommended" (https://www.clay.com/blog/websites-that-allow-web-scraping).
- Outreach: "not to provide your password to any third party"; it may "suspend or terminate the Services ...
  with or without cause" (https://www.outreach.ai/terms). Its acceptable-use policy targets email practices
  (https://www.outreach.ai/acceptable-use-policy).
- Labcorp (blood work): see Q12.

Worker inference: the engine acts as John, with John's session on John's VM, and never holds his password
as a separate party. The company Outreach account needs the employer's approval first, with the API preferred.

**Contradictions.** A "spiders, crawlers, or scrapers" clause was found at outreach.as/terms, which refers to
"Resonate", a different company. It was read only through search highlights. https://www.outreach.ai/terms
(opened) shows no such clause. The evidence favours outreach.ai as Outreach's terms. John's signed contract is
not public (Open questions).

### Q8. Where should the browser run?

**Confidence: medium.**

**Recommendation (sessions note):** John's Ubuntu VM, running headed Chrome with a dedicated persistent profile
on a virtual X display. John watches and logs in through noVNC, "a HTML VNC client JavaScript library and an
application" (https://github.com/novnc/noVNC), reached over a private network. Worker inference (not in the
source): Xvfb plus x11vnc bound to localhost, with Tailscale or an SSH tunnel; never expose VNC publicly.

This matches the runtime decision in research/findings/engineer-runtime.md (Q7: "a dedicated persistent
Chromium profile for logins", pattern https://github.com/browser-use/bux).

**Hosted browsers (Browserbase, Steel, Anchor, Hyperbrowser):**
- They persist logins, but "recordings, cookies, and persistent profiles all live on someone else's
  infrastructure" (https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/).
- Browserbase: "Every plan scales past its included usage" (https://www.browserbase.com/pricing). Worker
  inference (not in the source): Free 15-minute sessions; $20/month and $99/month plans; $0.12 and $0.10 per
  extra hour.
- "self-hosted Steel runs one session at a time and has no CAPTCHA solving or Credentials API"
  (https://indexagentica.com/compare/cloud-browsers-for-agents.md).
- "Steel lists 15 minutes (Launch), 1 hour (Scale), and up to 24 hours (Enterprise)" as session caps, and
  "Anchor re-authenticates automatically" (https://llms.anchorbrowser.io/anchor-browser-vs-steel). This is a
  vendor-authored comparison.

Rejected for John's logins and health data (worker inference).

**John's own Chrome (Claude in Chrome or Playwright extension mode):** best IP and device trust, but it is not
unattended. Chrome integration needs subscription auth, "the browser extension can't authenticate with those
credentials", and it "isn't supported in Windows Subsystem for Linux (WSL)". "Your Business Associate
Agreement (BAA) with Anthropic doesn't cover data sent to third-party sites through Claude in Chrome"
(https://code.claude.com/docs/en/chrome).

**Computer use** is macOS-only in the CLI and interactive only (https://code.claude.com/docs/en/computer-use),
so it is not a login path.

**Contradictions.** None on facts. Hyperbrowser and Browserless prices were not read from primary pages.

### Q9. Which reliability patterns make UI changes dependable?

**Confidence: medium-high** on the patterns; **medium** on applying them to Attio and Clay.

- **Waits and traces.** Playwright "auto-waits for all the relevant checks to pass and only then performs the
  requested action" (https://playwright.dev/docs/actionability). Traces are recorded "on first retry of each
  test" (https://playwright.dev/docs/trace-viewer-intro).
- **Stagehand fallback.** "If the recorded selector no longer resolves, Stagehand falls back to full inference"
  (https://docs.stagehand.dev/v4/best-practices/caching).
- **Idempotency.** Retries "are unsafe around mutations unless the destination supports a genuine idempotency
  token". An ambiguous state "means the system attempted a mutation but could not prove whether the external
  effect occurred". The agent must "refuse to guess when an external effect is at stake"
  (https://dev.to/harshithvaddiparthy/designing-browser-agents-that-dont-double-post-state-idempotency-and-verification-3be).
- **Verify through the API.** Attio's API reads "view titles" (research/tool-registry.md:122) and the registry
  notes "no view or workflow tool" (research/tool-registry.md:123). View filters and sorts are not in the
  53-path spec (https://api.attio.com/openapi/api), so checking view configuration is itself a browser read. Clay
  tables are "Enterprise only" (research/tool-registry.md:124) and have no list endpoint
  (https://developers.clay.com/tables.md).
- **Drift is ongoing.** "81.7% of repaired tests break again within six months". LLMs "can successfully repair
  a substantial portion" with diagnostic context (https://kdyao.github.io/resources/papers/ASE2025_Haonan.pdf).
  Checkly runs Playwright visual checks "against production, 24x7"
  (https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/).

Worker inference:
- One recorded Playwright script per flow, regenerated when it fails.
- Retry only observation steps.
- Check before create: for Attio, list view titles first.
- After each action, verify through the API or a fresh UI read plus screenshot.
- A nightly read-only smoke run with traces, self-hosted by cron.
- Clay UI writes are verified only by re-reading the UI.

**Contradictions.** Stagehand v4's act docs (https://docs.stagehand.dev/v4/basics/act, search highlight only)
say the cache needs a Browserbase browser and does nothing locally. The v3 docs show a local `cacheDir`
(https://docs.stagehand.dev/v3/best-practices/caching, opened). Neither act page was fully opened. Unresolved:
check the installed version before relying on local caching (Open questions).

### Q10. Which guardrails exist natively, what must be built, and which actions always need John's approval?

**Confidence: high** on the features, **medium** on how well they work.

**Native in Claude in Chrome:**
- It "shares your browser's login state". "Site-level permissions are inherited from the Chrome extension",
  and "a repository you check out must not be able to connect Claude to your browser"
  (https://code.claude.com/docs/en/chrome).
- The August 2026 GA post: "If the action doesn't match your request, it's blocked"
  (https://claude.com/resources/articles/claude-in-chrome-generally-available).
- The help centre advises "a separate browser profile without access to sensitive accounts" and offers
  "Manually approve" (https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely).
- Anthropic: "A 1% attack success rate ... still represents meaningful risk"
  (https://www.anthropic.com/research/prompt-injection-defenses).

**Native in Claude Code:**
- "Rules are evaluated in order: deny, then ask, then allow", and "Claude Code evaluates deny and ask rules
  regardless of what a PreToolUse hook returns" (https://code.claude.com/docs/en/permissions).
- Hooks match whole MCP servers by appending `.*`, and "A timed-out `command`, `http`, or `mcp_tool` hook
  doesn't block the tool call" unless set to block (https://code.claude.com/docs/en/hooks).
- Auto mode blocks things like "Mass deletion on cloud storage" (shell and infrastructure, not browser clicks).
  In `-p` runs, "Claude Code doesn't stop the run" on repeated blocks. "`bypassPermissions` offers no
  protection against prompt injection" (https://code.claude.com/docs/en/permission-modes).

**Limits and incidents:**
- "Playwright MCP is not a security boundary" (https://github.com/microsoft/playwright-mcp).
- Willison: avoid private data, untrusted content and external communication together ("avoid that lethal
  trifecta combination entirely") (https://simonwillison.net/2025/jun/16/the-lethal-trifecta/).
- OpenAI: "prompt injection remains an open challenge", across "an effectively unbounded surface area"
  (https://openai.com/index/hardening-atlas-against-prompt-injection/).
- A reporter says a browser agent deleted a production record with "Accept Edits was ON" (the issue was closed
  as not planned; this is the reporter's claim) (https://github.com/anthropics/claude-code/issues/65563).
- Approvals can be relayed by phone through Remote Control and Channels (research/tool-registry.md:54,56).

**Must build (worker inference):**
- A PreToolUse hook that denies or asks on click and type targets matching delete, send, pay, publish or
  submit (spike the real `tool_input` fields).
- A domain-allowlist hook on navigation.
- A dedicated engineer profile.
- A read-only recon mode, an action receipt log, and a stop on credential or state mismatch enforced by the
  supervisor, because `-p` does not halt on blocks.

**Never without John's approval (worker inference):**
1. Money: checkout, plan changes, credits, seats, paid Clay enrichment runs, auto-recharge.
2. Deletion or irreversible change: deleting, archiving, merging or bulk-updating records, views, columns,
   tables, sequences, workflows, workspaces or integrations; revoking keys.
3. App-store submission, pricing or release.
4. Outbound actions: email, Outreach sequence activation or enrolment, publishing, posting, inviting users.
5. Credentials and permissions: API keys, OAuth grants, sharing, roles.
6. Anything on banking, healthcare or government domains, or in password managers.

Additive, reversible edits (create a view, add a column) may proceed with the receipt-and-verify pattern.

**Contradictions.** The reliability note lists vendor attack-success figures from different dates and models:
Aug 2025 (search highlight only), the help centre and the GA post. They come from vendor-internal evaluations
and the note carries no quotes for them, so they are not compared here (Open questions).

### Q11. Per task: API or MCP versus browser

**Confidence: high** for the Attio spec reading and the Clay docs; **medium** for the Attio MCP (docs page, not a
live tools/list), n8n (master branch) and Outreach.

In the "Human step" column, entries without their own source are worker inference.

| Task | API or MCP path | Browser needed | Human step | Source |
| --- | --- | --- | --- | --- |
| Attio: create/update objects | REST POST/PATCH ("Creates a new custom object") | no | API key once | https://api.attio.com/openapi/api |
| Attio: attributes, select options, statuses, relationships | REST ("optionally create a bidirectional relationship"; "Adds a select option") | no | none | https://api.attio.com/openapi/api |
| Attio: lists, list attributes | REST POST /v2/lists ("Creates a new list"), no DELETE list route; MCP `create-list` | no | none | https://api.attio.com/openapi/api; https://docs.attio.com/changelog/mcp.md |
| Attio: views (table, Kanban), filters, sorts, grouping | GET only ("Lists saved views for an object/list") | **yes** | maybe | https://api.attio.com/openapi/api |
| Attio: Workflows build/edit | none; run by "Webhook received" trigger once built | **yes** | none | https://attio.com/help/reference/automations/workflows/workflows-block-library |
| Attio: App SDK app | Developer console sign-in, then SDK adds Workflow blocks | **yes** (console) | admin approval unknown | https://docs.attio.com/sdk/guides/creating-an-app.md; https://docs.attio.com/sdk/overview.md |
| Clay: search, run functions, Workflows (Alpha) | Clay plugin/CLI, Public API, MCP | first CLI sign-in only ("Sign-in opens a browser") | authorise CLI once | https://developers.clay.com/routines/workflows-alpha.md; https://developers.clay.com/quickstart.md |
| Clay: create tables, columns, enrichment columns, sources | none ("you **cannot** create tables programmatically") | **yes** | none | https://github.com/clay-run/agent-plugins clay/skills/clay/SKILL.md:96 (commit b9952b6) |
| Clay: read table rows | Enterprise-only query; "does not include a list-tables endpoint" | no | table ids | https://developers.clay.com/tables.md |
| Clay: custom functions; custom and web-intent signals | build in UI; API/MCP toggle in UI | **yes** | none | https://developers.clay.com/routines/custom-functions.md; https://developers.clay.com/signals.md |
| n8n: workflows, credentials, tags, variables, projects, executions | public API / CLI / MCP (credential create route) | no | create API key | https://docs.n8n.io/connect/n8n-api.md; https://github.com/n8n-io/n8n packages/cli/src/public-api/v1/handlers/ (commit 21221ad) |
| n8n: owner setup | env vars "from n8n 2.17.0" (self-hosted) | Cloud: yes (worker inference) | none | https://docs.n8n.io/deploy/host-n8n/configure-n8n/manage-settings-using-environment-variables.md |
| n8n: community node install | API route (self-hosted; Cloud unverified) or UI by owner/admin | Cloud: probably | owner/admin | https://github.com/n8n-io/n8n .../installPackage.generated.yml:5 (commit 21221ad); https://docs.n8n.io/integrations/community-nodes/installation-and-management/install-verified-community-nodes.md |
| n8n: OAuth credential connect | none ("select **Sign in with Google**") | **yes** | consent click | https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service.md |
| Outreach: sequences, templates, mailboxes | REST create/update; MCP `sequence_create`; "Permissions inherit from the user" | no | create app, authorise; employer approval | https://developers.outreach.io/api/reference/sequence.md; https://developers.outreach.io/mcp-server/authentication |
| WHOOP / Withings: developer app | dashboard / Partner Hub | **yes** | register, consent per account | https://developer.whoop.com/docs/developing/getting-started; https://developer.withings.com/developer-guide/v3/get-access/sign-up-for-a-developer-account |
| WHOOP / Withings: data pull | REST with refresh token ("request the offline scope"; "30 seconds to exchange") | no | none after consent | https://developer.whoop.com/docs/developing/oauth; https://developer.withings.com/developer-guide/v3/integration-guide/public-health-data-api/get-access/oauth-web-flow |
| Blood-work portals (Labcorp, Quest/MyQuest, Function) | no personal API found; PDF download; Quest feeds Apple Health | **no unattended browser** (Labcorp terms) | John signs in and downloads | Q12 |

Other details:
- Attio rate limits: "100 requests per second" read and "25 requests per second" write
  (https://docs.attio.com/rest-api/guides/rate-limiting.md).
- The Attio MCP's "write operations request confirmation" (https://docs.attio.com/mcp/overview.md).
- "Only workspace admins can grant a workspace-level token" (https://docs.attio.com/rest-api/guides/authentication.md).
- The n8n API "isn't available on the free trial" (https://docs.n8n.io/connect/n8n-api.md).
- Withings accounts created after the change "will need a membership to share health data with a free-plan
  app" (https://developer.withings.com/developer-guide/v3/get-access/sign-up-for-a-developer-account).

Worker inference: the engineer builds the whole Attio data model through REST. The browser's Attio job is
views and Workflow construction, and verifying a view's configuration is itself a browser read.

**Contradictions.** None found.

### Q12. What is the route for blood work?

**Confidence: medium.**

**No lab gives John a personal API:**
- Labcorp offers the "Official Report", which downloads "typically as a PDF"
  (https://patient.labcorp.com/help-center/q-and-a/3000/2).
- Quest offers "integrated results through Apple Health" (https://www.questdiagnostics.com/patients/test-results).
- Function lets members "download them as a PDF" and draws its labs at Quest
  (https://www.functionhealth.com/faq).

**Epic:**
- "no special relationship is required to develop or deploy an app"
  (https://open.epic.com/DeveloperResources).
- But "There is no central Epic endpoint", so connections are made per health system (same page).
- Its sandbox must hold no "individually identifiable information"
  (https://fhir.epic.com/Documentation?docId=patientfacingfhirapps).

**Android Health Connect:** its medical-records Play Policy "is still being developed"
(https://developer.android.com/health-and-fitness/health-connect/medical-records).

**Aggregators:**
- Fasten OnPrem "is not able to import data from healthcare providers directly" and is "Status: ARCHIVED"
  (https://github.com/fastenhealth/fasten-onprem/).
- Fasten's TEFCA route has "additional fees" (https://docs.connect.fastenhealth.com/guides/tefca-ias).
- Flexpa live access starts with a demo request ("Start at flexpa.com/demo")
  (https://www.flexpa.com/docs/guides/getting-started). Its price and the claim that it has no free live plan
  were seen only in search highlights (Open questions).

**Terms:** Labcorp bans "any automated means ... including robots, spiders, or scrapers, without our prior
written permission" and "credential stuffing", but allows "a single copy of Content for your personal,
non-commercial, informational use"
(https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement).

Recommendation (gap note, worker inference):
1. John downloads the PDF to a gitignored inbox, and the engineer builds and tests a local parser on synthetic
   PDFs.
2. If John has an iPhone, an Apple Health export dropped in the same inbox. The export-format source was seen
   only in a search highlight; spike it.
3. An Epic SMART app only if his results sit in a MyChart system and he wants automation.
4. Aggregators and unattended portal logins rejected.

A persistent logged-in medical profile on the VM is a standing PHI credential that a prompt-injected page
could drive (worker inference).

**Contradictions.**
- The computer-control note's task buckets (inference) list "the blood-work portal (login, MFA, download of
  PDFs)" as a browser task. The sessions note says the portal stays "human-in-the-loop". The portals note,
  citing Labcorp's agreement (URL above), rules out unattended login. The evidence favours the portals note for
  Labcorp, because it is the only one resting on an opened terms page.
- Quest and Function terms were not opened, so whether the ban also applies to them is unresolved (Open
  questions).

### Q13. Which open questions from the existing-systems run do these notes settle?

**Confidence: high** for item 1, **medium** for the others.

1. **Are Attio views GET-only? Settled: yes.** The worker enumerated all 53 paths of the downloaded spec. The
   only view paths are GET /v2/objects/{object}/views and GET /v2/lists/{list}/views, and there is no Workflows
   tag or path (https://api.attio.com/openapi/api). View contents (filters, sorts, grouping, Kanban column) can
   be neither read nor written by REST (worker inference from the listing).
2. **Does listing webhooks need `webhook:read`? Answered by the worker, without a verbatim quote.** The note
   states "the list webhooks route needs `webhook:read`". The quote it carries covers only "`webhook:read-write`"
   for create (https://api.attio.com/openapi/api). Treat as likely; the verifier should confirm.
3. **Can any Clay client export table contents and enrichment column settings? Partly settled.** Official
   routes read table rows only on Enterprise, with no list-tables endpoint (https://developers.clay.com/tables.md),
   and cannot create tables (https://github.com/clay-run/agent-plugins clay/skills/clay/SKILL.md:96 (commit
   b9952b6)). No source opened says whether column or enrichment settings can be exported; still open.
4. **Where does John's GTM configuration live? Not settled.** It needs John.

### Q14. Recommendation, alternatives, rejected candidates and spike list

**Confidence: medium.** The six notes agree on the split: API first, a Playwright browser on the VM for the rest,
no desktop control in v1, and manual download for blood work. They differ only on whether the Playwright CLI or
MCP leads, and on storage state versus persistent profile (Q1, Q6).

**One recommendation.** Claude Code on John's Ubuntu VM:

1. **API and MCP first** (Q11). Attio REST for the data model (https://api.attio.com/openapi/api), the Clay
   plugin for Workflows (https://developers.clay.com/routines/workflows-alpha.md), the n8n API
   (https://docs.n8n.io/connect/n8n-api.md), the Outreach API or MCP (https://developers.outreach.io/mcp-server/authentication).
2. **Playwright for the browser-only remainder,** in one headed Chrome with a dedicated persistent
   `--user-data-dir` on Xvfb, with noVNC behind a private network for John's one-time logins and live view
   (https://github.com/microsoft/playwright-mcp, https://github.com/novnc/noVNC). Use the `@playwright/cli`
   skill or Playwright MCP for exploration (https://github.com/microsoft/playwright-cli). Act by element
   reference by default and drag by coordinates or `dragTo` as the fallback (https://arxiv.org/html/2608.18307).
3. **Record once and replay.** Playwright Test Agents generate `.spec.ts` flows, the healer proposes patches,
   and Claude is called only on failure (https://playwright.dev/docs/test-agents).
4. **Reliability.** Auto-wait and traces (https://playwright.dev/docs/actionability,
   https://playwright.dev/docs/trace-viewer-intro). Check before create, and no blind retries of mutations
   (https://dev.to/harshithvaddiparthy/designing-browser-agents-that-dont-double-post-state-idempotency-and-verification-3be).
   Verify after every write through the API or a fresh read. A nightly read-only smoke run.
5. **Guardrails.** Deny and ask rules plus PreToolUse hooks on `mcp__<browser>__.*` for destructive, payment,
   send and publish targets and for domains off the allowlist (https://code.claude.com/docs/en/hooks,
   https://code.claude.com/docs/en/permissions). Approval relay through Remote Control or Channels; never
   `bypassPermissions` or Accept Edits on production (https://code.claude.com/docs/en/permission-modes,
   https://github.com/anthropics/claude-code/issues/65563).
6. **Logins.** John logs in by hand, Google included (https://support.google.com/accounts/answer/7675428).
   TOTP comes from a vault wrapper (https://www.1password.dev/cli/secret-references), with a per-site
   logged-in check and a re-login item in the approval digest. Stop on any CAPTCHA.
7. **Blood work.** PDF inbox plus local parser; no unattended portal login
   (https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement).

Free and self-hosted throughout. Worker inference: the cost is model tokens only.

**Alternatives:**
- Playwright MCP as the main driver, if in-context snapshots help (https://github.com/microsoft/playwright-mcp).
- agent-browser or Chrome DevTools MCP (https://github.com/vercel-labs/agent-browser,
  https://github.com/ChromeDevTools/chrome-devtools-mcp).
- Claude in Chrome on John's machine for attended one-offs (https://code.claude.com/docs/en/chrome).
- browser-harness on a real Chrome over CDP, unvetted (https://github.com/browser-use/browser-harness).
- Stagehand's local `cacheDir` replay if scripts prove brittle; it needs its own LLM key
  (https://docs.stagehand.dev/v3/best-practices/caching).
- Checkly hosted monitors, price not checked
  (https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/).
- For Clay, rebuild table logic as Workflows (Alpha) through the CLI to avoid the browser.
- For Attio views, a hand-recorded runbook.
- For the desktop: Cua Driver MCP in a disposable VM (https://github.com/trycua/cua); the Anthropic computer
  toolset in E2B Desktop or a Docker XFCE container (https://github.com/e2b-dev/desktop); Claude Desktop computer
  use on a spare Mac (https://code.claude.com/docs/en/desktop).
- For blood work: Apple Health export, an Epic SMART app (https://open.epic.com/DeveloperResources), or Fasten
  Connect or 1up if an individual account is allowed.

**Rejected, with reasons:**
- Magnitude: the name is reused and it has only a self-reported benchmark (https://github.com/magnitudedev/magnitude).
- workflow-use: "we don't recommend using this in production" (https://github.com/browser-use/workflow-use/).
- browser-use as primary: a second LLM loop (worker inference).
- Skyvern for now: needs its server (https://www.skyvern.com/blog/asking-ai-to-build-scrapers-should-be-easy-right/),
  plus its own LLM; licence AGPL (worker inference, not in the source).
- Puppeteer direct: subsumed (https://github.com/puppeteer/puppeteer).
- OpenClaw as controller: `mcp serve` exposes only conversations (https://github.com/openclaw/openclaw
  docs/cli/mcp.md:25 (commit 58d7e878)).
- Bytebot: archived (https://github.com/bytebot-ai/bytebot).
- UI-TARS Desktop and Agent S: separate agents that duplicate the engine (worker inference).
- ChatGPT agent and Operator: closed and not drivable from Claude Code; "retired" was seen only in a search
  result.
- Built-in Claude Code computer use for unattended work: macOS-only and interactive
  (https://code.claude.com/docs/en/computer-use).
- Hosted browsers for logged-in work: vendor holds the cookies
  (https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/).
- Stealth plugins, CAPTCHA solvers and residential proxies: evasion
  (https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/).
- Storage-state files as the primary session store (https://playwright.dev/docs/auth).
- `bypassPermissions` or Accept Edits on production, blind retry decorators, the Playwright MCP origin list as a
  boundary, and the model's own confirmation as the only gate (sources in Q10).
- The unofficial Clay session-cookie API: unofficial and fragile (api-vs-browser note recommendation).
- Unattended Labcorp portal login: terms (URL above).
- Fasten OnPrem as a puller: archived, no import (https://github.com/fastenhealth/fasten-onprem/).
- Health Connect: experimental (https://developer.android.com/health-and-fitness/health-connect/medical-records).
- Flexpa, Metriport, Health Gorilla, Particle for solo use: price and eligibility, seen in search highlights
  only (Open questions).

**Spike list (try for real before building):**
1. Five to ten real Attio and Clay tasks on a sandbox workspace, with the Playwright CLI skill versus Playwright
   MCP versus agent-browser: success by state check, tokens and time per task.
2. A Kanban drag in Attio: `dragTo` or ref drag versus coordinate drag, verified afterwards; the Playwright healer
   on a broken drag or locator; LLM repair rate on John's own flows.
3. A persistent profile on the VM under Xvfb with an explicit `--user-data-dir`: log in by noVNC, restart Claude
   Code and Chrome, and confirm the session survives. Run for two to three weeks and log expiry per site.
4. Challenge rate for headed Chrome from the VM's IP versus a home exit node, on the Attio, Clay, n8n and
   Outreach logins.
5. Google: a hand-logged profile stays signed in, Google SSO into Attio and Clay survives, and no script touches
   accounts.google.com.
6. A TOTP wrapper (`op` service account or pyotp) returns a code without the seed entering context; NTP sync;
   cost in reads.
7. A per-site logged-in check, plus a stall alert into the digest.
8. PreToolUse hooks fire on Playwright MCP and `mcp__claude-in-chrome__*` click and type calls with usable
   `tool_input`; a domain-allowlist hook on navigation.
9. An Attio view created in the UI, then read back through the API, filters included (confirm id and title
   only); check-before-create by title.
10. A Clay column created and verified without the Enterprise API; which Clay plan John has; credit-consuming
    clicks.
11. n8n: the community-package route and owner setup on John's edition, and whether the master-branch routes are
    released.
12. Outreach: whether John can create an app, what its token can edit, and whether his employer allows UI
    automation.
13. Whether the Attio App SDK is blocked at John's org.
14. Clay's later terms sections; Quest, MyQuest and Function terms.
15. Blood work: parse a real Labcorp PDF and a real Quest or Function PDF; check that an Apple Health export
    includes John's labs; which lab and portal (MyChart?) he uses; ask Fasten and 1up whether an individual
    account is allowed, and the price.
16. Optional desktop work: Cua Driver MCP on a headless Linux VM, one native-app task with time and tokens per
    step; whether Withings or WHOOP pairing works without a real phone; an Android emulator with KVM and adb
    screencap; a protected-path hook blocks `rm -rf` on home in all modes.
17. Only if scripts prove brittle: Stagehand local cache with `env: "LOCAL"` and a Claude model, on the
    installed version.

## Evidence

All opened 2026-10-16 unless noted. The tool is as the note states it. Notes: T = tool-landscape, C =
computer-control, S = sessions-and-hosting, R = reliability-and-guardrails, A = api-vs-browser, P =
gap-patient-portals. "Exa search highlights" or "Exa search page content" marks pages the note lists as opened
but read through Exa search output; the verifier should give these priority. Repo citations are kept as the
notes wrote them.

Tool landscape (T):
- T1 https://github.com/microsoft/playwright-mcp — Exa web_fetch — Playwright MCP (Microsoft): accessibility-snapshot driven, Apache-2.0, 38,194 stars, drives Claude Code via a standard MCP stdio config. Quote: "This server enables LLMs to interact with web pages through structured accessibility snapshots, bypassing the need for screenshots or visually-tuned models."
- T2 https://playwright.dev/mcp/introduction — Exa search highlights of the page — Playwright MCP tool list includes native drag and drop, JS evaluate and a "run Playwright code" tool. Quote: "`browser_drag` | Drag and drop between elements"
- T3 https://playwright.dev/mcp/introduction — Exa search highlights of the page — Playwright MCP keeps login state by default. Quote: "Persistent sessions — login state and cookies preserved between sessions by default"
- T4 https://github.com/microsoft/playwright-cli — Exa web_fetch — Playwright CLI (`@playwright/cli`, Apache-2.0, 14,220 stars on the metadata page): installs skills that Claude Code uses; Microsoft itself recommends it over MCP for coding agents. Quote: "Claude Code, GitHub Copilot and others will use the locally installed skills." and "playwright-cli install --skills"
- T5 https://github.com/microsoft/playwright-mcp — Exa web_fetch — Microsoft's own framing of CLI vs MCP. Quote: "MCP remains relevant for specialized agentic loops that benefit from persistent state, rich introspection, and iterative reasoning over page structure"
- T6 https://github.com/puppeteer/puppeteer — Exa web_fetch — Puppeteer: Apache-2.0 JS library, 95,697 stars, and its README now points to chrome-devtools-mcp as the MCP route. Quote: "Install `chrome-devtools-mcp`, a Puppeteer-based MCP server for browser automation and debugging."
- T7 https://github.com/ChromeDevTools/chrome-devtools-mcp — Exa web_fetch — Chrome DevTools MCP: Google-maintained, Apache-2.0, 53,561 stars, created 2025-09-11, Puppeteer-based, debugging/perf focus, CLI also provided, officially Chrome/Chrome for Testing only. Quote: "Uses puppeteer to automate actions in Chrome and automatically wait for action results."
- T8 https://github.com/vercel-labs/agent-browser — Exa web_fetch — agent-browser (Vercel Labs): Apache-2.0, 44,026 stars, created 2026-01-11, native Rust CLI, accessibility snapshot with refs, installs Chrome for Testing, Linux deps flag. Quote: "agent-browser snapshot                    # Get accessibility tree with refs"
- T9 https://github.com/browser-use/browser-use — Exa web_fetch — browser-use: MIT, 118,157 stars, Python (and TypeScript) agent library plus paid Browser Use Cloud; offers a CLI skill installable into Claude Code. Quote: "Install or upgrade browser-use to the latest stable version with uv using Python 3.12, run `browser-use skill install` to register the skill". Page contains instructions addressed to agents; not followed. Quoted as data: "AI agents and crawlers: read browser-use.com/llms.txt for the product map".
- T10 https://github.com/browser-use/browser-harness — Exa search page content — browser-harness (browser-use): MIT, lets Claude Code drive the user's real Chrome over CDP, exposes MCP over stdio. Quote: "`browser-harness-mcp` exposes the browser control helpers as MCP tools over stdio, so any MCP client (Claude Code, Devin, Cursor, etc.) can drive the browser". Page contains instructions addressed to agents ("Paste one prompt into your coding agent to set it up"); not followed.
- T11 https://github.com/browserbase/stagehand — Exa web_fetch — Stagehand (Browserbase): MIT, 25,669 stars, TypeScript SDK (Python port also), `act/extract/observe`, `selfHeal` default true, local or Browserbase env. Quote: "act() self-heals when the site redesigns its form"
- T12 https://docs.stagehand.dev/v3/references/stagehand — Exa search page content — Stagehand options: `env: "LOCAL" | "BROWSERBASE"`, `selfHeal`, `cacheDir`, `serverCache`. Quote: "Enable self-healing mode where actions can recover from failures. Default: `true`"
- T13 https://github.com/Skyvern-AI/skyvern — Exa web_fetch — Skyvern: vision-LLM + Playwright SDK, 23,208 stars, licence is AGPL-3.0 (strong copyleft; matters only if hosted for others). Quote: "Skyvern relies on Vision LLMs to learn and interact with the websites."
- T14 https://www.skyvern.com/pricing/ — Exa search page content — Skyvern cloud pricing: Free 5,000 credits, Hobby $29/mo, Pro $149/mo. Quote: "Free (5,000 credits), Hobby ($29/mo), Pro ($ 149/mo), and Enterprise plans."
- T15 https://github.com/magnitudedev/browser-agent and https://github.com/magnitudedev/magnitude — Exa web_fetch — Magnitude browser agent (vision-first, Apache-2.0, 4,134 stars) lives at magnitudedev/browser-agent; the name magnitudedev/magnitude is now an unrelated local-model inference engine created 2026-06-12. Quote: "Magnitude is an open source inference engine that tunes its kernels on your hardware to find the fastest way to run each model."
- T16 https://github.com/magnitudedev/browser-agent — Exa web_fetch — Magnitude's own claim and drag example (self-reported). Quote: "Magnitude is state-of-the-art, scoring 94% on WebVoyager!"
- T17 https://code.claude.com/docs/en/chrome — WebFetch (T, S, R notes) — Claude in Chrome: extension plus `claude --chrome`; visible Chrome, shares logins, pauses on login/CAPTCHA, needs a direct Anthropic plan, off with API key or setup-token. Quote: "If you authenticate with an API key or a long-lived token from `claude setup-token`, Claude Code keeps Chrome integration off"
- T18 https://code.claude.com/docs/en/chrome — WebFetch (T, S, R notes) — Claude in Chrome pauses for humans. Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- T19 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome blocked by JS dialogs. Quote: "JavaScript dialogs block browser events and prevent Claude from receiving commands."
- T20 https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool — Exa web_fetch — New 2026 Anthropic API primitive: `browser_toolset_20260801` with accessibility-tree refs plus coordinates, `left_click_drag`, `left_mouse_down/up`, `zoom`; you supply the executor (not a ready tool for Claude Code). Quote: "Claude works with the page both through its structure (the accessibility tree, elements, forms, and tabs) and through screenshots and viewport coordinates."
- T21 https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool — Exa web_fetch — Same page: executor model. Quote: "Your application runs every call against its own browser automation; nothing runs on Anthropic's side."
- T22 https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — Exa web_fetch — Computer use (desktop) toolset also exists and Anthropic points web-only tasks to the browser tool. Quote: "For tasks that stay inside webpages, the browser use tool is the closer fit"
- T23 https://arxiv.org/html/2504.01382v4 — Exa search page content — Online-Mind2Web showed over-optimism in earlier numbers. Quote: "Frontier web agents show a drastic drop in success rate when evaluated on Online-Mind2Web (human evaluation) compared with those reported on WebVoyager"
- T24 https://arxiv.org/html/2504.01382v4 — Exa search page content — Human-eval figures in that paper: Claude Computer Use 3.7 56.3%, Operator 61.3%, browser-use with GPT-4o 30.0%. Quote: "Browser Use | $30.0$"; "Claude Computer Use 3.7 | $56.3$"
- T25 https://leaderboard.steel.dev/leaderboards/online-mind2web/ — Exa web_fetch — Current Online-Mind2Web board (updated 2026-10-11) has self-reported 90%+ entries but warns about judges. Quote: "Browser Use Cloud (bu-max)"; "97.0%"; "OpenAI's score uses a different screenshot-based judge — not directly comparable."
- T26 https://leaderboard.steel.dev/leaderboards/online-mind2web/ — Exa web_fetch — Same board: harness result with generated browser code reaching 89.4%. Quote: "GPT-5.5 uses a terminal/filesystem harness and generated browser code, so this is a harness result rather than a GUI-only model score."
- T27 https://leaderboard.steel.dev/leaderboards/online-mind2web/ — Exa web_fetch — Same board: Stagehand with Sonnet 4.5 scored 55.0% (Browserbase-reported, Mar 2026). Quote: "Stagehand (Sonnet 4.5)"; "55.0%"
- T28 https://hal.cs.princeton.edu/online_mind2web — Exa search page content — HAL independent board: Browser-Use with Claude Sonnet 4 40.00%; SeeAct with GPT-5 42.33%; costs flagged as overstated 2x for some rows (Oct 5, 2026). Quote: "Nested trace spans counted the same API response twice, so affected models are inflated by exactly 2×."
- T29 https://arxiv.org/html/2608.18307 — Exa web_fetch — ComponentBench (Amazon AGI SF Lab/Duke, 2026): observation space changes success by 30+ points for the same model. Quote: "GPT-5 mini falls from 83.1% with accessibility-tree observations to 48.9% with coordinate-only Pixel control."
- T30 https://arxiv.org/html/2608.18307 — Exa web_fetch — ComponentBench on drag and drop: DOM-level browser-use actions lose, pixel wins. Quote: "Browser-Use's DOM-level action surface cannot replicate genuine spatial drag operations on tasks like Kanban boards"
- T31 https://arxiv.org/html/2608.18307 — Exa web_fetch — ComponentBench: spatial manipulations stay hard for every agent. Quote: "sliders, drag-and-drop lists, and splitters—remain below 60% mean pass rate across all agents tested."
- T32 https://arxiv.org/html/2608.18307 — Exa web_fetch — ComponentBench: drag/drop favours pixel, editors favour browser-use. Quote: "Drag/Drop favors Pixel over Browser-Use, while Advanced Editors strongly favor Browser-Use."
- T33 https://arxiv.org/html/2511.17131 — Exa search page content — UI-CUBE (UiPath, 2025): pixel computer-use agents collapse on complex enterprise workflows. Quote: "Simple UI interactions achieve 67-85% success rates (compared to 97.9% human performance), but complex workflows drop precipitously to 9-19%."
- T34 https://arxiv.org/html/2609.35026 — Exa search page content — WebPageBench (Sep 2026): DOM harnesses beat screenshot-only for one model (Qwen3.8-27B, one run per pair); the 41-point gap is one harness's completion rate minus EMS (gpt-5.6-luna with openmanus, 1.00 vs 0.59), not a per-task declared-done count (corrected after hand check, 2026-10-16). Quote: "Qwen3.8-27B scores 0.737–0.763 through DOM harnesses and 0.480 through screenshots."
- T35 https://arxiv.org/html/2609.35026 — Exa search page content — Same page: agents over-report success. Quote: "the gap between what agents declare finished and what the log confirms reaches 41 points"
- T36 https://arxiv.org/html/2607.04334 — Exa search page content — Pixels vs structure disagreement: models trust stale structure over pixels. Quote: "on unedited stale snapshots from live pages the same models follow the outdated structure on up to $0.88$ of probes."
- T37 https://browser-use.com/posts/ai-browser-agent-benchmark — Exa search page content — Browser Use's own BU Bench V1 (100 hard tasks incl. iframes, drag-and-drop): LLM judge, claude-fable-5 80.0% at $580.87 per 100-task run, Claude Opus 4.6 62.0%, Sonnet 4.6 59.0%. Quote: "Anthropic's claude-fable-5 set a new high score of 80.0% running on the open-source library"
- T38 https://benchmarklist.com/benchmarks/webarena_verified/ — Exa search page content — WebArena-Verified (812 tasks, self-hosted sites): top self-reported Pass@1 about 71% as of Sep 2026. Quote: "A manually re-audited 812-task WebArena release covering six self-hosted web environments"; "Claude Opus 4.8 | 71.2% | Self-reported"
- T39 https://playwright.dev/docs/test-agents — Exa web_fetch — Playwright Test Agents; `init-agents --loop=claude` generates Claude Code agent definitions. Quote: "planner explores the app and produces a Markdown test plan"; "generator transforms the Markdown plan into the Playwright Test files"
- T40 https://playwright.dev/docs/test-agents — Exa web_fetch — Healer repairs failures. Quote: "Suggests a patch (e.g., locator update, wait adjustment, data fix)"
- T41 https://github.com/microsoft/playwright-cli — Exa web_fetch — Playwright CLI README: "Record and generate Playwright code" (repo description). Quote: "CLI for common Playwright actions. Record and generate Playwright code, inspect selectors and take screenshots."
- T42 https://docs.stagehand.dev/v3/best-practices/caching — Exa web_fetch / search highlights — Stagehand local cache: first run uses LLM, later runs replay, committed cache is portable. Quote: "Stagehand saves every action and agent step to a local file on first run, then replays those cached actions on subsequent runs with no LLM calls"
- T43 https://docs.stagehand.dev/v3/best-practices/deterministic-agent — Exa search page content — Stagehand cache clearing on site change; vendor speed claim. Quote: "If the website structure changes, clear the cache to force fresh exploration"; "Cached agent workflows run 10-100x faster"
- T44 https://browserbase.com/blog/stagehand-caching/ — Exa search page content — Stagehand server cache is Browserbase-hosted only, project-scoped, 48 hours. Quote: "cache entries are project-scoped (by Project ID), stored server-side on Browserbase, and valid for 48 hours."
- T45 https://www.skyvern.com/blog/asking-ai-to-build-scrapers-should-be-easy-right/ — Exa search page content — Skyvern explore/replay compiles to Playwright with LLM fallback; cost 0.11 to 0.04 per run, 2.7x cheaper. Quote: "Replay mode, it compiles those learnings into deterministic Playwright and runs fast and cheap, only falling back to the agent when something new or weird happens"
- T46 https://www.skyvern.com/blog/asking-ai-to-build-scrapers-should-be-easy-right/ — Exa search page content — Skyvern code-gen currently needs its server. Quote: "It currently requires a Skyvern server running, but soon it will be the default behaviour."
- T47 https://github.com/browser-use/workflow-use/ — Exa search page content — browser-use workflow-use: record, generate JSON workflow, run with no AI; fallback to agent; maintainers say not production-ready. Quote: "This project is in very early development so we don't recommend using this in production."
- T48 https://github.com/browser-use/workflow-use/ — Exa search page content — Self-healing in workflow-use still on its to-do list. Quote: "Self healing, if it fails automatically agent kicks in and updates the workflow file"
- T49 https://browser-use.com/browser-harness — Exa search page content — Browser Harness lets the agent write and keep its own helpers. Quote: "The agent adds what a site needs, uses it, and keeps it for next time."
- T50 https://playwright.dev/agent-cli/introduction — Exa search page content — Microsoft's own docs rate CLI cheaper. Quote: "Token cost | Lower — concise CLI output, skills loaded on demand | Higher — tool schemas + snapshots in context"
- T51 https://dev.to/aswani25/playwright-cli-vs-playwright-mcp-which-should-you-use-with-claude-code-1olh — Exa search page content — A July 2026 re-benchmark found parity after MCP began writing snapshots to disk. Quote: "The ~4× token gap has essentially closed."
- T52 https://dev.to/aswani25/playwright-cli-vs-playwright-mcp-which-should-you-use-with-claude-code-1olh — Exa search page content — Same page, fixed overhead. Quote: "MCP keeps its ~24 tool definitions (~18k characters) in the session's tool list the whole time, while the CLI reads a skill file once (~12.6k characters)"
- T53 https://www.test-lab.ai/blog/playwright-mcp-vs-cli-agentic-testing — Exa search page content — Earlier Feb 2026 figure now historical. Quote: "One published comparison measured roughly 114,000 tokens with MCP versus 27,000 with CLI on the same flow."
- T54 https://outpost.ranger.net/post/the-hidden-cost-of-fewer-tokens/ — Exa search page content — April 2026 benchmark: CLIs use half the context but MCP is faster and not costlier. Quote: "The MCP case consistently took about half the time as the CLI. It also doesn't necessarily correlate to cost, and the MCP ended up slightly cheaper."
- T55 https://outpost.ranger.net/post/the-hidden-cost-of-fewer-tokens/ — Exa search page content — Same page, mechanism. Quote: "the agents used dramatically more tool calls (2-3x) to accomplish the same goal with the CLIs."
- T56 https://outpost.ranger.net/post/the-hidden-cost-of-fewer-tokens/ — Exa search page content — Same page, numbers. Quote: "the Playwright CLI and agent-browser average about 22k-24k tokens to complete scenario 1. The MCP requires 50k."
- T57 https://arxiv.org/html/2608.18307 — Exa web_fetch — Pixel observation also costs steps: pixel drops accuracy and efficiency. Quote: "GPT-5 mini Pixel passes 48.9% but only 19.0% within human steps"
- T58 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome adds context when always on. Quote: "Enabling Chrome by default increases context usage since the browser tools and their instructions are always loaded."

Computer control (C):
- C1 https://code.claude.com/docs/en/computer-use — WebFetch — CLI computer use is macOS-only, research preview, Pro/Max only, interactive only. Quote: "Computer use is a research preview on macOS that requires a Pro or Max plan. It is not available on Team or Enterprise plans. It requires an interactive session"
- C2 https://code.claude.com/docs/en/computer-use — WebFetch (C, S notes) — Explicitly not available on Linux or with `-p`. Quote: "Computer use in the CLI is not available on Linux or Windows."
- C3 https://code.claude.com/docs/en/computer-use — WebFetch — Anthropic's own routing puts it last. Quote: "Computer use is the broadest and slowest, so Claude tries the most precise tool first"
- C4 https://code.claude.com/docs/en/computer-use — WebFetch — It runs on the real desktop, not a sandbox; one session at a time. Quote: "Unlike the sandboxed Bash tool, computer use runs on your actual desktop with access to the apps you approve."
- C5 https://code.claude.com/docs/en/computer-use — WebFetch — Guardrails: per-app approval, terminal excluded from screenshots, Esc abort, lock file. Quote: "Per-app approval: Claude can only control apps you've approved in the current session."
- C6 https://code.claude.com/docs/en/desktop — WebFetch — Desktop app: macOS and Windows, app must be running; browsers are view-only, terminals/IDEs click-only (and, in Q4 of the note, browsers are view-only in Desktop computer use, so the desktop tool cannot type in a browser). Quote: "Computer use is a research preview on macOS and Windows that requires a Pro or Max plan." and "View only | See the app in screenshots | Browsers, trading platforms"
- C7 https://code.claude.com/docs/en/desktop — WebFetch — Desktop: Dispatch sessions can use it with 30-minute approvals; whether scheduled tasks can use it was not stated in the part read. Quote: "Dispatch-spawned Code sessions can use it too. App approvals in those sessions expire after 30 minutes and re-prompt"
- C8 https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — WebFetch — API tool: current version GA on Claude API, with the list of supporting models including claude-sonnet-5-5 and claude-haiku-5-5. Quote: "Computer use is available on the Claude API and Google Cloud as the `computer_toolset_20260801` toolset."
- C9 https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — WebFetch — Cost driver: screenshot tokens. Quote: "Long agent loops accumulate screenshots quickly (roughly 1,000–1,800 input tokens each)."
- C10 https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — WebFetch — Anthropic's own security advice for the API tool: VM, no sensitive data, domain allowlist, human confirmation. Quote: "Using a dedicated virtual machine or container with minimal privileges to prevent direct system attacks or accidents."
- C11 https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — WebFetch — Same page admits injection risk persists. Quote: "In some circumstances, Claude will follow commands found in content even when they conflict with your instructions."
- C12 https://leaderboard.steel.dev/leaderboards/osworld/ — WebFetch — OSWorld-Verified leaderboard (aggregator, all self-reported): top rows Qwen3.8-Max 86.1%, Claude Mythos 5 / Fable 5 85.0%, Opus 4.8 83.4%, Claude Sonnet 5 81.2%; best open weights MiMo-V2.6-Pro-RL 82.0%. Quote: "Claude Sonnet 5 | 81.2% | 2026-06-30 | Yes, in the Claude Sonnet 5 system card" (fetch-tool table rendering, row text paraphrased by the fetch model; treat as medium confidence)
- C13 https://github.com/openclaw/openclaw docs/nodes/computer-use.md:11 (commit 58d7e878) — git clone — The computer tool controls the Gateway desktop or a paired node's desktop with Peekaboo (default on macOS) or CUA. Quote: "Computer use lets an agent see and control the Gateway's own desktop or a paired node's desktop through one built-in `computer` tool."
- C14 docs/nodes/computer-use.md:21 (same clone) — git clone — Windows/Linux support is experimental. Quote: "Windows and Linux can use the optional, experimental `cua-computer` plugin, which calls the packaged CUA Driver SDK directly."
- C15 docs/nodes/computer-use.md:44 (same clone) — git clone — Headless Linux has a managed desktop. Quote: "On a headless Linux Gateway, enable the managed desktop."
- C16 docs/nodes/computer-use.md:30 (same clone) — git clone — Needs a vision model and tool policy; Full profile does not grant computer permissions. Quote: "Full tool selection does not grant computer-control permissions."
- C17 docs/tools/browser.md:12-14 (same clone) — git clone — Browser: separate agent-only Chromium profile, or attach to your real signed-in Chrome. Quote: "The built-in `user` profile attaches to your real signed-in Chrome session instead, via Chrome DevTools MCP."
- C18 docs/tools/chrome-extension.md:9 (same clone) — git clone — Chrome extension automates signed-in tabs. Quote: "The OpenClaw Chrome extension lets the browser tool automate eligible tabs in your signed-in Chrome profile."
- C19 docs/cli/mcp.md:25 (same clone) — git clone — Connection to Claude Code: `openclaw mcp serve` exposes only channel conversations. Quote: "Let an external MCP client read/send OpenClaw channel conversations | `openclaw mcp serve` | OpenClaw is the MCP server and exposes Gateway-backed conversations over stdio."
- C20 docs/tools/acp-agents.md:25 (same clone) — git clone — The other direction (OpenClaw hosts Claude Code) is ACP / claude-cli. Quote: "To let Codex or Claude Code connect as an external MCP client directly to existing OpenClaw channel conversations, use `openclaw mcp serve` instead of ACP."
- C21 package.json:3 (commit 58d7e878) — git clone — Maintenance: calendar-versioned, version 2026.10.4. Quote: "\"version\": \"2026.10.4\","
- C22 /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q6, lines 340-390) — Read (earlier findings) — Security posture and 255+ advisories, sandbox off by default. Quote: "OpenClaw has already published over 255 GitHub Security Advisories."
- C23 https://github.com/trycua/cua — WebFetch — Cua Driver: operates native apps and browsers on macOS, Windows, Linux via CLI, MCP or SDK. Quote: "Give your agent tools to inspect and operate native desktop apps and browsers on macOS, Windows, and Linux."
- C24 https://github.com/trycua/cua — WebFetch — Licence split: MIT for everything but Spaces/Driver Bench; Spaces is FSL. Quote: "Everything outside Cua Spaces and Cua Driver Bench is MIT-licensed."
- C25 https://github.com/trycua/cua — WebFetch — Installer can register the MCP for Claude Code. Quote: "the cua MCP server into your AI coding agents (Claude Code, Codex, Cursor, and others)"
- C26 https://github.com/trycua/cua — WebFetch — Cua repo warns against its own older npm package. Quote: "Do not run it: it has known security issues."
- C27 https://github.com/e2b-dev/desktop — WebFetch — E2B Desktop: open-source Linux/Xfce virtual desktop for LLM computer use, Apache-2.0, 1.5k stars. Quote: "E2B Desktop Sandbox is an open source secure virtual desktop ready for Computer Use."
- C28 https://github.com/bytebot-ai/bytebot — WebFetch — Bytebot: archived. Quote: "This repository was archived by the owner on Mar 7, 2026. It is now read-only."
- C29 https://github.com/bytedance/UI-TARS-desktop — WebFetch — UI-TARS Desktop / Agent TARS: Apache-2.0 native GUI agent driven by UI-TARS and Seed models; newest news item 2025-11-05. Quote: "This project is licensed under the Apache License 2.0."
- C30 https://code.claude.com/docs/en/computer-use — WebFetch — Anthropic's own order of preference: MCP, Bash, Chrome, then computer use. Quote: "Screen control is reserved for things nothing else can reach: native apps, simulators such as the iOS Simulator, and tools without an API."
- C31 https://code.claude.com/docs/en/computer-use — WebFetch — Documented use cases are native-app and simulator tests, not SaaS UIs. Quote: "Drive GUI-only tools: interact with design tools, hardware control panels, the iOS Simulator, or proprietary apps that have no CLI or API."
- C32 research/tool-registry.md rows "Attio REST API + OpenAPI", "Attio MCP (official)", "Clay developer platform + CLI", "n8n public API", "Outreach REST API" — Read (earlier runs, verified 2026-10-16) — Existing API/MCP routes for John's SaaS tools. Quote: none carried in the note (row names only).
- C33 https://github.com/anthropics/claude-code/issues/99198 — WebFetch — Claude Code sub-agent `rm -rf` on a Windows home folder; deletion continued about 45 minutes after stop; issue open with no maintainer reply. Quote: "no protection that prevents such a command from reaching the home directory, and no reliable way to stop it once started."

Sessions and hosting (S):
- S1 https://github.com/microsoft/playwright-mcp — WebFetch (summarised) — Playwright MCP persists a profile on disk by default; `--isolated` keeps it in memory; `--storage-state` only applies to isolated sessions. Quote: "path to the storage state file for isolated sessions."
- S2 https://github.com/microsoft/playwright-mcp — WebFetch — The same README documents the profile locations and that a custom directory is possible. Quote: "path to the user data directory. If not specified, a temporary directory will be created."
- S3 https://github.com/microsoft/playwright-mcp — WebFetch — Extension mode connects to an existing Chrome/Edge to reuse logged-in tabs. Quote: "Connect to a running browser instance (Edge/Chrome only)."
- S4 https://github.com/microsoft/playwright-mcp — WebFetch — Playwright MCP is headed by default; headless idle timeout is one hour, headed never. Quote: "Defaults to one hour for headless browsers, never for headed ones."
- S5 https://playwright.dev/docs/auth — WebFetch — Storage state covers cookies, localStorage, IndexedDB and passkey auth, but not sessionStorage, and the file can impersonate the account (also: Playwright storage state includes passkey (WebAuthn) based auth state). Quote: "Reusing authenticated state covers cookies, local storage, IndexedDB and passkey (WebAuthn) based authentication."
- S6 https://playwright.dev/docs/auth — WebFetch — Playwright says to delete state when it expires; no auto refresh. Quote: "Note that you need to delete the stored state when it expires."
- S7 https://playwright.dev/docs/auth — WebFetch — The auth file is a credential; keep it out of git. Quote: "We strongly discourage checking them into private or public repositories."
- S8 https://playwright.dev/docs/api/class-browsertype — WebFetch — Persistent context and the real Chrome profile: automating Chrome's default profile is unsupported. Quote: "automating the default Chrome user profile is not supported."
- S9 https://developer.chrome.com/blog/remote-debugging-port — WebFetch — Since Chrome 136, remote-debugging switches are ignored on the default profile, so any CDP attach needs a non-default dir. Quote: "These switches will no longer be respected if attempting to debug the default Chrome data directory."
- S10 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome's connection drops on idle. Quote: "The Chrome extension's service worker can go idle during extended sessions, which breaks the connection."
- S11 https://support.google.com/accounts/answer/7675428 — WebFetch (summarised) — Google may refuse sign-in from automated or embedded browsers. Quote: "Are being controlled through software automation rather than a human."
- S12 https://support.google.com/accounts/answer/7675428 — WebFetch — Same page, embedded frameworks. Quote: "Are embedded in a different application."
- S13 https://www.1password.dev/cli/secret-references — Exa search highlights — 1Password secret references can fetch the OTP attribute of a field. Quote: "include the `attribute` (or `attr`) query parameter with the attribute you want to get."
- S14 https://1password.com/blog/1password-cli-2-0 — Exa search highlights — 1Password CLI has long supported `op item get --otp`. Quote: "npm publish --otp $(op item get npmjs --otp)"
- S15 https://www.1password.dev/service-accounts/use-with-1password-cli — Exa search highlights — 1Password service accounts: vault-scoped, rate-limited; `op item get` and `op read` each cost 3 reads unless IDs are passed. Quote: "Service accounts have hourly and daily limits on the total number of requests the service account can make."
- S16 https://bitwarden.com/help/secrets-manager-cli/ — WebFetch — Bitwarden Secrets Manager CLI authenticates with a machine-account token; the page says nothing about TOTP. Quote: "The Secrets Manager CLI can be logged in to using an access token generated for a particular machine account."
- S17 https://github.com/feder-cr/invisible_playwright/wiki/automating-totp-2fa-login-playwright — Exa highlights (third-party wiki, tool is a stealth wrapper which is rejected; the TOTP section is generic) — TOTP is computed locally from the seed (RFC 6238); the seed is long-lived and never rotated by lockout; NTP clock sync matters. Quote: "The shared secret is a long-lived credential, not a one-time value; anyone who has it can generate valid codes for as long as 2FA stays configured"
- S18 https://github.com/blhutchings/google-login-service — Exa highlights (2023, unvetted; lists a CAPTCHA solver, rejected) — A third-party Google login automation reports only TOTP is reliable; Google prompt and passkey "unlikely". Quote: "Currently only TOTP works reliably."
- S19 https://docs.stably.ai/use-cases/testing-google-auth-and-2fa — Exa highlights — A testing vendor advises against automating personal Google accounts. Quote: "Do not automate personal Google accounts or rely on one-time manual approvals in CI. Use dedicated test identities only."
- S20 /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q3 section) — Read (earlier findings) — 1Password for Claude (vault fill without exposing secrets) is Mac only. Quote: "Claude never sees the vault item, password, or one-time code"
- S21 https://developers.cloudflare.com/bots/concepts/bot-score/ — Exa highlights — Cloudflare JSD targets headless browsers. Quote: "Catches headless browsers (browsers controlled by software, with no visible window or human operator) and other automation tools."
- S22 https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/ — Exa highlights — Cloudflare says automation frameworks cannot be relied on for production challenges, and offers test keys for Turnstile. Quote: "Browser automation frameworks, such as Selenium, Puppeteer, Playwright, and Cypress, are not supported for solving production challenges."
- S23 https://developers.cloudflare.com/bots/concepts/bot-detection-engines/ — Exa highlights — Cloudflare's ML engine scores headers, session characteristics and browser signals. Quote: "Request features, including headers, session characteristics, and browser signals, collected from traffic across the Cloudflare network."
- S24 https://developers.cloudflare.com/browser-run/reference/automatic-request-headers/ — Exa highlights — Cloudflare's own browser product signs requests with Web Bot Auth so sites can verify them. Quote: "Web Bot Auth leverages cryptographic signatures in HTTP messages to verify that a request comes from an automated bot."
- S25 https://support.google.com/accounts/answer/7675428 — WebFetch — Google blocks software-automated sign-in. Quote: "Google doesn’t let you sign in from some browsers."
- S26 /home/user/Autonomy-Research/research/tool-registry.md (Playwright MCP row) — Read — Playwright MCP headless was blocked by Cloudflare/Vercel bot checks in this project. Quote: "blocked by Cloudflare/Vercel bot checks; 45-95 KB snapshots"
- S27 https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/ — Exa highlights (third-party comparison, 2026-08-12) — Hosted-browser vendors sell stealth and CAPTCHA solving as features. Quote: "Stealth mode, residential proxies, CAPTCHA solving, per its docs"
- S28 https://attio.com/legal/terms-and-conditions — WebFetch (summarised) — Attio Customer Agreement: no clause on bots/scripts/scraping; credential and API-abuse clauses exist. Quote: "You will be responsible for ensuring the security and confidentiality of all log-on identifiers"
- S29 https://attio.com/legal/terms-and-conditions — Exa highlights — Attio bars circumventing limits including API call counts. Quote: "attempt to exceed or circumvent any express or implied limitations on use of the Attio Services, including, but not limited to, in relation to the number of calls to the Attio API"
- S30 https://attio.com/legal/terms-and-conditions — WebFetch — Attio bars letting third parties use the service. Quote: "permit or facilitate any third party to access or use the Attio Services"
- S31 https://attio.com/legal/acceptable-use — Exa highlights — Attio Acceptable Use also bars circumventing security or access controls. Quote: "circumvent, disable, or interfere with any security or access controls"
- S32 https://www.clay.com/terms-of-service — Exa fetch (first 8,000 characters only) — Clay Terms (last updated May 23, 2024): customer is responsible for account credentials. Quote: "You are solely responsible for maintaining the confidentiality of your account information, including username and password, and for all activities that occur under your account."
- S33 https://www.clay.com/terms-of-service — Exa fetch — Clay Terms: no transfer of the account. Quote: "You agree not to license, sell, or transfer your account without our prior written approval."
- S34 https://www.clay.com/blog/websites-that-allow-web-scraping — Exa highlights — Clay's own blog advises against CAPTCHA solvers and IP rotation on sites that forbid scraping. Quote: "using them is not recommended"
- S35 https://www.outreach.ai/terms — WebFetch (summarised) — Outreach (outreach.ai/terms): do not give your password to any third party; account may be suspended. Quote: "you agree not to provide your password to any third party"
- S36 https://www.outreach.ai/terms — WebFetch — Same page: suspension. Quote: "We reserve the right to suspend or terminate the Services in whole or part at any time, with or without cause"
- S37 https://www.outreach.ai/acceptable-use-policy — Exa highlights — Outreach Acceptable Use Policy focuses on email sending practices. Quote: "Using the Outreach Services in connection with any unsolicited or harassing messages"
- S38 https://github.com/novnc/noVNC — WebFetch — noVNC is a browser VNC client that needs websockify as the WebSocket proxy; MPL 2.0. Quote: "noVNC is both a HTML VNC client JavaScript library and an application built on top of that library."
- S39 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome: local, visible, needs a subscription login, not for API-key or setup-token auth. Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`, because the browser extension can't authenticate with those credentials."
- S40 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome is not covered by Anthropic's BAA for third-party sites (relevant to the health portal). Quote: "Your Business Associate Agreement (BAA) with Anthropic doesn't cover data sent to third-party sites through Claude in Chrome."
- S41 https://code.claude.com/docs/en/chrome — WebFetch — Claude in Chrome does not run in WSL. Quote: "Chrome integration isn't supported in Windows Subsystem for Linux (WSL)."
- S42 https://code.claude.com/docs/en/computer-use — WebFetch — Same page: not in `-p` mode. Quote: "Computer use is not available in non-interactive mode with the `-p` flag."
- S43 https://www.browserbase.com/pricing — WebFetch (summarised) — Browserbase pricing: Free 3 concurrent, 1 hour, 15-minute sessions, 7-day retention; Developer $20/month, 100 hours then $0.12/hr, 30-day retention; Startup $99/month, 500 hours then $0.10/hr. Quote: "Every plan scales past its included usage, so no caps or throttling as you build, billed at your plan’s rate."
- S44 https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/ — Exa highlights (third-party) — Hosted-browser comparison (2026-08-12): Browserbase context-style persistence, Steel persistent profiles, Hyperbrowser profiles via API; warns credentials concentrate risk at the vendor, and Steel self-hosting is the escape hatch. Quote: "recordings, cookies, and persistent profiles all live on someone else's infrastructure."
- S45 https://indexagentica.com/compare/cloud-browsers-for-agents.md — Exa highlights (third-party, dated 2026-10-12) — Self-hosted Steel limitations. Quote: "self-hosted Steel runs one session at a time and has no CAPTCHA solving or Credentials API."
- S46 https://llms.anchorbrowser.io/anchor-browser-vs-steel — Exa highlights (vendor-authored, biased) — Anchor vs Steel prices from vendor-authored comparison: Anchor $0.05/browser-hour with $50/month Starter; Steel Launch $0/month plus $0.10/hr, Scale $250/month; Steel Launch sessions capped at 15 minutes. Quote: "Steel lists 15 minutes (Launch), 1 hour (Scale), and up to 24 hours (Enterprise)"
- S47 https://llms.anchorbrowser.io/anchor-browser-vs-steel — Exa highlights — Steel Credentials API handles TOTP; Anchor adds email OTP mailboxes and auto re-auth (vendor claim). Quote: "Anchor re-authenticates automatically when a session needs it."
- S48 /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q3, Q4) — Read (earlier findings) — Remote Control and Channels allow phone-based monitoring of a session on John's machine/VM. Quote: "Claude keeps running locally the entire time, so your code execution and filesystem access stay on your machine"
- S49 /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q4) — Read (earlier findings) — Remote Control pushes needed decisions to John's phone. Quote: "Claude decides when to push. It typically sends one when a long-running task finishes or when it needs a decision from you to continue."
- S50 /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q4) — Read (earlier findings) — Channels can relay permission prompts to Telegram/Discord/iMessage, with a sender allowlist. Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority"
- S51 /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q3, from https://github.com/browser-use/bux) — Read (earlier findings) — Reference pattern: a persistent Chromium on a VPS with hand-off on login walls. Quote: "A real Chromium session via browser-harness — cookies persist, logins stick"
- S52 https://menuagentic.com/blogs/browserbase-vs-steel-vs-hyperbrowser-vs-anchor-browser/ — Exa highlights — Hosted vendors confirm the "first login" problem: managed profiles persist the session but something still supplies the password. Quote: "without solving the first-login problem, since something still has to supply the password."
- S53 https://menuagentic.com/blogs/browserbase-vs-steel-vs-hyperbrowser-vs-anchor-browser/ — Exa highlights — Guidance to keep passwords out of the prompt. Quote: "If the password ever appears in a prompt it is in your traces and reachable by prompt injection"

Reliability and guardrails (R):
- R1 https://playwright.dev/docs/actionability — WebFetch — Playwright auto-waits for actionability checks (visible, stable, receives events, enabled) before acting, so sleeps are unnecessary. Quote: "auto-waits for all the relevant checks to pass and only then performs the requested action."
- R2 https://playwright.dev/docs/trace-viewer-intro — WebFetch — Playwright docs recommend recording traces only on first retry; trace.zip holds per-step DOM snapshots, network, console. Quote: "record traces on first retry of each test"
- R3 https://docs.stagehand.dev/v4/best-practices/caching — WebFetch — Stagehand replays a cached action deterministically and falls back to LLM inference if the selector no longer resolves. Quote: "If the recorded selector no longer resolves, Stagehand falls back to full inference."
- R4 https://dev.to/harshithvaddiparthy/designing-browser-agents-that-dont-double-post-state-idempotency-and-verification-3be — WebFetch — Retries around mutations are unsafe without an idempotency token; an "ambiguous" state must be reconciled before retry. Quote: "They are unsafe around mutations unless the destination supports a genuine idempotency token."
- R5 same URL — WebFetch — Same source: ambiguous outcome definition. Quote: "It means the system attempted a mutation but could not prove whether the external effect occurred."
- R6 same URL — WebFetch — Same source: agent should stop rather than guess; the design verifies "exact normalized text ... canonical URL" per action type before marking verified. Quote: "refuse to guess when an external effect is at stake"
- R7 https://code.claude.com/docs/en/hooks — WebFetch — Claude Code docs: PreToolUse hooks can deny MCP browser tool calls; MCP matcher needs `.*`. Quote: "To match every tool from a server, append `.*` to the server prefix."
- R8 /home/user/Autonomy-Research/research/tool-registry.md:122 — Read — Attio REST API can read objects, attributes, lists, entries and view titles (so a UI-created view can be read back). Quote: "Reads objects, attributes, lists, entries, view titles, webhooks, read-only SQL"
- R9 /home/user/Autonomy-Research/research/tool-registry.md:123 — Read — Registry notes the Attio API/MCP have gaps for views and workflows. Quote: "no view or workflow tool"
- R10 /home/user/Autonomy-Research/research/tool-registry.md:124 — Read — Clay tables are only queryable by API on Enterprise. Quote: "tables Enterprise only"
- R11 https://kdyao.github.io/resources/papers/ASE2025_Haonan.pdf — Exa fetch — 81.7% of repaired web GUI tests broke again within six months. Quote: "81.7% of repaired tests break again within six months, primarily due to similar recurring issues"
- R12 same URL — Exa fetch — LLMs with diagnostic context can repair many brittle tests, humans still needed for complex ones. Quote: "Large Language Models, when provided with human-like diagnostic context, can successfully repair a substantial portion of these brittle tests"
- R13 same URL — Exa fetch — Brittleness is a persistent maintenance cost that leads teams to rewrite suites. Quote: "many organizations opt to abandon and rewrite their test suites entirely"
- R14 https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/ — WebFetch — Checkly runs Playwright visual-regression tests against production on a schedule and shows a golden-image diff. Quote: "With Checkly, you can run these tests against production, 24x7."
- R15 https://code.claude.com/docs/en/chrome — WebFetch — Chrome integration shares login state and runs in a visible window; pauses on login/CAPTCHA. Quote: "Claude opens new tabs for browser tasks and shares your browser's login state, so it can access any site you're already signed into."
- R16 https://code.claude.com/docs/en/chrome — WebFetch — Site permissions come from the extension; auto-mode classifier approval can skip the per-site check unless a deny rule exists. Quote: "Site-level permissions are inherited from the Chrome extension."
- R17 https://code.claude.com/docs/en/chrome — WebFetch — A project cannot turn on Chrome integration itself. Quote: "a repository you check out must not be able to connect Claude to your browser."
- R18 https://www.anthropic.com/research/prompt-injection-defenses — WebFetch — Anthropic Nov 2025: even a 1% success rate is meaningful. Quote: "A 1% attack success rate—while a significant improvement—still represents meaningful risk."
- R19 https://claude.com/resources/articles/claude-in-chrome-generally-available — WebFetch — Aug 2026 GA post: classifier checks actions against the original request. Quote: "If the action doesn't match your request, it's blocked."
- R20 https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely — WebFetch — Help center: classifiers, blocklists, confirmations, manual approve mode, and an explicit recommendation for a separate profile. Quote: "consider using a separate browser profile without access to sensitive accounts."
- R21 same URL — WebFetch — Same page: Manually-approve mode exists. Quote: "Switch to \"Manually approve\" if you want to review every action."
- R22 https://code.claude.com/docs/en/permissions — WebFetch (grep of saved page) — Claude Code permissions: deny evaluated first; allow globs on MCP require a literal server prefix; `mcp__*` deny removes all MCP tools. Quote: "Rules are evaluated in order: deny, then ask, then allow."
- R23 https://code.claude.com/docs/en/permissions — WebFetch — A PreToolUse hook cannot override deny/ask rules. Quote: "Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns"
- R24 https://code.claude.com/docs/en/hooks — WebFetch — PreToolUse hook can deny a tool call; a timed-out hook does not block unless `onFailure: "block"`. Quote: "A timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call."
- R25 https://code.claude.com/docs/en/permission-modes — WebFetch (grep of saved page) — Auto mode blocks by default production deploys and mass deletion, but this list is about shell/infra, not browser UI clicks. Quote: "Mass deletion on cloud storage"
- R26 https://code.claude.com/docs/en/permission-modes — WebFetch — In `-p` runs with no prompt, repeated classifier blocks do not stop the run. Quote: "When repeated blocks reach a threshold, the action doesn't run and Claude keeps working. Claude Code doesn't stop the run."
- R27 https://code.claude.com/docs/en/permission-modes — WebFetch — `bypassPermissions` gives no injection protection. Quote: "`bypassPermissions` offers no protection against prompt injection or unintended actions."
- R28 https://github.com/microsoft/playwright-mcp — WebFetch — Playwright MCP origin allowlist is not a security boundary; offers isolated in-memory profile and opt-in caps. Quote: "Playwright MCP is not a security boundary."
- R29 https://simonwillison.net/2025/jun/16/the-lethal-trifecta/ — WebFetch — Simon Willison's trifecta: avoid private data + untrusted content + external communication together. Quote: "The only way to stay safe there is to avoid that lethal trifecta combination entirely."
- R30 https://openai.com/index/hardening-atlas-against-prompt-injection/ — Exa fetch — OpenAI Atlas: prompt injection remains open; confirmations for consequential actions; recommends logged-out mode. Quote: "prompt injection remains an open challenge for agent security, and one we expect to continue working on for years to come."
- R31 https://openai.com/index/hardening-atlas-against-prompt-injection/ — Exa fetch — OpenAI describes the exposure surface for browser agents. Quote: "the agent may encounter untrusted instructions across an effectively unbounded surface area"
- R32 https://github.com/anthropics/claude-code/issues/65563 — WebFetch — Real incident: Claude clicked "Delete" confirm on a production record via browser automation with Accept Edits on (reporter's claim; issue closed not planned). Quote: "Accept Edits was ON (auto-accepting changes)"; same page: "The record was permanently deleted from the production Supabase database."
- R33 /home/user/Autonomy-Research/research/tool-registry.md:54,56 — Read — Remote Control, Channels give live approvals from phone. Quote: "Use for browser logins, monitoring and live approvals"

API versus browser (A):
- A1 https://api.attio.com/openapi/api — curl (downloaded, parsed with python -I) — REST views are read-only for objects: the only views route on objects is GET, scope object_configuration:read. I enumerated all 53 paths of the downloaded spec; the only paths containing "views" are GET /v2/objects/{object}/views and GET /v2/lists/{list}/views. Quote: "Lists saved views for an object. Results are ordered by view ID (`id.view_id` ascending)."
- A2 https://api.attio.com/openapi/api — curl — Same for list views, scope list_configuration:read. Quote: "Lists saved views for a list. Results are ordered by view ID (`id.view_id` ascending)."
- A3 https://api.attio.com/openapi/api — curl — No workflows path exists in the spec: the tag list has no Workflows tag (tags include Objects, Object views, List views, Attributes, Lists, Entries, Webhooks, SQL, Sequences). Quote: "Required scopes: `webhook:read-write`." (webhook create; the spec has webhooks but no workflow routes)
- A4 https://api.attio.com/openapi/api — curl — Create object is POST, update PATCH, delete DELETE; scope object_configuration:read-write. Quote: "Creates a new custom object in your workspace."
- A5 https://api.attio.com/openapi/api — curl — Attribute create works on objects, lists and activities, with bidirectional relationships. Quote: "For record-reference attributes, you can optionally create a bidirectional relationship by providing a `relationship` object."
- A6 https://api.attio.com/openapi/api — curl — Select options can be added by REST on objects, lists and activities (statuses have their own POST/PATCH routes). Quote: "Adds a select option to a select attribute on an object, a list or an activity."
- A7 https://api.attio.com/openapi/api — curl — Lists are created by POST /v2/lists, PATCH updates; no DELETE list route exists in the spec path listing. Quote: "Creates a new list."
- A8 https://api.attio.com/openapi/api — curl — Scopes are per area, for example object_configuration, list_configuration, activity_configuration, webhook, record_permission; webhooks are workspace-level tokens only. Quote: "Required scopes: `webhook:read-write`. Supported token levels: `workspace`."
- A9 https://docs.attio.com/rest-api/guides/authentication.md — curl — Auth: API key or OAuth; only admins grant workspace-level OAuth tokens. Quote: "Only workspace admins can grant a workspace-level token."
- A10 https://docs.attio.com/rest-api/guides/rate-limiting.md — curl — Rate limits. Quote: "Our rate limit across the whole API is **100 requests per second** for read requests, **25 requests per second** for write requests."
- A11 https://docs.attio.com/mcp/overview.md — curl — Official MCP is OAuth, hosted at https://mcp.attio.com/mcp; writes ask confirmation. Quote: "Authenticates as your Attio user with OAuth, and read operations are auto-approved while write operations request confirmation"
- A12 https://docs.attio.com/changelog/mcp.md — curl — MCP tool list on that page (from the table): list-objects, list-attribute-definitions, list-lists, create-list, update-list, list-list-attribute-definitions, add-record-to-list, update-list-entry-by-id, create/update/upsert-record, merge-records, notes, tasks, comments, activities records, run-basic-report, query-particle-sql. No view, workflow, create-attribute or create-object tool appears. create-list is documented in the changelog. Quote: "`create-list` allows you to create a new list to group and track records of a single object type."
- A13 https://attio.com/help/reference/automations/workflows/workflows-block-library — curl — Workflows can be triggered by an HTTP request once built in the UI. Quote: "Webhook received starts a workflow when an external application sends a request to a provided URL."
- A14 https://docs.attio.com/sdk/overview.md — curl — App SDK can add blocks to Workflows, not create workflows. Quote: "Add custom triggers and steps to the Attio Workflows builder: subscribe to external events or call external APIs as part of a workflow run."
- A15 https://docs.attio.com/sdk/guides/creating-an-app.md — curl — App SDK setup needs a developer account in the Developer console (a browser step). Quote: "Head over to our [Developer console](https://build.attio.com) and sign in with your Attio account."
- A16 https://developers.clay.com/routines/workflows-alpha.md — curl — Workflows (Alpha) are buildable by agent via plugin/CLI. Quote: "With the Clay plugin, agents can read and edit Workflows, validate the graph, run test actions, start runs, inspect failed steps, pause or resume runs, and restore snapshots."
- A17 https://developers.clay.com/routines/custom-functions.md — curl — Custom functions are built in the UI, run by API/CLI/MCP. Quote: "Build and manage the function in the Clay UI."
- A18 https://developers.clay.com/routines/custom-functions.md — curl — Exposing a function to API or MCP is a toggle in the UI. Quote: "Enable the integrations you need, such as **API** or **MCP**."
- A19 https://developers.clay.com/tables.md — curl — Tables: Enterprise only, read only, no list endpoint. Quote: "The current public API does not include a list-tables endpoint."
- A20 https://github.com/clay-run/agent-plugins clay/skills/clay/SKILL.md:96 (commit b9952b6) — git clone + grep — Tables cannot be created programmatically. Quote: "Query **existing** Clay tables only — you **cannot** create tables programmatically"
- A21 same file, line 91 — git clone + grep — Plugin also covers campaigns (email sequences), audiences, searches. Quote: "Create, improve, compare, and analyze outbound email sequences"
- A22 https://developers.clay.com/quickstart.md — curl — API key creation can be done by CLI, but CLI sign-in needs a browser once. Quote: "Sign-in opens a browser to authorize the CLI."
- A23 https://developers.clay.com/quickstart.md — curl — Keys by CLI. Quote: "Run `clay api-keys create --name \"<key name>\"` with the `clay` CLI."
- A24 https://developers.clay.com/public-api/webhooks.md — curl — Clay webhooks here are run-finished notifications (outbound), created by CLI. Quote: "Webhooks let Clay notify your service when a routine run finishes, so you can react without polling."
- A25 https://developers.clay.com/signals.md — curl — Signals: most created by CLI, custom and web-intent UI only. Quote: "Custom and Web intent signal triggers are configured in the Clay web app."
- A26 https://developers.clay.com/public-api/rate-limits.md — curl — Rate limit is per workspace; no number is given. Quote: "The Clay Public API enforces a per-workspace request rate limit."
- A27 https://developers.clay.com/quickstart.md — curl — The plugin requires a shell host (Claude Code works). Quote: "It requires a coding-agent host with a shell — Claude Code, Codex, or Cursor"
- A28 https://docs.n8n.io/connect/n8n-api.md — curl — API availability. Quote: "It isn't available on the free trial."
- A29 https://docs.n8n.io/connect/n8n-api.md — curl — Self-hosted all editions, Cloud Starter and above. Quote: "**Self-hosted:** All editions"
- A30 https://github.com/n8n-io/n8n packages/cli/src/public-api/v1/handlers/community-packages/spec/paths/installPackage.generated.yml:5 (commit 21221ad) — sparse git clone — Community package install is an API route with its own scope. Quote: "description: Install a community package by npm name and optional version."
- A31 .../handlers/credentials/spec/paths/createCredential.generated.yml:5 (commit 21221ad) — sparse git clone — Credential create route. Quote: "description: Creates a credential that can be used by nodes of the specified type."
- A32 https://github.com/n8n-io/n8n packages/cli/src/public-api/v1/handlers/ (commit 21221ad) — sparse git clone — Handler directories exist for variables, tags, projects, workflows, users, source-control, settings (SAML, OIDC, LDAP). Quote: "createVariable.generated.yml" and "updateSamlConfiguration.generated.yml" (file names from the directory listing).
- A33 https://docs.n8n.io/deploy/host-n8n/configure-n8n/manage-settings-using-environment-variables.md — curl — Owner setup via env on self-hosted. Quote: "Instance owner management through environment variables is available from n8n 2.17.0."
- A34 same page — curl — Same page lists SSO and community packages as env-managed. Quote: "Community packages: `N8N_COMMUNITY_PACKAGES_MANAGED_BY_ENV`"
- A35 https://docs.n8n.io/integrations/community-nodes/installation-and-management/install-verified-community-nodes.md — curl — UI install of verified community nodes needs owner/admin. Quote: "The n8n instance owner and admin accounts can install and manage verified community nodes."
- A36 https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service.md — curl — OAuth credentials need a human consent click. Quote: "In n8n, select **Sign in with Google** to complete your Google authentication."
- A37 https://docs.n8n.io/connect/n8n-api.md — curl — The n8n MCP server (connected in this session) and CLI wrap the API. Quote: "It wraps the public API and is a good fit for:"
- A38 https://developers.outreach.io/api/reference/mailbox.md — curl — Mailbox create and update exist. Quote: "## Update a Mailbox"
- A39 https://developers.outreach.io/api/reference/mailbox/paths/~1mailboxes~1%7Bid%7D/patch.md — curl — Mailbox attribute shows per-user edit permission. Quote: "A boolean value to indicate if the user has the permission to edit mailbox fields."
- A40 https://developers.outreach.io/api/reference/sequence.md — curl — Sequence and template create routes (search excerpt pages opened as .md): sequence.md lists POST /sequences; template.md lists POST /templates. Quote: "## Create a New Sequence"
- A41 https://developers.outreach.io/api/oauth — curl — OAuth acts as the user; app creation and scopes are set in the portal. Quote: "To begin using the REST API you need to create an Outreach app."
- A42 https://developers.outreach.io/api/oauth — curl — Dev credentials are immediate; production needs publish and review. Quote: "Development credentials are provisioned immediately"
- A43 https://developers.outreach.io/mcp-server/authentication — curl — MCP: 32 tools, OAuth with dynamic client registration, RBAC inherited. Quote: "Permissions inherit from the user."
- A44 https://developers.outreach.io/mcp-server/tool-catalog — curl — MCP write tools include sequence creation. Quote: "sequence_create destructiveHint: false Create a new sequence"
- A45 https://developer.whoop.com/docs/developing/getting-started — curl — WHOOP app creation is a dashboard step with WHOOP login. Quote: "To create your first App, head to the App creation flow in the Developer Dashboard."
- A46 https://developer.whoop.com/docs/developing/getting-started — curl — WHOOP app limit. Quote: "You can create up to 5 Apps."
- A47 https://developer.whoop.com/docs/developing/oauth — curl — WHOOP refresh needs the offline scope. Quote: "You must request the offline scope to receive a refresh token."
- A48 https://developer.whoop.com/docs/developing/rate-limiting — curl — WHOOP rate limits. Quote: "100 requests per minute."
- A49 https://developer.whoop.com/docs/developing/app-approval — curl — WHOOP sandbox tier suffices for one user. Quote: "Every new app starts on the Sandbox tier, which allows up to 10 WHOOP members to connect."
- A50 https://developer.withings.com/developer-guide/v3/get-access/sign-up-for-a-developer-account — curl — Withings app registration in Partner Hub. Quote: "Register in the Partner Hub to get your client credentials."
- A51 same page — curl — Withings plan change. Quote: "Withings accounts created after that date will need a membership to share health data with a free-plan app, including apps that are already live."
- A52 https://developer.withings.com/developer-guide/v3/integration-guide/public-health-data-api/get-access/oauth-web-flow — curl — Withings OAuth consent is a human step; code must be exchanged fast. Quote: "You have 30 seconds to exchange the authorization code for an access token and a refresh token."
- A53 same page — curl — Withings data pull after consent includes history. Quote: "you will have access not only to new data but also to all historical health data collected by the devices"

Patient portals (P):
- P1 https://patient.labcorp.com/help-center/q-and-a/3000/2 — Exa fetch — Labcorp lets a signed-in patient download the doctor-identical report, typically as PDF. Quote: "The Official Report is the same document shared with your doctor."
- P2 same URL — Exa fetch — Labcorp Official Report downloads as PDF from web or app. Quote: "The report will download to your computer (typically as a PDF)."
- P3 https://www.questdiagnostics.com/patients/test-results — Exa fetch — Quest MyQuest is the patient channel; its results page lists no API or CSV export, only the app, doctor copies, and Apple Health. Quote: "We offer integrated results through Apple Health."
- P4 https://www.functionhealth.com/faq — Exa fetch — Function Health (draws at Quest) exposes results as a member-initiated PDF download; no API is mentioned on its FAQ. Quote: "Once your results are ready, you can log in and download them as a PDF to share with your healthcare provider."
- P5 same URL — Exa fetch — Function Health labs are Quest sites. Quote: "We partner with Quest for easily accessible labs (2,000+ locations across the US)"
- P6 same URL — Exa fetch — Function lets members connect wearables but only as inbound apps. Quote: "You can log into Function and connect supported apps to sync your health data"
- P7 https://open.epic.com/DeveloperResources — Exa fetch — Epic: self-service registration, no Epic relationship required. Quote: "no special relationship is required to develop or deploy an app."
- P8 same URL — Exa fetch — Epic is federated: connection is per health system. Quote: "There is no central Epic endpoint. To exchange data with organizations using Epic, you'll need to establish connections directly with individual organizations."
- P9 same URL — Exa fetch — Epic patient-authorized apps have extra distribution options (TEFCA IAS, auto-distribution). Quote: "If you are deploying an automatically-distributed patient-authorized app, you can connect directly to customer endpoints listed here."
- P10 https://fhir.epic.com/Documentation?docId=patientfacingfhirapps — Exa fetch — Epic sandbox must not hold real data. Quote: "You agree not to put individually identifiable information in any Epic-provided sandboxes."
- P11 https://developer.android.com/health-and-fitness/health-connect/medical-records — Exa fetch — Health Connect Medical Records (FHIR, includes laboratory permission) is experimental, needs Android 16 SDK, Play policy not finished; page updated 2026-09-22. Quote: "The Play Policy for Medical Records access is still being developed, and apps may need to meet additional requirements before they can be released on the Play Store."
- P12 https://github.com/fastenhealth/fasten-onprem/ — Exa fetch — Fasten OnPrem is archived (GPL-3.0) and cannot sync with providers. Quote: "Fasten Onprem is not able to import data from healthcare providers directly. You can only use this application to manually enter data, or upload FHIR Bundles"
- P13 same page — Exa fetch — Same page shows status. Quote: "Status: ARCHIVED"
- P14 https://docs.connect.fastenhealth.com/guides/tefca-ias — Exa fetch — Fasten TEFCA IAS has extra live fees and needs CLEAR or ID.me identity proofing. Quote: "There are additional fees involved with TEFCA IAS in `live` mode."
- P15 https://www.flexpa.com/docs/guides/getting-started — Exa fetch — Flexpa live access: no free plan, demo intake first. Quote: "Start at flexpa.com/demo."
- P16 https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement — Exa fetch and search highlight — Labcorp User Agreement (updated 2026-07-22) bans automated collection. Quote: "use any automated means to collect information or Content from, index, crawl, or otherwise access the Online Services, including robots, spiders, or scrapers, without our prior written permission"
- P17 same agreement — Exa fetch and search highlight — Same agreement allows personal single downloads. Quote: "You may print or download a single copy of Content for your personal, non-commercial, informational use"
- P18 same agreement — Exa fetch and search highlight — Same agreement bans credential stuffing and bypassing authentication. Quote: "password mining, credential stuffing, or any other unauthorized means"
- P19 /home/user/Autonomy-Research/research/runs/engineer-browser/notes/sessions-and-hosting.md:179 — Read — Earlier run note records the hand-over pattern (John logs in, profile chmod 700, excluded from git, in permissions.deny). Quote: "(2) John logs in manually (including Google, with his own 2FA, so no script touches Google's login)"
- P20 /home/user/Autonomy-Research/research/runs/engineer-browser/notes/sessions-and-hosting.md:66 — Read — Same note says portal 2FA type is unknown. Quote: "Whether Attio, Clay, n8n, Outreach and the blood-work portal offer TOTP, passkey-only or SMS 2FA for John's accounts: unknown; ask John."

## Implications for the autonomous engineer (and the researcher plugin)

**For the engineer:**
1. **A `browser` capability ladder in the engineer's skills:** API or MCP first (the Q11 table as a checked-in
   routing file), then a Playwright flow script, then exploratory Playwright (CLI skill or MCP), then John. The
   browser is never the first choice when a route in Q11 says "no".
2. **Bootstrap additions to `scripts/bootstrap.sh`** (engineer-runtime.md):
   - Playwright and its browsers;
   - Xvfb, a minimal window manager, x11vnc bound to localhost, and noVNC with websockify;
   - a systemd unit that keeps Chrome and the display alive;
   - a fixed profile directory under the engineer user, `chmod 700`, in `.gitignore` and in `permissions.deny`
     for Read.
3. **Flow artefacts:** `flows/<app>/<task>.spec.ts`, generated by Playwright Test Agents, each with:
   - a precondition (logged-in check, check-before-create);
   - parameterised names;
   - a postcondition assertion (API read for Attio titles; fresh UI read otherwise);
   - trace on retry.

   A nightly read-only smoke run of every flow catches drift.
4. **Guardrail layer, in settings and hooks, not in prompts:**
   - deny or ask rules on `mcp__playwright__.*` and `mcp__claude-in-chrome__*` write tools;
   - a PreToolUse hook that classifies click and type targets against the never-without-approval list (Q10)
     and the domain allowlist, with `onFailure: "block"`;
   - the supervisor stops on repeated blocks, because `-p` does not.
5. **Approval digest items** gain two kinds: "fresh login needed (site, symptom, noVNC link, tasks parked)" and
   "gated browser action (site, action, target, receipt)". Both go through Channels or Remote Control.
6. **Secrets:** the TOTP wrapper returns only the six-digit code, and the seed never enters context. Google and
   portal logins are human-only.
7. **Health:** a gitignored lab-PDF inbox, a parser tested on synthetic PDFs, and a CI check that no health file
   is tracked. No portal profile on the VM.
8. **Desktop control** stays out of v1. If added, it goes in a disposable VM with a protected-path hook.

**For the researcher plugin:**
1. The notes mix "opened with WebFetch or Exa fetch" with "opened via Exa search highlights". The note schema
   should force a distinct tool label for highlight-only reads, so synthesizers and verifiers can treat them
   consistently (see Open questions, policy note).
2. The registry's research-tools row for Playwright MCP ("Last resort ... blocked by Cloudflare/Vercel bot
   checks") stays valid for headless research use. The engineer row is separate and does not override it.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Playwright CLI (@playwright/cli) | https://github.com/microsoft/playwright-cli | CLI plus skills for coding agents; ref snapshots; record and generate code; Apache-2.0 | local | 2026-10-16 | **Use**: primary driver; spike on real Attio/Clay tasks |
| Playwright MCP (engineer use, persistent profile) | https://github.com/microsoft/playwright-mcp | Accessibility-snapshot MCP, `browser_drag`, persistent profile or isolated + storage-state, extension mode; headed by default; "not a security boundary" | local stdio MCP, VM | 2026-10-16 | **Use** as alternate and for logins; always pass explicit `--user-data-dir` (default persistence contradictory) |
| Playwright Test Agents | https://playwright.dev/docs/test-agents | planner/generator/healer to .spec.ts; `init-agents --loop=claude` | local | 2026-10-16 | **Use**: record once, replay free; spike healer on drag |
| Playwright actionability + trace viewer | https://playwright.dev/docs/actionability | Auto-wait; trace on first retry | local | 2026-10-16 | **Use** as deterministic layer |
| Playwright storageState | https://playwright.dev/docs/auth | Cookie/localStorage/IndexedDB/passkey snapshot; delete when expired | local | 2026-10-16 | Fallback only; the file is a credential |
| Puppeteer | https://github.com/puppeteer/puppeteer | JS browser API; README points to chrome-devtools-mcp | local | 2026-10-16 | Skip; subsumed |
| Chrome DevTools MCP | https://github.com/ChromeDevTools/chrome-devtools-mcp | Puppeteer-based MCP + CLI; network, console, traces | local | 2026-10-16 | Fallback for network/console inspection |
| agent-browser (Vercel Labs) | https://github.com/vercel-labs/agent-browser | Rust CLI, accessibility refs | local | 2026-10-16 | Fallback; spike vs Playwright CLI |
| Stagehand | https://github.com/browserbase/stagehand | act/extract/observe, self-heal, `cacheDir` replay; server cache on Browserbase 48 h | local or Browserbase | 2026-10-16 | Fallback replay layer; own LLM key; local cache in current version unconfirmed (v3/v4 docs differ) |
| browser-use | https://github.com/browser-use/browser-use | Python agent + CLI skill; paid cloud | local or cloud | 2026-10-16 | Skip as primary (second LLM loop) |
| browser-harness | https://github.com/browser-use/browser-harness | Claude Code drives real Chrome over CDP via MCP | local | 2026-10-16 | Fallback; unvetted, spike first |
| workflow-use | https://github.com/browser-use/workflow-use/ | Record-to-JSON workflows | local | 2026-10-16 | Skip; not production-ready per maintainers |
| Skyvern | https://github.com/Skyvern-AI/skyvern | Vision-LLM agent, explore/replay to Playwright; cloud Free/$29/$149 | local server or cloud | 2026-10-16 | Skip for now |
| Magnitude browser agent | https://github.com/magnitudedev/browser-agent | Vision-first TS agent; name reused by an inference engine | local | 2026-10-16 | Reject |
| Claude in Chrome (+ safety features) | https://code.claude.com/docs/en/chrome | Logged-in visible Chrome; pauses on login/CAPTCHA; classifier, blocklists, Manually approve | John's machine | 2026-10-16 | Fallback for attended one-offs |
| Anthropic browser use tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool | API toolset, refs + coordinates; you write the executor | Claude API | 2026-10-16 | Reference design only |
| Anthropic computer use tool | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | `computer_toolset_20260801`; 1,000-1,800 tokens per screenshot | Claude API + own VM | 2026-10-16 | Fallback for desktop if Cua fails |
| Claude Code computer use (CLI) | https://code.claude.com/docs/en/computer-use | Screen control; macOS only, Pro/Max, interactive, not `-p` | John's Mac | 2026-10-16 | Not for the unattended engineer |
| Claude Desktop computer use | https://code.claude.com/docs/en/desktop | macOS/Windows; browsers view-only; Dispatch approvals 30 min | John's Mac/Windows | 2026-10-16 | Alternative on a spare machine |
| OpenClaw computer/browser tools | https://github.com/openclaw/openclaw | `computer` tool; `mcp serve` exposes only conversations (commit 58d7e878) | local/VM | 2026-10-16 | Reject as controller |
| Cua (Driver, SDK, Spaces) | https://github.com/trycua/cua | Desktop/browser driver via CLI, MCP, SDK; MIT except Spaces/Driver Bench | Mac/Win/Linux | 2026-10-16 | Spike first as optional desktop add-on |
| E2B Desktop | https://github.com/e2b-dev/desktop | Apache-2.0 Linux Xfce sandbox for computer use | E2B cloud (price not retrieved) | 2026-10-16 | Alternative sandbox |
| Bytebot | https://github.com/bytebot-ai/bytebot | Docker desktop agent | Docker | 2026-10-16 | Reject: archived 2026-03-07 |
| UI-TARS Desktop / Agent TARS | https://github.com/bytedance/UI-TARS-desktop | Apache-2.0 GUI agent app, own models | local | 2026-10-16 | Reject: separate agent |
| Agent S (Simular) | https://github.com/simular-ai/Agent-S | Research GUI agent framework | local | 2026-10-16 (search result only) | Reference only; claims unverified |
| OpenAI ChatGPT agent / Operator | https://help.openai.com/en/articles/11752874-agent | Closed hosted agent | OpenAI | 2026-10-16 (search result only) | Reject: not drivable from Claude Code |
| noVNC + websockify | https://github.com/novnc/noVNC | Browser VNC client (MPL 2.0) | VM | 2026-10-16 | **Use** behind a private network for logins and live view; spike |
| 1Password CLI service accounts | https://www.1password.dev/service-accounts/use-with-1password-cli | Vault reads incl. OTP attribute; hourly/daily limits | VM | 2026-10-16 (Exa search highlights) | Use if John has 1Password; else local seed + pyotp; spike |
| Bitwarden Secrets Manager CLI | https://bitwarden.com/help/secrets-manager-cli/ | Machine-account token CLI; no TOTP documented | VM | 2026-10-16 | Fallback for static secrets |
| Browserbase | https://www.browserbase.com/pricing | Hosted browsers, paid plans | hosted | 2026-10-16 | Skip for logged-in work |
| Steel / Anchor Browser | https://llms.anchorbrowser.io/anchor-browser-vs-steel | Hosted browsers with credential stores (vendor-authored comparison) | hosted / Docker | 2026-10-16 (Exa search highlights) | Skip; reference only |
| Hyperbrowser / Browserless | https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/ | Hosted browsers; stealth/CAPTCHA features | hosted | 2026-10-16 (third-party page, Exa search highlights) | Reject (evasion focus) |
| Stealth plugins, CAPTCHA solvers, residential proxies | https://github.com/blhutchings/google-login-service | Bot-detection evasion | n/a | 2026-10-16 (Exa search highlights) | Rejected as evasion; not evaluated |
| Claude Code PreToolUse hooks + MCP permission rules | https://code.claude.com/docs/en/hooks | Deny/ask browser MCP calls; deny beats hook; timed-out hook does not block by default | Claude Code | 2026-10-16 | **Build point** for the guardrail layer; spike `tool_input` |
| Checkly Playwright monitors | https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/ | Scheduled Playwright checks against production | hosted, paid (price not checked) | 2026-10-16 | Fallback; self-host a cron smoke run first |
| Simon Willison lethal trifecta | https://simonwillison.net/2025/jun/16/the-lethal-trifecta/ | Threat model for agent design | n/a | 2026-10-16 | Use as design rule |
| ComponentBench | https://arxiv.org/html/2608.18307 | Component-level benchmark; AX-tree vs pixel vs DOM actions | dataset (not run) | 2026-10-16 | Evidence; possible drag-spike harness |
| Online-Mind2Web boards (Steel, HAL) | https://leaderboard.steel.dev/leaderboards/online-mind2web/ | Live-web benchmark boards | web | 2026-10-16 | Evidence only |
| Attio REST API (views/workflows check) | https://api.attio.com/openapi/api | 53 paths; views GET-only; no workflow routes; data-model writes | hosted | 2026-10-16 | Use for data model; browser for views and Workflows |
| Attio MCP (re-checked) | https://docs.attio.com/mcp/overview.md | OAuth hosted; create-list, records; no attribute/view/workflow tool | hosted | 2026-10-16 | Use for records and lists |
| Clay agent plugin + CLI | https://github.com/clay-run/agent-plugins | Workflows (Alpha), searches, signals, campaigns; no table creation | Claude Code with shell | 2026-10-16 | Use; tables and columns stay UI |
| n8n public API handlers (master) | https://github.com/n8n-io/n8n | Community packages, credentials, variables, tags, projects, SSO routes (commit 21221ad) | self-hosted/cloud | 2026-10-16 | Use; confirm release and Cloud availability |
| Outreach MCP server | https://developers.outreach.io/mcp-server | OAuth, RBAC inherited, `sequence_create` | hosted | 2026-10-16 | Use for sequences; REST for templates and mailboxes |
| WHOOP developer API | https://developer.whoop.com/docs/developing/getting-started | OAuth2, offline-scope refresh, 100 req/min | hosted | 2026-10-16 | Use after one-time registration and consent |
| Withings Public API | https://developer.withings.com/developer-guide/v3/get-access/sign-up-for-a-developer-account | OAuth2 web flow; membership rule for newer accounts | hosted | 2026-10-16 | Use; check plan terms |
| Labcorp User Agreement | https://www.labcorp.com/compliance/privacy/privacy-notice/online-services-user-agreement | Bans robots/scrapers without permission; allows personal downloads | n/a | 2026-10-16 | No unattended portal login |
| Epic on FHIR patient-facing SMART app | https://open.epic.com/DeveloperResources | Self-service client IDs; per-health-system patient OAuth; sandbox forbids real PHI | Epic customers | 2026-10-16 | Fallback for MyChart labs |
| Fasten OnPrem | https://github.com/fastenhealth/fasten-onprem/ | Archived self-hosted FHIR viewer; no provider import | Docker | 2026-10-16 | Reject as puller |
| Fasten Connect | https://docs.connect.fastenhealth.com/quickstart | Commercial patient-authorized records API; TEFCA live fees; sandbox claim from search highlight | hosted | 2026-10-16 (TEFCA page opened; quickstart search highlight) | Fallback; ask about individual live account |
| Flexpa | https://www.flexpa.com/pricing | Patient-consented FHIR API; live access via demo request; price seen only in search highlights | hosted | 2026-10-16 (getting-started opened; pricing search highlight) | Reject pending price check (demo-gated; price unverified) |
| 1upHealth / Metriport / Health Gorilla / Particle | https://docs.1up.health/docs/get-started/third-party-apps | Sales- or vetting-gated aggregators | hosted | 2026-10-16 (search highlights only) | Reject for solo use; unverified |
| Android Health Connect Medical Records | https://developer.android.com/health-and-fitness/health-connect/medical-records | On-phone FHIR store; Play policy still being developed | Android | 2026-10-16 | Skip |
| Apple Health clinical-records export | https://www.johngoldin.com/blog/apple-health-export/2020-02-apple-health-export1/index.en.html | export.zip with FHIR JSON clinical records (2020 blog) | iPhone then local parse | 2026-10-16 (search highlight only) | Use if John has an iPhone; spike; source unverified |
| tomhallmain/health_data_parser | https://github.com/tomhallmain/health_data_parser | Parses Apple Health clinical lab records to CSV/JSON | local Python (not run) | 2026-10-16 (search highlight only) | Reference only; do not run on real data unvetted |
| trumpetsherald/HealthKitGrafana | https://github.com/trumpetsherald/HealthKitGrafana | Loads Apple Health export and Labcorp lab files into Postgres | Docker (not run) | 2026-10-16 (search highlight only) | Reference only |

## Open questions

**Policy note.** Some claims the notes list as "opened" were read through Exa search highlights or Exa search
page content, not a full fetch. Examples: the Cloudflare pages, the 1Password docs, Attio's acceptable-use
page, the Clay blog, Outreach's acceptable-use policy, the hosted-browser comparisons, and several benchmark
pages. They are kept in Evidence with that tool label, following the precedent in engineer-existing-systems.md.
The verifier should sample them first. Claims a note marks as "search result only", "via Exa search highlight
(page not re-fetched)", "not opened" or "search highlights only (not cited)" are excluded below.

**Excluded claims (no opened source; search result or highlight only). Count: 34.**
1. Sonnet 5.5 at $2/$10 per million tokens (https://www.vellum.ai/llm-leaderboard): search result only.
2. benchgap: Sonnet 5.5 at 85.6% and Opus 5.5 at 85.2% on OSWorld-Verified, "estimated ± 6.5 pp"
   (https://benchgap.net/b/osworld-verified/current): search result only. The Sonnet 5.5 system card was not
   opened, so the official figure is unknown.
3. Steel's note that Anthropic's "revised harness" makes older and newer OSWorld scores "not directly
   comparable": Steel search excerpt only.
4. Cua sandboxes run locally (gVisor, runc, QEMU, Lume) or in the cloud (https://cua.ai/,
   https://cua.ai/docs/cua-sdk/concepts/how-sandboxes-work): search result only.
5. Agent S3 at 72.6% on OSWorld with best-of-N (https://github.com/simular-ai/Agent-S): search result only.
6. Agent S3 at 69.9% (Simular blog, 2025-10-02): search result only. The 69.9% versus 72.6% "contradiction" is
   therefore not recorded.
7. "ChatGPT agent is no longer available" (https://help.openai.com/en/articles/11752874-agent): search result
   only.
8. Issue #97660, an auto-mode sub-agent deleting about 125 GB from the C: drive
   (https://nope.net/incidents/2026-claude-code-sub-agent-auto-mode-recursive-delete-wiped-windows-drive-root-about-125-gb-first-person):
   search result only.
9. An end-to-end exploit of OpenAI Operator to RCE through visual prompt injection
   (https://arxiv.org/html/2507.05445): search result only.
10. LayerX flaw in Claude's Chrome extension (IANS write-up, 2026-05-14): search result only.
11. outreach.as/terms "spiders, crawlers, or scrapers" clause (Resonate, not Outreach): Exa highlights, not
    listed as opened.
12. Stagehand v4: the cache needs a Browserbase browser and has no effect locally
    (https://docs.stagehand.dev/v4/basics/act): highlight only (see Q9).
13. Anthropic Aug 2025 pilot: 23.6% attack success without mitigations, 11.2% with; confirmations for
    publishing and purchasing (https://claude.com/resources/articles/claude-for-chrome): highlight only.
14. Help centre figure of "less than 0.08%" attack success for Opus 4.8: the page was opened, but the note gives
    no quote for the figure.
15. GA post figure of 0 to 0.3% on newer models: the page was opened, but the note gives no quote for the
    figure.
16. Brave on Comet (https://brave.com/blog/comet-prompt-injection/): sensitive actions such as sending email
    need confirmation. Highlight only.
17. Tom's Hardware on PocketOS: an agent deleted a production database and backups via the Railway API in
    9 seconds. Highlight only. The reliability note's "per the PocketOS incident" inference therefore rests on
    an unopened source.
18. parsercheat.com postcondition-before-replay article: not opened.
19. OpenAI Atlas lines on confirmations for purchases and email and on logged-out mode: highlight only (the
    fetched text was truncated before them).
20. A third-party issue-thread comment that PreToolUse hooks fire on Playwright MCP tools: not opened.
21. Apple Health export format, where export.xml ClinicalRecord elements point to FHIR JSON
    (https://www.johngoldin.com/blog/apple-health-export/2020-02-apple-health-export1/index.en.html): search
    highlight only, from a 2020 blog.
22. tomhallmain/health_data_parser turns the export into lab CSV/JSON: search highlight only.
23. trumpetsherald/HealthKitGrafana loads lab DiagnosticReport files into Postgres: search highlight only.
24. ONC: "any individual can authorize apps of their choice ... without any additional or out-of-band steps"
    (https://healthit.gov/certification-health-it/conditions-ccg/application-programming-interfaces/): highlight
    only.
25. ONC: no BAA is needed for patient-chosen apps (same URL): highlight only.
26. Epic: "over 500 patient-authorized health apps have connected ... in 2025"
    (https://open.epic.com/DesignOverview): highlight only.
27. Epic issues production and non-production client IDs by form
    (https://fhir.epic.com/Documentation?docId=patient_facing_apps): highlight only.
28. Health Connect permission `READ_MEDICAL_DATA_LABORATORY_RESULTS`
    (https://developer.android.com/health-and-fitness/health-connect/medical-records/read-data): highlight
    only.
29. Fasten Connect "Free developer sandbox" and test-mode limits (https://docs.connect.fastenhealth.com/quickstart):
    highlight only.
30. Flexpa pricing "$20,000/year" Startup tier and MCP tiers (https://www.flexpa.com/pricing): highlight only.
31. Flexpa "We do not have a free plan for live mode" (getting-started page): highlight only. The opened page
    shows only "Start at flexpa.com/demo".
32. 1upHealth: "Developer requests production access", plus the saasworthy price listing: highlight or
    third-party only.
33. Metriport (repo, Fierce 2023, its blog on network agreements), Health Gorilla ("Submit a request via our
    contact page") and Particle ("See if you qualify for production access"): highlights only.
34. Labcorp spotlight viewer terms banning "trawl, mine, scrape"
    (https://www.labcorp.com/labcorp-spotlight-viewer-terms-conditions): highlight only.

Also not carried as findings:
- the Magnitude to sagekit redirect (a LibHunt snippet);
- E2B Desktop pricing (the page "doesn't mention E2B pricing");
- the "Gmail connector" route for email codes (the worker says it is not independently sourced);
- the HAL 40.00% and 42.33% figures and the BU Bench Opus 4.6 and Sonnet 4.6 figures, which appear in the
  notes' claims but not in their quotes.

**Gaps (from the notes; pages not opened or not researched):**
- Release cadence and last-commit dates for every candidate repo: the GitHub API was blocked. Star counts are
  single-day snapshots from Exa metadata.
- No benchmark or published example on Attio or Clay UIs. No "create a view in the Attio UI, then read it via
  the API" or "create a Clay column, then read the table" example.
- WebArena-Verified numbers come from aggregators, not the paper. Mind2Web (original), BrowserGym and WorkArena
  were not opened.
- No opened source on the screenshot token cost per step inside Claude Code, or on latency per step for Claude
  in Chrome or computer use.
- The Playwright healer on drag and drop and canvas-like tables; Stagehand's local cache with the `LOCAL` env
  and a Claude model.
- Whether Claude in Chrome can run unattended on a headed VM display. This is runtime open question 30, still
  open.
- Whether OpenClaw's `computer` tool can be exposed through a plugin. Advisories specific to the computer tool.
- Cua Driver on headless Linux (display, accessibility tree). E2B and Cua pricing. Browser Use desktop.
- Whether Withings or WHOOP pairing works on an emulator.
- Real session lifetimes for Attio, Clay, n8n, Outreach, Google and the portal. Whether Playwright MCP's
  profile survives MCP restarts (see the Q1 contradiction).
- The two-factor types on John's accounts (ask John). Passkeys in headed Chrome on a Linux VM with no
  authenticator.
- Bitwarden Secrets Manager TOTP, Infisical and pass: not opened.
- Cloudflare Turnstile treatment of a headed automated Chrome with a real profile: the concepts page held no
  detail. No source on bot protection at the Attio, Clay or Outreach logins.
- Clay terms beyond the first 8,000 characters (https://www.clay.com/terms returned 404). Outreach's signed
  master agreement is not public, and the outreach.ai terms came through a summarising fetch.
- Terms for the blood-work portal, Quest/MyQuest and Function, and Google's terms beyond the sign-in help page.
- Hyperbrowser, Browserless, Anchor and Steel primary pricing pages. Hosted-vendor data handling beyond
  Browserbase retention.
- x11vnc and Xvfb docs: not opened, so the install and hardening steps are worker inference.
- No standard "fresh login request" message format. Whether the approval channel can carry a live noVNC link
  with an expiry.
- The Claude in Chrome permissions guide (the exact list of high-risk actions). Whether PreToolUse hooks fire
  on `mcp__claude-in-chrome__*`. No source for destructive-button detection that works across SaaS UIs.
- The ASE paper's 82.7% LLM fix rate: the text was truncated, so it is not quoted.
- How often Attio or Clay change their UI. Checkly pricing. No documented self-hosted Playwright-plus-cron
  recipe.
- Which Clay UI clicks consume credits. App-store submission flows.
- The Attio App SDK block at John's org; Attio's "Ask Attio" AI automation features; a live Attio MCP
  tools/list.
- Clay: John's plan (Enterprise?); the Clay MCP connector's tool list; inbound table-webhook sources;
  Workflows (Alpha) rate and credit limits.
- n8n: whether the master-branch routes are in John's release; the community-package route on Cloud; whether
  API keys are created in the UI; scopes; variables on non-Enterprise plans.
- Outreach: sequence-step routes, scope names and rate limits; admin approval and John's role.
- Withings plan details (JS page unreadable); WHOOP webhooks and Withings notifications.
- Whether Quest or Labcorp offer an official patient FHIR endpoint. Fasten's Quest client could not be cloned
  (it needed credentials).
- Whether John has an iPhone, which lab he uses, and whether a doctor or a direct-to-consumer service ordered
  the tests.
- Apple Health Records institutions and iOS 2026 export changes. Epic auto-distribution criteria for a
  one-person developer. Blue Button. A direct-to-individual TEFCA route. Fasten Connect, 1up, Health Gorilla
  and Particle current prices. HIPAA or other law on PHI on a personal VM.

**Unresolved contradictions carried from the answers:**
- Playwright MCP default persistence: persistent by default versus a temporary directory if none is given (Q1).
- Playwright CLI versus MCP token cost across February, April and July 2026 (Q4).
- Stagehand v3 versus v4 local caching (Q9).
- Whether Labcorp's automation ban extends to Quest and Function (Q12).
- 2025 versus 2026 Online-Mind2Web scores (Q2): favoured as vendor claims, but not settled for John's apps.

**Open questions from the existing-systems run (research/open-questions.md):**
- Attio views GET-only: **settled** (Q13.1).
- `webhook:read` for listing webhooks: **answered by the worker without a verbatim quote**; needs verifier
  confirmation (Q13.2).
- Clay export of table contents and enrichment column settings: **partly settled**. Official routes cannot
  create tables and read rows only on Enterprise; column-settings export is still unknown (Q13.3).
- Where John's GTM configuration lives: **not settled**; it needs John (Q13.4).

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 cited claims.
Verified: 19. Unverified: 1.
- Unverified: Attio webhooks are workspace-level tokens only ("Supported token levels: `workspace`") — https://api.attio.com/openapi/api (POST /v2/webhooks, A8) — the POST scope line "Required scopes: `webhook:read-write`" was confirmed, but the token-level line was not returned in the chunks read, so uncertain.
