# Logged-in sessions, two-factor, bot detection, terms, and where the browser runs

Brief: Work out how an unattended engineer keeps John's logins (Attio, Clay, n8n, Outreach on a company account, a blood-work portal, Google) working for weeks, and where its browser should run.
Run: research/runs/engineer-browser/PLAN.md

Recommendation (one line): run a headed Chrome with a dedicated persistent `--user-data-dir` on the engineer's own Ubuntu VM inside an Xvfb + VNC/noVNC desktop reached over a private network (Tailscale), driven by Playwright MCP in persistent-profile mode; John logs in once through noVNC; TOTP-capable accounts get a vault-held seed generated outside the model; API/MCP first for Attio, Clay, n8n, Outreach so the browser is the fallback; Google and the blood-work portal stay human-in-the-loop. Spikes listed at the end of Q6.

## Q1 Persistent profiles vs storage-state, headed vs headless, session life, re-login detection

### Takeaway
Use a persistent profile directory (Playwright MCP default, `--user-data-dir`) rather than a storage-state file for a weeks-long headed setup: it keeps cookies, localStorage, IndexedDB and everything else the browser holds, while storage-state is a snapshot that explicitly misses sessionStorage and must be deleted when it expires. Session lifetime is set by each site, not by Playwright; no source found gives weeks-long figures for the named apps, so re-login must be detected by the engineer (login-page URL or element check) and escalated. Confidence: medium-high on mechanics, low on lifetimes.

### Cited findings
- Playwright MCP persists a profile on disk by default; `--isolated` keeps it in memory; `--storage-state` only applies to isolated sessions — https://github.com/microsoft/playwright-mcp, opened 2026-10-16, WebFetch (summarised) — Quote: "path to the storage state file for isolated sessions."
- The same README documents the profile locations and that a custom directory is possible — https://github.com/microsoft/playwright-mcp, opened 2026-10-16, WebFetch — Quote: "path to the user data directory. If not specified, a temporary directory will be created."
- Extension mode connects to an existing Chrome/Edge to reuse logged-in tabs — https://github.com/microsoft/playwright-mcp, opened 2026-10-16, WebFetch — Quote: "Connect to a running browser instance (Edge/Chrome only)."
- Playwright MCP is headed by default; headless idle timeout is one hour, headed never — https://github.com/microsoft/playwright-mcp, opened 2026-10-16, WebFetch — Quote: "Defaults to one hour for headless browsers, never for headed ones."
- Storage state covers cookies, localStorage, IndexedDB and passkey auth, but not sessionStorage, and the file can impersonate the account — https://playwright.dev/docs/auth, opened 2026-10-16, WebFetch — Quote: "Reusing authenticated state covers cookies, local storage, IndexedDB and passkey (WebAuthn) based authentication."
- Playwright says to delete state when it expires; no auto refresh — https://playwright.dev/docs/auth, opened 2026-10-16, WebFetch — Quote: "Note that you need to delete the stored state when it expires."
- The auth file is a credential; keep it out of git — https://playwright.dev/docs/auth, opened 2026-10-16, WebFetch — Quote: "We strongly discourage checking them into private or public repositories."
- Persistent context and the real Chrome profile: automating Chrome's default profile is unsupported — https://playwright.dev/docs/api/class-browsertype, opened 2026-10-16, WebFetch — Quote: "automating the default Chrome user profile is not supported."
- Since Chrome 136, remote-debugging switches are ignored on the default profile, so any CDP attach needs a non-default dir — https://developer.chrome.com/blog/remote-debugging-port, opened 2026-10-16, WebFetch — Quote: "These switches will no longer be respected if attempting to debug the default Chrome data directory."
- Claude in Chrome shares the real browser's login state and pauses on login/CAPTCHA — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- Claude in Chrome's connection drops on idle — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "The Chrome extension's service worker can go idle during extended sessions, which breaks the connection."

### Contradictions
- None found.

### Inferences
- (mine) Persistent profile + headed beats storage-state for weeks: sessionStorage loss and the "delete when expired" note (Playwright auth page) make a snapshot fragile; the profile is what a real user's Chrome is. Rests on the Playwright MCP and auth-page findings.
- (mine) Re-login detection is not provided by Playwright; the engineer must assert a logged-in element per site at task start (and treat a redirect to a login URL as "needs John"). Rests on "you need to delete the stored state when it expires".
- (mine) Extension mode on John's daily Chrome gives the best session reuse but depends on John's machine being on and the extension service worker awake; it is a fallback, not the unattended path.

### Gaps
- Real session lifetimes for Attio, Clay, n8n, Outreach, Google and the blood-work portal in a persistent profile: no vendor page opened states them; must be measured in a spike (log in, check daily for 2-3 weeks).
- Whether Playwright MCP's persistent profile survives restarts of the MCP process under Claude Code on the VM: not tested.

## Q2 Two-factor and Google sign-in

### Takeaway
TOTP is the automatable factor: a vault or script can generate the code locally from the seed; SMS, push prompts and passkeys are not reliably automatable and should route to John. 1Password service accounts can read items including OTP via secret references; Bitwarden Secrets Manager's CLI page does not document TOTP generation. Google explicitly blocks sign-in from browsers "controlled through software automation", so Google should be logged in once by John by hand in the persistent profile and never re-driven by script. Confidence: medium-high.

### Cited findings
- Google may refuse sign-in from automated or embedded browsers — https://support.google.com/accounts/answer/7675428, opened 2026-10-16, WebFetch (summarised) — Quote: "Are being controlled through software automation rather than a human."
- Same page, embedded frameworks — https://support.google.com/accounts/answer/7675428, opened 2026-10-16, WebFetch — Quote: "Are embedded in a different application."
- 1Password secret references can fetch the OTP attribute of a field — https://www.1password.dev/cli/secret-references, opened 2026-10-16, Exa search highlights — Quote: "include the `attribute` (or `attr`) query parameter with the attribute you want to get."
- 1Password CLI has long supported `op item get --otp` — https://1password.com/blog/1password-cli-2-0, opened 2026-10-16, Exa search highlights — Quote: "npm publish --otp $(op item get npmjs --otp)"
- 1Password service accounts: vault-scoped, rate-limited; `op item get` and `op read` each cost 3 reads unless IDs are passed — https://www.1password.dev/service-accounts/use-with-1password-cli, opened 2026-10-16, Exa search highlights — Quote: "Service accounts have hourly and daily limits on the total number of requests the service account can make."
- Bitwarden Secrets Manager CLI authenticates with a machine-account token; the page says nothing about TOTP — https://bitwarden.com/help/secrets-manager-cli/, opened 2026-10-16, WebFetch — Quote: "The Secrets Manager CLI can be logged in to using an access token generated for a particular machine account."
- TOTP is computed locally from the seed (RFC 6238); the seed is long-lived and never rotated by lockout; NTP clock sync matters — https://github.com/feder-cr/invisible_playwright/wiki/automating-totp-2fa-login-playwright, opened 2026-10-16, Exa highlights (third-party wiki, tool is a stealth wrapper which is rejected; the TOTP section is generic) — Quote: "The shared secret is a long-lived credential, not a one-time value; anyone who has it can generate valid codes for as long as 2FA stays configured"
- A third-party Google login automation reports only TOTP is reliable; Google prompt and passkey "unlikely" — https://github.com/blhutchings/google-login-service, opened 2026-10-16, Exa highlights (2023, unvetted; lists a CAPTCHA solver, rejected) — Quote: "Currently only TOTP works reliably."
- A testing vendor advises against automating personal Google accounts — https://docs.stably.ai/use-cases/testing-google-auth-and-2fa, opened 2026-10-16, Exa highlights — Quote: "Do not automate personal Google accounts or rely on one-time manual approvals in CI. Use dedicated test identities only."
- Playwright storage state includes passkey (WebAuthn) based auth state — https://playwright.dev/docs/auth, opened 2026-10-16, WebFetch — Quote: "Reusing authenticated state covers cookies, local storage, IndexedDB and passkey (WebAuthn) based authentication."
- 1Password for Claude (vault fill without exposing secrets) is Mac only — /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q3 section) — Quote: "Claude never sees the vault item, password, or one-time code"

### Contradictions
- None found.

### Inferences
- (mine) Do not give the model the TOTP seed. A small host script (`op read "op://vault/item/field?attribute=otp"` or `pyotp`) invoked by a tool wrapper returns a six-digit code only at the moment of login. Rests on the 1Password OTP attribute and "long-lived credential" findings. Not run.
- (mine) Hosting Google sign-in in a persistent profile hand-logged by John (and, if his Google account uses passkeys or phone prompts, keeping it that way) avoids the "software automation" block entirely, because no script drives Google's login page. Rests on the Google help page. Where Attio/Clay/n8n use "Sign in with Google", the session cookie from that one human login is what is reused.
- (mine) SMS/email codes: email codes can be read by the engineer through the Gmail connector already in the session; SMS and push have no safe automation; route both to John. Not independently sourced; 'Gmail connector' appears in the session's tool list only.
- (mine) Prefer dedicated service identities (API key for Attio/Clay/n8n/Outreach; a limited user) over John's own accounts, per the Stably advice and OpenClaw guidance quoted in engineer-runtime.md.

### Gaps
- Whether Attio, Clay, n8n, Outreach and the blood-work portal offer TOTP, passkey-only or SMS 2FA for John's accounts: unknown; ask John.
- Bitwarden Secrets Manager TOTP, Infisical and pass: not opened; no claim made.
- Passkey behaviour in headed Chrome on a Linux VM with no authenticator hardware: not found.

## Q3 Bot detection and legitimate mitigations

### Takeaway
Cloudflare states browser automation frameworks "are not supported for solving production challenges", and has a JavaScript-detections engine aimed at headless browsers; Google blocks software-controlled sign-ins. The legitimate posture is: a real headed Chrome in a stable profile with a consistent IP, driving only after a human login, plus official APIs where they exist. Stealth plugins and CAPTCHA solvers exist (hosted browsers sell them) and are rejected. Confidence: medium (vendor docs, not a measured test against John's sites).

### Cited findings
- Cloudflare JSD targets headless browsers — https://developers.cloudflare.com/bots/concepts/bot-score/, opened 2026-10-16, Exa highlights — Quote: "Catches headless browsers (browsers controlled by software, with no visible window or human operator) and other automation tools."
- Cloudflare says automation frameworks cannot be relied on for production challenges, and offers test keys for Turnstile — https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/, opened 2026-10-16, Exa highlights — Quote: "Browser automation frameworks, such as Selenium, Puppeteer, Playwright, and Cypress, are not supported for solving production challenges."
- Cloudflare's ML engine scores headers, session characteristics and browser signals — https://developers.cloudflare.com/bots/concepts/bot-detection-engines/, opened 2026-10-16, Exa highlights — Quote: "Request features, including headers, session characteristics, and browser signals, collected from traffic across the Cloudflare network."
- Cloudflare's own browser product signs requests with Web Bot Auth so sites can verify them — https://developers.cloudflare.com/browser-run/reference/automatic-request-headers/, opened 2026-10-16, Exa highlights — Quote: "Web Bot Auth leverages cryptographic signatures in HTTP messages to verify that a request comes from an automated bot."
- Google blocks software-automated sign-in (see Q2) — https://support.google.com/accounts/answer/7675428, opened 2026-10-16 — Quote: "Google doesn’t let you sign in from some browsers."
- Claude in Chrome and the existing tool-registry note: Playwright MCP headless was blocked by Cloudflare/Vercel bot checks in this project — /home/user/Autonomy-Research/research/tool-registry.md (Playwright MCP row) — Quote: "blocked by Cloudflare/Vercel bot checks; 45-95 KB snapshots"
- Hosted-browser vendors sell stealth and CAPTCHA solving as features — https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/, opened 2026-10-16, Exa highlights (third-party comparison, 2026-08-12) — Quote: "Stealth mode, residential proxies, CAPTCHA solving, per its docs"

### Contradictions
- None found.

### Inferences
- (mine) The named SaaS logins (Attio, Clay, n8n, Outreach) are authenticated app UIs; none of the opened pages shows what bot detection they apply, so the practical risk is at the login step and at Google SSO, both handled by the human one-time login. No test was run.
- (mine) A VM in a datacentre IP may score worse than John's home IP. Mitigation without evasion: run the VM at home/office or reach the sites through John's own Tailscale exit node; a stable IP also avoids "new location" security emails. Not sourced; spike it.
- (mine) Rejected as evasion: stealth plugins, fingerprint spoofing wrappers (the invisible_playwright repo seen in search), CAPTCHA-solving services, rotating residential proxies. The engineer's rule: on a CAPTCHA or challenge, stop and ask John (Claude in Chrome behaves the same way, per its docs).

### Gaps
- Cloudflare Turnstile concepts page (https://developers.cloudflare.com/turnstile/concepts/) opened but contained no detail; no first-party statement on how Turnstile treats a headed automated Chrome with a real profile.
- Attio, Clay, Outreach login bot protection: no source found.

## Q4 Terms of service (Attio, Clay, Outreach)

### Takeaway
None of the three opened terms pages bans a logged-in customer's own automation of the UI by name, but each makes the customer responsible for credentials and bars sharing them with third parties; Attio forbids circumventing limits and security, and the Outreach host page I found (Resonate-branded) bans "spiders, crawlers, or scrapers" while the Outreach.ai page opened shows no such clause. The main risk is credential-sharing and rate/circumvention clauses, not a "bot" clause. A company Outreach account adds an employer-policy risk the terms do not cover. Confidence: medium; legal reading is not advice.

### Cited findings
- Attio Customer Agreement: no clause on bots/scripts/scraping; credential and API-abuse clauses exist — https://attio.com/legal/terms-and-conditions, opened 2026-10-16, WebFetch (summarised) — Quote: "You will be responsible for ensuring the security and confidentiality of all log-on identifiers"
- Attio bars circumventing limits including API call counts — https://attio.com/legal/terms-and-conditions, opened 2026-10-16, Exa highlights — Quote: "attempt to exceed or circumvent any express or implied limitations on use of the Attio Services, including, but not limited to, in relation to the number of calls to the Attio API"
- Attio bars letting third parties use the service — https://attio.com/legal/terms-and-conditions, opened 2026-10-16, WebFetch — Quote: "permit or facilitate any third party to access or use the Attio Services"
- Attio Acceptable Use also bars circumventing security or access controls — https://attio.com/legal/acceptable-use, opened 2026-10-16, Exa highlights — Quote: "circumvent, disable, or interfere with any security or access controls"
- Clay Terms (last updated May 23, 2024): customer is responsible for account credentials — https://www.clay.com/terms-of-service, opened 2026-10-16, Exa fetch (first 8,000 characters only) — Quote: "You are solely responsible for maintaining the confidentiality of your account information, including username and password, and for all activities that occur under your account."
- Clay Terms: no transfer of the account — https://www.clay.com/terms-of-service, opened 2026-10-16, Exa fetch — Quote: "You agree not to license, sell, or transfer your account without our prior written approval."
- Clay's own blog advises against CAPTCHA solvers and IP rotation on sites that forbid scraping — https://www.clay.com/blog/websites-that-allow-web-scraping, opened 2026-10-16, Exa highlights — Quote: "using them is not recommended"
- Outreach (outreach.ai/terms): do not give your password to any third party; account may be suspended — https://www.outreach.ai/terms, opened 2026-10-16, WebFetch (summarised) — Quote: "you agree not to provide your password to any third party"
- Same page: suspension — https://www.outreach.ai/terms, opened 2026-10-16, WebFetch — Quote: "We reserve the right to suspend or terminate the Services in whole or part at any time, with or without cause"
- Outreach Acceptable Use Policy focuses on email sending practices — https://www.outreach.ai/acceptable-use-policy, opened 2026-10-16, Exa highlights — Quote: "Using the Outreach Services in connection with any unsolicited or harassing messages"

### Contradictions
- https://www.outreach.ai/terms (WebFetch summary) found no clause on spiders/scrapers; https://outreach.as/terms (Exa highlights) contains "Use automated means such as spiders, crawlers, or scrapers to extract or collect data from the Services" but refers to "Resonate", so it is a different company's terms, not Outreach.io. Do not cite outreach.as for Outreach; confirm John's actual contract.

### Inferences
- (mine) Giving an automation the user's password is arguably "providing your password to a third party" under Outreach and Attio wording; the safer reading is that the engineer acts as John on John's machine with John's own session (as Claude in Chrome does), not as a separate party holding credentials, and APIs/OAuth/S2S tokens are used where available (the Outreach and Attio APIs are in the registry already).
- (mine) For a company Outreach account John should ask his admin/employer before UI automation; the worker found nothing that makes this safe to assume. Prefer the Outreach API with an admin-approved app.
- (mine) Keep volume human-like and read-mostly on Attio; the explicit risk clauses are API-limit circumvention and security-control circumvention.

### Gaps
- Clay terms beyond the first 8,000 characters (acceptable-use or restrictions clauses might sit later) not read; the https://www.clay.com/terms URL returned 404.
- Outreach master customer agreement (the signed contract) is not public; the Outreach.ai terms summary came from a summarising fetch, not the full text.
- Terms of John's blood-work portal and Google ToS beyond the sign-in help page: not opened.

## Q5 Where the browser runs

### Takeaway
Best fit for unattended weeks-long logins: the engineer's own Ubuntu VM with a persistent headed Chrome profile on a virtual desktop (Xvfb plus VNC, viewed in a browser through noVNC), reachable only over a private network. It is free, keeps cookies and the health portal off third parties, and gives John a live view to step in. Hosted browsers (Browserbase, Steel, Anchor) persist logins and have live views but put session cookies and health data on a vendor, and cost $0.05-0.12 per browser hour plus plan fees. John's own machine (Claude in Chrome) has the best IP and trust, but is not unattended-safe. Confidence: medium.

### Cited findings
- noVNC is a browser VNC client that needs websockify as the WebSocket proxy; MPL 2.0 — https://github.com/novnc/noVNC, opened 2026-10-16, WebFetch — Quote: "noVNC is both a HTML VNC client JavaScript library and an application built on top of that library."
- Claude in Chrome: local, visible, needs a subscription login, not for API-key or setup-token auth — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`, because the browser extension can't authenticate with those credentials."
- Claude in Chrome is not covered by Anthropic's BAA for third-party sites (relevant to the health portal) — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Your Business Associate Agreement (BAA) with Anthropic doesn't cover data sent to third-party sites through Claude in Chrome."
- Claude in Chrome does not run in WSL — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Chrome integration isn't supported in Windows Subsystem for Linux (WSL)."
- Computer use in the CLI is macOS only and interactive only — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Computer use in the CLI is not available on Linux or Windows."
- Same page: not in `-p` mode — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Computer use is not available in non-interactive mode with the `-p` flag."
- Browserbase pricing: Free 3 concurrent, 1 hour, 15-minute sessions, 7-day retention; Developer $20/month, 100 hours then $0.12/hr, 30-day retention; Startup $99/month, 500 hours then $0.10/hr — https://www.browserbase.com/pricing, opened 2026-10-16, WebFetch (summarised) — Quote: "Every plan scales past its included usage, so no caps or throttling as you build, billed at your plan’s rate."
- Hosted-browser comparison (2026-08-12): Browserbase context-style persistence, Steel persistent profiles, Hyperbrowser profiles via API; warns credentials concentrate risk at the vendor, and Steel self-hosting is the escape hatch — https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/, opened 2026-10-16, Exa highlights (third-party) — Quote: "recordings, cookies, and persistent profiles all live on someone else's infrastructure."
- Self-hosted Steel limitations — https://indexagentica.com/compare/cloud-browsers-for-agents.md, opened 2026-10-16, Exa highlights (third-party, dated 2026-10-12) — Quote: "self-hosted Steel runs one session at a time and has no CAPTCHA solving or Credentials API."
- Anchor vs Steel prices from vendor-authored comparison: Anchor $0.05/browser-hour with $50/month Starter; Steel Launch $0/month plus $0.10/hr, Scale $250/month; Steel Launch sessions capped at 15 minutes — https://llms.anchorbrowser.io/anchor-browser-vs-steel, opened 2026-10-16, Exa highlights (vendor-authored, biased) — Quote: "Steel lists 15 minutes (Launch), 1 hour (Scale), and up to 24 hours (Enterprise)"
- Steel Credentials API handles TOTP; Anchor adds email OTP mailboxes and auto re-auth (vendor claim) — https://llms.anchorbrowser.io/anchor-browser-vs-steel, opened 2026-10-16, Exa highlights — Quote: "Anchor re-authenticates automatically when a session needs it."
- Remote Control and Channels allow phone-based monitoring of a session on John's machine/VM — /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q3, Q4) — Quote: "Claude keeps running locally the entire time, so your code execution and filesystem access stay on your machine"

### Contradictions
- None found on facts. Note the sources for hosted-browser prices are a vendor page (Browserbase) plus third-party and vendor-authored comparisons (Anchor/Steel/Hyperbrowser); Hyperbrowser and Browserless prices were not read from primary pages.

### Inferences
- (mine) Comparison table:
  - Own VM, Xvfb + x11vnc + noVNC, headed Chrome, persistent dir: cost $0 extra; logins persist as long as sites allow; privacy best (data stays on John's VM); reliability depends on keeping Chrome alive (systemd unit + restart + Xvfb); live view via noVNC over Tailscale; datacentre IP risk.
  - Hosted (Browserbase/Steel/Anchor): about $20-99/month or $0.05-0.12/hr; session cap on Free; profile stored at vendor; live view built in; stealth/CAPTCHA add-ons are exactly what is rejected; health-portal data and Google-linked cookies at a third party. Not recommended for John's logins. Fine for public-web research tasks without logins.
  - John's own Chrome via Claude in Chrome or Playwright extension mode: best IP and device trust, free; not unattended (laptop sleeps, service worker idles, needs `/login` subscription auth); use only for tasks John starts.
  - Claude desktop computer use: macOS/Windows desktop only, interactive, browsers are view-only tier per the computer-use page, so not a login path.
- (mine) Keep the VM desktop minimal: Xvfb on `:99`, a window manager, x11vnc bound to localhost, noVNC proxied behind Tailscale or an SSH tunnel; never expose the VNC port to the internet. noVNC doc supports the websockify design only; hardening advice is mine.
- (mine) If the VM's IP gets challenged, move the VM to John's home network or use a Tailscale exit node at his home; cheaper and more legitimate than any proxy product.

### Gaps
- Hyperbrowser, Browserless, Anchor and Steel primary pricing/docs pages not opened; figures above for those come from third-party/vendor-authored comparisons found through Exa highlights.
- Data-handling terms (encryption, retention) for hosted vendors: only Browserbase retention (7/30 days) read.
- x11vnc/Xvfb docs not opened; install/hardening steps unverified.

## Q6 Login hand-over and later re-requests

### Takeaway
One setup session: John opens the VM's noVNC desktop (or Remote Control/phone link), logs into each app in the engineer's Chrome profile, confirms logged-in state, and the engineer records only a per-site "logged-in check" (URL/selector). Later, on a failed check, the engineer stops that task, writes an approval item ("Attio needs fresh login; open noVNC link; 2 minutes") into the batched-approval digest, and continues other work; for TOTP sites it generates the code itself via the vault wrapper. Confidence: medium (design from sourced parts; the approval channel itself is in engineer-runtime.md).

### Cited findings
- Claude in Chrome's own pattern is pause-and-ask on login — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- Remote Control pushes needed decisions to John's phone — /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q4) — Quote: "Claude decides when to push. It typically sends one when a long-running task finishes or when it needs a decision from you to continue."
- Channels can relay permission prompts to Telegram/Discord/iMessage, with a sender allowlist — /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q4) — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority"
- Reference pattern: a persistent Chromium on a VPS with hand-off on login walls — /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q3, from https://github.com/browser-use/bux) — Quote: "A real Chromium session via browser-harness — cookies persist, logins stick"
- Hosted vendors confirm the "first login" problem: managed profiles persist the session but something still supplies the password — https://menuagentic.com/blogs/browserbase-vs-steel-vs-hyperbrowser-vs-anchor-browser/, opened 2026-10-16, Exa highlights — Quote: "without solving the first-login problem, since something still has to supply the password."
- Guidance to keep passwords out of the prompt — same page — Quote: "If the password ever appears in a prompt it is in your traces and reachable by prompt injection"

### Contradictions
- None found.

### Inferences
- (mine) Hand-over steps: (1) engineer starts Chrome with a fixed `--user-data-dir` and the noVNC page; (2) John logs in manually (including Google, with his own 2FA, so no script touches Google's login); (3) John does not type secrets into the chat; (4) engineer saves per-site check recipes; (5) profile directory is chmod 700, excluded from git, and listed in permissions.deny for Read.
- (mine) Re-request message format (in the batched digest): site, symptom (redirected to /login), what John must do (open link, log in, press done), expiry, and the tasks parked. A TOTP-needing site is handled without John if the seed is in the vault; email codes via the Gmail connector; SMS/push codes ask John.
- (mine) Fallback ladder for a site: API or MCP connector (Attio MCP, Clay developer platform, n8n API, Outreach API per the registry) first; then browser; then John.

### Spikes before building
1. Playwright MCP persistent profile on the VM under Xvfb: log in by noVNC, restart Claude Code and Chrome, confirm session survives; run for 2-3 weeks, log expiry per site.
2. Headed Chrome (Chrome for Testing vs real Chrome) from the VM's IP vs a Tailscale home exit node: challenge rate on Attio, Clay, n8n, Outreach login and the portal.
3. Google: confirm a hand-logged profile stays signed in and that Google SSO into Attio/Clay survives; confirm no script touches accounts.google.com.
4. `op` service account (or Bitwarden/pass) TOTP wrapper returns a code without the seed reaching model context; check clock sync (NTP) and 3-read request cost.
5. Re-login detection: per-site selector check, plus a stall alert into the digest.
6. Outreach: ask admin/employer whether UI automation is allowed; test the API app route instead.
7. Check Clay's later terms sections and the portal's terms.

### Gaps
- No source describes a standard "fresh login request" message; the design is inferred.
- Whether the batched-approval channel can carry a live noVNC link with an expiry: not tested.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Playwright MCP persistent profile / --storage-state / --extension | https://github.com/microsoft/playwright-mcp | Persistent on-disk profile by default; isolated mode with storage-state; extension mode attaches to a running Chrome/Edge | local, VM | 2026-10-16 | Use persistent profile on the VM; extension mode only as a John-machine fallback |
| Playwright storageState | https://playwright.dev/docs/auth | Saves cookies/localStorage/IndexedDB/passkey state to a file; no sessionStorage | local | 2026-10-16 | Fallback only; treat file as a credential |
| noVNC (+ websockify, Xvfb, VNC server) | https://github.com/novnc/noVNC | Browser-based VNC client, MPL 2.0 | VM | 2026-10-16 | Use behind Tailscale/SSH tunnel for the one-time login and live view; spike |
| 1Password CLI service accounts (op read / --otp) | https://www.1password.dev/service-accounts/use-with-1password-cli | Vault-scoped CLI reads including OTP attribute; rate limited | VM | 2026-10-16 | Use if John already has 1Password (paid); otherwise a local seed store with pyotp; spike |
| Bitwarden Secrets Manager CLI | https://bitwarden.com/help/secrets-manager-cli/ | Machine-account token CLI for secrets; no TOTP documented on page | VM | 2026-10-16 | Fallback for static secrets; TOTP unverified |
| Browserbase | https://www.browserbase.com/pricing | Hosted browsers; Free 15-min sessions; $20 and $99 plans, $0.12/$0.10 per extra hour; 7/30-day retention | hosted | 2026-10-16 | Skip for logged-in work (credentials and health data at vendor); fine for public-web tasks |
| Steel (steel-browser) | https://llms.anchorbrowser.io/anchor-browser-vs-steel | Apache-2.0 browser API, hosted or self-hosted; Credentials API with TOTP (vendor-authored comparison) | hosted / Docker | 2026-10-16 | Reference only; self-host adds nothing over Playwright on the VM |
| Anchor Browser | https://llms.anchorbrowser.io/anchor-browser-vs-steel | Hosted browser with secret injection, email-OTP mailbox, auto re-auth; $0.05/hr, $50/month (vendor-authored) | hosted | 2026-10-16 | Skip; paid, vendor holds logins; revisit only if re-auth automation is needed |
| Hyperbrowser / Browserless | https://ryanalberts.github.io/best-of-Agent-Harnesses/compare/browser-infrastructure/ | Hosted browsers; stealth and CAPTCHA are headline features (Hyperbrowser) | hosted | 2026-10-16 (third-party page only) | Reject: stealth and CAPTCHA solving is what we do not use; primary pages not opened |
| Stealth plugins, CAPTCHA solvers, rotating residential proxies (e.g. invisible_playwright, google-login-service) | https://github.com/blhutchings/google-login-service | Evade bot detection | n/a | 2026-10-16 (search highlights only) | Rejected: evasion; not installed or evaluated |
| Claude in Chrome | https://code.claude.com/docs/en/chrome | Real logged-in Chrome, visible; pauses on login/CAPTCHA | John's machine | 2026-10-16 | Fallback for John-started tasks; not unattended |
| Claude Code computer use | https://code.claude.com/docs/en/computer-use | GUI control; macOS CLI, Desktop on macOS/Windows; interactive only; browsers view-only | John's machine | 2026-10-16 | Not a login path for the VM |
