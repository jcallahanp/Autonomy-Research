# Observability and crash resumption for unattended runs

Brief: Decide how John (and the engineer itself) sees what happened overnight, and how work resumes cleanly after a crash, a reboot or a usage-limit stop.
Run: research/runs/engineer-protocol/PLAN.md

Recommendation (one line): the supervisor owns observability. Per attempt it keeps the `--output-format json` result (session_id, cost, subtype), appends one line to an `events.jsonl`, writes `RUN_STATUS.json` from a trap, renders a short `MORNING.md`, and pushes one Telegram message of at most 4096 characters. OTel to a local collector and ccusage are optional add-ons, not v1. Resume is a supervisor loop over `claude -p --resume <session_id>` plus git state, because Claude Code's own limit auto-continue is not offered in `-p` runs.

## Q1 Claude Code telemetry (OTel, stream-json, transcripts, statusline, hooks)
### Takeaway
Everything the morning report needs is already emitted for free: the `-p --output-format json` result (session_id, total_cost_usd, subtype), `stream-json` events (including `system/api_retry` with an error category such as `rate_limit`), transcripts on disk (30-day retention by default), and, optionally, OTel metrics/events. The statusline `rate_limits` fields give five-hour and weekly percent and reset time, but only to the statusline script of a session, so they are a live-view tool, not a headless one. Hooks (`StopFailure`, `Notification`, `SessionEnd`, `TaskCompleted`) are the event taps. Confidence: high on what exists, medium on how it behaves under `-p` (not spiked).

### Cited findings
- OTel is off until enabled, and the quick start exports OTLP metrics and logs via env vars — https://code.claude.com/docs/en/monitoring-usage (also read as .md), opened 2026-10-16, WebFetch + curl — Quote: "To verify a setup that exports metrics, check your backend for the `claude_code.session.count` metric, which Claude Code emits when a session starts."
- Metrics named in the doc include token usage by type, cost in USD, commit and pull-request counts, with `session.id` as an attribute (WebFetch summary of the metrics table; the doc text on session id is quoted here) — https://code.claude.com/docs/en/monitoring-usage.md line 153, opened 2026-10-16, curl — Quote: "Include session.id and, on cloud sessions, ccr.session.id attributes in metrics"
- Prompt text and tool content are redacted unless opted in — https://code.claude.com/docs/en/monitoring-usage.md line 177, opened 2026-10-16, curl — Quote: "Spans redact user prompt text, tool input details, and tool content by default."
- Traces are beta and need a second flag — https://code.claude.com/docs/en/monitoring-usage.md line 166, opened 2026-10-16, curl — Quote: "Tracing is off by default. To enable it, set both `CLAUDE_CODE_ENABLE_TELEMETRY=1` and `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`"
- `json` output carries session id and cost; `stream-json` ends with a result line — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "The last line of the stream is a `result` message with the final response text, cost, and session metadata."
- Cost is a client-side estimate and a resumed run reports the whole conversation's total — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "When you continue an earlier conversation with `--continue` or `--resume`, the run reports the conversation's whole total, earlier runs' spend included."
- Stream emits retry events with an error category incl. `rate_limit` and `billing_error` — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "`rate_limit`, `overloaded`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error`, or `unknown`"
- Unattended permission denials are reported in the stream and the final result — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "denials appear as `permission_denied` system messages, and the final result message lists them in `permission_denials`."
- Transcripts are JSONL under `~/.claude/projects/`, format is internal, retention is 30 days by default — https://code.claude.com/docs/en/sessions, opened 2026-10-16, WebFetch — Quote: "By default, Claude Code stores transcripts as JSONL at `~/.claude/projects/<project>/<session-id>.jsonl`"; "Change the 30-day retention"
- The doc warns against parsing transcripts directly — https://code.claude.com/docs/en/sessions, opened 2026-10-16, WebFetch — Quote: "scripts that parse these files directly can break on any release."
- Statusline JSON includes five-hour and seven-day usage and reset epoch, only for claude.ai Pro/Max and only after the first API response — https://code.claude.com/docs/en/statusline (saved tool output lines 195-196, 345), opened 2026-10-16, WebFetch — Quote: "`rate_limits.five_hour.resets_at`, `rate_limits.seven_day.resets_at` | Unix epoch seconds when the 5-hour or 7-day rate limit window resets"
- Hook events include `StopFailure` (matcher `rate_limit` among API errors) and `Notification` matchers `quota_auto_resume_fired|stale|disabled` — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch (first 100k chars) — Quote: "`StopFailure` | When the turn ends due to an API error"
- `SessionEnd` runs on SIGTERM, with a small default budget — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "Claude Code then runs `SessionEnd` hooks and exits."
- Cost in a crashed call may be zero, so persist the last good totals (from earlier engineer-context note, not re-opened this session) — /home/user/Autonomy-Research/research/findings/engineer-context.md:80, read 2026-10-16 — Quote: "a crash \"may carry zeroed `usage`, `total_cost_usd`, and `modelUsage`, so recover the call's totals from what arrived before it.\""

### Contradictions
- None found.

### Inferences
- (Mine) Metrics export is optional for a single user: `json` results already give per-attempt cost, session_id and subtype, and the supervisor can sum them. OTel earns its place only if John wants a per-tool-call timeline or a dashboard; then enable metrics+logs only (traces are beta, and their hook spans need a further beta flag).
- (Mine) The statusline `rate_limits` feed is the only documented machine-readable five-hour/weekly percentage. A statusline command can append it to a file each refresh, giving the supervisor a pre-flight "am I near the limit" check even in `-p` runs, if the statusline runs at all under `-p`. That is unverified and is a spike item.
- (Mine) Do not rely on transcripts as the audit trail: 30-day sweep and an internal format. The supervisor's `events.jsonl` and per-attempt JSON result are the durable record; copy `transcript_path` into it from a `SessionEnd` hook if a replay is wanted.

### Gaps
- `StopFailure` input schema was in the unread part of the hooks page (read 100k of 270k chars). Whether `StopFailure` and the statusline fire under `claude -p` is untested.
- The metrics table was read through a WebFetch summary; exact metric and attribute names should be rechecked against a live collector in the spike.

## Q2 Lightweight self-hosted viewing
### Takeaway
For one user on a phone, the most-read artifact is the pushed Telegram digest, not a dashboard. Of the dashboards: ccusage is zero-infrastructure and reads local JSONL (daily, session, 5-hour blocks, JSON output); SigNoz or a Grafana stack accepts Claude Code's OTLP metrics+logs but is a docker-compose stack; Langfuse self-host needs ClickHouse, Postgres, Redis and blob storage; Phoenix is one container but is traces-only and source-available (Elastic License 2.0). Recommend: no dashboard in v1; ccusage as an optional on-demand report; revisit SigNoz only if John asks for charts. Confidence: medium (setup cost from vendor and third-party pages; nothing run).

### Cited findings
- ccusage reads local agent data and reports daily/weekly/monthly/session, plus 5-hour blocks and JSON — https://github.com/ccusage/ccusage, opened 2026-10-16 (Exa fetch highlights, not cloned) — Quote: "ccusage reads local usage data from coding agent CLIs and turns it into daily, weekly, monthly, and session reports."
- ccusage `blocks --json` includes active flag, time remaining, burn rate and projected cost — https://github.com/ccusage/ccusage/blob/main/docs/guide/json-output.md, opened 2026-10-16 (Exa highlights) — Quote: "burnRate: Tokens per hour rate (active blocks only)"
- Langfuse self-host stack — https://langfuse.com/compare/arize-phoenix, opened 2026-10-16 (Exa highlights) — Quote: "A production Langfuse self-host runs ClickHouse, Postgres, Redis, and blob storage. Docker Compose brings that stack up on one VM."
- Langfuse core is MIT; Phoenix is source-available and one container — https://langfuse.com/compare/arize-phoenix, opened 2026-10-16 — Quote: "Phoenix is source-available under the Elastic License 2.0 (not an OSI-approved open-source license) and self-hosts on SQLite or PostgreSQL."
- Vendor bias: that page is Langfuse's own comparison, so the Phoenix criticisms are from a competitor. Same page on Arize: "Dynatrace completed its acquisition of Arize on October 1, 2026." (ownership change relevant to Phoenix's future).
- Phoenix rejects metrics; SigNoz takes traces, metrics and logs — https://briancaffey.github.io/hermes-otel/backends/overview, opened 2026-10-16 (Exa highlights; third-party plugin docs) — Quote: "SigNoz | ✅ | ✅ | ✅" (traces, metrics, logs row) and "Phoenix | ✅ | ❌ (rejects `/v1/metrics`"
- Practitioner view on cost of self-hosting Langfuse/Phoenix for one person — https://tokenjam.dev/blog/2026-05-15-how-to-monitor-claude-code, opened 2026-10-16 (Exa highlights; vendor of a competing tool `tj`) — Quote: "The cost is a weekend on Docker Compose and a ClickHouse cluster, with a reverse proxy in front."
- ntfy publishes by plain curl, supports priorities and tap-action buttons — https://docs.ntfy.sh/publish/, opened 2026-10-16, WebFetch — Quote: "curl -d \"Backup successful 😀\" ntfy.sh/mytopic"

### Contradictions
- None found. (Third-party pages are vendors of the tools they compare; treat setup-weight claims as directional.)

### Inferences
- (Mine) Phone-readability ranking: Telegram/ntfy message (read in 10 seconds) > a markdown file linked from the message > ccusage table > any web dashboard (needs a tunnel/Tailscale and a login on a phone). Dashboards answer "what happened in this tool call"; John's morning question is "what do I need to decide".
- (Mine) Langfuse and Phoenix are LLM-app tracing tools (generations, evals, prompt management). The engineer needs run-level state, which the supervisor already holds; their value would be drill-down into one failed attempt, and the transcript plus `--resume` already offers that.
- (Mine) If a dashboard is wanted later, SigNoz or a Grafana/Prometheus pair fits better than Langfuse or Phoenix because Claude Code's primary export is metrics and logs, and Phoenix rejects metrics.

### Gaps
- SigNoz and Grafana LGTM own docs (resource needs, licence) not opened; claims come from a third-party table. Free-tier prices of Langfuse Cloud/SigNoz Cloud not checked (self-host first anyway).
- ccusage was read from search highlights, not cloned; whether it handles `-p` sessions and the 2026 transcript format is not verified.

## Q3 Morning report and delivery to the approval channel
### Takeaway
One short message at terminal state, one file for detail. Telegram `sendMessage` is a single HTTPS call with a 4096-character text limit, so the push carries a counted summary and the approvals needed, and links to (or attaches) `MORNING.md`. Reference overnight tools converge on the same shape: per-run SUMMARY.md, a Telegram debrief, a circuit breaker. Confidence: medium-high.

### Cited findings
- Telegram bot call shape and size limit — https://core.telegram.org/bots/api, opened 2026-10-16, curl + WebFetch — Quote: "All queries to the Telegram Bot API must be served over HTTPS and need to be presented in this form:" and "1-4096 characters after entities parsing"
- Channels, the Telegram approval route chosen in wave 1, only works while a session is open — /home/user/Autonomy-Research/research/findings/engineer-runtime.md (Q4, from https://code.claude.com/docs/en/channels) — Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal"
- Wave 1 contract for the end state — /home/user/Autonomy-Research/research/findings/engineer-context.md:120 — Quote: "One `RUN_STATUS.json` written from a `trap` handler with `done | blocked | stopped_by_bound | crashed`"
- "1 note = 1 decision request" pattern from the overnight audit — /home/user/Autonomy-Research/research/findings/engineer-context.md:80 (quoting https://yoheinakamura.dev/night-loop-audit/) — Quote: "1 note = 1 decision request"
- Reference: a small bash overnight loop writes one report per run with PASS/FAIL, branch, diffstat, duration and Claude's own handover summary — https://github.com/creativoma/auto-claude README.md (commit 4a52b22), read 2026-10-16, git clone — Quote: "One task at a time, one worktree per task, one report per run. In the morning you read a single file."
- Reference: nightshift sends a Telegram debrief and stops after 3 consecutive failures — https://github.com/keskinonur/nightshift/blob/main/README.md, opened 2026-10-16 (Exa highlights; not cloned) — Quote: "06:30  nightshift stops. Sends you a Telegram debrief."
- Reference: OvernightAgent renders SUMMARY.md with "task outcomes, step tables, open P0/P1 issues" — https://github.com/a20185/OvernightAgent, opened 2026-10-16 (Exa highlights; not cloned) — Quote: "Auto-rendered `SUMMARY.md` per run — task outcomes, step tables, open P0/P1 issues, links to per-attempt prompts and logs."

### Contradictions
- None found.

### Inferences
- (Mine) Morning message layout (fits 4096 chars, plain text):
  1. Line 1: status word (`done | blocked | stopped_by_bound | crashed`) and, if the nightly or weekly limit ended it, the reset time.
  2. Counts: tasks done / blocked / skipped; commits and branches; tests green at HEAD.
  3. Spend: sum of `total_cost_usd` (estimate), attempts used vs cap, `session` and `weekly` usage percent if captured, stop reason or breaker reason.
  4. Approvals needed: one numbered line per decision request, each with a recommended default and the reply token (`1 yes`), mapping to Channels relay or a next-morning reply the supervisor reads.
  5. Pointers: `MORNING.md` path, branch/PR links, `RUN_STATUS.json`.
  Everything else (per-attempt table, diffstat, failing-test sets) lives in `MORNING.md`.
- (Mine) Send path: the supervisor posts with `curl` to `api.telegram.org/bot<token>/sendMessage` itself, independent of any Claude session, so a crashed or limit-stopped run still reports. Channels is for live approval relay in a running session; the supervisor's push is the "tell John" path. Use a second bot (or ntfy) so the push does not share the allowlisted Channels sender. If John wants approvals answered while the run is stopped, the supervisor needs a small poller (getUpdates) that writes answers to `decisions.json`; this is the new build item.
- (Mine) The engineer itself should read `RUN_STATUS.json` and `PROGRESS.md`, never a chat message, at the start of the next run; chat is transport only.

### Gaps
- No source opened on reply-handling for a stopped run via Telegram `getUpdates`; designed from the API shape only.
- nightshift and OvernightAgent were read from search highlights only; their code was not inspected, so nothing about them is vetted for adoption.

## Q4 Crash resumption and usage limits
### Takeaway
`claude -p --resume <session_id>` restores history and marks cut-off tool calls so Claude checks before repeating them, so resume works headless. A SIGTERM leaves the turn unfinished with no result. The decisive gap: Claude Code's auto-continue after a usage limit is documented as not offered in `-p` runs, so the supervisor must detect the limit, sleep to the printed reset time, and resume the same session itself. Weekly limits reset days out and should end the night with `stopped_by_bound`. Confidence: high on the documents, medium on exact headless limit output (needs a spike).

### Cited findings
- Resume by session id from any directory, headless — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "session_id=$(claude -p \"Start a review\" --output-format json | jq -r '.session_id')"
- Interrupted tool calls are not re-run on resume — https://code.claude.com/docs/en/sessions, opened 2026-10-16, WebFetch — Quote: "Claude sees the call marked as cut off before its result was recorded and is told to check whether it took effect before running it again"
- Option to continue the interrupted turn — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "To have Claude Code continue the interrupted turn on resume instead, set `CLAUDE_CODE_RESUME_INTERRUPTED_TURN=1`."
- SIGTERM semantics — https://code.claude.com/docs/en/headless, opened 2026-10-16, WebFetch — Quote: "Claude Code exits with code 143. Claude Code leaves the turn that was in progress unfinished and records no result for it."
- Background work does not survive a restart; some flags must be re-passed — https://code.claude.com/docs/en/sessions, opened 2026-10-16, WebFetch — Quote: "pass them again when you resume"
- `-p` sessions are hidden from the picker and `--continue` (without `-p`) but can be resumed by id — https://code.claude.com/docs/en/sessions, opened 2026-10-16, WebFetch — Quote: "You can still resume one by passing its session ID to `claude --resume <session-id>`."
- Old cached sessions: resuming a long idle session re-reads the full history once — https://code.claude.com/docs/en/sessions, opened 2026-10-16, WebFetch — Quote: "so the next request processes the full history once no matter which of the dialog's options you pick."
- Limit messages carry the reset time — https://code.claude.com/docs/en/errors.md line 726, opened 2026-10-16, curl — Quote: "You've hit your session limit · resets 3:45pm" and "You've hit your weekly limit · resets Mon 12:00am"
- The limit is shared and blocks until reset — https://code.claude.com/docs/en/errors.md, opened 2026-10-16, curl — Quote: "Claude Code blocks further requests until the reset time shown in the message."
- Auto-continue (v2.1.234+) is not offered for `-p` or background sessions, nor beyond 24 hours — https://code.claude.com/docs/en/interactive-mode.md lines ~755-760, opened 2026-10-16, curl — Quote: "Background sessions and `-p` runs**: the menu row isn't available."
- Auto-continue's own caveat on unattended execution — https://code.claude.com/docs/en/interactive-mode.md line 766, opened 2026-10-16, curl — Quote: "because the setting grants unattended execution."
- 429/529 retry watchdog for unattended sessions, but not for exhausted usage — https://code.claude.com/docs/en/errors.md line 461, opened 2026-10-16, curl — Quote: "Claude Code fails at once when a standard-speed request gets a `429` that reports a spend limit or exhausted usage credits"
- Five-hour/weekly structure and reset rules — https://support.claude.com/en/articles/11049741-what-is-the-max-plan, opened 2026-10-16 (Exa highlights) — Quote: "The weekly limit resets at a fixed time each week that is assigned to your account."
- Five-hour wrap-up allowance on Max — https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan, opened 2026-10-16, WebFetch — Quote: "On the Max plan, it can apply each time you reach a five-hour session limit, within your weekly limit."
- Shared limits across Claude and Claude Code, so John's own use eats the night's allowance — same page, opened 2026-10-16 — Quote: "These limits are shared across Claude and Claude Code, meaning all activity in both tools counts against the same limits."
- Reference limit handling in a shell supervisor: reads `api_error_status` from the result JSON, treats 401/403 as fatal, 429/529 or limit wording as sleep-and-resume the same task — https://github.com/creativoma/auto-claude auto-claude.sh:196-215 (commit 4a52b22), read 2026-10-16, git clone — Quote: "if [[ \"$status\" == \"429\" || \"$status\" == \"529\" ]] \\"
- Same repo: interrupted tasks are requeued and worktrees are per task — README.md (commit 4a52b22) — Quote: "Tasks left in `queue/doing/` are requeued at the start of the next run"
- systemd restart policy — https://man7.org/linux/man-pages/man5/systemd.service.5.html lines 926-930, opened 2026-10-16, curl — Quote: "Setting this to on-failure is the recommended choice for long-running services, in order to increase reliability by attempting automatic recovery from errors."
- on-failure covers non-zero exit and signals — same page line 871 — Quote: "the service will be restarted when the process exits with a non-zero exit code, is terminated by a signal"
- Wave 1 per-attempt bounds and kill semantics — /home/user/Autonomy-Research/research/findings/engineer-context.md:76 — Quote: "the outer supervisor must own a total-attempt counter in a file outside the container"

### Contradictions
- Secondary blogs (getclaudeskills.com, builderwithin.com, 2026-08) describe "Claude Code resumes after usage limits" without saying it is interactive-only; the official interactive-mode page (opened) says `-p` runs are excluded. Official page taken as authority; a 5-minute spike on a real Max account settles it.

### Inferences
- (Mine) What this adds beyond wave 1's RUN_STATUS.json: (a) a limit-aware state `waiting_for_reset` with the parsed reset time (distinct from `stopped_by_bound` and `blocked`) so a restart does not consume an attempt; (b) a per-task `session_id` stored before launch and after every result, so resume is `--resume <id>`, not `--continue` (which skips `-p` sessions unless run with `-p`); (c) a crash-safe `events.jsonl` append (one line per attempt start/end) from which RUN_STATUS and MORNING.md are rendered, so the trap handler is not the only writer (SIGKILL, power loss and reboot never run a trap); (d) a startup reconcile step.
- (Mine) Startup reconcile, run by the systemd unit before anything else: read `RUN_STATUS.json`; if `state` is not terminal, treat it as crashed. For the in-flight task, compare `git status --porcelain`, current branch, `git rev-parse HEAD` against the recorded pre-attempt HEAD. Dirty tree or new commits without a recorded success means half-finished: either resume the same session with a prompt to verify state first (Claude is already told to check cut-off tools), or `git stash -u` to a named ref and restart the task clean after the second failed attempt (bounded by the 2-attempts rule from wave 1). Steps must be idempotent: each task step has a script-checkable done-condition, so re-running a finished step is a no-op.
- (Mine) Limit policy: parse `resets <time>` from the result text and `api_error_status`/subtype from JSON (field name seen only in the auto-claude script, not in Claude docs). Session limit: sleep until reset plus margin if the reset is within the night's wall-clock bound, then `--resume`; set `waiting_for_reset` and send one early Telegram notice only once. Weekly limit (or reset beyond the night window): finalize `stopped_by_bound`, push once, and do not spin. Also keep a pre-flight guard: refuse to start a new task when the last statusline `rate_limits.five_hour.used_percentage` is high, so the night does not die mid-edit. Cap per-night spend by `--max-budget-usd` as wave 1 did; note that on a flat-rate Max plan the dollar cap is an estimate and the real constraint is the subscription window.
- (Mine) systemd: `Restart=on-failure` with `RestartSec` and a start-limit burst, `ExecStopPost` to send a "supervisor died" Telegram ping, and a oneshot `ExecStartPre` reconcile. A reboot restarts the unit; a clean terminal state exits 0 so it does not loop. Because Channels needs an open session, the live-approval session is a separate unit from the unattended supervisor.
- (Mine) Auto-continue stays off for the unattended path (`autoContinueAtUsageLimit` false) if John ever runs interactive sessions on the same machine, since it "grants unattended execution" and could resume a stale session; the supervisor is the single resumer.

### Gaps
- Exact headless output at a limit (text vs `api_error_status`, exit code, `result.subtype`, `StopFailure` firing) not tested; needs one deliberate spike on a spare window.
- `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` vs a fresh "verify then continue" prompt: which gives cleaner recovery is unmeasured.
- Whether `-p` runs count the wrap-up allowance and whether Max weekly reset times are exposed outside `/usage` and the statusline is unverified.
- systemd StartLimit defaults not read (the man7 text on StartLimitBurst points to systemd.unit(5), not opened).
- `getUpdates` reply path and Claude Code on the always-on VM (login expiry, 401 detection) are covered by other facets.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Claude Code OTel (metrics, events, traces beta) | https://code.claude.com/docs/en/monitoring-usage | OTLP export of session count, tokens, cost, tool results, API requests | Claude Code | 2026-10-16 | Optional add-on; enable metrics+logs only if charts wanted |
| Claude Code statusline `rate_limits` | https://code.claude.com/docs/en/statusline | Five-hour and seven-day percent and reset epoch to a script | Claude Code (Pro/Max) | 2026-10-16 | Use as pre-flight limit guard; spike under `-p` |
| StopFailure / Notification hooks | https://code.claude.com/docs/en/hooks | Event taps for API errors and quota auto-resume | Claude Code | 2026-10-16 | Use as taps; spike under `-p` |
| ccusage | https://github.com/ccusage/ccusage | Reports from local transcripts: daily, session, 5-hour blocks, JSON | local (bunx/npx) | 2026-10-16 (highlights only) | Optional on-demand report; not cloned |
| Langfuse (self-host) | https://langfuse.com/compare/arize-phoenix | MIT LLM tracing; ClickHouse+Postgres+Redis+blob | Docker | 2026-10-16 | Skip for v1; heavy for one user |
| Arize Phoenix | https://briancaffey.github.io/hermes-otel/backends/overview | One-container trace UI; traces only; Elastic License 2.0; Dynatrace owns Arize since 2026-10-01 | Docker | 2026-10-16 | Skip: no metrics, licence, ownership change |
| SigNoz / Grafana LGTM | https://briancaffey.github.io/hermes-otel/backends/overview | Traces+metrics+logs OTLP backends | Docker compose | 2026-10-16 (third-party table; own docs not opened) | Fallback if a dashboard is requested |
| ntfy | https://docs.ntfy.sh/publish/ | curl-publish push with priority and action buttons | hosted or self-host | 2026-10-16 | Fallback to Telegram for one-way pushes |
| Telegram Bot API sendMessage | https://core.telegram.org/bots/api | HTTPS push, 4096-char text | hosted | 2026-10-16 | Use for the morning push (supervisor-side) |
| creativoma/auto-claude | https://github.com/creativoma/auto-claude | Bash loop with worktrees, limit sleep-resume, requeue, per-run report | local (cloned, not run) | 2026-10-16 | Reference design for limit handling and requeue; do not adopt |
| OvernightAgent / nightshift / nachtschicht | https://github.com/a20185/OvernightAgent | Overnight queue runners with SUMMARY.md, resume, Telegram | local (search highlights only) | 2026-10-16 | Reference only; unvetted, not cloned |
| systemd Restart=on-failure | https://man7.org/linux/man-pages/man5/systemd.service.5.html | Restart policy for long-running services | Linux | 2026-10-16 | Use for the supervisor unit |
