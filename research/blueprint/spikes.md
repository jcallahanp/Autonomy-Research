# Spikes

Purpose: every spike named in the 14 digests, de-duplicated, ordered by how much of the build each one blocks.

"Sources" names the digest and its spike number (e.g. "human-loop 23" is spike 23 in `digests/human-loop.md`). Where a digest gave no pass line, the column says what is recorded instead. Nothing here has been run.

## A. Blocks the auth decision and every unattended run
| ID | Spike and probe | Pass criterion | Blocks | Sources |
| --- | --- | --- | --- | --- |
| SP01 | Re-read Anthropic's Agent SDK billing article and the legal page; check the Oct 7, 2026 "monthly API credits" note against `claude -p` | Current terms recorded with the quote | Ruling 1 (Path A or B) | human-loop 23; runtime 11, 2 |
| SP02 | `/login` vs `setup-token` vs API key on the VM: connectors, Remote Control, Chrome, artifact publishing | What each path loses, listed | Ruling 1 | runtime 6; briefing 9 |
| SP03 | Hardened container running `claude -p` under subscription login and under a trial-only key, with and without `--bare` | `--bare` works; exit codes 0 and 143 and budget-stop exits seen | Trial auth, supervisor | feasibility 2 |
| SP04 | `--permission-mode auto --permission-prompts none` on a task that triggers blocks | Exit code, `permission_denials`, behaviour past 20 blocks recorded | Denial counter, R15 | human-loop 17 |
| SP05 | `--max-turns`, `--max-budget-usd` exit codes and `result.subtype`; stub supervisor on a real repo; Ralph via `-p` with a cap | Bounds reported reliably; "no git diff in 3 attempts" detected | Supervisor, R18 | context 4 |
| SP06 | Stop and TaskCompleted hooks: exit 2 vs JSON block under `-p`; TaskCompleted for subagent tasks; `onFailure: "block"` on timeout; doc gate with an unchanged named doc | Hook blocks; false-positive rate measured | Done gate, DEPENDENTS gate, security gate | context 3; protocol 9; planning S5; human-loop 20; security 7 |
| SP07 | Deliberate headless usage limit: output text, `api_error_status`, exit code, `result.subtype`, StopFailure, statusline, `autoContinueAtUsageLimit`, `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` vs a verify-first prompt | Supervisor parses the reset time and resumes | Ruling 5, Q3 | protocol 8 |
| SP08 | Overnight VM run with watchdog; Channels relay under headless tmux | Restarts on 401 or stall; relay prompt answered | Runtime, daytime relay | runtime 1; human-loop 12 |
| SP09 | Bash sandbox on Ubuntu 24.04 with the AppArmor bubblewrap profile, `allowUnsandboxedCommands: false` | Sandbox active; `failIfUnavailable` confirmed | Every unattended run | feasibility 4; human-loop 19 |
| SP10 | Non-root user under root-owned managed settings, no MDM | Settings honoured | Guard layer | human-loop 21 |
| SP11 | `engineer` tries `sudo -l`, `ps`, `/proc/*/environ` | No secret value readable | Ruling 6 | human-loop 8 |
| SP12 | Full run, then grep `~/.claude/projects/`, logs and hook output for a canary; pipe a vault secret into wrangler, vercel, fly setters | Canary absent everywhere | Ruling 6, deploy secrets | human-loop 10; deploy 10 |
| SP13 | Deny-rule bypasses: `cat`, `python -c`, `grep -r`, `git -C . push`, `sh -c`, aliases; Bash writes to tests and test config; `.env` and n8n credential reads; `claude -p` on a denied path | Bypasses listed; protected writes blocked; server rule holds | Protected oracle, secrets | human-loop 9, 18; protocol 2, 6; existing-systems 5; security 8 |
| SP14 | PostToolUse `updatedToolOutput` vs transcript JSONL and the "file changed" notice | Replacement is what gets written | Defence in depth | human-loop 7 |
| SP15 | Reply parser on `1 y 2 n`, `all y`, `CONFIRM 4 SPEND $12` and junk | Unknown formats never approve | Approvals | human-loop 14 |
| SP16 | One Telegram bot shared by Channels plugin and supervisor; managed bot via `getManagedBotToken` | Works, or two bots needed; token fetched | Channel setup | human-loop 13, 4 |
| SP17 | Hook blocks code edits on approval-hash mismatch; `permissions.deny` on `plan.approved.vN`; ExitPlanMode vs file flag | Edits blocked; ExitPlanMode need known | Plan approval | planning S2; intake 8 |

## B. Blocks a core-loop component
| ID | Spike and probe | Pass criterion | Blocks | Sources |
| --- | --- | --- | --- | --- |
| SP18 | Throwaway private repo on John's GitHub plan: protection, required check, CODEOWNERS; bot push to main and force push; `gh pr merge --auto`; PR approval from mobile; code-scanning merge protection; environment reviewers | Auto-merge at 0 approvals; CODEOWNERS path blocks; bot pushes refused; mobile approval possible | Ruling 2 (R16), promote gate | protocol 5; planning S4; security 11; deploy step 7 |
| SP19 | Two weeks of shadow mode: proposed tier vs John's merge | Agreement measured; no threshold given | Turning R16 on | protocol 7 |
| SP20 | 20 planted faults (deleted, skipped test, mock, phantom file, fake package, stale doc, no test run); Sonnet vs Opus vs second family; backcheck and Proof under `-p` | Catch and false-positive rates; cost within 2-4x | Auditor | protocol 4 |
| SP21 | "Done" claims with failed checks, with and without the Stop-hook verifier; truncation hook; cache hit rate across `-p` | Fewer false "done"; trimming keeps pass rate | Done gate | context 8 |
| SP22 | Chromium and Playwright install and launch in VM bootstrap and cloud setup; mermaid-cli dark SVG headless | Installs, launches, renders | Bootstrap, briefing | runtime 3; briefing 2 |
| SP23 | Superpowers, Beads `bd setup claude`, Ralph Stop hook and repo SessionStart together | Collision count; none fatal | Bootstrap | runtime 5 |
| SP24 | Seeded decisions through `/compact` and auto-compact, with and without Compact Instructions and the hook; Superpowers ledger | Seeded decisions survive | Context design | context 2 |
| SP25 | Task list formats (Markdown, JSON, YAML, about 5 runs); `CLAUDE_CODE_ENABLE_TASKS`; Beads vs `tasks.json` over 3 compactions | Adherence and task loss compared | `tasks.json` format | intake 7; planning S12; context 7 |
| SP26 | Host proxy injects a test token with TLS termination | A tool ignoring `HTTP_PROXY` fails closed | Trials | feasibility 3 |
| SP27 | Three parallel trials, then a forced kill | No leaked secret, no orphan worktree | Trials | feasibility 5 |
| SP28 | `ls /dev/kvm` on the VM; `sbx` if present | KVM known | Trial runtime | feasibility 1 |
| SP29 | AskUserQuestion under `claude -p` and the Agent SDK, with and without `canUseTool` | Block, error or skip observed | Ruling 11 check | intake 5 |
| SP30 | Async answers over the channel and timeout; John's reply latency; cost of a stalled prompt overnight | Timeouts set from data | T1 timeouts | intake 6; human-loop 15, 16 |
| SP31 | Auto-mode classifier cost per action | Tokens and latency recorded | Permission mode cost | human-loop 22 |
| SP32 | Paired tier test on 20-30 of John's tasks per role, 3 repeats; Haiku verifier on seeded bad citations | Cheaper tier pass^3 not lower | Model tiers, Q1 | context 6 |
| SP33 | 10 tasks with and without reviewer and plan via `claude plugin eval`; same vs different reviewer tier | First-try gate passes and rubric recorded | Reviewer cadence | protocol 1, 3 |
| SP34 | Seeded bugs in 20-30 PRs: fresh Claude vs Claude plus Codex (and Gemini), same-model control; `codex-plugin-cc` on 5 diffs | Codex adds findings beyond a second fresh Claude | Ruling 4 cross-family | models S3, S2 |
| SP35 | 10 tasks at about 50, 100, 300 lines on Sonnet 5.5 and Opus 5.5; one-commit vs Superpowers sizing; planner `files` lists; METR raw data | Real caps set; lists accurate | Task contract | planning S8-S11 |
| SP36 | Box size for one trial worker | Box that fits (about 60 turns unvalidated) | Trials | feasibility 6 |

## C. Blocks one phase
| ID | Spike and probe | Pass criterion | Blocks | Sources |
| --- | --- | --- | --- | --- |
| SP37 | 3 past John briefs: two-phase vs free-form intake; `claude plugin eval` graders | Non-user option and hidden constraint surfaced | Intake skill | intake 1, 9 |
| SP38 | Recommended-default vs neutral closed questions | Bias recorded | Closed phase | intake 2 |
| SP39 | Glossary repair on a real dictated transcript | Names corrected | Glossary | intake 3 |
| SP40 | One feature with and without anti-goals and decision log | Score difference | Spec template | intake 4 |
| SP41 | Explore branch on one real topic; planted fake tool names; 3 vs 5 rounds | Fakes caught; John can state requirements | Explore branch | intake 10, 11, 12 |
| SP42 | Mapping pipeline on Health-Management; verifier on 30 cited facts vs long context; pydeps and dependency-cruiser edges; Explore vs 1M on 20 questions | Tokens, time, accuracy; 128K-256K ceiling confirmed | As-is scan | existing-systems 1, 2, 3; models S1 |
| SP43 | Agent context diagram vs John's knowledge; GTM integration map from snapshots vs hand-made | Differences listed; validity rate | As-is sign-off | existing-systems 12; feasibility 9 |
| SP44 | gitleaks `--redact` report; gitleaks vs TruffleHog verified on John's history; each core security tool once | Fields masked; precision settled; Semgrep offline | Credential inventory, security stack | existing-systems 6; security 1, 9 |
| SP45 | Plan set for one real project; 1-page brief vs full set | Review time; adherence | Plan template | planning S1, S3 |
| SP46 | LLM plan-vs-diff audit on 3 past repos; lychee with and without `--accept 429` | Precision; false broken-link rate | Drift gates | planning S6, S7 |
| SP47 | Score 3 paths 5 times; John explains 3 ADRs; change one design input | Stable ratings; decision and undo stated; stale map flagged | Feasibility decide | feasibility 11, 12, 13 |
| SP48 | mermaid-lint on 20 diagrams; C4 block where John views docs; GitHub's Mermaid version; SVG byte stability | Failures counted; renders; version; stability known | Diagrams | feasibility 10, 14; briefing 7, 10 |
| SP49 | Brief on John's phone: Mermaid in claude.ai, dark vs light and contrast, explain-back, 6-9 vs 10-15 vs 25 lines | Renders; 4.5:1 and 3:1 met; preference and node count chosen | Brief template | briefing 1, 2, 3, 6 |
| SP50 | Change from model file vs image; parity check over 3 changes | Score; drift caught | System model | briefing 4, 5 |
| SP51 | Unattended run commits brief; interactive or RC session publishes | Hand-off works | Ruling 7 | briefing 9 |
| SP52 | Rotation at 40 vs 100 tool calls; context rot at clean, 150K, 400K | Coverage recorded | Rotation rule | context 5, 1 |
| SP53 | Hook that greps `dead-ends.md` and the registry | Behaviour changes | Step 0 lookups | tool-discovery 8; feasibility 7 |
| SP54 | Registry latency x10; vendor-namespace entries for Attio, Clay, n8n, Supabase; D1 on 3 capabilities; one full ladder pass | Timeout set; envelope calibrated; typed blocks | Discovery | tool-discovery 1, 2, 7, 12 |
| SP55 | `tools/list` hash and re-fetch diff; vendor-domain recheck at install; agent-scan in a throwaway VM | Rug-pull detected; defence works | MCP pinning | tool-discovery 11, 13, 10 |
| SP56 | `/context` cost of Attio, Clay, n8n MCP with tool search on and off | Cost measured | MCP route | tool-discovery 6 |
| SP57 | One MCP write with approval in an unattended session | Write completes | MCP writes under `-p` | tool-discovery 9 |
| SP58 | Semgrep with ASVS tags; ZAP authenticated baseline; Playwright two-user authz and log canary; seeded repo through `/security-review` and the plugin; MASTG; PTES, NIST, n8n GHSA text | Each as stated in security digest | Security protocol | security 2-6, 12 |
| SP59 | Data-class wrapper on unlabelled and `health` paths; hook vs vendor CLIs; subprocess env | Refused; denied; no stray keys | Second model (off) | models S6, S7, S8 |

## D. Blocks one integration or project
| ID | Spike and probe | Pass criterion | Blocks | Sources |
| --- | --- | --- | --- | --- |
| SP60 | Attio: full OpenAPI spec has no view or workflow writes; view made in UI read back by API; UI-only list; merge undo in sandbox; webhook scope; App SDK at John's org | List confirmed; ID and title read back | Ruling 12; GTM | browser 9, 13; existing-systems 10 |
| SP61 | Attio Kanban drag by ref vs coordinate; healer on a broken drag | Drag verified; repair rate | GTM views | browser 2 |
| SP62 | 5-10 Attio and Clay sandbox tasks: Playwright CLI vs MCP vs agent-browser | Success by state check | Driver choice | browser 1 |
| SP63 | Profile under Xvfb for 2-3 weeks; Google SSO into Attio and Clay; challenge rate VM vs home IP; logged-in check alert; TOTP wrapper; Claude in Chrome unattended | Sessions survive; alert in digest; code without seed | Logins, Q8 | browser 3-7; runtime 7 |
| SP64 | PreToolUse hooks on Playwright MCP and `mcp__claude-in-chrome__*`; domain allowlist | Fires with usable `tool_input` | Browser guardrails | browser 8 |
| SP65 | Clay: plan, `clay workflows` JSON dump, API surface, column made without the Enterprise API, key-create endpoint, terms, table export | Known | GTM Clay | existing-systems 8; feasibility 17; browser 10, 14; human-loop 6 |
| SP66 | n8n: credential list fields, API on his plan, community packages, API and instance MCP create on a throwaway, key endpoint, n8nmermaid | Confirmed | GTM tooling | existing-systems 7; feasibility 18; browser 11; deploy 5; human-loop 6; briefing 8 |
| SP67 | Outreach: can his profile create an API app; employer policy; dev vs production credentials | Known | GTM Outreach | existing-systems 9; browser 12; feasibility 16 |
| SP68 | Slack: app from manifest then install; manifest export on apps he did not create | One click; works or not | Slack | human-loop 2; existing-systems 13 |
| SP69 | Compliance API route; CodeQL licence | Route answers; terms read | Optional | existing-systems 11, 4 |
| SP70 | Google OAuth publishing status with real scopes; service-account key create | No 7-day Testing token; key or block recorded | Google row | feasibility 15; human-loop 3 |
| SP71 | Cloudflare child token with TTL; least-privilege `wrangler deploy`; Access app by API with phone login; zone DNS token | All work | Deploy, parent tokens | human-loop 1; deploy 1, 2, 11 |
| SP72 | Preview, promote, rollback, migrate-with-backup; Cloud Run via Workload Identity; Supabase idle pause; `Persistent=`; uptime alert to Telegram; domain quote without charge | Each passes | Deploy | deploy 3, 4, 7, 12, 13, 14 |
| SP73 | WHOOP and Withings test events with HMAC; refresh-token rotation store; Withings+ need; four-case webhook tests | Verified; token stored per refresh | Health app | deploy 6; feasibility 19; human-loop 5; security 10 |
| SP74 | `./gradlew assembleRelease`, Health Connect, `adb`; first `eas submit` vs fastlane | Builds and installs; settled | R21 Android | deploy 8, 9 |
| SP75 | John's test accounts; minutes per setup step in the sitting | Accounts exist; times fed back | Trials; setup list | feasibility 8, 20 |
| SP76 | Labcorp and Quest PDFs; Apple Health export; Fasten or 1up accounts | Parser works; options known | Health labs | browser 15 |

## E. Optional, only if the option is wanted
| ID | Spike and probe | Pass criterion | Blocks | Sources |
| --- | --- | --- | --- | --- |
| SP77 | Longest Routine and quota draw; Routine digest round-trip | Measured | Routines (off) | runtime 2, 4 |
| SP78 | Codespaces persistence; Agent SDK daemon; NanoClaw or OpenClaw | Recorded | Runtime alternatives | runtime 8, 9, 10 |
| SP79 | Infisical Agent Vault preview | Viable or not | Secrets alternative | human-loop 11 |
| SP80 | Blind A/B Sonnet 5.5 vs Argon vs GPT-6.1 Sol; `agy` headless; Argon limits and Claude pricing page; screenshot review recall | Recorded before any spend | Second model | models S4, S5, S9, S10 |
| SP81 | Stagehand local cache; Cua Driver, Android emulator, protected-path hook vs `rm -rf` | Works; hook blocks in all modes | Browser alternatives | browser 16, 17 |
| SP82 | Structurizr export without Java; plugin fetch from cloud; Smithery at volume; GitHub search with a local token | Works or not | Discovery and diagram alternatives | briefing 11; tool-discovery 3, 4, 5 |
