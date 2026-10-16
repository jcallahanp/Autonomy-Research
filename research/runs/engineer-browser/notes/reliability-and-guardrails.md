# Reliability engineering and safety guardrails for UI automation

Brief: Find the patterns that make an agent's UI changes in production SaaS apps reliable and safe when no human watches.
Run: research/runs/engineer-browser/PLAN.md

Connectors note: Parallel Search returned "Too Many Requests" on both calls; Exa and WebFetch were used instead.

## Reliability patterns (waits, retries, self-healing, traces, idempotency)

### Takeaway
Use Playwright's built-in actionability auto-waits and trace-on-first-retry as the deterministic layer; use LLM repair (Stagehand-style cache then re-infer) only as a fallback; make every mutation idempotent via check-before-create and never blind-retry a click that may have committed. Confidence: medium-high (patterns well sourced; no published head-to-head of LLM self-healing on Attio/Clay).

### Cited findings
- Playwright auto-waits for actionability checks (visible, stable, receives events, enabled) before acting, so sleeps are unnecessary — https://playwright.dev/docs/actionability, opened 2026-10-16, WebFetch — Quote: "auto-waits for all the relevant checks to pass and only then performs the requested action."
- Playwright docs recommend recording traces only on first retry; trace.zip holds per-step DOM snapshots, network, console — https://playwright.dev/docs/trace-viewer-intro, opened 2026-10-16, WebFetch — Quote: "record traces on first retry of each test"
- Stagehand replays a cached action deterministically and falls back to LLM inference if the selector no longer resolves — https://docs.stagehand.dev/v4/best-practices/caching, opened 2026-10-16, WebFetch — Quote: "If the recorded selector no longer resolves, Stagehand falls back to full inference."
- Retries around mutations are unsafe without an idempotency token; an "ambiguous" state must be reconciled before retry — https://dev.to/harshithvaddiparthy/designing-browser-agents-that-dont-double-post-state-idempotency-and-verification-3be, opened 2026-10-16, WebFetch — Quote: "They are unsafe around mutations unless the destination supports a genuine idempotency token."
- Same source: ambiguous outcome definition — same URL, opened 2026-10-16, WebFetch — Quote: "It means the system attempted a mutation but could not prove whether the external effect occurred."
- Same source: agent should stop rather than guess — same URL, opened 2026-10-16, WebFetch — Quote: "refuse to guess when an external effect is at stake"
- Claude Code docs: PreToolUse hooks can deny MCP browser tool calls; MCP matcher needs `.*` — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch — Quote: "To match every tool from a server, append `.*` to the server prefix."

### Contradictions
- Stagehand v4 docs say the cache needs a Browserbase browser and has no effect locally — https://docs.stagehand.dev/v4/basics/act (via Exa highlight); v3 docs show local `cacheDir` caching — https://docs.stagehand.dev/v3/basics/act (Exa highlight). Version change; verify against the installed version before relying on local caching. Neither page was fully opened with WebFetch beyond the caching page.

### Inferences
- (Mine) For a Claude Code engineer the equivalent of Stagehand caching is a recorded Playwright script per SaaS flow, with the agent regenerating the script when it fails and a postcondition check (next question) deciding success. This rests on the Stagehand replay-then-infer pattern and the idempotency findings.
- (Mine) Never put a generic retry decorator around a create/submit step; retry only observation steps, which matches the dev.to guidance.

### Gaps
- No published measurement of LLM self-healing success on Attio or Clay UIs; needs a spike.
- Stagehand cache behavior with a local browser in the current version not confirmed from source (not cloned).

## Verification after a UI action (act in UI, verify through API)

### Takeaway
Treat the UI click as unproven until an independent read confirms the postcondition (API record, list view, confirmation event); toasts and screenshots are weak evidence. Published examples are generic (not Attio/Clay-specific), so the Attio-view and Clay-column checks must be designed in the spike. Confidence: medium.

### Cited findings
- The dev.to design verifies "exact normalized text ... canonical URL" per action type before marking verified — https://dev.to/harshithvaddiparthy/designing-browser-agents-that-dont-double-post-state-idempotency-and-verification-3be, opened 2026-10-16, WebFetch — Quote: "refuse to guess when an external effect is at stake"
- Attio REST API can read objects, attributes, lists, entries and view titles (so a UI-created view can be read back) — /home/user/Autonomy-Research/research/tool-registry.md:122, read 2026-10-16, Read — Quote: "Reads objects, attributes, lists, entries, view titles, webhooks, read-only SQL"
- Registry notes the Attio API/MCP have gaps for views and workflows — /home/user/Autonomy-Research/research/tool-registry.md:123, read 2026-10-16, Read — Quote: "no view or workflow tool"
- Clay tables are only queryable by API on Enterprise — /home/user/Autonomy-Research/research/tool-registry.md:124, read 2026-10-16, Read — Quote: "tables Enterprise only"

### Contradictions
- None found.

### Inferences
- (Mine) Attio: after creating a view in the UI, list view titles via the REST API and assert exactly one matches the intended name (also serves as the idempotency pre-check). View filters/sort may not be readable via API per registry row; fall back to a fresh UI read plus screenshot compared to the intended spec.
- (Mine) Clay: without Enterprise table query, verification of a new column must be a fresh UI read of the table schema (or the claycast unofficial API, rejected for production), so Clay is the weaker link; mark Clay UI writes as verify-by-UI-reread only.

### Gaps
- No published "create view in Attio UI then read via API" or "create Clay column then read table" example found.
- parsercheat.com page not opened with a fetch tool; its claims are not cited as findings.

## Failure data and drift detection

### Takeaway
UI test breakage after front-end change is persistent and not fixable once: in an ASE 2025 study 81.7% of repaired tests broke again within six months. Drift detection in practice is scheduled production runs with traces, screenshots and golden-image diffs. LLM repair works well when given diagnostic context. Confidence: medium (one academic study on Mind2Web-derived tests; not SaaS-admin-UI specific).

### Cited findings
- 81.7% of repaired web GUI tests broke again within six months — https://kdyao.github.io/resources/papers/ASE2025_Haonan.pdf, opened 2026-10-16, Exa fetch — Quote: "81.7% of repaired tests break again within six months, primarily due to similar recurring issues"
- LLMs with diagnostic context can repair many brittle tests, humans still needed for complex ones — same URL, opened 2026-10-16, Exa fetch — Quote: "Large Language Models, when provided with human-like diagnostic context, can successfully repair a substantial portion of these brittle tests"
- Brittleness is a persistent maintenance cost that leads teams to rewrite suites — same URL, Exa fetch — Quote: "many organizations opt to abandon and rewrite their test suites entirely"
- Checkly runs Playwright visual-regression tests against production on a schedule and shows a golden-image diff — https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/, opened 2026-10-16, WebFetch — Quote: "With Checkly, you can run these tests against production, 24x7."

### Contradictions
- None found.

### Inferences
- (Mine) 82.7% LLM fix rate figure appears in the same paper but the fetched text I opened was truncated before it; do not quote it. The abstract supports "a substantial portion".
- (Mine) Cheapest drift detection for John: a nightly (or per-run pre-flight) read-only smoke script per SaaS flow that asserts key locators and takes a trace; self-hosted via a cron/routine, Checkly only if a hosted dashboard is wanted (paid, price not checked).

### Gaps
- No data on how often Attio or Clay specifically change their UI; no vendor changelog cadence read.
- Checkly pricing not checked; self-hosted equivalent (Playwright + cron + alert) not found as a documented recipe.

## Safety guardrails and what Claude Code / Claude in Chrome provide natively

### Takeaway
Claude in Chrome natively gives site permissions inherited from the extension, a prompt-injection probe on page content, a per-action classifier, site blocklists and confirmations for high-risk actions, but it is local, uses the real logged-in browser and the vendor says the risk is not zero. Claude Code gives permission rules (deny first, MCP tool globs), auto-mode classifier blocks, and PreToolUse hooks that can deny browser MCP clicks in any mode; domain allowlists, per-profile separation, destructive-button detection and "read-only browser" must be built. Confidence: high on features, medium on effectiveness.

### Cited findings
- Chrome integration shares login state and runs in a visible window; pauses on login/CAPTCHA — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Claude opens new tabs for browser tasks and shares your browser's login state, so it can access any site you're already signed into."
- Site permissions come from the extension; auto-mode classifier approval can skip the per-site check unless a deny rule exists — same URL — Quote: "Site-level permissions are inherited from the Chrome extension."
- Chrome integration is off under API-key/setup-token auth — same URL — Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`"
- A project cannot turn on Chrome integration itself — same URL — Quote: "a repository you check out must not be able to connect Claude to your browser."
- Anthropic Nov 2025: even a 1% success rate is meaningful — https://www.anthropic.com/research/prompt-injection-defenses, opened 2026-10-16, WebFetch — Quote: "A 1% attack success rate—while a significant improvement—still represents meaningful risk."
- Aug 2026 GA post: classifier checks actions against the original request — https://claude.com/resources/articles/claude-in-chrome-generally-available, opened 2026-10-16, WebFetch — Quote: "If the action doesn't match your request, it's blocked."
- Help center: classifiers, blocklists, confirmations, manual approve mode, and an explicit recommendation for a separate profile — https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely, opened 2026-10-16, WebFetch — Quote: "consider using a separate browser profile without access to sensitive accounts."
- Same page: Manually-approve mode exists — same URL — Quote: "Switch to \"Manually approve\" if you want to review every action."
- Claude Code permissions: deny evaluated first; allow globs on MCP require a literal server prefix; `mcp__*` deny removes all MCP tools — https://code.claude.com/docs/en/permissions, opened 2026-10-16, WebFetch (grep of saved page) — Quote: "Rules are evaluated in order: deny, then ask, then allow."
- Hooks cannot be weakened by permission rules in reverse: a PreToolUse hook cannot override deny/ask rules — https://code.claude.com/docs/en/permissions — Quote: "Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns"
- PreToolUse hook can deny a tool call; a timed-out hook does not block unless `onFailure: "block"` — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch — Quote: "A timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call."
- Auto mode blocks by default production deploys and mass deletion, but this list is about shell/infra, not browser UI clicks — https://code.claude.com/docs/en/permission-modes, opened 2026-10-16, WebFetch (grep of saved page) — Quote: "Mass deletion on cloud storage"
- In `-p` runs with no prompt, repeated classifier blocks do not stop the run — same URL — Quote: "When repeated blocks reach a threshold, the action doesn't run and Claude keeps working. Claude Code doesn't stop the run."
- `bypassPermissions` gives no injection protection — same URL — Quote: "`bypassPermissions` offers no protection against prompt injection or unintended actions."
- Playwright MCP origin allowlist is not a security boundary; offers isolated in-memory profile and opt-in caps — https://github.com/microsoft/playwright-mcp, opened 2026-10-16, WebFetch — Quote: "Playwright MCP is not a security boundary."
- Simon Willison's trifecta: avoid private data + untrusted content + external communication together — https://simonwillison.net/2025/jun/16/the-lethal-trifecta/, opened 2026-10-16, WebFetch — Quote: "The only way to stay safe there is to avoid that lethal trifecta combination entirely."
- OpenAI Atlas: prompt injection remains open; confirmations for consequential actions; recommends logged-out mode — https://openai.com/index/hardening-atlas-against-prompt-injection/, opened 2026-10-16, Exa fetch — Quote: "prompt injection remains an open challenge for agent security, and one we expect to continue working on for years to come."
- Real incident: Claude clicked "Delete" confirm on a production record via browser automation with Accept Edits on (reporter's claim; issue closed not planned) — https://github.com/anthropics/claude-code/issues/65563, opened 2026-10-16, WebFetch — Quote: "Accept Edits was ON (auto-accepting changes)"
  Same page: "The record was permanently deleted from the production Supabase database."

### Contradictions
- Anthropic Aug 2025 post reports 11.2% attack success with mitigations — https://claude.com/resources/articles/claude-for-chrome (highlight); Help Center says "less than 0.08%" for Opus 4.8 with current config; GA post (Aug 2026) reports 0 to 0.3% on newer models. Different models, eval sets and dates, not a conflict, but the numbers are vendor-internal evaluations and not comparable. Treat all as optimistic upper-bound-of-trust.

### Inferences
- (Mine) Native versus build table for the engineer:
  - Native, use: Chrome extension site permissions; injection probes and action classifier; Claude Code deny/ask/allow rules incl. `mcp__claude-in-chrome__*` globs; managed `deniedMcpServers`; PreToolUse hooks; project cannot self-enable Chrome.
  - Must build: a hook that denies browser clicks/typing whose target text matches delete/send/pay/publish/submit (needs payload inspection; spike the real `tool_input` fields); a domain allowlist hook on navigate calls; a dedicated Chrome profile for the engineer with only the SaaS apps John allows; staging/sandbox workspace use; a read-only recon mode (snapshot/read tools only); action receipt log; stop conditions for credential/state mismatch.
- (Mine) Claude in Chrome is local, needs subscription login, and is visible; for unattended runs a separate Playwright-driven profile with a saved storage state, scripted flows and a hook gate is more controllable, but this has no vendor safety classifier, so scripted (not free-form agentic) flows for production writes lower injection exposure. Based on the Chrome docs, Playwright MCP caveat and Willison's trifecta.
- (Mine) Auto mode in `-p` does not halt on repeated blocks, so the supervisor must enforce stop conditions.

### Gaps
- Claude in Chrome "permissions guide" page (support.claude.com) not opened; exact list of "high-risk actions" requiring confirmation not confirmed. Help center only says "certain high-risk actions" (file downloads, sensitive data entry per fetch summary).
- Whether Claude Code PreToolUse hooks fire on `mcp__claude-in-chrome__*` tools not tested (the issue-thread claim is for Playwright MCP, by a third-party commenter, not opened as a verified source).
- Brave, Anthropic GA early-2025 post, Tom's Hardware pages known only from search highlights; not cited as findings.
- No source found for page-content-based destructive-button detection that works across SaaS UIs.

## Actions never allowed without John's approval

### Takeaway
Map to his hard gates: any browser action that spends money (purchase, plan upgrade, add seats, credits top-up, pay-per-enrichment runs), deletes or irreversibly overwrites data (delete view/column/table/record, bulk merge, workspace deletion), or submits to an app store, plus sends/publishes externally (email sequences, enrolments, posts), changes sharing/permissions or credentials, and anything on financial/sensitive sites. These need an approval gate outside the model (hook + push approval), not just the model's own confirmation. Confidence: medium (policy inference grounded in sources).

### Cited findings
- OpenAI describes the exposure surface for browser agents — https://openai.com/index/hardening-atlas-against-prompt-injection/, opened 2026-10-16, Exa fetch — Quote: "the agent may encounter untrusted instructions across an effectively unbounded surface area"
- Claude Code Chrome docs: Claude pauses on login/CAPTCHA for the human — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- Incident evidence of an unconfirmed delete click and destructive API call — https://github.com/anthropics/claude-code/issues/65563, opened 2026-10-16, WebFetch — Quote: "The record was permanently deleted from the production Supabase database."
- Remote Control, Channels give live approvals from phone — /home/user/Autonomy-Research/research/tool-registry.md:54,56, read 2026-10-16, Read — Quote: "Use for browser logins, monitoring and live approvals"

### Contradictions
- None found.

### Inferences
- (Mine) Never-without-approval list for the engineer in a browser: (1) money: checkout, upgrade/downgrade plan, buy credits, add seat, enable paid enrichment/credit-consuming runs in Clay, enable auto-recharge; (2) deletion: delete/archive/merge/bulk-update of records, views, columns, tables, sequences, workflows, workspaces, integrations; revoking API keys; (3) app store: submit for review, change pricing/availability, release; (4) outbound: sending email, activating Outreach sequences or enrolments, publishing, posting, inviting users; (5) credentials/permissions: creating API keys, OAuth grants, sharing, role changes; (6) anything on banking/healthcare/government domains or password managers. Edits that are additive and reversible on a named staging copy (create a view, add a column) may be allowed with the receipt + verify pattern.
- (Mine) Enforce with layers: allowlisted domains and a dedicated profile (prevents wrong-site), hook-level deny of destructive-class clicks (prevents mode bypass, per the Accept-Edits incident), approval relay to John via Remote Control/Channels, and a supervisor that treats credential/state mismatch as stop (per the PocketOS incident).

### Gaps
- Exact Clay credit-consumption triggers in the UI (which clicks spend credits) not researched.
- App-store submission UI flows (App Store Connect, Play Console) not researched; the gate is by policy only.

## Recommendation, alternatives, rejected, spikes

- Recommendation: Drive SaaS UI changes with recorded, locator-based Playwright scripts (agent-authored, replayed deterministically) in a dedicated browser profile, with Claude Code as engineer; wrap with (a) PreToolUse deny/ask hooks on destructive/payment/send/publish targets and non-allowlisted domains, (b) check-before-create and action receipts, (c) post-action API or fresh-read verification, (d) trace/screenshot on failure and a scheduled read-only smoke run for drift, (e) approval relay to John for gated actions. Free and self-hosted.
- Alternatives: Claude in Chrome for attended work (native classifier, but real logged-in profile and local); Stagehand with Browserbase cache (paid cloud for caching, price not checked); Checkly hosted monitors (paid, price not checked).
- Rejected: `bypassPermissions` or Accept-Edits for any browser session touching production (no injection protection; incident #65563); blind retry decorators around submits; relying on Playwright MCP origin allowlist as a boundary (its docs say it is not one); using the model's own confirmation as the only gate.
- Spike before building: (1) do PreToolUse hooks fire and expose usable `tool_input` for `mcp__claude-in-chrome__*` and Playwright MCP click/type; (2) Attio view create-then-API-read round trip incl. filters; (3) Clay column create and verify without Enterprise API; (4) LLM repair rate when a locator breaks, on John's own flows; (5) saved storage-state login lifetime for Attio/Clay unattended.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Playwright actionability, trace viewer, retries | https://playwright.dev/docs/actionability | Auto-waiting, trace on first retry, retries | local | 2026-10-16 | Use as the deterministic layer |
| Stagehand caching/self-heal | https://docs.stagehand.dev/v4/best-practices/caching | Cached act() replay with LLM re-inference fallback; server cache needs Browserbase (per search highlight) | Browserbase or local | 2026-10-16 | Reference pattern; adopt only if needed; paid cache not justified before spike |
| Playwright MCP | https://github.com/microsoft/playwright-mcp | Isolated profile, origin allow/block lists | local | 2026-10-16 | Use with hooks; docs say not a security boundary |
| Claude in Chrome safety features | https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely | Classifiers, blocklists, confirmations, manual approve | John's machine | 2026-10-16 | Use for attended work; not sole guard |
| Claude Code PreToolUse hooks + permission rules for MCP | https://code.claude.com/docs/en/hooks | Deny/ask browser MCP calls in any mode | Claude Code | 2026-10-16 | Use as the build point for the guardrail layer; spike payload fields |
| Checkly Playwright monitors | https://www.checklyhq.com/docs/detect/synthetic-monitoring/browser-checks/visual-regressions/ | Hosted scheduled Playwright checks with visual diffs | hosted, paid (price not checked) | 2026-10-16 | Fallback; self-host a cron smoke run first |
| Simon Willison lethal trifecta | https://simonwillison.net/2025/jun/16/the-lethal-trifecta/ | Threat model for agent design | n/a | 2026-10-16 | Use as design rule |

## Moved to Gaps (known only from search highlights, not opened as pages)
- Anthropic Aug 2025 pilot post (https://claude.com/resources/articles/claude-for-chrome): 23.6% attack success without mitigations, 11.2% with; confirmations for publishing/purchasing.
- Brave Comet post (https://brave.com/blog/comet-prompt-injection/): sensitive actions such as sending email need explicit user confirmation.
- Tom's Hardware PocketOS write-up: agent deleted production DB and backups via Railway API in 9 seconds.
- parsercheat.com postcondition-before-replay article; Stagehand ActCache.ts source (not cloned); Stagehand local-browser cache limitation.
- OpenAI Atlas page: the confirmation-for-purchases/email and logged-out-mode lines were visible only in a search highlight (fetched text was truncated before them).
