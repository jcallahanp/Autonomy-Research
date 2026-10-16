# Bot flagging for a logged-in agent

Brief: Tell John which host setup gets flagged least when the engineer works in his own logged-in accounts, without evasion tricks.
Run: research/runs/engineer-host/PLAN.md

## 1. What signals do bot-detection systems use?

### Takeaway
Vendors score several independent layers: network (IP, ASN, TLS/TCP fingerprint), browser (headless, automation flags, fingerprint consistency) and behaviour. A data-center ASN is a strong prior on its own, and a clean browser cannot fix a flagged IP. Confidence: medium-high. Cloudflare docs are primary; the ASN claim rests on non-vendor sources.

### Cited findings
- Cloudflare's JavaScript Detections engine targets headless browsers; the bot score comes from a layered set of engines (heuristics, ML, JSD). — https://developers.cloudflare.com/bots/concepts/bot-score/, opened 2026-10-16, WebFetch — Quote: "Catches headless browsers (browsers controlled by software, with no visible window or human operator)"
- Cloudflare's ML inputs are request features and browser signals, not named IP/ASN on that page; fingerprint databases sit in Heuristics. (Cloudflare docs do not list ASN as an input on this page.) — https://developers.cloudflare.com/bots/concepts/bot-score/, opened 2026-10-16, WebFetch — Quote: "Request features, including headers, session characteristics, and browser signals"
- Google says it may refuse sign-in from automation-controlled browsers (Google sign-in risk check, first-party statement). — https://support.google.com/accounts/answer/7675428?hl=en, opened 2026-10-16, WebFetch — Quote: "Are being controlled through software automation rather than a human"
- Playwright maintainers confirm Google can deny sign-in to a Playwright-driven browser, e.g. via the webdriver flag; stealth is not a Playwright goal. — https://github.com/microsoft/playwright/issues/19420, opened 2026-10-16, WebFetch — Quote: "Google has all kinds of antibot protection and since the browser is controlled by browser automation tool"
- Measured 2026 (Playwright 1.57, Tranco top 10k, one Hetzner data-center IP, no stealth): headless Chromium is the outlier at 15.2% soft blocks versus about 7% for headed Chromium and both Firefox modes. — https://arxiv.org/html/2606.14525v1, opened 2026-10-16, WebFetch — Quote: "Chromium headless is a clear outlier at 15.2%, while the remaining three conditions cluster between 6.8–7.2%."
- Same paper: Cloudflare and Akamai blocked far above average; navigator.webdriver probed on 34% of sites and DevTools probes on 21%. — https://arxiv.org/html/2606.14525v1, opened 2026-10-16, WebFetch — Quote: "The most prevalent Tier 1 signal is navigator.webdriver, accessed on 2,730 (34%) of 7,944 successfully scanned sites."
- Same paper warns data-center scanning shifts absolute block rates (so the 7% headed figure is a data-center floor, not a residential one). — https://arxiv.org/html/2606.14525v1, opened 2026-10-16, WebFetch — Quote: "scanning from a datacenter IP rather than a residential network affects absolute blocking rates"

### Contradictions
- None found.

### Inferences
- (mine) Headed real Chrome removes the largest browser-level penalty (headless), but the paper measured on a data-center IP, so it does not isolate the IP effect. No opened vendor page gave a numeric data-center vs residential challenge rate for the SaaS apps John uses.
- (mine) The IP/ASN claim is vendor-sourced only for Cloudflare's alert docs (ASN is a filter dimension; seen in a search excerpt, not opened). Treat "data-center ASN is a strong prior" as widely asserted but not vendor-confirmed in this note.

### Gaps
- DataDome signal list: https://datadome.co/bot-management-protection/client-side-detection-is-essential-for-bot-protection returned 403 to WebFetch; not cited. Akamai, hCaptcha and reCAPTCHA vendor docs not opened.
- Cloudflare community thread on Playwright login Turnstile (https://community.cloudflare.com/t/disable-cloudflare-captcha-for-specific-ips/866592) returned 403; not cited.
- Numeric residential vs data-center challenge rate from a 2025-2026 engineering post: only vendor-marketing proxy blogs found (search excerpts, not opened); none cited.

## 2. Are Attio, Clay, n8n Cloud, Outreach, Google Workspace and Slack protected, and is there evidence of challenges?

### Takeaway
Observed edge: Attio and n8n.io answer from Cloudflare; Clay from Netlify/CloudFront; Google from GSE. No 2025-2026 report found of Attio, Clay, Outreach, n8n Cloud or Slack web apps challenging a logged-in data-center session. Google sign-in is the one documented, real blocker. Confidence: low-medium (single header probe, no challenge evidence either way).

### Cited findings
- Header probe from this sandbox's egress (via agent proxy, a data-center IP): app.attio.com and www.n8n.io return `server: cloudflare` with cf-ray; app.clay.com returns `server: Netlify` via CloudFront; accounts.google.com returns `server: GSE`. — curl -D against each host, run 2026-10-16, Bash — Quote: "server: cloudflare"
  (Probe returned HTTP 200 for app.attio.com and app.clay.com, 301 for www.n8n.io, 403 from slack.com/signin (server: Apache, via slack-prod.tinyspeck.com), 502 from app.outreach.io. The 403/502 may come from the proxy, so they are not evidence of bot blocking.)
- Google's own help page lists automation as a reason to refuse sign-in, which is the documented risk for the Google Workspace and "sign in with Google" steps. — https://support.google.com/accounts/answer/7675428?hl=en, opened 2026-10-16, WebFetch — Quote: "Are being controlled through software automation rather than a human"

### Contradictions
- None found.

### Inferences
- (mine) Cloudflare in front of a SaaS host does not by itself mean challenges: the owner picks the rule. The first-load 200 for Attio from a data-center IP suggests no blanket challenge on the app shell, but this is one unauthenticated request.
- (mine) Risk ranking for John's list: Google sign-in highest; Cloudflare-fronted Attio and n8n medium-low; Clay, Outreach, Slack unknown.

### Gaps
- No source found that shows Clay, Outreach or Slack bot protection at login. Outreach and Slack probes were blocked by the proxy, so their edge is unknown.
- No 2025-2026 incident reports for any of the six vendors challenging data-center IPs; spike needed (log in once from the candidate host and note challenges).
- n8n Cloud app host (not www.n8n.io) not probed.

## 3. Does the operating system matter?

### Takeaway
Not as a policy: no opened source reports an OS effect. The paper found no OS result. The OS matters only through consistency (user-agent and platform vs the TCP/TLS stack and GPU/screen), plus common-denominator effects. Confidence: low.

### Cited findings
- The 2026 measurement paper reports nothing about operating system. — https://arxiv.org/html/2606.14525v1, opened 2026-10-16, WebFetch — Quote: "scanning from a datacenter IP rather than a residential network affects absolute blocking rates"  (fetch summary: the paper "does not mention an operating system"; absence only)
- Playwright says real Chrome and Edge are selectable via channel on the machine and that their new headless mode differs from the default headless shell. — https://playwright.dev/docs/browsers, opened 2026-10-16, WebFetch — Quote: "You can opt into the new headless mode by using 'chromium' channel."

### Contradictions
- None found.

### Inferences
- (mine) Non-vendor sources I only saw as search excerpts (TCP/IP OS-fingerprint tools, DataDome text) say network stacks can be compared with the claimed UA OS. If true, an honest Linux Chrome on Linux is consistent; Windows UA on a Linux box is the mismatch. This argues for no UA spoofing, not for a specific OS.
- (mine) Linux data-center Chrome is the most common automation profile, so it shares a population with bots; macOS or Windows on a home line shares a population with people. Unmeasured.

### Gaps
- No vendor doc or measurement isolating Windows vs Linux vs macOS flag rates. Excerpts on TCP/IP fingerprints were not opened.

## 4. Legitimate options that reduce flags

### Takeaway
Least-flagged and still legitimate: run on John's own machine at home (home ISP IP, real branded Chrome, headed, persistent profile) with John signing in by hand once; use APIs for Attio, n8n, Outreach and Slack; use Cloudflare Web Bot Auth only where you own the site. Stealth plugins, residential-proxy rotation and CAPTCHA solvers stay rejected. Confidence: medium.

### Cited findings
- Playwright can drive branded Google Chrome already on the machine via `channel`. — https://playwright.dev/docs/browsers, opened 2026-10-16, WebFetch — Quote: "can operate against the branded Google Chrome and Microsoft Edge browsers available on the machine"
- Chrome 136+ ignores --remote-debugging-port on the default profile; automation must use a non-default --user-data-dir. — https://developer.chrome.com/blog/remote-debugging-port, opened 2026-10-16, WebFetch — Quote: "These switches will no longer be respected if attempting to debug the default Chrome data directory."
- Chrome's own supported agent route: Chrome 144+ lets DevTools MCP attach to a running Chrome after the user allows it in a dialog. — https://developer.chrome.com/docs/devtools/agents/get-started/configuration, opened 2026-10-16, WebFetch — Quote: "When the agent attempts to connect, Chrome shows a dialog asking for permission."
- Cloudflare verified bots include user-driven agents but require honest self-identification and non-abusive behaviour. — https://developers.cloudflare.com/bots/concepts/bot/verified-bots/, opened 2026-10-16, WebFetch — Quote: "A Verified bot is a bot or agent that Cloudflare has confirmed is transparent about who it is and what it does"
- Web Bot Auth requires a hosted key directory and registering the bot with Cloudflare; it is written for bot operators, not for visiting a third-party SaaS as a customer. — https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/, opened 2026-10-16, WebFetch — Quote: "You need to register your bot and its key directory to add your bot to the list of verified bots."
- Google's terms prohibit bypassing protective measures, which frames stealth as a ToS issue. — https://policies.google.com/terms, opened 2026-10-16, WebFetch — Quote: "spamming, hacking, or bypassing our systems or protective measures"

### Contradictions
- Third-party Playwright wrappers (search excerpts only, not opened) claim a "Google CDP-block bypass" by logging in once in real Chrome and reusing the profile; Playwright's own maintainer reply (above) says automation-controlled browsers may be denied and offers no such fix. Needs a spike on John's host; neither source settles it.

### Inferences
- (mine) Signed-agent programmes protect site owners' own traffic. The SaaS vendors (Attio, Clay, Slack) set the Cloudflare rules, so John cannot register with Cloudflare to get through their rules. The legitimate route there is the vendor's API, or asking the vendor to allowlist his IP.
- (mine) Legitimate and evasion lines: home IP, headed real Chrome, persistent profile, human sign-in, low rate = legitimate (the browser is what it claims to be). Stealth patches, rotating residential proxies, CAPTCHA solvers, UA or fingerprint spoofing = evasion.
- (mine) Ranking, least flagged first: (1) Mac Mini or PC at home, headed Chrome, persistent non-default profile, Chrome 144+ attach or Playwright channel chrome; (2) same on a rented VM with static IP, higher IP-risk; (3) headless on a VM, highest.

### Gaps
- Static-IP effect on Google risk checks: no vendor doc found.
- Whether Google's sign-in block applies to a profile logged in by hand then driven later: untested; only third-party claims.
- Home-ISP uptime, CGNAT and power risks are the host-comparison facet's job, not covered here.

## 5. Terms-of-service limits

### Takeaway
None of the opened terms forbids the account owner using automation in general. Attio bans circumventing security controls and caps API use; Google bans bypassing protective measures and scraping content that is not yours; Clay's terms have no such clause. Slack's Acceptable Use Policy could not be read. Confidence: medium.

### Cited findings
- Attio's Acceptable Use terms bar circumventing access controls and limits (fetch summary: no words "scraping", "bots" or "scripts"). — http://attio.com/legal/acceptable-use, opened 2026-10-16, WebFetch — Quote: "circumvent, disable, or interfere with any security or access controls"
- Attio caps API use. — http://attio.com/legal/acceptable-use, opened 2026-10-16, WebFetch — Quote: "attempt to exceed or circumvent any express or implied limitations on use of the Attio Services"
- Clay's terms (last updated May 23, 2024) have no automation clause. — https://www.clay.com/terms-of-service, opened 2026-10-16, WebFetch — Quote: "Clay Labs has the right to review and monitor all use of the Services"
- Google's terms restrict automated access that violates robots.txt and scraping content not yours. — https://policies.google.com/terms, opened 2026-10-16, WebFetch — Quote: "scraping content that doesn’t belong to you"
- Slack's User Terms incorporate the Acceptable Use Policy by reference; the AUP text was not on the page. — https://slack.com/terms-of-service/user, opened 2026-10-16, WebFetch — Quote: "you agree to comply with the most recent version of our Acceptable Use Policy"

### Contradictions
- None found.

### Inferences
- (mine) Driving John's own account at human-like pace is unlikely to hit the opened clauses; the real exposure is circumventing a challenge (Attio 4.5, Google "bypassing protective measures"). That is a further reason to treat challenges as a stop-and-hand-to-John event rather than something to defeat.

### Gaps
- Slack AUP (slack.com/acceptable-use-policy page only links a PDF), Outreach terms and AUP (only the Jan 2021 AUP seen in a search excerpt), n8n Cloud terms, and Google Workspace-specific terms not opened.
- Attio clause numbers come from the fetch summary, not a direct quote of the numbering.
- Not legal advice.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Cloudflare Web Bot Auth / verified bots | https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/ | Signed HTTP requests plus registration so Cloudflare marks a bot verified | Cloudflare dashboard + own domain + key directory | 2026-10-16 | Skip: for bot operators; does not change how Attio or n8n's own Cloudflare rules treat John |
| Chrome DevTools MCP --autoConnect | https://developer.chrome.com/docs/devtools/agents/get-started/configuration | Attaches an agent to a running Chrome after a permission dialog (Chrome 144+) | John's machine | 2026-10-16 | Fallback: legit and visible; permission dialog makes it unsuited to unattended runs |
| Playwright channel: chrome | https://playwright.dev/docs/browsers | Drives branded Chrome installed on the host | local | 2026-10-16 | Use: headed real Chrome with a non-default persistent profile |
| playwright-personas, stealth plugins, CloakBrowser, CAPTCHA solvers | https://github.com/RyanCollinsAI/playwright-personas | Wrappers and patches to get past Google/Cloudflare checks (search excerpts only, not opened) | local | not opened | Reject: evasion, per earlier ruling |
