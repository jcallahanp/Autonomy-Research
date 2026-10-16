# Browser and computer control (Area 6) - digest
Source: research/findings/engineer-browser.md; verification: 19 of 20 verified, 1 unverified (Attio webhook token level, A8)

## Decision
Confidence medium (Q14). Claude Code on John's Ubuntu VM, API first, Playwright for the rest:
- API or MCP first. Attio views are GET-only (A1, A2), Attio has no Workflows routes (A3), Clay "cannot create tables programmatically" (A20) though agents can edit Workflows (A16), and n8n's API covers nearly everything except OAuth consent clicks (A28, A36). The browser's job is Attio views, Kanban and Workflows; Clay tables, columns, custom functions and custom signals (A17, A18, A25); OAuth consent; and one-time developer-app sign-ups (A45, A50).
- Playwright drives it, through the `@playwright/cli` skill (T4) or Playwright MCP with `browser_drag` (T1; T2 was read only as Exa search highlights). Act by element reference by default and drag by coordinates. ComponentBench: 83.1% with accessibility-tree observations falls to 48.9% with pixel-only input, "Drag/Drop favors Pixel", and drag tasks stay below 60% (T29-T32).
- Agents over-report success by up to 41 points (T34, T35; Exa search page content), so a separate read checks every write.
- Record once, then replay. Playwright Test Agents generate `.spec.ts` files and a healer proposes patches (T39, T40). Calling Claude only on failure is worker inference.
- Runs in headed Chrome with a dedicated persistent `--user-data-dir` on Xvfb. John logs in once through noVNC (S38) over a private network. Storage state misses sessionStorage and must be deleted when it expires (S5, S6). The Xvfb and x11vnc steps are worker inference (Open questions).
- Logins. John signs in to Google by hand, because Google refuses automated browsers (S11, S25). TOTP comes from a vault (S13; Exa highlights only). Stop on any CAPTCHA. Stealth tools and solvers are rejected (S22; Exa highlights).
- Guardrails sit in settings and hooks: deny and ask rules plus PreToolUse hooks on browser MCP tools (R7, R22-R24). The Playwright MCP origin list "is not a security boundary" (R28). An agent clicked Delete with Accept Edits on (R32). Check before create and never blind-retry a mutation (R4-R6). Money, deletion, sends, publishing and permission changes go to John.
- No desktop control in v1: Claude Code computer use "is not available on Linux" (C1, C2), and Cua Driver is an optional add-on to spike (C23). Blood work: John downloads the PDF and it is parsed locally. Labcorp bans robots (P16).

## Alternatives and rejected
- Playwright MCP as the main driver - kept as alternative - in-context snapshots may help (T1, T5)
- agent-browser / Chrome DevTools MCP - kept as alternative (T8, T7)
- Claude in Chrome on John's machine - kept for attended one-offs (T17, R15)
- browser-harness over CDP - kept as alternative, unvetted (T10)
- Stagehand local `cacheDir` replay - kept as alternative if scripts prove brittle; needs its own LLM key (T42); v3/v4 local cache contradictory (R3, Open questions)
- Checkly hosted monitors - kept as alternative, price not checked (R14)
- Clay table logic rebuilt as Workflows (Alpha) via CLI - kept as alternative to the browser (A16)
- Attio views via a hand-recorded runbook - kept as alternative (Q14; no evidence ID)
- Cua Driver MCP in a disposable VM / E2B Desktop / Claude Desktop on a spare Mac - kept as desktop alternatives (C23, C27, C6)
- Blood work: Epic SMART app (P7, P8); Apple Health export (search highlight only, excluded claim 21); Fasten Connect or 1up (P14; prices unverified) - kept as alternatives
- Magnitude - rejected - name reused, self-reported benchmark only (T15, T16)
- workflow-use - rejected - "we don't recommend using this in production" (T47)
- browser-use as primary - rejected - second LLM loop (T9; worker inference)
- Skyvern - rejected for now - needs its server and its own LLM; AGPL (T13, T45, T46)
- Puppeteer direct - rejected - subsumed (T6)
- OpenClaw as controller - rejected - `mcp serve` exposes only conversations (C19)
- Bytebot - rejected - archived (C28)
- UI-TARS Desktop / Agent S - rejected - separate agents (C29; Agent S search result only)
- ChatGPT agent / Operator - rejected - closed, not drivable; "retired" seen only in a search result
- Claude Code computer use for unattended work - rejected - macOS-only, interactive, not `-p` (C1, C2, S42)
- Hosted browsers for logged-in work - rejected - vendor holds the cookies (S27, S44; Exa highlights)
- Stealth plugins, CAPTCHA solvers, residential proxies - rejected - evasion (S22)
- Storage-state files as the main session store - rejected (S5, S6)
- `bypassPermissions` or Accept Edits on production, blind retries, origin list as a boundary - rejected (R27, R32, R4, R28)
- Unofficial Clay session-cookie API - rejected - unofficial and fragile (Q14)
- Unattended Labcorp portal login - rejected - terms (P16)
- Fasten OnPrem (P12), Health Connect (P11), Flexpa and similar for solo use (P15; price from search highlights only) - rejected

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Playwright CLI (`@playwright/cli`) | Primary driver and exploration skill | VM | Free, Apache-2.0 | T4, T41 |
| Playwright MCP | Alternate driver, `browser_drag`, persistent profile | VM, stdio MCP | Free, Apache-2.0 | T1, T2, S1, S4 |
| Playwright Test Agents | Generate and heal `.spec.ts` flows | VM | Free | T39, T40 |
| Playwright auto-wait and trace viewer | Deterministic layer, trace on first retry | VM | Free | R1, R2 |
| Headed Chrome, explicit `--user-data-dir`, Xvfb | Persistent logged-in sessions | VM | Free | S1, S2, S8 |
| noVNC + websockify | John's one-time logins and live view | VM, private network | Free, MPL 2.0 | S38 |
| 1Password CLI service account, or local seed + pyotp | TOTP code without the seed in context | VM | Not stated | S13, S15 (Exa highlights) |
| Claude Code permissions + PreToolUse hooks | Guardrail layer on browser tools | Claude Code | Free | R7, R22-R24 |
| Remote Control / Channels | Approval and re-login relay to John's phone | Claude Code + phone | Not stated | S48-S50, R33 |
| Attio REST + MCP, Clay plugin/CLI, n8n API, Outreach MCP | API-first routes | Hosted | John's plans | A1-A8, A11, A16, A28, A43 |
Overall: "Free and self-hosted throughout"; the cost is model tokens only (Q14, worker inference).

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1. Bootstrap adds Playwright and browsers, Xvfb, a window manager, x11vnc on localhost, noVNC, and a systemd unit for Chrome and the display (Implications 2) | Automated | Chrome and the display survive a restart (spike 3). Install steps are worker inference |
| 2. Profile directory under the engineer user: `chmod 700`, gitignored, Read in `permissions.deny` | Automated | Deny-rule read test (Implications 2) |
| 3. Private network to noVNC (Tailscale or an SSH tunnel; worker inference, Q8) | Not stated | VNC is not exposed publicly |
| 4. **John logs in by hand through noVNC to Attio, Clay, n8n and Outreach, and to Google** | John | Per-site logged-in check (spike 7); session survives a restart and lasts weeks (spikes 3, 5) |
| 5. **TOTP seeds go into the vault (1Password if he has it, else a local seed + pyotp)** | John | The wrapper returns only the code (spike 6) |
| 6. **Attio API key; Clay CLI first sign-in opens a browser (A22); n8n API key** | John (once) | API read-back (Q11) |
| 7. **Outreach app, authorisation and employer approval (A41, A42)** | John | Spike 12 |
| 8. **WHOOP and Withings developer apps, consent per account (A45, A50, A52)** | John | Data pull with refresh token (A47, A53) |
| 9. Deny and ask rules plus a PreToolUse classifier hook with `onFailure: "block"` | Automated | Hooks fire on click and type calls (spike 8) |
| 10. **Approval relay through Remote Control or Channels** | John pairs (S48-S50) | Test gated action reaches the phone |
| 11. Gitignored lab-PDF inbox and a CI check that no health file is tracked (Implications 7) | Automated | CI check |
| 12. Nightly read-only smoke run of every flow (Implications 3) | Automated | Run log |

## Repo composition
- Skill: `browser` capability ladder (API or MCP, then a flow script, then exploratory Playwright, then John), with the Q11 table checked in as a routing file (Implications 1).
- Scripts: bootstrap additions (step 1 above) and a systemd unit (Implications 2).
- Files: `flows/<app>/<task>.spec.ts`. Each has a precondition (logged-in check, check-before-create), parameterised names, a postcondition assertion (API read for Attio titles, a fresh UI read otherwise) and a trace on retry (Implications 3).
- Hooks and settings: deny or ask rules on `mcp__playwright__.*` and `mcp__claude-in-chrome__*` write tools; a PreToolUse hook classifying targets against the never-without-approval list and a domain allowlist; the supervisor stops on repeated blocks, because `-p` does not (R26, Implications 4).
- Approval digest: two new item kinds, "fresh login needed" and "gated browser action" (Implications 5).
- MCP servers: Playwright MCP (alternate). Secrets: the TOTP wrapper (Implications 6).
- Superpowers, Beads, Ralph: not discussed in this findings file.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1 | 5-10 real Attio and Clay tasks on a sandbox workspace: Playwright CLI vs MCP vs agent-browser | Success by state check; tokens and time per task recorded |
| 2 | Attio Kanban drag: `dragTo` or ref vs coordinate; healer on a broken drag or locator | Drag verified afterwards; LLM repair rate recorded |
| 3 | Persistent profile under Xvfb with explicit `--user-data-dir`; restart Claude Code and Chrome; run 2-3 weeks | Session survives; expiry logged per site |
| 4 | Challenge rate from the VM's IP vs a home exit node on four logins | Rates recorded |
| 5 | Hand-logged Google profile; Google SSO into Attio and Clay | Stays signed in; no script touches accounts.google.com |
| 6 | TOTP wrapper (`op` service account or pyotp) | Code returned without seed in context; NTP synced; read cost known |
| 7 | Per-site logged-in check plus stall alert | Alert lands in digest |
| 8 | PreToolUse hooks on Playwright MCP and `mcp__claude-in-chrome__*`; domain-allowlist hook | Fires with usable `tool_input` |
| 9 | Attio view made in the UI, read back via API; check-before-create by title | ID and title (filters too, if possible) confirmed |
| 10 | Clay column created and verified without the Enterprise API | Verified; John's Clay plan and credit-consuming clicks known |
| 11 | n8n community-package route and owner setup on John's edition | Routes released on his version |
| 12 | Outreach app creation and token scope | John can create it; employer allows UI automation |
| 13 | Attio App SDK at John's org | Blocked or not confirmed |
| 14 | Clay later terms; Quest, MyQuest, Function terms | Terms read |
| 15 | Parse real Labcorp and Quest/Function PDFs; Apple Health export; Fasten/1up individual accounts | Parser works; lab, portal and prices known |
| 16 | Optional: Cua Driver on headless Linux; WHOOP/Withings pairing without a phone; Android emulator; protected-path hook vs `rm -rf` | One native task timed; hook blocks in all modes |
| 17 | Only if scripts are brittle: Stagehand local cache, `env: "LOCAL"` + Claude | Works on the installed version |

## Requirements served
- R12: logins, OAuth consent and developer-app sign-ups are done in the browser where allowed. Google login, CAPTCHA, Labcorp and Outreach employer approval are marked human (S11, S22, P16, A41).
- R13: Attio views, Kanban and Workflows and Clay tables and columns go through Playwright, and the result is confirmed through the Attio API read (A1, spike 9).
- R14: the gated browser action and fresh-login items are parked in the approval digest while other work continues (Implications 5).
- R15: replayed `.spec.ts` flows run without the model and are checked by a nightly smoke run (T39, Implications 3).
- R17 / Q4: every write has a postcondition read, because agents over-report (T34, T35).
- R18 / Q3: the supervisor stops on repeated hook blocks; stop on CAPTCHA (R26, Q14).
- R11: one setup sitting covers the logins, TOTP seeds and keys (setup steps above).
- R23: bootstrap additions to `scripts/bootstrap.sh` (Implications 2).
- Q6: no paid service is recommended.

## GTM scenario
- Scan as-is: Attio view titles come through the API, while view configuration is a browser read (Q11). Gap otherwise; see the existing-systems digest.
- Fix Attio tables and views: the data model goes through REST (A4-A7), and views, Kanban and Workflows go through Playwright flows with an API read-back (A1-A3, spikes 2 and 9).
- Clay workflows: Workflows (Alpha) through the Clay plugin (A16). Tables, columns and custom functions go through the browser (A17, A20). Which clicks consume credits is a gap (spike 10).
- Clean data: gap in this area.
- Finish tooling: n8n through the API, with the browser only for OAuth consent (A28, A36). Outreach through MCP or REST once an app exists (A43).

## Tensions
- Attio views GET-only is called "settled" here (Q13.1, A1 from a full curl download of the spec). The existing-systems verifier marked the same claim (its S4) uncertain because it read only the first 100k characters.
- The claim that Attio webhooks are workspace-level tokens only (A8) is unverified.
- CLI vs MCP as the lead driver and their token cost across February, April and July 2026 are unresolved (Q4, T50-T56).
- Playwright MCP's default persistence contradicts itself: persistent by default (T3, Exa highlights) versus a temp directory when none is given (Q1). The decision forces an explicit `--user-data-dir`.
- Stagehand v3 vs v4 local caching (Q9) and whether Labcorp's ban covers Quest and Function (Q12) are unresolved.
- R12 and G4 want minimal manual setup, but Google, portal logins, Outreach approval and re-logins stay human. Session lifetimes per site are unknown (Open questions).
- Q7 accepts broad permissions, but this area rejects `bypassPermissions` and Accept Edits on production (R27, R32).
- R15 vs ask rules: in `-p`, repeated classifier blocks do not stop the run (R26), so a supervisor is needed. The Attio MCP asks for confirmation on writes (A11).
- Whether PreToolUse hooks fire on `mcp__claude-in-chrome__*` is unknown (Open questions), and the third-party claim for Playwright MCP was not opened (excluded claim 20). The guardrail layer rests on spike 8.
- Whether Claude in Chrome can run unattended on a headed VM display is still open (runtime open question 30).
- The TOTP vault (S13, S15), Cloudflare (S22) and hosted-browser (S27) claims rest on Exa search highlights.

## Open for John
- Which two-factor types his accounts use, and whether he has 1Password.
- Which Clay plan he is on (Enterprise or not).
- Whether his employer allows Outreach UI automation and app creation.
- Whether the Attio App SDK is blocked at his org.
- Which lab and portal he uses, and whether he has an iPhone.
- Approving the private-network route to noVNC and the never-without-approval action list.
