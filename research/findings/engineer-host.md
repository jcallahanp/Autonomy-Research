# Engineer host: where the autonomous engineer should live (bot flagging, browser and desktop control, chat control)

Put the engineer on a rented Linux (Ubuntu) VPS in US East. Run headed, branded Chrome through Playwright with a persistent, non-default profile under Xvfb with noVNC, and control it from the phone with Claude Code's own Remote Control plus a Telegram channel. NanoClaw is not the best remote for it.

- **Bot flagging.** Headless Chromium is the measured outlier for soft blocks: 15.2%, against about 7% for headed Chromium, measured from a data-center IP (https://arxiv.org/html/2606.14525v1). Google says it may refuse sign-in to browsers "controlled through software automation" (https://support.google.com/accounts/answer/7675428?hl=en). So headed real Chrome with John signing in by hand is the legitimate baseline. A home residential IP probably flags less, but no opened source measures the data-center versus residential difference (worker inference).
- **Desktop control.** Claude Code's built-in computer use is macOS-only in the CLI and is not available with `-p` (https://code.claude.com/docs/en/computer-use). The broadest native desktop control (macOS, Windows) therefore cannot be the unattended engineer's hands. Attio, Clay, n8n and Outreach are web apps, which browser control covers (worker inference).
- **Cost.** A DigitalOcean Basic 4 vCPU / 8 GiB Droplet is $48/month (https://www.digitalocean.com/pricing/droplets), and so is an Akamai/Linode 8 GB (https://www.akamai.com/cloud/pricing/north-america). Both cost less than cloud-desktop products such as Windows 365 Business 4 vCPU/16 GB at $56 (https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing) or a MacStadium M4 at $149 (https://macstadium.com/pricing).
- **Chat control.** NanoClaw runs its own Agent SDK agent in Docker (https://github.com/nanocoai/nanoclaw README.md:87 (commit 2105169)). It does not steer John's engineer session. Anthropic's legal page and its Help Center also disagree on using the Agent SDK with a Max login. Remote Control (https://code.claude.com/docs/en/remote-control) and Channels (https://code.claude.com/docs/en/channels) attach to the session on John's own host.

Overall confidence: medium.

## Recommendation

Cited facts carry a URL or a `path:line`. Lines marked **Synthesis reasoning** are the lead's or synthesizer's judgement, and lines marked **Worker inference** are a worker's judgement. Neither is cited fact.

**Already decided (from the lead's brief, not research):**
- Claude Max plan with `/login` (Path A).
- Overnight runs.
- GitHub Pro for self-merge.
- No 1Password.
- The first project is the GTM framework over Attio, Clay and n8n, which are web apps.

**Recommended setup:**
- **Host: a rented VPS (cloud VM), not a cloud-desktop product and not a home machine as the default.**
  - Each DigitalOcean Droplet has its own public IPv4 and costs $48/month at 4 vCPU / 8 GiB (https://www.digitalocean.com/pricing/droplets).
  - Windows 365 Flex keeps Dedicated Cloud PCs powered on only "for two hours after the user session becomes inactive" (https://learn.microsoft.com/en-us/windows-365/enterprise/windows-365-flex-cloud-pc-session-time-limits).
  - **Synthesis reasoning:** a VPS running Xvfb and noVNC already is a virtual computer, and it has none of a desktop product's idle limits.
- **OS: Ubuntu Linux.**
  - Claude Code supports Ubuntu 20.04+ with 4 GB+ RAM (https://code.claude.com/docs/en/setup).
  - The Anthropic computer-use reference build is a Linux Xvfb desktop (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
  - Windows over SSH runs in Session 0, "which has no desktop" (https://cua.ai/docs/cua-driver/guides/vms-and-remote).
  - **Worker inference:** Xvfb or a VNC desktop never locks, which makes Linux the best fit for unattended work.
- **Service: DigitalOcean Basic 4 vCPU / 8 GiB in US East, $48/month.**
  - Snapshots are $0.06/GB per month (https://www.digitalocean.com/pricing/droplets).
  - **Equal alternative:** Akamai/Linode 8 GB at $48/month, plus $10/month for backups (https://www.akamai.com/cloud/pricing/north-america).
  - **Cheap alternative, only if the sign-in spike passes from a German IP:** Hetzner CX33 at $9.99/month, excluding IPv4 (https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/).
  - **Worker inference:** the DigitalOcean setup with snapshots lands near $55-60/month.
- **Browser: Playwright driving branded Google Chrome, headed, with a persistent profile in a non-default `--user-data-dir`.**
  - Playwright can drive the branded Chrome installed on the machine (https://playwright.dev/docs/browsers).
  - Chrome 136+ ignores remote-debugging switches on the default profile (https://developer.chrome.com/blog/remote-debugging-port).
  - John signs in by hand once over noVNC.
  - Any challenge is a stop-and-hand-to-John event, never something to defeat. This follows the Google terms (https://policies.google.com/terms) and the Attio Acceptable Use terms (http://attio.com/legal/acceptable-use).
- **Desktop add-on: only if a non-browser need appears.**
  - Cua Driver registers with Claude Code as an MCP server (https://cua.ai/docs/cua-driver/guides/connect-your-agent) and supports Linux X11 with limits (https://cua.ai/docs/cua-driver/concepts/platform-support).
- **Chat control: Remote Control in server mode, plus the Telegram channel, on the host session, logged in with `claude auth login`.**
  - Remote Control is the phone cockpit: it shows a live view and sends push notifications (https://code.claude.com/docs/en/remote-control).
  - Telegram carries chat tasks and relays approval prompts (https://code.claude.com/docs/en/channels).
  - Remote Control does not accept `setup-token` (https://code.claude.com/docs/en/remote-control), which matches Path A.
  - NanoClaw is not recommended as the remote.
  - If WhatsApp or Slack must be the primary chat, run NanoClaw as a separate assistant on an API key funded by Max's monthly API credits (https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans). Use its Slack channel rather than Baileys WhatsApp (worker inference; see Q6).
- **Fallback host if the sign-in spike fails from a data-center IP: a Mac mini M6 at home.**
  - It costs $899 one-off (https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/) and idles at 4 W (https://support.apple.com/en-gb/103253).
  - Reach it through Tailscale (https://tailscale.com/plans) or Cloudflare Tunnel (https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/).
  - **Worker inference:** it trades a residential IP for consumer-grade uptime and harder isolation.

**Rejected:**

| Option | Why |
| --- | --- |
| AWS EC2 Mac | 24-hour dedicated-host minimum (https://aws.amazon.com/ec2/dedicated-hosts/pricing/); the about $898/month figure is unverified. |
| Windows 365 / Amazon WorkSpaces / Shadow PC | Windows-first or built around a human session, and dearer than a VPS (sources in Q3). |
| Claude Code CLI computer use as the unattended engineer's hands | Interactive only (https://code.claude.com/docs/en/computer-use). |
| Microsoft UFO as the engine | Brings its own LLM config (https://github.com/microsoft/UFO). |
| Stealth plugins, residential-proxy rotation, CAPTCHA solvers | Evasion; an earlier ruling already rejects them. |
| NanoClaw on a Max `setup-token` | Policy-contested (Q6 Contradictions). |

**Setup-day spikes that would change the call:**
1. Google sign-in and Attio sign-in from the VPS data-center IP, in both US East and Hetzner EU, noting every challenge. If Google blocks sign-in, move to the home Mac mini (residential IP).
2. Chrome logins surviving a snapshot restore, using the persistent `--user-data-dir` profile. If logins do not survive, plan a re-login runbook.
3. Remote Control and the Telegram channel attached to one session at the same time. If they cannot share a session, pick one of them for live approvals.
4. Memory use with real Attio, Clay, n8n and Outreach tabs on 8 GB. If memory is short, resize the VPS.
5. The chosen provider's acceptable-use policy. Only Hetzner's terms were opened.
6. Only if a desktop need appears: Cua Driver on Xvfb/XFCE under `claude -p`.
7. Only if Windows is chosen: Windows-MCP in an auto-logon VM, surviving an RDP disconnect.
8. Only if NanoClaw is kept: its approval-card flow on the phone, and a Slack custom channel.

## Questions and answers

### 1. What avoids bot flagging most?
Confidence: medium.

**Recommendation:** the least-flagged legitimate setup is headed, branded Chrome with a persistent profile that John signs into by hand, run at a human pace, with vendor APIs used wherever they exist. On the network side, a residential (home) IP is probably better than a data-center IP, but no opened source measures that.

**Browser layer (cited):**
- In a 2026 measurement (Playwright 1.57, the Tranco top 10k sites, one Hetzner data-center IP, no stealth), headless Chromium was the outlier at 15.2% soft blocks, against about 7% for headed Chromium and for both Firefox modes (https://arxiv.org/html/2606.14525v1).
- In the same paper, `navigator.webdriver` was probed on 34% of sites (https://arxiv.org/html/2606.14525v1).
- Cloudflare's JavaScript Detections engine "Catches headless browsers" (https://developers.cloudflare.com/bots/concepts/bot-score/).

**Network layer (cited):**
- The same paper warns that "scanning from a datacenter IP rather than a residential network affects absolute blocking rates", so its 7% headed figure is a data-center floor (https://arxiv.org/html/2606.14525v1).
- **Worker inference:** "data-center ASN is a strong prior" is widely asserted but not vendor-confirmed in the notes. The Cloudflare bot-score page lists request features and browser signals, not IP/ASN, as its ML inputs (https://developers.cloudflare.com/bots/concepts/bot-score/).

**The one documented hard blocker is Google sign-in:**
- Google may refuse sign-in to browsers "controlled through software automation rather than a human" (https://support.google.com/accounts/answer/7675428?hl=en).
- Playwright maintainers confirm this can happen and say stealth is not a Playwright goal (https://github.com/microsoft/playwright/issues/19420).

**John's SaaS apps:**
- A header probe from this sandbox's data-center egress, run 2026-10-16, found:
  - app.attio.com and www.n8n.io are behind Cloudflare.
  - app.clay.com is on Netlify via CloudFront.
  - accounts.google.com answers from GSE.
  - Attio's first load returned 200.
- The Slack and Outreach responses (403 and 502) may come from the proxy, so they are not evidence of bot blocking.
- No opened report shows these apps challenging a logged-in data-center session.

**Legitimate levers (cited):**
- Playwright can drive the branded Chrome installed on the machine (https://playwright.dev/docs/browsers).
- Chrome 136+ requires a non-default `--user-data-dir` for remote debugging (https://developer.chrome.com/blog/remote-debugging-port).
- In Chrome 144+, DevTools MCP can attach to a running Chrome after a permission dialog (https://developer.chrome.com/docs/devtools/agents/get-started/configuration).
- Cloudflare Web Bot Auth requires registering your own bot and its key directory (https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/). **Worker inference:** it therefore does not help John as a customer of Attio or n8n.

**Terms of service (cited):**
- Google bars "bypassing our systems or protective measures" (https://policies.google.com/terms).
- Attio bars attempts to "circumvent, disable, or interfere with any security or access controls" (http://attio.com/legal/acceptable-use).
- Clay's terms have no automation clause (https://www.clay.com/terms-of-service).
- Slack's Acceptable Use Policy was not read (https://slack.com/terms-of-service/user).

**Worker inferences:**
- Ranking, least flagged first:
  1. A home Mac Mini or PC with headed Chrome and a persistent non-default profile.
  2. The same setup on a rented VM with a static IP.
  3. Headless on a VM.
- The legitimate line is that the browser is what it claims to be. Stealth patches, rotating residential proxies, CAPTCHA solvers and UA spoofing are evasion.

**Contradictions:**
- Third-party Playwright wrappers claim a "Google CDP-block bypass": log in once in real Chrome, then reuse the profile. This was seen in search excerpts only and was not opened.
- Playwright's maintainer reply says automation-controlled browsers may be denied and offers no such fix (https://github.com/microsoft/playwright/issues/19420).
- Unresolved. The wrapper side is unverified. Spike 1 settles it on John's host.

### 2. What gives the most browser automation and full desktop control?
Confidence: medium (high for the computer-use limits).

**Recommendation:**
- For unattended work, the most control comes from a Linux VM with headed branded Chrome under Playwright, with a desktop MCP (Cua Driver) added only when a non-browser app must be driven.
- macOS and Windows have the broadest first-party desktop control, but it is interactive and supervised.

**Claude Code's built-in computer use (cited):**
- It requires an interactive session and "is not available in non-interactive mode with the `-p` flag" (https://code.claude.com/docs/en/computer-use).
- It is "not available on Linux or Windows" in the CLI; Windows gets it only through Desktop (https://code.claude.com/docs/en/computer-use).
- It runs one session at a time, under a lock (https://code.claude.com/docs/en/computer-use).
- Apps need per-session approval (https://code.claude.com/docs/en/computer-use).
- Browsers are view-only (https://code.claude.com/docs/en/computer-use).
- In Desktop, Dispatch approvals expire after 30 minutes (https://code.claude.com/docs/en/desktop).

**Anthropic's API computer-use tool (cited):**
- It is OS-agnostic, with a Linux Xvfb reference build (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
- The developer writes the agent loop (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
- **Worker inference:** this means a second loop beside Claude Code.

**Desktop MCP servers that keep Claude Code as the engine (cited):**
- Cua Driver registers with Claude Code in one command (https://cua.ai/docs/cua-driver/guides/connect-your-agent).
- It covers Mac, Windows and Linux. On Linux, standard Wayland blocks raw input to unfocused windows (https://cua.ai/docs/cua-driver/concepts/platform-support).
- Trusted pointer input to Chrome on X11 is unavailable (https://cua.ai/docs/cua-driver/concepts/platform-support).
- Windows-MCP installs with `claude mcp add` (https://github.com/CursorTouch/Windows-MCP).
- E2B Desktop is an Apache-2.0 Linux Xfce sandbox (https://github.com/e2b-dev/desktop).

**Browser control (cited):**
- Claude in Chrome pauses at a login page or CAPTCHA and asks the user to handle it (https://code.claude.com/docs/en/chrome).
- Claude Code keeps Chrome integration off under API-key or setup-token credentials (https://code.claude.com/docs/en/chrome).
- Chrome integration is not supported in WSL (https://code.claude.com/docs/en/chrome).
- The project registry already names a Playwright persistent profile as the engineer's primary driver (/home/user/Autonomy-Research/research/tool-registry.md:204-205).

**Is desktop control needed for GTM? (cited):**
- The computer-use docs reserve screen control "for things nothing else can reach: native apps, simulators such as the iOS Simulator, and tools without an API" (https://code.claude.com/docs/en/computer-use).
- **Worker inference:** Attio, Clay, n8n and Outreach are web apps, so browser control covers them. A Windows or Mac host wins only if a native app must be automated, and none is named.

**Synthesis reasoning:** "most control" and "unattended overnight" pull in different directions. The recommendation takes unattended reliability, because the first project is web-only.

### 3. VPS or virtual computer (cloud desktop)?
Confidence: medium.

**Recommendation:** a VPS.

**Cloud-desktop products (cited):**
- Windows 365 Business is $36 for 2 vCPU/8 GB, $56 for 4 vCPU/16 GB and $108.80 for 8 vCPU/32 GB, per user per month (https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing). It is a Windows desktop.
- The Windows 365 Flex doc says Dedicated Cloud PCs stay powered on only two hours after the session goes inactive (https://learn.microsoft.com/en-us/windows-365/enterprise/windows-365-flex-cloud-pc-session-time-limits). This is the Flex doc, not the Business plan.
- Amazon WorkSpaces Personal has AlwaysOn (flat monthly) and AutoStop (hourly). A Power Ubuntu AutoStop bundle is $7.25/month + $0.66/hour (https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/). The Ubuntu AlwaysOn price was not retrieved.
- The Shadow page opened is a gaming product with mostly monthly subscriptions (https://www.shadow.tech/en-us/pricing/).

**VPS (cited):**
- DigitalOcean is $48/month for 4 vCPU / 8 GiB. Snapshots are $0.06/GB per month, backups are 20-30% of the Droplet cost, and each Droplet has its own IPv4 (https://www.digitalocean.com/pricing/droplets).
- Hetzner snapshots stay stored until deleted and survive deletion of the server (https://www.hetzner.com/cloud/cost-optimized/).

**Worker inference:**
- Desktop products are designed around a human session.
- Unattended overnight work on them would need AlwaysOn and a no-idle-limit policy.
- A $48 Linux VPS with noVNC beats them on price and control.

### 4. Windows or Linux (and macOS)?
Confidence: medium (high on the computer-use limits; low on any OS effect on bot flagging).

**Recommendation:** Linux (Ubuntu).

**Linux:**
- Claude Code supports Ubuntu 20.04+ (https://code.claude.com/docs/en/setup).
- The computer-use reference desktop is Linux Xvfb (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
- Cua Driver supports X11, with toolkit limits (https://cua.ai/docs/cua-driver/concepts/platform-support).
- **Limits (cited):** no Claude Code built-in computer use (https://code.claude.com/docs/en/computer-use), and Wayland input limits (https://cua.ai/docs/cua-driver/concepts/platform-support).
- **Worker inference:** Linux cannot run Mac-only or Windows-only apps, and a browser-only GTM stack does not need them.

**Windows:**
- **Strengths (cited):**
  - Desktop app computer use works on Windows (https://code.claude.com/docs/en/desktop).
  - Windows-MCP covers Windows 7 to 11 (https://github.com/CursorTouch/Windows-MCP).
  - Microsoft UFO2 uses native UIA/Win32 control (https://github.com/microsoft/UFO).
- **Limits (cited):**
  - Windows OpenSSH runs in Session 0, which has no desktop (https://cua.ai/docs/cua-driver/guides/vms-and-remote).
  - Windows-MCP prefers English Windows and must run on the Windows side even from WSL (https://github.com/CursorTouch/Windows-MCP).
  - Claude in Chrome is not supported in WSL (https://code.claude.com/docs/en/chrome).
- That RDP disconnect locks the desktop (needing a tscon workaround) was seen in search excerpts only, so it is unverified.
- **Worker inference:** overnight work on Windows needs an auto-logon VM with the session kept attached to the console, which adds work that Linux does not.

**macOS:**
- **Strengths (cited):**
  - The most polished first-party path: CLI and Desktop computer use (https://code.claude.com/docs/en/computer-use).
  - Cua Lume VMs on Apple Silicon (https://github.com/trycua/cua).
- **Limits (cited):**
  - Needs Accessibility and Screen Recording grants (https://code.claude.com/docs/en/computer-use).
  - Hides other apps while Claude works (https://code.claude.com/docs/en/computer-use).
  - Is not available with third-party providers such as Bedrock (https://code.claude.com/docs/en/computer-use).
  - Mac desktops sleep when the display is off (https://www.apple.com/mac-mini/).
- Behaviour with a locked or asleep screen is undocumented.

**Bot flagging and OS:**
- The 2026 measurement paper reports nothing about the operating system. This is absence of evidence only (https://arxiv.org/html/2606.14525v1).
- **Worker inference:** the OS matters only through consistency, which argues for no UA spoofing, not for a particular OS.

### 5. The best services for the plan, with prices
Confidence: medium (prices pulled 2026-10-16; Vultr, Oracle A1, OVH, AVD and MacinCloud not checked).

| Service | Spec and price (cited) | Fit |
| --- | --- | --- |
| DigitalOcean Basic Droplet | 4 vCPU / 8 GiB, $48/month; snapshots $0.06/GB/month; backups 20% weekly or 30% daily (https://www.digitalocean.com/pricing/droplets) | **Recommended**, US East |
| Akamai / Linode 8 GB | 4 vCPU, 160 GB, $48/month; backups $10/month (https://www.akamai.com/cloud/pricing/north-america) | Equal alternative |
| Hetzner CX33 (Germany/Finland) | $9.99/month excluding IPv4, after the 15 June 2026 adjustment (https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | Cheap alternative, if the EU latency and sign-in spike pass |
| Hetzner CPX31 (US ASH/HIL) | $73.49/month excluding IPv4 (https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | Dearer than DigitalOcean in the US |
| AWS Lightsail Compute Optimized | 8 GB / 4 vCPU, $84/month (https://aws.amazon.com/lightsail/pricing/) | Skip |
| GCP e2-standard-4 | 4 vCPU / 16 GiB, $0.13402284/hour (https://cloud.google.com/products/compute/pricing/general-purpose); about $98/month at 730 h (worker arithmetic) | Skip |
| Vultr | Snapshots $0.05/GB/month (https://www.vultr.com/pricing/); 4 vCPU / 8 GB price not read | Unverified |
| Oracle Cloud Always Free (Ampere A1) | Idle accounts may be terminated after 30 days (https://www.oracle.com/cloud/free/) | Fallback only |
| Windows 365 Business | 4 vCPU / 16 GB, $56/user/month (https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing) | Skip |
| Amazon WorkSpaces Personal | Power Ubuntu AutoStop $7.25/month + $0.66/hour (https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/) | Skip |
| Mac mini M6 (buy, home) | From $899 (https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/); 4 W idle (https://support.apple.com/en-gb/103253) | Home fallback |
| MacStadium | M4 16 GB / 256 GB $149/month; M4 Pro 48 GB $349 (https://macstadium.com/pricing) | Fallback if macOS is needed without buying |
| Scaleway Mac mini M4 | EUR 149/month, 24 h minimum, Paris (https://www.scaleway.com/en/pricing/apple-silicon/) | Fallback; EU latency |
| AWS EC2 Mac | Dedicated host, 24 h minimum (https://aws.amazon.com/ec2/dedicated-hosts/pricing/); the about $898/month figure rests on an unverified hourly rate | Reject on cost |
| Tailscale Personal | Free; 3 users, 100 devices (https://tailscale.com/plans) | Use for private access |
| Cloudflare Tunnel | Outbound-only connections (https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/); price not on the page | Alternative to Tailscale |
| Max monthly API credits | Max 5x $100, Max 20x $200; apply only with an API key (https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans) | Use only for any Agent SDK bridge |

**Worker inferences:**
- DigitalOcean plus snapshots comes to about $55-60/month.
- The $899 Mac mini equals about 19 months of a $48 VPS.
- Renting a cloud Mac breaks even with buying after about 6 months.
- Claude Code needs 4 GB+ RAM (https://code.claude.com/docs/en/setup), so 4 vCPU / 8 GB covers Claude Code, Xvfb/noVNC and 2-3 browsers. This is an unmeasured estimate (Spike 4).

**Contradictions:**
- Hetzner CX33: Hetzner's own table says EUR 8.49 / $9.99 (https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/), while a third-party list (eucloudcost.com, search excerpt only) says EUR 10.70. The vendor table is favoured.
- Tailscale's free tier: "Limited to 3 users" on https://tailscale.com/plans, against 6 users on third-party pages (search excerpts only). The vendor page is favoured, and one user fits either.

### 6. Is NanoClaw the best way to control the engineer from WhatsApp or Slack, and what is better?
Confidence: medium (high on the facts, medium on fit).

**Recommendation:** no.
- Use Claude Code's own **Remote Control** in server mode as the phone cockpit.
- Add the **Telegram channel** for chat tasks and relayed approvals.
- Keep NanoClaw only if WhatsApp or Slack must be the primary chat. In that case run it as a separate assistant on an API key funded by Max API credits, and prefer its Slack channel over Baileys WhatsApp.

**What NanoClaw is (cited):**
- It offers WhatsApp, Telegram, Slack, Teams, iMessage and other channels as add-on skills (https://github.com/nanocoai/nanoclaw README.md:91 (commit 2105169)).
- It "natively uses Claude Code via Anthropic's official Claude Agent SDK" (https://github.com/nanocoai/nanoclaw README.md:87 (commit 2105169); https://github.com/nanocoai/nanoclaw container/agent-runner/package.json:12 (commit 2105169)).
- It runs one Docker container per session behind a credential gateway (https://github.com/nanocoai/nanoclaw README.md:97 (commit 2105169); https://github.com/nanocoai/nanoclaw docs/SECURITY.md:24-28 (commit 2105169)).
- Its WhatsApp adapter uses Baileys (https://github.com/nanocoai/nanoclaw docs/api-details.md:221 (commit 2105169)).
- It offers subscription OAuth or an API key (https://github.com/nanocoai/nanoclaw docs/SPEC.md:391 and :397 (commit 2105169)).
- Its setup captures the `claude setup-token` output (https://github.com/nanocoai/nanoclaw setup/lib/captured-token.ts:49 (commit 2105169)).
- The repo has 30,951 stars and 1,048 open issues (https://github.com/nanocoai/nanoclaw).
- Release 2026.10.0 closes "a credential-injection bypass" (https://github.com/nanocoai/nanoclaw CHANGELOG.md (commit 2105169)).
- **Worker inference:** NanoClaw runs its own agent and does not attach to John's host session. The engineer's Playwright, Chrome and noVNC setup would have to be rebuilt inside the container or mounted into it.

**Anthropic-native options (cited):**
- **Channels:**
  - Supports Telegram, Discord and iMessage only (https://code.claude.com/docs/en/channels).
  - Needs an open session (https://code.claude.com/docs/en/channels).
  - Relays permission prompts, and anyone who can reply through the channel can approve (https://code.claude.com/docs/en/channels).
  - Is a research preview (https://code.claude.com/docs/en/channels).
- **Remote Control:**
  - Pro/Max only; "API keys are not supported" (https://code.claude.com/docs/en/remote-control).
  - Has a server mode for a headless host (https://code.claude.com/docs/en/remote-control).
  - Sends push notifications (https://code.claude.com/docs/en/remote-control).
  - Keeps subagent progress in sync across devices (https://code.claude.com/docs/en/remote-control).
  - Gives up after about 10 minutes offline (https://code.claude.com/docs/en/remote-control).
  - Cannot be established with setup-token tokens (https://code.claude.com/docs/en/remote-control).
- **Claude in Slack:**
  - Starts cloud sessions (https://code.claude.com/docs/en/slack).
  - Works only in channels, not DMs, and only on GitHub repos (https://code.claude.com/docs/en/slack).
  - Claude Tag isn't available on individual plans (https://code.claude.com/docs/en/slack).
  - **Worker inference:** neither can reach the VPS browser session.

**WhatsApp (cited):**
- A Baileys bridge "carries a small risk of account restrictions", and its authors advise a dedicated number (https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp).
- Meta's AI Provider clause was seen in search excerpts only, so whether a private single-user bot on the Cloud API is allowed is unsettled.

**Worker inferences:**
- There is no native WhatsApp or Slack channel for a local session.
- A custom channel could bridge Slack without a second agent, but this is untested.

**Contradictions:**
- The Anthropic legal page says: "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication". It also says Anthropic does not permit routing "through Free, Pro, or Max plan credentials on behalf of their users" (https://code.claude.com/docs/en/legal-and-compliance).
- The Help Center (updated 2026-10-07) says: "You can still use the Claude Agent SDK, claude -p, and third-party apps with your subscription limits" (https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan).
- NanoClaw's docs offer a subscription OAuth token (https://github.com/nanocoai/nanoclaw docs/SPEC.md:391 (commit 2105169)).
- The legal page expressly allows "an end user ... signing in to the unmodified Claude Code binary with their own Claude subscription" (https://code.claude.com/docs/en/legal-and-compliance).
- **What the evidence favours:**
  - Remote Control, Channels and `claude -p` on John's own login sit on the safe side of both pages.
  - Whether NanoClaw (an Agent SDK harness) on John's own Max token is allowed is **unresolved**: the legal clause targets third parties serving other users, and a single owner is not addressed directly.
  - Settling it needs written confirmation from Anthropic. It is listed under Open questions.
- Press excerpts (pcmag, oflight; not opened) report that Anthropic's 2026 policy on subscriptions in third-party harnesses reversed more than once. They are not cited.

## Evidence

All sources opened 2026-10-16.

### Bot flagging (notes/bot-flagging.md)
- E1. https://developers.cloudflare.com/bots/concepts/bot-score/ — 2026-10-16, WebFetch — Claim: Cloudflare's JavaScript Detections engine targets headless browsers; the bot score comes from a layered set of engines (heuristics, ML, JSD). — Quote: "Catches headless browsers (browsers controlled by software, with no visible window or human operator)"
- E2. https://developers.cloudflare.com/bots/concepts/bot-score/ — 2026-10-16, WebFetch — Claim: Cloudflare's ML inputs are request features and browser signals, not named IP/ASN on that page; fingerprint databases sit in Heuristics. (Cloudflare docs do not list ASN as an input on this page.) — Quote: "Request features, including headers, session characteristics, and browser signals"
- E3. https://support.google.com/accounts/answer/7675428?hl=en — 2026-10-16, WebFetch — Claim: Google says it may refuse sign-in from automation-controlled browsers (Google sign-in risk check, first-party statement). — Quote: "Are being controlled through software automation rather than a human"
- E4. https://support.google.com/accounts/answer/7675428?hl=en — 2026-10-16, WebFetch — Claim: Google's own help page lists automation as a reason to refuse sign-in, which is the documented risk for the Google Workspace and "sign in with Google" steps. — Quote: "Are being controlled through software automation rather than a human"
- E5. https://github.com/microsoft/playwright/issues/19420 — 2026-10-16, WebFetch — Claim: Playwright maintainers confirm Google can deny sign-in to a Playwright-driven browser, e.g. via the webdriver flag; stealth is not a Playwright goal. — Quote: "Google has all kinds of antibot protection and since the browser is controlled by browser automation tool"
- E6. https://arxiv.org/html/2606.14525v1 — 2026-10-16, WebFetch — Claim: Measured 2026 (Playwright 1.57, Tranco top 10k, one Hetzner data-center IP, no stealth): headless Chromium is the outlier at 15.2% soft blocks versus about 7% for headed Chromium and both Firefox modes. — Quote: "Chromium headless is a clear outlier at 15.2%, while the remaining three conditions cluster between 6.8–7.2%."
- E7. https://arxiv.org/html/2606.14525v1 — 2026-10-16, WebFetch — Claim: Same paper: Cloudflare and Akamai blocked far above average; navigator.webdriver probed on 34% of sites and DevTools probes on 21%. — Quote: "The most prevalent Tier 1 signal is navigator.webdriver, accessed on 2,730 (34%) of 7,944 successfully scanned sites."
- E8. https://arxiv.org/html/2606.14525v1 — 2026-10-16, WebFetch — Claim: Same paper warns data-center scanning shifts absolute block rates (so the 7% headed figure is a data-center floor, not a residential one). — Quote: "scanning from a datacenter IP rather than a residential network affects absolute blocking rates"
- E9. Header probe (`curl -D`) of app.attio.com, www.n8n.io, app.clay.com, accounts.google.com, slack.com/signin and app.outreach.io from this sandbox's egress via the agent proxy (a data-center IP), run 2026-10-16, Bash — Claim: app.attio.com and www.n8n.io return `server: cloudflare` with cf-ray; app.clay.com returns `server: Netlify` via CloudFront; accounts.google.com returns `server: GSE`. (Probe returned HTTP 200 for app.attio.com and app.clay.com, 301 for www.n8n.io, 403 from slack.com/signin (server: Apache, via slack-prod.tinyspeck.com), 502 from app.outreach.io. The 403/502 may come from the proxy, so they are not evidence of bot blocking.) — Quote: "server: cloudflare"
- E10. https://arxiv.org/html/2606.14525v1 — 2026-10-16, WebFetch — Claim: The 2026 measurement paper reports nothing about operating system (fetch summary: the paper "does not mention an operating system"; absence only). — Quote: "scanning from a datacenter IP rather than a residential network affects absolute blocking rates"
- E11. https://playwright.dev/docs/browsers — 2026-10-16, WebFetch — Claim: Playwright says real Chrome and Edge are selectable via channel on the machine and that their new headless mode differs from the default headless shell. — Quote: "You can opt into the new headless mode by using 'chromium' channel."
- E12. https://playwright.dev/docs/browsers — 2026-10-16, WebFetch — Claim: Playwright can drive branded Google Chrome already on the machine via `channel`. — Quote: "can operate against the branded Google Chrome and Microsoft Edge browsers available on the machine"
- E13. https://developer.chrome.com/blog/remote-debugging-port — 2026-10-16, WebFetch — Claim: Chrome 136+ ignores --remote-debugging-port on the default profile; automation must use a non-default --user-data-dir. — Quote: "These switches will no longer be respected if attempting to debug the default Chrome data directory."
- E14. https://developer.chrome.com/docs/devtools/agents/get-started/configuration — 2026-10-16, WebFetch — Claim: Chrome's own supported agent route: Chrome 144+ lets DevTools MCP attach to a running Chrome after the user allows it in a dialog. — Quote: "When the agent attempts to connect, Chrome shows a dialog asking for permission."
- E15. https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ — 2026-10-16, WebFetch — Claim: Cloudflare verified bots include user-driven agents but require honest self-identification and non-abusive behaviour. — Quote: "A Verified bot is a bot or agent that Cloudflare has confirmed is transparent about who it is and what it does"
- E16. https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/ — 2026-10-16, WebFetch — Claim: Web Bot Auth requires a hosted key directory and registering the bot with Cloudflare; it is written for bot operators, not for visiting a third-party SaaS as a customer. — Quote: "You need to register your bot and its key directory to add your bot to the list of verified bots."
- E17. https://policies.google.com/terms — 2026-10-16, WebFetch — Claim: Google's terms prohibit bypassing protective measures, which frames stealth as a ToS issue. — Quote: "spamming, hacking, or bypassing our systems or protective measures"
- E18. http://attio.com/legal/acceptable-use — 2026-10-16, WebFetch — Claim: Attio's Acceptable Use terms bar circumventing access controls and limits (fetch summary: no words "scraping", "bots" or "scripts"). — Quote: "circumvent, disable, or interfere with any security or access controls"
- E19. http://attio.com/legal/acceptable-use — 2026-10-16, WebFetch — Claim: Attio caps API use. — Quote: "attempt to exceed or circumvent any express or implied limitations on use of the Attio Services"
- E20. https://www.clay.com/terms-of-service — 2026-10-16, WebFetch — Claim: Clay's terms (last updated May 23, 2024) have no automation clause. — Quote: "Clay Labs has the right to review and monitor all use of the Services"
- E21. https://policies.google.com/terms — 2026-10-16, WebFetch — Claim: Google's terms restrict automated access that violates robots.txt and scraping content not yours. — Quote: "scraping content that doesn’t belong to you"
- E22. https://slack.com/terms-of-service/user — 2026-10-16, WebFetch — Claim: Slack's User Terms incorporate the Acceptable Use Policy by reference; the AUP text was not on the page. — Quote: "you agree to comply with the most recent version of our Acceptable Use Policy"

### Desktop and browser control (notes/desktop-control.md)
- E23. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: CLI computer use is a macOS research preview, Pro/Max only, interactive only. — Quote: "It requires an interactive session, so it is not available in non-interactive mode with the `-p` flag."
- E24. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: The CLI server does not exist on Linux or Windows. — Quote: "Computer use in the CLI is not available on Linux or Windows. On Windows, use computer use in Desktop instead."
- E25. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Comparison table: Desktop is macOS and Windows, CLI macOS only. — Quote: "| Platforms | macOS and Windows | macOS only |"
- E26. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: It controls the real desktop, one session at a time, via a lock held until the session exits. — Quote: "Only one session at a time can use your computer. A session takes a lock at its first computer use action and releases it when the session exits"
- E27. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Per-app approval prompts appear in the terminal each session (human in the loop). — Quote: "Choose **Allow for this session** or **Deny**. Approvals last for the current session."
- E28. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Browsers are view-only for computer use; Claude prefers other tools first. — Quote: "browsers and trading platforms are view-only, terminals and IDEs are click-only, and everything else gets full control."
- E29. https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — 2026-10-16, WebFetch — Claim: Anthropic API tool: reference implementation is a Linux Xvfb desktop in Docker. — Quote: "A virtual X11 display server (using Xvfb) that renders the desktop interface Claude will see through screenshots and control with mouse/keyboard actions."
- E30. https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — 2026-10-16, WebFetch — Claim: The developer implements the loop and executors. — Quote: "An agent loop that interacts with the Claude API and runs the `tool_use` results using your tool implementations"
- E31. https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — 2026-10-16, WebFetch — Claim: Not on Managed Agents; sandbox required; resolution advice. — Quote: "Computer use requires a sandboxed computing environment where Claude can safely interact with applications and the web." Also "Avoid resolutions above 1920x1080 to prevent performance issues."
- E32. https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool — 2026-10-16, WebFetch — Claim: Security advice includes keeping login data out of the model's reach. — Quote: "Avoiding giving the model access to sensitive data, such as account login information, to prevent information theft."
- E33. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Claude Code itself still does not reach computer use via Chrome fallback: browser work goes to Claude in Chrome first. — Quote: "If the task is browser work and you have Claude in Chrome set up, Claude uses that."
- E34. https://github.com/CursorTouch/Windows-MCP — 2026-10-16, Parallel fetch — Claim: Windows-MCP: MIT, Windows 7 to 11, one-line Claude Code install. — Quote: "claude mcp add --transport stdio windows-mcp -- uvx windows-mcp serve"
- E35. https://github.com/CursorTouch/Windows-MCP — 2026-10-16, Parallel fetch — Claim: Windows-MCP needs Python 3.13+ and prefers English Windows. — Quote: "`English` as the default language in Windows preferred else disable the `App-Tool` in the MCP Server for Windows with other languages."
- E36. https://github.com/CursorTouch/Windows-MCP — 2026-10-16, Parallel fetch — Claim: Windows-MCP from WSL still runs on Windows side. — Quote: "If you run Claude Code from WSL, the MCP server must still execute on the Windows side (it needs Windows APIs for UI automation)."
- E37. https://cua.ai/docs/cua-driver/concepts/platform-support — 2026-10-16, Parallel fetch — Claim: Cua Driver supports Windows, with a limit on elevated apps. — Quote: "Some background Chromium gestures and elevated-integrity targets refuse or are unproven."
- E38. https://cua.ai/docs/cua-driver/guides/vms-and-remote — 2026-10-16, Parallel fetch — Claim: Cua on Windows over SSH sees nothing: SSH runs in Session 0. — Quote: "Windows OpenSSH runs in Session 0, which has no desktop, so window tools return empty results there."
- E39. https://cua.ai/docs/cua-driver/guides/connect-your-agent — 2026-10-16, Parallel fetch — Claim: Cua registers with Claude Code in one command. — Quote: "claude mcp add --transport stdio cua-driver -- cua-driver mcp"
- E40. https://github.com/microsoft/UFO — 2026-10-16, Parallel fetch — Claim: Microsoft UFO: UFO2 is the single-device Windows agent in LTS, MIT, brings its own LLM config (OpenAI default, Claude listed). — Quote: "Status | ✅ LTS (Long-Term Support)" and "Windows UIA, Win32, WinCOM native control"
- E41. https://code.claude.com/docs/en/desktop — 2026-10-16, WebFetch — Claim: Desktop app computer use works on Windows with a toggle, app must be running, background operation macOS only. (Same page: background operation is macOS only, paraphrase of the fetch summary.) — Quote: "Computer use is a research preview on macOS and Windows that requires a Pro or Max plan."
- E42. https://cua.ai/docs/cua-driver/concepts/platform-support — 2026-10-16, Parallel fetch — Claim: Cua Driver on Linux: X11 supported with toolkit limits, Wayland with compositor limits. — Quote: "Standard Wayland: an ordinary client cannot send raw input to an unfocused, occluded window. AT-SPI actions still work in the background."
- E43. https://cua.ai/docs/cua-driver/concepts/platform-support — 2026-10-16, Parallel fetch — Claim: Cua on Linux X11 Chrome cannot do trusted pointer input. — Quote: "Trusted pointer returns `browser_input_trust_unavailable`; dialogs need foreground."
- E44. https://github.com/trycua/cua — 2026-10-16, Parallel fetch — Claim: Cua licensing: Driver MIT, Spaces FSL-1.1-MIT, optional perception extension AGPL. — Quote: "Cua Spaces is source-available under FSL-1.1-MIT"
- E45. https://github.com/trycua/cua — 2026-10-16, Parallel fetch — Claim: Cua install is a curl-pipe script (page instruction to install; not followed, nothing run; quoted as data). — Quote: "/bin/bash -c \"$(curl -fsSL https://cua.ai/driver/install.sh)\""
- E46. https://github.com/e2b-dev/desktop — 2026-10-16, Parallel fetch — Claim: E2B Desktop: Apache-2.0 Linux Xfce sandbox with streaming. — Quote: "The desktop-like environment is based on Linux and Xfce at the moment."
- E47. https://code.claude.com/docs/en/chrome — 2026-10-16, WebFetch — Claim: Claude in Chrome is not supported on WSL and is interactive only. — Quote: "Chrome integration isn't supported in Windows Subsystem for Linux (WSL)."
- E48. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Needs Accessibility and Screen Recording grants; first-time prompt. — Quote: "Accessibility: lets Claude click, type, and scroll" and "Screen Recording: lets Claude see what's on your screen"
- E49. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Other apps are hidden while Claude works. — Quote: "When Claude starts controlling your screen, other visible apps are hidden so Claude interacts with only the approved apps."
- E50. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Esc aborts and the session keeps the lock. — Quote: "The session keeps the computer use lock until it exits."
- E51. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Not available with API-key/third-party auth. — Quote: "Computer use is not available with third-party providers like Amazon Bedrock"
- E52. https://code.claude.com/docs/en/desktop — 2026-10-16, WebFetch — Claim: Desktop: Dispatch approvals expire. — Quote: "App approvals in those sessions expire after 30 minutes and re-prompt, rather than lasting the full session like regular Code sessions."
- E53. https://github.com/trycua/cua — 2026-10-16, Parallel fetch — Claim: Cua on macOS: needs Accessibility and Screen Recording, supports background delivery, Lume VMs on Apple Silicon. — Quote: "Lume: local macOS and Linux VMs on Apple Silicon"
- E54. https://cua.ai/docs/cua-driver/guides/vms-and-remote — 2026-10-16, Parallel fetch — Claim: Cua in a Lume VM still needs permission prompts approved. — Quote: "Approve three kinds of prompt: Accessibility and Screen Recording for CuaDriver"
- E55. https://code.claude.com/docs/en/chrome — 2026-10-16, WebFetch — Claim: Claude in Chrome already handles logged-in web apps and pauses on login/CAPTCHA. — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- E56. https://code.claude.com/docs/en/chrome — 2026-10-16, WebFetch — Claim: But it is not suited to unattended use: requires subscription login, off under API key or setup-token. — Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`, because the browser extension can't authenticate with those credentials."
- E57. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Claude Code itself prefers the precise tool first and treats computer use as last resort. — Quote: "Computer use is the broadest and slowest, so Claude tries the most precise tool first"
- E58. https://code.claude.com/docs/en/computer-use — 2026-10-16, WebFetch — Claim: Computer-use docs list what only screen control reaches. — Quote: "Screen control is reserved for things nothing else can reach: native apps, simulators such as the iOS Simulator, and tools without an API."
- E59. /home/user/Autonomy-Research/research/tool-registry.md:204-205 — 2026-10-16, Read — Claim: Existing project registry: Playwright CLI/MCP persistent profile is the engineer's browser driver. — Quote: "primary driver for the engineer; spike on real Attio/Clay tasks"

### Hosting services (notes/hosting-services.md)
- E60. https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ — 2026-10-16, curl+parse — Claim: Hetzner CX33 (4 vCPU / 8 GB) Germany/Finland is $9.99/month excl. IPv4 after the 15 June 2026 adjustment (EUR 8.49). — Quote: "CX33|0.0104 / 6.49|0.0136 / 8.49|0.0128 / 7.99|0.0160 / 9.99" (old EUR/new EUR/old USD/new USD, hourly / monthly; parsed from table HTML).
- E61. https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ — 2026-10-16, Parallel fetch — Claim: Hetzner US (ASH/HIL) list in that table carries CCX and CPX types; CPX31 is $73.49/month excl. IPv4 after the increase. — Quote: "|CPX31 |0.0336 / 20.99 |0.1001 / 62.49 |0.0400 / 24.99 |0.1178 / 73.49 |"
- E62. https://www.hetzner.com/cloud/cost-optimized/ — 2026-10-16, Parallel fetch — Claim: Hetzner snapshots are manual copies kept until deleted; they survive deletion of the server. — Quote: "Snapshots are one-time, manually created copies of the server hard drive that remain permanently stored until they are actively deleted."
- E63. https://www.hetzner.com/legal/terms-and-conditions/ — 2026-10-16, Parallel fetch — Claim: Hetzner terms prohibit DDoS, open mail relays, spam and crypto mining; I found no clause against browser automation. — Quote: "The operation of applications for mining cryptocurrencies remains prohibited."
- E64. https://www.digitalocean.com/pricing/droplets — 2026-10-16, Parallel fetch — Claim: DigitalOcean Basic 4 vCPU / 8 GiB is $48/month; snapshots $0.06/GB/month; backups 20% (weekly) or 30% (daily) of Droplet cost; each Droplet has its own public IPv4. — Quote: "|Droplet Snapshots |$0.06/GB per month |"; "| 8 GiB | 4 vCPUs | 5,000 GiB | 160 GiB | $0.07143 | [$48.00]"
- E65. https://www.akamai.com/cloud/pricing/north-america — 2026-10-16, Parallel fetch — Claim: Akamai/Linode 8 GB shared is 4 vCPU, 160 GB, $48/month; backups for that size $10/month. — Quote: "| Linode 8 GB | $48.00 | $0.0720 | 8 GB | 4 | 160 GB | 5 TB | 40/5 Gbps |"
- E66. https://www.vultr.com/pricing/ — 2026-10-16, Parallel fetch — Claim: Vultr stored snapshots cost $0.05/GB/month, automatic backups add 20%. — Quote: "Stored snapshots will cost $0.05/GB per month - pricing subject to change."
- E67. https://aws.amazon.com/lightsail/pricing/ — 2026-10-16, Parallel fetch — Claim: AWS Lightsail: Compute Optimized 8 GB / 4 vCPU is $84/month (General Purpose 8 GB is only 2 vCPU at $44), public IPv4 included. — Quote: "$84 USD/mo **8 GB** Memory **4** vCPUs **320 GB** SSD Disk **6 TB** Transfer*"
- E68. https://cloud.google.com/products/compute/pricing/general-purpose — 2026-10-16, Parallel fetch — Claim: GCP e2-standard-4 (4 vCPU / 16 GiB) lists at $0.13402284/hour on-demand (about $98/month at 730 h); e2-standard-2 (2 vCPU / 8 GiB) $0.06701142/hour; us-east1/east4/east5 regions exist. — Quote: "|e2-standard-4 |4 |16 GiB |$0.13402284 / 1 hour"
- E69. https://www.oracle.com/cloud/free/ — 2026-10-16, Parallel fetch — Claim: Oracle Always Free includes Arm Ampere A1 compute, but idle accounts can be terminated. — Quote: "Accounts left idle for 30 days or more may be deemed abandoned and become eligible for suspension or termination."
- E70. https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing — 2026-10-16, Parallel fetch — Claim: Windows 365 Business: 2 vCPU/8 GB/128 GB $36; 4 vCPU/16 GB/128 GB $56; 8 vCPU/32 GB/256 GB $108.80 per user per month. — Quote: "Windows 365 Business 4 vCPU, 16 GB, 128 GB ... $56.00 user/month"
- E71. https://learn.microsoft.com/en-us/windows-365/enterprise/windows-365-flex-cloud-pc-session-time-limits — 2026-10-16, Parallel fetch — Claim: Windows 365 Flex Cloud PCs (the shared/idle-limited variant) sign users out on idle and keep dedicated ones powered only two hours after the session goes inactive; this is the Flex doc, not the Business always-on plan. — Quote: "Windows 365 Flex Cloud PCs in Dedicated mode remain powered on for two hours after the user session becomes inactive."
- E72. https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/ — 2026-10-16, Parallel fetch — Claim: Amazon WorkSpaces Personal has AlwaysOn (flat monthly, unlimited use) and AutoStop (stops after disconnect, hourly billing); a Power Ubuntu AutoStop bundle is $7.25/month + $0.66/hour. — Quote: "AlwaysOn virtual desktops are billed at a predictable, flat monthly rate for unlimited usage"
- E73. https://www.shadow.tech/en-us/pricing/ — 2026-10-16, Parallel fetch — Claim: Shadow PC page opened is a French-language gaming landing page, mostly "cloud gaming"; no US price extracted. — Quote: "Shadow subscriptions are mostly monthly-based."
- E74. https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/ — 2026-10-16, Parallel fetch — Claim: Apple: Mac mini with M6 starts at $899 (US), education $799; M5 Pro $1,699; shipping from 22 September 2026. — Quote: "Mac mini with M6 starts at **$899** (U.S.) and **$799** (U.S.) for education"
- E75. https://support.apple.com/en-gb/103253 — 2026-10-16, Parallel fetch — Claim: Apple support power table: Mac mini M6 16 GB/256 GB idle 4 W, max 70 W; M4 idle 4 W, max 65 W. — Quote: "| 4 W | 70W | 14 BTU/h | 239 BTU/h |"
- E76. https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/ — 2026-10-16, Parallel fetch — Claim: Apple newsroom pitches this Mac mini for "always-on agentic computing". — Quote: "supercharging the leading desktop for always-on agentic computing"
- E77. https://macstadium.com/pricing — 2026-10-16, WebFetch — Claim: MacStadium Mac mini monthly: M2 8 GB $109, M4 16 GB/256 GB $149, M4 24 GB/512 GB $249, M4 Pro 48 GB $349. — Quote: "M4.S Mac mini M4 10 Core 16 GB 256 GB SSD $149" (text from the fetched table; WebFetch summarised it).
- E78. https://www.scaleway.com/en/pricing/apple-silicon/ and https://www.scaleway.com/en/mac-mini-m4 — 2026-10-16, Parallel fetch — Claim: Scaleway Mac mini M4: EUR 149/month (16 GB/256 GB), EUR 199/month (32 GB/1 TB), M4 Pro 64 GB EUR 335; hourly EUR 0.22; Paris only; 24-hour minimum; macOS only. — Quote: "| M4-S | Apple M4 CPU 10C / GPU 10C / Neural 16C - 4.4Ghz | 16 GB | 1 × 256 GB SSD | 1 Gbps | €149 /MONTH €0.22 /HOUR |"
- E79. https://aws.amazon.com/ec2/dedicated-hosts/pricing/ — 2026-10-16, Parallel fetch — Claim: AWS EC2 Mac is billed as a dedicated host with a 24-hour minimum. — Quote: "On-Demand EC2 Mac Dedicated Hosts have a minimum host allocation and billing duration of 24 hours."
- E80. https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ — 2026-10-16, Parallel fetch — Claim: Cloudflare Tunnel uses outbound-only connections, no publicly routable IP needed, and can have all inbound traffic blocked at the firewall. — Quote: "a lightweight daemon in your infrastructure (`cloudflared`) creates outbound-only connections to Cloudflare's global network."
- E81. https://tailscale.com/plans — 2026-10-16, Parallel fetch — Claim: Tailscale Personal plan is free forever, 100 devices, 3 users on the current plans page. — Quote: "Limited to 3 users 100 devices Access nearly all of Tailscale's features Use Tailscale for free, indefinitely"
- E82. https://www.apple.com/mac-mini/ — 2026-10-16, Parallel fetch — Claim: Apple states Mac desktops sleep when the display is off, to be handled in System Settings > Energy. — Quote: "To conserve energy, Mac desktops automatically sleep when the display is off."
- E83. https://code.claude.com/docs/en/setup — 2026-10-16, Parallel fetch — Claim: Claude Code needs 4 GB+ RAM, x64 or ARM64, macOS 13+/Windows 10 1809+/Ubuntu 20.04+. — Quote: "**Hardware**: 4 GB+ RAM, x64 or ARM64 processor"
- E84. https://www.akamai.com/cloud/pricing/north-america — 2026-10-16, Parallel fetch — Claim: DigitalOcean/Hetzner/Akamai resize in place (price grid rises smoothly: DO Basic 8 vCPU/16 GB $96 per a third-party page; Akamai 16 GB (6 vCPU) $96, 32 GB (8 vCPU) $192). (Synthesizer note: the DO $96 figure rests on a third-party page that was not opened; only the Akamai figures are backed by this source.) — Quote: "| Linode 32 GB | $192.00 | $0.2880 | 32 GB | 8 | 640 GB | 16 TB | 40/7 Gbps |"
- E85. https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing — 2026-10-16, Parallel fetch — Claim: Windows 365 Business step-ups: 8 vCPU/32 GB $108.80. — Quote: "Windows 365 Business 8 vCPU, 32 GB, 256 GB ... $108.80 user/month"
- E86. https://macstadium.com/pricing — 2026-10-16, WebFetch — Claim: Cloud Mac rentals scale by SKU: M4 Pro 48 GB $349 at MacStadium. — Quote: "M4.L Mac mini M4 Pro 12 Core 48 GB 1 TB SSD $349"

### Chat control (notes/chat-control.md)
- E87. https://github.com/nanocoai/nanoclaw README.md:91 (commit 2105169) — read 2026-10-16, git clone — Claim: Channels: WhatsApp, Telegram, Discord, Slack, Teams, iMessage and others, installed on demand by `/add-<channel>` skills. — Quote: "WhatsApp, Telegram, Discord, Slack, Microsoft Teams, iMessage, Matrix, Google Chat, Webex, Linear, GitHub, WeChat, and email via Resend."
- E88. https://github.com/nanocoai/nanoclaw README.md:87 (commit 2105169) — 2026-10-16, git clone — Claim: Engine is the Agent SDK, not the `claude` TUI. — Quote: "NanoClaw natively uses Claude Code via Anthropic's official Claude Agent SDK"
- E89. https://github.com/nanocoai/nanoclaw container/agent-runner/package.json:12 (commit 2105169) — 2026-10-16, git clone — Claim: Agent SDK is a dependency of the in-container runner. — Quote: "@anthropic-ai/claude-agent-sdk": "^0.3.296","
- E90. https://github.com/nanocoai/nanoclaw docs/SPEC.md:391 and :397 (commit 2105169) — 2026-10-16, git clone — Claim: Auth options include a Claude subscription OAuth token or an API key. — Quote: "Option 1: Claude Subscription (OAuth token)" ... "Option 2: Pay-per-use API Key"
- E91. https://github.com/nanocoai/nanoclaw setup/lib/captured-token.ts:49 (commit 2105169) — 2026-10-16, git clone — Claim: Setup captures the token from `claude setup-token`. — Quote: "Extract the Claude OAuth token from a PTY capture of `claude setup-token`,"
- E92. https://github.com/nanocoai/nanoclaw README.md:97 (commit 2105169) — 2026-10-16, git clone — Claim: Isolation: Docker container per session, mounts only; credential gateway injects keys. — Quote: "agents never hold raw API keys. Outbound requests route through a credential gateway that injects credentials at request time"
- E93. https://github.com/nanocoai/nanoclaw docs/SECURITY.md:24-28 (commit 2105169) — 2026-10-16, git clone — Claim: Container boundary is the primary defence. — Quote: "Container Isolation (Primary Boundary)"
- E94. https://github.com/nanocoai/nanoclaw docs/api-details.md:221 and `.claude/skills/` listing (commit 2105169) — 2026-10-16, git clone — Claim: WhatsApp adapter uses Baileys (unofficial WhatsApp Web emulation); a separate `add-whatsapp-cloud` skill exists. — Quote: "The WhatsApp/Baileys adapter is the canonical example"
- E95. https://github.com/nanocoai/nanoclaw — 2026-10-16, Exa fetch — Claim: Repo health: 30,951 stars, 1,048 open issues, MIT, created 2026-01-31. — Quote: "Open issues: 1048"
- E96. https://github.com/nanocoai/nanoclaw CHANGELOG.md (commit 2105169; no line given in the note) — 2026-10-16, git clone — Claim: Release 2026.10.0 of 2026-10-09 carries a BREAKING gateway upgrade for a credential-injection bypass. — Quote: "upgrade the OneCLI gateway to exactly 1.42.0, which closes a credential-injection bypass."
- E97. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Channels support: "Telegram, Discord, and iMessage are included in the research preview." — Quote: "Telegram, Discord, and iMessage are included in the research preview."
- E98. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Channels need an open session; always-on means a background process. — Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- E99. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Channels auth: claude.ai or Console key; Pro/Max without an org skip admin checks. — Quote: "Pro and Max users without an organization skip these checks entirely"
- E100. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Permission relay forwards approval prompts to chat; any allowlisted sender can approve. — Quote: "Anyone who can reply through the channel can approve or deny tool use in your session"
- E101. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Channels are a research preview; flags may change; custom channels can be built. — Quote: "Channels are a research preview feature."
- E102. https://code.claude.com/docs/en/remote-control — 2026-10-16, WebFetch (saved output line 28) — Claim: Remote Control needs subscription login, not an API key. — Quote: "available on Pro, Max, Team, and Enterprise plans. API keys are not supported."
- E103. https://code.claude.com/docs/en/remote-control — 2026-10-16, WebFetch (line 53) — Claim: Remote Control server mode on a headless host, QR code for phone. — Quote: "The process stays running in your terminal in server mode, waiting for remote connections."
- E104. https://code.claude.com/docs/en/remote-control — 2026-10-16, WebFetch (line 345) — Claim: Remote Control gives up after about 10 min offline in server mode. — Quote: "Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."
- E105. https://code.claude.com/docs/en/remote-control — 2026-10-16, WebFetch (line 407) — Claim: `setup-token`/`CLAUDE_CODE_OAUTH_TOKEN` cannot establish Remote Control. — Quote: "These tokens can only make model requests, so they can't establish Remote Control sessions."
- E106. https://code.claude.com/docs/en/remote-control — 2026-10-16, WebFetch (line 306) — Claim: Remote Control sends push notifications to the phone. — Quote: "When Remote Control is active, Claude can send push notifications to your phone."
- E107. https://code.claude.com/docs/en/slack — 2026-10-16, WebFetch — Claim: Claude in Slack starts cloud sessions, channels only (no DMs), needs Pro/Max and GitHub. — Quote: "creates a Claude Code cloud session, allowing you to delegate development work without leaving your team conversations."
- E108. https://code.claude.com/docs/en/slack — 2026-10-16, WebFetch — Claim: Same page: "Claude Code in Slack only works in channels (public or private). It does not work in direct messages (DMs)." and "GitHub only: repositories must be on GitHub." — Quote: "It does not work in direct messages (DMs)."
- E109. https://code.claude.com/docs/en/slack — 2026-10-16, WebFetch — Claim: Claude Tag is the Team/Enterprise successor; legacy bot retired for connected workspaces on 2026-10-05. — Quote: "Claude Tag isn't available on individual plans"
- E110. https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp — 2026-10-16, WebFetch — Claim: Hermes Agent's Baileys bridge states the risk. — Quote: "Using a third-party bridge carries a small risk of account restrictions."
- E111. https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp — 2026-10-16, WebFetch — Claim: Hermes advice: dedicated number, no bulk, no unsolicited outbound. — Quote: "Use a dedicated phone number for the bot (not your personal number)"
- E112. research/tool-registry.md lines 161, 76 — 2026-10-16, Read — Claim: OpenClaw and Hermes: registry rows verified 2026-10-16. — Quote: "MIT Node gateway daemon, 20+ chat channels, drives Claude Code via claude-cli backend or ACP; install via curl script/npm/Docker; sandbox off by default; 255+ advisories"
- E113. https://code.claude.com/docs/en/legal-and-compliance — 2026-10-16, WebFetch — Claim: API-key rule for SDK developers. — Quote: "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication"
- E114. https://code.claude.com/docs/en/legal-and-compliance — 2026-10-16, WebFetch — Claim: Same page, no third-party routing. — Quote: "Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- E115. https://code.claude.com/docs/en/legal-and-compliance — 2026-10-16, WebFetch — Claim: Same page, own use of unmodified binary allowed. — Quote: "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription"
- E116. https://code.claude.com/docs/en/legal-and-compliance — 2026-10-16, WebFetch — Claim: Same page, enforcement without notice. — Quote: "Anthropic reserves the right to take measures to enforce these restrictions and may do so without prior notice."
- E117. https://code.claude.com/docs/en/legal-and-compliance — 2026-10-16, WebFetch — Claim: Same page, usage limits assumption. — Quote: "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK."
- E118. https://www.anthropic.com/legal/consumer-terms — 2026-10-16, WebFetch — Claim: Consumer Terms automation clause. — Quote: "Except when you are accessing our Services via an Anthropic API Key or where we otherwise explicitly permit it"
- E119. https://www.anthropic.com/legal/consumer-terms — 2026-10-16, WebFetch — Claim: Consumer Terms credential sharing. — Quote: "You may not share your Account login information, Anthropic API key, or Account credentials with anyone else."
- E120. https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan — 2026-10-16, WebFetch — Claim: Help Center (updated 2026-10-07): SDK, `claude -p` and third-party apps still use subscription limits. — Quote: "You can still use the Claude Agent SDK, claude -p, and third-party apps with your subscription limits."
- E121. https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan — 2026-10-16, WebFetch — Claim: Max now includes monthly API credits for the Agent SDK. — Quote: "Claude Max and Team plans now include monthly API credits"
- E122. https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans — 2026-10-16, WebFetch — Claim: Credits: Max 5x $100, Max 20x $200; apply only with an API key; not to interactive Claude Code. — Quote: "API credits cover `claude -p` and the Claude Agent SDK when you run them yourself with an API key."
- E123. https://code.claude.com/docs/en/remote-control — 2026-10-16, WebFetch — Claim: Remote Control: use local environment remotely, subagent and workflow progress in sync, send files from phone. — Quote: "the conversation and the progress of subagents and dynamic workflows stay in sync across all connected devices"
- E124. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Channels: approvals from phone. — Quote: "Channel servers that declare the permission relay capability can forward these prompts to you so you can approve or deny remotely."
- E125. https://code.claude.com/docs/en/channels — 2026-10-16, WebFetch — Claim: Channels: chat answers from phone, work on own machine. — Quote: "ask Claude something from your phone via Telegram, Discord, or iMessage, and the answer comes back in the same chat while the work runs on your machine"
- E126. https://code.claude.com/docs/en/slack — 2026-10-16, WebFetch — Claim: Claude in Slack: progress posts, summary, buttons. — Quote: "Claude posts status updates to your Slack thread as work progresses"
- E127. https://github.com/nanocoai/nanoclaw README.md (commit 2105169; no line given in the note) — 2026-10-16, git clone — Claim: NanoClaw: scheduled tasks with optional script gates. — Quote: "recurring jobs executed by the agent, with optional script gates that avoid waking it when there is no work"

## Implications for the engineer blueprint (research/blueprint/)

- **Keep the host assumption the blueprint already makes:** a rented Ubuntu VM with headed Chrome, Playwright and noVNC.
  - Name DigitalOcean Basic 4 vCPU / 8 GiB at $48/month as the default (E64).
  - Name Akamai/Linode as the equal alternative (E65) and Hetzner CX33 as the EU option that depends on the spike (E60).
  - Record the Mac mini M6 ($899, E74) as the residential-IP fallback, not the default.
- **Browser profile rule:** branded Chrome through Playwright `channel` (E12), headed, never headless (E6), with a non-default `--user-data-dir` (E13). Snapshot the VM after John's hand sign-in, then verify that restore keeps the logins (Spike 2).
- **Challenge rule (EARS):** When a login page, CAPTCHA or bot challenge appears, the engineer shall stop the task and notify John through Remote Control or Telegram, and shall not attempt to bypass it (E17, E18).
- **Auth rule (EARS):** When the engineer host is set up, the operator shall log in with an interactive `claude auth login` rather than `setup-token`, so that Remote Control works (E105).
- **Chat-control wiring:**
  - Remote Control server mode, kept alive by a restart script, because it exits after about 10 minutes offline (E104).
  - The Telegram channel in a persistent background session (E98), with a sender allowlist. Anyone who can reply can approve (E100).
- **Desktop add-on:** none by default. If one is needed, Cua Driver as an MCP server (E39), after a throwaway-VM spike.
- **NanoClaw:** take it out of the default path. If it is added later, run it on an API key funded by Max API credits (E122), with its own container mounts, and log that its Agent SDK use on a Max token is policy-contested (E113 to E120).

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| DigitalOcean Droplet (Basic 4 vCPU/8 GiB) | https://www.digitalocean.com/pricing/droplets | VPS $48/mo; snapshots $0.06/GB/mo; backups 20-30%; own public IPv4 | cloud | 2026-10-16 | Recommended US-East default |
| Akamai Cloud / Linode 8 GB | https://www.akamai.com/cloud/pricing/north-america | 4 vCPU/8 GB $48/mo, backups $10/mo | cloud | 2026-10-16 | Equal alternative to DO |
| Hetzner Cloud CX33 / CPX31 | https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ | CX33 $9.99/mo (EU, excl. IPv4); CPX31 $73.49/mo (US ASH/HIL); manual snapshots | cloud (Germany/Finland/US) | 2026-10-16 | Cheapest; use EU only if latency and sign-in IP spike pass |
| Vultr Cloud Compute | https://www.vultr.com/pricing/ | Snapshots $0.05/GB, backups +20%; 4 vCPU/8 GB price not read | cloud | 2026-10-16 | Unverified for the target size |
| AWS Lightsail | https://aws.amazon.com/lightsail/pricing/ | 4 vCPU/8 GB $84/mo (compute-optimized) | cloud | 2026-10-16 | Skip; pricier than DO |
| GCP Compute Engine e2 | https://cloud.google.com/products/compute/pricing/general-purpose | e2-standard-4 (16 GB) $0.134/h (about $98/mo) | cloud | 2026-10-16 | Skip; pricier |
| Oracle Cloud Free Tier | https://www.oracle.com/cloud/free/ | Always Free Ampere A1; 30-day idle termination clause | cloud | 2026-10-16 | Fallback only; reclaim risk, limits not read |
| Windows 365 Business | https://www.microsoft.com/en-us/windows-365/business/compare-plans-pricing | Windows Cloud PC: 4 vCPU/16 GB $56/mo | cloud | 2026-10-16 | Skip; Windows, interactive design |
| Amazon WorkSpaces Personal | https://aws.amazon.com/workspaces/desktop-as-a-service/pricing/ | AlwaysOn flat monthly or AutoStop hourly desktops | cloud | 2026-10-16 | Skip; AlwaysOn needed, Ubuntu price not read |
| Shadow PC | https://www.shadow.tech/en-us/pricing/ | Cloud gaming Windows PC | cloud | 2026-10-16 | Skip; gaming product, price not read |
| Kasm Workspaces CE | https://kasm.com/community-edition | Container desktop streaming (search excerpt only) | self-hosted | not opened (search excerpt only) | Unverified |
| Apple Mac mini M6 | https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/ | $899 base, 4 W idle; buy for home | home | 2026-10-16 | Fallback host if the data-center sign-in spike fails, or if macOS is wanted |
| MacStadium | https://macstadium.com/pricing | Dedicated Mac mini M4 16 GB $149/mo | cloud | 2026-10-16 | Fallback if macOS needed without buying |
| Scaleway Mac mini M4 | https://www.scaleway.com/en/pricing/apple-silicon/ | M4-S EUR 149/mo, 24 h minimum, Paris | cloud | 2026-10-16 | Fallback; EU latency |
| AWS EC2 Mac | https://aws.amazon.com/ec2/dedicated-hosts/pricing/ | Dedicated host, 24 h minimum; about $898/mo rests on an unverified hourly rate | cloud | 2026-10-16 | Reject on cost |
| MacinCloud | https://www.macincloud.com/pages/pricing | Hosted Macs | cloud | page 404 | Unverified |
| Cloudflare Tunnel | https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/ | Outbound-only access to a home/VPS service | home or VPS | 2026-10-16 | Use for web access without open ports |
| Tailscale Personal | https://tailscale.com/plans | Free mesh VPN, 3 users, 100 devices | home or VPS | 2026-10-16 | Use; non-commercial rule seen in search excerpt only, check |
| Claude Code CLI computer use | https://code.claude.com/docs/en/computer-use | Built-in screen control, macOS only, interactive only | John's Mac | 2026-10-16 | Not for the unattended engineer |
| Claude Desktop computer use | https://code.claude.com/docs/en/desktop | Same engine on macOS and Windows; browsers view-only; Dispatch approvals 30 min | John's Mac/Windows | 2026-10-16 | Supervised only |
| Anthropic computer-use tool + Xvfb container | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | API tool, Linux Docker reference, you write the loop | API + VM | 2026-10-16 | Fallback; second agent loop |
| Cua Driver | https://github.com/trycua/cua | MIT cross-OS driver, MCP for Claude Code; Linux X11/Wayland limits | Mac/Win/Linux | 2026-10-16 | Spike first, only if a desktop need appears |
| Windows-MCP (CursorTouch) | https://github.com/CursorTouch/Windows-MCP | MIT MCP server for Windows 7-11 UI control; Python 3.13+ | Windows | 2026-10-16 | Spike if a Windows host is chosen |
| Microsoft UFO / UFO2 | https://github.com/microsoft/UFO | MIT Windows agent (UIA/Win32); own LLM config | Windows | 2026-10-16 | Reject as engine; reference only |
| E2B Desktop | https://github.com/e2b-dev/desktop | Apache-2.0 Linux Xfce sandbox SDK | E2B cloud | 2026-10-16 | Alternative; price unchecked |
| sqrew/rmcp-xdotool | https://github.com/sqrew/rmcp-xdotool | Rust xdotool MCP, X11 only | Linux X11 | README via search excerpt only | Fallback; unvetted |
| vito1317/linux-control-mcp | https://github.com/vito1317/linux-control-mcp | X11 MCP (xdotool, wmctrl, OCR) | Linux X11 | search excerpt only | Fallback; unvetted |
| Power Automate desktop flows | https://learn.microsoft.com/en-us/power-automate/desktop-flows/run-unattended-desktop-flows | Windows RPA | Windows | not opened (search excerpt only) | Skip; not Claude-driven |
| Playwright channel: chrome | https://playwright.dev/docs/browsers | Drives branded Chrome installed on the host | local | 2026-10-16 | Use: headed real Chrome with a non-default persistent profile |
| Chrome DevTools MCP --autoConnect | https://developer.chrome.com/docs/devtools/agents/get-started/configuration | Attaches an agent to a running Chrome after a permission dialog (Chrome 144+) | John's machine | 2026-10-16 | Fallback; dialog unsuited to unattended runs |
| Cloudflare Web Bot Auth / verified bots | https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/ | Signed requests plus registration so Cloudflare marks a bot verified | Cloudflare dashboard + own domain | 2026-10-16 | Skip: for bot operators, not SaaS customers |
| playwright-personas, stealth plugins, CloakBrowser, CAPTCHA solvers | https://github.com/RyanCollinsAI/playwright-personas | Evasion wrappers (search excerpts only) | local | not opened | Reject: evasion |
| NanoClaw | https://github.com/nanocoai/nanoclaw | Container-per-agent assistant on Agent SDK; WhatsApp (Baileys/Cloud API), Slack, Telegram skills; release 2026.10.0; MIT | VM, Docker | 2026-10-16 | Not the best remote for the engineer; use only if WhatsApp/Slack UI is a must, with an API key |
| Claude Code Channels | https://code.claude.com/docs/en/channels | Telegram, Discord, iMessage into a running local session; permission relay | VM/host | 2026-10-16 | Use Telegram for chat control and approvals |
| Remote Control | https://code.claude.com/docs/en/remote-control | Phone/web view of local session; server mode; push; subscription login only | VM/host | 2026-10-16 | Use as the main phone cockpit |
| Claude Code in Slack / Claude Tag | https://code.claude.com/docs/en/slack | @Claude starts a cloud session on a GitHub repo; channels only | Anthropic cloud | 2026-10-16 | Skip for the VPS engineer |
| Hermes Agent WhatsApp (Baileys) page | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp | Baileys bridge with stated ban risk | VPS | 2026-10-16 | Evidence for ban risk; skip |
| Monthly API credits for Max | https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-and-team-plans | $100/$200 a month API credit for SDK/`claude -p` with an API key | Anthropic billing | 2026-10-16 | Use if running any Agent SDK bridge |

## Open questions

### From the PLAN's facet gaps
- **Bot flagging:**
  - No vendor rate comparing data-center and residential IPs, and no OS comparison.
  - The DataDome signal page and the Cloudflare community thread returned 403.
  - Slack and Outreach edges and terms were not read: the Slack AUP is a PDF only, and the Outreach terms, n8n Cloud terms and Google Workspace terms were not opened. The n8n Cloud app host was not probed.
- **Desktop control:**
  - Locked-Mac and asleep-Mac behaviour is undocumented.
  - The RDP/tscon and Power Automate claims are search-excerpt only.
  - No Cua-on-Xvfb spike has been run.
  - OSWorld scores come from excerpts only.
  - Unknown whether the API computer-use tool can be driven from a Claude Code subagent without a separate API key.
- **Hosting:**
  - Vultr (4 vCPU / 8 GB price), Oracle A1 (allowance and idle reclaim), OVH, Azure Virtual Desktop and MacinCloud (pricing page 404) were not checked.
  - Acceptable-use policies were read only for Hetzner.
  - Not found: Hetzner's IPv4 fee, and whether CX types exist at Ashburn.
  - Not found: the WorkSpaces Ubuntu AlwaysOn price, and Windows 365 Business (non-Flex) idle behaviour.
  - Home uptime, and noVNC/Screen Sharing on macOS after reboot (FileVault).
- **Chat control:**
  - NanoClaw CVEs and the WhatsApp Business terms are known from search excerpts only.
  - Channels and Remote Control in one session is untested.
  - No Slack bridge has been vetted.
  - NanoClaw's approval-card flow (`src/gateway-approval-presentation.ts`) was not read.
  - Not verified whether Max OAuth through the OneCLI gateway still works on v2.
  - NanoClaw commit cadence is not measurable from a depth-1 clone.

### Unresolved contradictions
- **Agent SDK on a Max login** (the legal page, E113/E114, against the Help Center, E120): is a single owner's own Agent SDK bridge (NanoClaw) on his Max token allowed? This needs written confirmation from Anthropic.
- **Google sign-in reuse:** does Google's sign-in block apply to a profile signed in by hand and driven later? The third-party "CDP-block bypass" claims are excerpts only, and the Playwright maintainers give no fix (E5). Spike 1.

### Unverified (search excerpt only) — 29 claims excluded from findings
1. Cloudflare alert docs list ASN as a filter dimension (Cloudflare alerts page, excerpt only).
2. Third-party Playwright wrappers claim a "Google CDP-block bypass" by reusing a hand-logged-in profile (excerpts).
3. TCP/IP OS-fingerprint tools and DataDome text say network stacks are compared with the claimed UA OS (excerpts).
4. playwright-personas, CloakBrowser and stealth plugins: what they do (excerpts; rejected anyway).
5. Outreach Acceptable Use Policy of January 2021 (excerpt).
6. OSWorld 2.1: Sonnet 5.5 80.1%, Opus 5.5 81.8% (emergent.sh, excerpt only).
7. OSWorld 2.1 strict score 43.5% for Sonnet 5.5 (llm-stats.com, excerpt only). This contradicts item 6; neither is cited.
8. An RDP disconnect locks the desktop, so GUI automation fails, with tscon as the workaround (WinAppDriver doc and Microsoft Learn, excerpts).
9. Power Automate unattended flows lock the screen and need all users signed out (Microsoft Learn, excerpt).
10. sqrew/rmcp-xdotool README contents (excerpt of the file).
11. kira-mcp is X11 only (pypi, excerpt).
12. Noah3521/hermes-computer-use is a pixel-level Chrome MCP (excerpt).
13. vito1317/linux-control-mcp has 35 tools (excerpt).
14. Hetzner CX33 at EUR 10.70 / "from EUR 7.13" (eucloudcost.com, excerpt).
15. Hetzner CPX31 is 4 vCPU / 8 GB (third-party excerpt).
16. WorkSpaces AutoStop stops after 20 minutes without a client connection (AWS docs, excerpt).
17. Kasm CE is free only for non-commercial use, with 5 sessions; Starter pricing (kasm.com, excerpt).
18. AWS mac-m4.metal at $1.23/hour, about $898/month (instances.vantage.sh, excerpt).
19. MacinCloud at $25-$49/month (third-party pages, not opened; the vendor page returned 404).
20. The Tailscale free plan is non-commercial only, and a custom-domain tailnet counts as business use (tailscale.com/pricing, excerpt).
21. The Tailscale free plan allows 6 users (ssdnodes, comparedge, excerpts).
22. DigitalOcean Basic 8 vCPU / 16 GB at $96 (third-party page).
23. NanoClaw CVE-2026-56402 (an approval-handler privilege flaw before 2.1.17; the NVD page returned no content).
24. NanoClaw CVE-2026-7875 and GHSA-mhq9-hcw8-22mj (excerpts; severity unknown).
25. A third-party NanoClaw site says NanoClaw needs an API key (not opened).
26. The WhatsApp Business Solution Terms "AI Provider" clause, effective 2026-01-15 (TechCrunch and whatsapp.com, excerpts).
27. Anthropic banned OpenClaw on subscriptions in April 2026, then reversed, then paused a credit pool in June (pcmag, oflight, excerpts).
28. A zeroclaw issue describing a task runner with Slack progress and SSH/tmux handoff (excerpt).
29. Numeric challenge rates for residential versus data-center IPs (vendor-marketing proxy blogs, excerpts).

### Registry note for the lead
The registry rows already carry two claims that rest on search excerpts only:
- `research/tool-registry.md:639` states the Tailscale non-commercial rule as fact.
- `research/tool-registry.md:626` lists "CVE-2026-56402 reported".

The synthesizer did not rewrite those rows.
