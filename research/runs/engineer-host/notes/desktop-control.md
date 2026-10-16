# Desktop and browser control by OS

Brief: Tell John which OS gives the engineer the most browser automation and full desktop control (any app, not just web pages) with Claude Code as engine.
Run: research/runs/engineer-host/PLAN.md

## Q1 Claude Code's own computer use, and Anthropic's computer-use tool on Linux

### Takeaway
Claude Code CLI computer use is macOS-only and interactive-only (not `-p`); Windows gets it only through the Desktop app, Linux gets none. Anthropic's API computer-use tool is OS-agnostic: the reference build is a Linux Docker container (Xvfb + Mutter), but you write the agent loop yourself, so it is not "Claude Code as engine". Confidence: high (docs opened today).

### Cited findings
- CLI computer use is a macOS research preview, Pro/Max only, interactive only — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "It requires an interactive session, so it is not available in non-interactive mode with the `-p` flag."
- The CLI server does not exist on Linux or Windows — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Computer use in the CLI is not available on Linux or Windows. On Windows, use computer use in Desktop instead."
- Comparison table: Desktop is macOS and Windows, CLI macOS only — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "| Platforms | macOS and Windows | macOS only |"
- It controls the real desktop, one session at a time, via a lock held until the session exits — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Only one session at a time can use your computer. A session takes a lock at its first computer use action and releases it when the session exits"
- Per-app approval prompts appear in the terminal each session (human in the loop) — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Choose **Allow for this session** or **Deny**. Approvals last for the current session."
- Browsers are view-only for computer use; Claude prefers other tools first — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "browsers and trading platforms are view-only, terminals and IDEs are click-only, and everything else gets full control."
- Anthropic API tool: reference implementation is a Linux Xvfb desktop in Docker — https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool, opened 2026-10-16, WebFetch — Quote: "A virtual X11 display server (using Xvfb) that renders the desktop interface Claude will see through screenshots and control with mouse/keyboard actions."
- The developer implements the loop and executors — same page, WebFetch — Quote: "An agent loop that interacts with the Claude API and runs the `tool_use` results using your tool implementations"
- Not on Managed Agents; sandbox required; resolution advice — same page, WebFetch — Quote: "Computer use requires a sandboxed computing environment where Claude can safely interact with applications and the web." Also "Avoid resolutions above 1920x1080 to prevent performance issues."
- Security advice includes keeping login data out of the model's reach — same page, WebFetch — Quote: "Avoiding giving the model access to sensitive data, such as account login information, to prevent information theft."
- Claude Code itself still does not reach computer use via Chrome fallback: browser work goes to Claude in Chrome first — https://code.claude.com/docs/en/computer-use, WebFetch — Quote: "If the task is browser work and you have Claude in Chrome set up, Claude uses that."
- Model quality (vendor-reported, Sept 2026): Sonnet 5.5 80.1% vs Opus 5.5 81.8% on OSWorld 2.1 — https://emergent.sh/learn/what-is-claude-sonnet-5-5, opened 2026-10-16, Parallel search excerpt only (page not fetched in full). See Gaps.

### Contradictions
- OSWorld 2.1 for Sonnet 5.5: 80.1% (vendor announcement partial score) vs 43.5% (System Card strict score) — llm-stats.com/blog/research/claude-sonnet-5-5-launch (search excerpt only). Strict number is the honest read; not fetched, so not cited as a finding.

### Inferences
- Because the CLI feature is macOS-only, interactive-only and holds a per-session app-approval prompt, it cannot be the unattended engineer's hands on any OS (rests on the findings above).
- On Linux the only Anthropic-supported route is the API tool in a container with your own loop, which means a second agent loop beside Claude Code; the way to keep Claude Code as engine is an MCP server (Q3).

### Gaps
- Whether the API computer-use tool can be driven from inside a Claude Code subagent without a separate API key: not found.
- Last 18k chars of the computer-use tool page unread (WebFetch truncated).
- OSWorld numbers are vendor or aggregator excerpts; no primary Anthropic page opened.

## Q2 Windows

### Takeaway
Windows has the broadest native desktop control (Desktop app computer use, Windows-MCP, Cua Driver, UFO) but needs a live, unlocked interactive session; unattended-overnight means a VM kept logged in with tscon-style tricks. Claude Code CLI can attach via MCP (Windows-MCP, Cua). Maturity: Windows-MCP and Cua Driver look active; UFO is Microsoft research code on LTS and uses its own LLM config. Confidence: medium.

### Cited findings
- Windows-MCP: MIT, Windows 7 to 11, one-line Claude Code install — https://github.com/CursorTouch/Windows-MCP, opened 2026-10-16, Parallel fetch — Quote: "claude mcp add --transport stdio windows-mcp -- uvx windows-mcp serve"
- Windows-MCP needs Python 3.13+ and prefers English Windows — same page — Quote: "`English` as the default language in Windows preferred else disable the `App-Tool` in the MCP Server for Windows with other languages."
- Windows-MCP from WSL still runs on Windows side — same page — Quote: "If you run Claude Code from WSL, the MCP server must still execute on the Windows side (it needs Windows APIs for UI automation)."
- Cua Driver supports Windows, with a limit on elevated apps — https://cua.ai/docs/cua-driver/concepts/platform-support, opened 2026-10-16, Parallel fetch — Quote: "Some background Chromium gestures and elevated-integrity targets refuse or are unproven."
- Cua on Windows over SSH sees nothing: SSH runs in Session 0 — https://cua.ai/docs/cua-driver/guides/vms-and-remote, opened 2026-10-16, Parallel fetch — Quote: "Windows OpenSSH runs in Session 0, which has no desktop, so window tools return empty results there."
- Cua registers with Claude Code in one command — https://cua.ai/docs/cua-driver/guides/connect-your-agent, opened 2026-10-16, Parallel fetch — Quote: "claude mcp add --transport stdio cua-driver -- cua-driver mcp"
- Microsoft UFO: UFO2 is the single-device Windows agent in LTS, MIT, brings its own LLM config (OpenAI default, Claude listed) — https://github.com/microsoft/UFO, opened 2026-10-16, Parallel fetch — Quote: "Status | ✅ LTS (Long-Term Support)" and "Windows UIA, Win32, WinCOM native control"
- Desktop app computer use works on Windows with a toggle, app must be running, background operation macOS only — https://code.claude.com/docs/en/desktop, opened 2026-10-16, WebFetch — Quote: "Computer use is a research preview on macOS and Windows that requires a Pro or Max plan." (Same page: background operation is macOS only, paraphrase of the fetch summary.)
- RDP disconnect locks the desktop and GUI automation fails; tscon is the known workaround — https://github.com/microsoft/WinAppDriver/blob/master/Docs/RunningOnRemoteMachine.md, via Parallel search excerpt only; Microsoft Learn page below was also excerpt only. See Gaps.
- Power Automate unattended flows lock the screen and need all users signed out — https://learn.microsoft.com/ar-sa/power-automate/desktop-flows/run-unattended-desktop-flows (search excerpt only). See Gaps.

### Contradictions
- None found.

### Inferences
- Windows lets Claude Code drive native apps through MCP (Windows-MCP, Cua), but for overnight runs John needs an auto-logon VM with the session kept attached to the console (tscon or a lock-prevent service). That adds an operational burden Linux does not have (rests on Session 0 finding and search excerpts on RDP lock).
- Windows-MCP vs Cua: Windows-MCP is narrower and simpler; Cua adds background input and cross-OS coverage. Choose after a spike.

### Gaps
- tscon/RDP-lock claims and Power Automate unattended constraints are from search excerpts, not pages I opened; not cited as findings.
- Windows-MCP stars, last release and issue health not checked.
- WindowsAgentArena scores not located.
- Windows licence cost for a cloud Windows VM not researched.

## Q3 Linux

### Takeaway
Linux is the best fit for unattended work: Xvfb or a VNC desktop never locks, Playwright headed plus noVNC is already the blueprint, and Cua Driver plus xdotool MCP servers give desktop-level clicking to Claude Code. What it cannot do: no Claude Code built-in computer use, Wayland blocks raw input to background windows, and no Windows/macOS-only apps. Confidence: medium.

### Cited findings
- Cua Driver on Linux: X11 supported with toolkit limits, Wayland with compositor limits — https://cua.ai/docs/cua-driver/concepts/platform-support, opened 2026-10-16, Parallel fetch — Quote: "Standard Wayland: an ordinary client cannot send raw input to an unfocused, occluded window. AT-SPI actions still work in the background."
- Cua on Linux X11 Chrome cannot do trusted pointer input — same page — Quote: "Trusted pointer returns `browser_input_trust_unavailable`; dialogs need foreground."
- Cua licensing: Driver MIT, Spaces FSL-1.1-MIT, optional perception extension AGPL — https://github.com/trycua/cua, opened 2026-10-16, Parallel fetch — Quote: "Cua Spaces is source-available under FSL-1.1-MIT"
- Cua install is a curl-pipe script — same page — Quote: "/bin/bash -c \"$(curl -fsSL https://cua.ai/driver/install.sh)\"" (page instruction to install; not followed, nothing run)
- E2B Desktop: Apache-2.0 Linux Xfce sandbox with streaming — https://github.com/e2b-dev/desktop, opened 2026-10-16, Parallel fetch — Quote: "The desktop-like environment is based on Linux and Xfce at the moment."
- xdotool MCP servers exist but are small and unvetted: sqrew/rmcp-xdotool needs X11 — https://github.com/sqrew/rmcp-xdotool/blob/master/README.md, opened 2026-10-16, Parallel search excerpt of the file — Quote: "MCP server for mouse and keyboard automation via xdotool. Gives Claude (or any MCP client) the ability to control your desktop."
- kira-mcp: X11 only — https://pypi.org/project/kira-mcp, search excerpt — Quote: "X11 sessions only — Wayland blocks raw screen grabs". Treated as excerpt, not a full read.
- Pixel-level Chrome MCP in Xvfb with noVNC exists (3 stars) — https://github.com/Noah3521/hermes-computer-use, search excerpt — Quote: "Pixel-level browser automation MCP server — drive a real Chrome with screenshot + xdotool, no CDP, no navigator.webdriver." Immature.
- Claude in Chrome is not supported on WSL and is interactive only — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "Chrome integration isn't supported in Windows Subsystem for Linux (WSL)."

### Contradictions
- None found.

### Inferences
- A Linux VM with Xvfb/Xfce plus Cua Driver (or a small xdotool MCP) gives Claude Code pixel/AT-SPI control of non-browser apps while keeping `claude -p` unattended, since MCP servers are not subject to the CLI computer-use restriction (rests on Cua registration finding; spike needed).
- Linux cannot run Mac/Windows-only apps (Outlook desktop, native Sales Navigator tooling); a browser-only GTM stack does not need them.

### Gaps
- No spike run; Cua Driver on a headless Xvfb session unverified (docs list X11 supported, not Xvfb specifically).
- E2B pricing not opened.
- xdotool MCP servers: star counts, maintenance and security not vetted.

## Q4 macOS

### Takeaway
macOS has the most polished first-party path (CLI and Desktop computer use, background operation, Cua Lume VMs) but it is interactive, single-session, uses John's real screen, and cannot be unattended in `-p`. It suits a supervised spare Mac, not the overnight engineer. Confidence: high for limits, medium for Lume.

### Cited findings
- Needs Accessibility and Screen Recording grants; first-time prompt — https://code.claude.com/docs/en/computer-use, opened 2026-10-16, WebFetch — Quote: "Accessibility: lets Claude click, type, and scroll" and "Screen Recording: lets Claude see what's on your screen"
- Other apps are hidden while Claude works — same page — Quote: "When Claude starts controlling your screen, other visible apps are hidden so Claude interacts with only the approved apps."
- Esc aborts and the session keeps the lock — same page — Quote: "The session keeps the computer use lock until it exits."
- Not available with API-key/third-party auth — same page — Quote: "Computer use is not available with third-party providers like Amazon Bedrock"
- Desktop: Dispatch approvals expire — https://code.claude.com/docs/en/desktop, opened 2026-10-16, WebFetch — Quote: "App approvals in those sessions expire after 30 minutes and re-prompt, rather than lasting the full session like regular Code sessions."
- Cua on macOS: needs Accessibility and Screen Recording, supports background delivery, Lume VMs on Apple Silicon — https://github.com/trycua/cua, opened 2026-10-16, Parallel fetch — Quote: "Lume: local macOS and Linux VMs on Apple Silicon"
- Cua in a Lume VM still needs permission prompts approved — https://cua.ai/docs/cua-driver/guides/vms-and-remote, Parallel fetch — Quote: "Approve three kinds of prompt: Accessibility and Screen Recording for CuaDriver"

### Contradictions
- None found.

### Inferences
- The docs do not say whether the screen may be locked or asleep (see Gaps); screen capture on a locked Mac almost certainly fails, so a Mac host would need display sleep and lock disabled. This is my inference, not sourced.
- Apple hardware means a Mac mini purchase or rented Mac; cost not researched.

### Gaps
- Locked or asleep screen behaviour: the Desktop doc fetch said it does not address the case. Not settled.
- Mac cloud rental prices not researched.

## Q5 Is desktop control needed for GTM (Attio, Clay, n8n, Outreach)?

### Takeaway
No for these four: all are web apps, so browser control (Playwright persistent profile, Chrome DevTools MCP, Claude in Chrome) covers them; desktop control unlocks only native apps, OS dialogs, browser chrome (extensions, native file pickers), and apps without a web UI. Confidence: medium (inference from the app types and existing registry rows; no GTM-specific test run).

### Cited findings
- Claude in Chrome already handles logged-in web apps and pauses on login/CAPTCHA — https://code.claude.com/docs/en/chrome, opened 2026-10-16, WebFetch — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- But it is not suited to unattended use: requires subscription login, off under API key or setup-token — same page — Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`, because the browser extension can't authenticate with those credentials."
- Claude Code itself prefers the precise tool first and treats computer use as last resort — https://code.claude.com/docs/en/computer-use, WebFetch — Quote: "Computer use is the broadest and slowest, so Claude tries the most precise tool first"
- Computer-use docs list what only screen control reaches — same page — Quote: "Screen control is reserved for things nothing else can reach: native apps, simulators such as the iOS Simulator, and tools without an API."
- Existing project registry: Playwright CLI/MCP persistent profile is the engineer's browser driver — /home/user/Autonomy-Research/research/tool-registry.md:204-205 — Quote: "primary driver for the engineer; spike on real Attio/Clay tasks"

### Contradictions
- None found.

### Inferences
- Desktop-only unlocks for GTM: native OS file pickers where Playwright cannot reach them (Playwright usually handles via setInputFiles), browser extensions with popups (e.g. LinkedIn/Sales Nav helpers), 2FA via desktop authenticator apps, and Google sign-in dialogs that detect automation. John does Google sign-in by hand, so even that is covered.
- Attio and Outreach also have APIs (registry lines 122-128), reducing the need for UI driving at all.
- Therefore OS choice should follow reliability of unattended headed Chrome (Linux VM, already decided) rather than desktop breadth. A Windows or Mac host only wins if John must automate a native app; none is named.

### Gaps
- No test of Attio/Clay drag-and-drop or Outreach UI on a pixel-based driver.
- Clay/Outreach bot-detection behaviour against headed Playwright not researched here.

## Recommendation (facet-level)
Keep Linux (Ubuntu VM, Xvfb/headed Chrome, noVNC) as the engineer host. Add Cua Driver MCP (or a small X11 MCP) only if a non-browser need appears. Use a spare Mac with Claude Code/Desktop computer use for supervised native-app work. Windows only if a Windows-only app must be automated. Alternatives: Windows VM with Windows-MCP plus tscon. Rejected: UFO as engine (own agent loop), Power Automate (unverified), Claude Code CLI computer use for unattended (interactive/macOS only). Spike: Cua Driver on Xvfb/XFCE under `claude -p`; Windows-MCP in an auto-logon VM surviving RDP disconnect.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code CLI computer use | https://code.claude.com/docs/en/computer-use | Built-in screen control, macOS only, interactive only | John's Mac | 2026-10-16 | Not for unattended engineer (existing row confirmed) |
| Claude Desktop computer use | https://code.claude.com/docs/en/desktop | Same engine on macOS and Windows; browsers view-only | John's Mac/Windows | 2026-10-16 | Supervised only (row confirmed) |
| Anthropic computer-use tool + Xvfb container | https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool | API tool, Linux Docker reference, you write loop | API + VM | 2026-10-16 | Fallback; second agent loop |
| Windows-MCP (CursorTouch) | https://github.com/CursorTouch/Windows-MCP | MIT MCP server for Windows 7-11 UI control; uvx install | Windows | 2026-10-16 | Spike if a Windows host is chosen |
| Microsoft UFO / UFO2 | https://github.com/microsoft/UFO | MIT Windows agent (UIA/Win32), UFO3 Galaxy multi-device; own LLM config | Windows | 2026-10-16 | Reject as engine; reference only |
| Cua Driver | https://github.com/trycua/cua | MIT cross-OS driver, MCP for Claude Code, background input | Mac/Win/Linux | 2026-10-16 | Spike first (existing row confirmed) |
| sqrew/rmcp-xdotool | https://github.com/sqrew/rmcp-xdotool | Rust xdotool MCP, X11 only | Linux X11 | 2026-10-16 (README via search excerpt) | Fallback; unvetted |
| vito1317/linux-control-mcp | https://github.com/vito1317/linux-control-mcp | 35-tool X11 MCP (xdotool, wmctrl, OCR) | Linux X11 | 2026-10-16 (search excerpt) | Fallback; unvetted, created 2026-04 |
| E2B Desktop | https://github.com/e2b-dev/desktop | Apache-2.0 Xfce sandbox SDK | E2B cloud | 2026-10-16 | Alternative; price unchecked |
| Power Automate desktop flows | https://learn.microsoft.com/en-us/power-automate/desktop-flows/run-unattended-desktop-flows | RPA on Windows; unattended flows lock the screen | Windows | not opened (search excerpt only) | Skip; not Claude-driven |
