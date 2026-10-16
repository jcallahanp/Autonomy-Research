# Protocol and audit (Area 11) - digest
Source: research/findings/engineer-protocol.md; verification: 17 of 20 verified, 3 unverified (two of them corrected in the text after verification, 2026-10-16)

## Decision
- The protocol is a set of external checks the engineer cannot rewrite; rituals count for little. The lead rule is "Give Claude a check it can run" (E15). Agents game tests they can edit, and read-only tests restore legitimate performance (E11). Telling a model not to cheat had "a nearly negligible effect" (E31).
- Per task: one fresh `claude -p` under the supervisor, in its own worktree and branch (E37, E38, E43). The plan is skipped when the diff fits one sentence (E24). Otherwise the acceptance check is written by the plan step or a separate test agent and frozen before the build (E3, E4, E10).
- Build with a protected oracle: a PreToolUse deny on tests, `conftest.py`, CI, hooks, `.claude/` and `audit/`, plus a test-diff guard (E11). Deny rules alone are not a boundary, because `git -C . push` is not matched (E77).
- Gate: a Stop/TaskCompleted hook runs the deterministic list in Q2 and exits 2 on failure (E15, E23). UI and service tasks also run the real artifact (E8, E27).
- Auditor, script first: `audit.sh` reruns the checks, guards the test diff, and checks claims against the transcript without an LLM (E138, E152). Then a fresh, read-only, same-family judge checks narrow claim-versus-evidence pairs in one capped round (E137, E144). It flags and never rewrites (E146). Its verdict is bound to the HEAD SHA it audited (E150), and the supervisor enforces a FAIL (E149, E170). Two caveats from verification: the AppWorld 0.953 vs 0.537 reading of E138 is uncertain, and the E144 wording was corrected to "matched or exceeded".
- Git: one squash-merged PR per task with a Conventional Commit title (E44, E46). Tier 1 paths self-merge through `gh pr merge --auto` once required checks pass (E54, E59). Everything else is Tier 2, NEEDS-JOHN (Q5). R16 stays off until the GitHub plan question is settled and two weeks of shadow mode pass (E50, E53, E70).
- Observability and recovery live in the supervisor. It appends `events.jsonl` and renders `RUN_STATUS.json` and `MORNING.md` from it. It sends one Telegram push of 1-4096 characters (E103) or ntfy (E102), because Channels needs an open session (E104). It stores `session_id` and resumes with `--resume <id>` (E108, E113). It adds a `waiting_for_reset` state parsed from the limit message (E115-E117). Under systemd it uses `Restart=on-failure` and a startup reconcile (E124, E125).

## Alternatives and rejected
- Superpowers' full flow with the TDD iron law and two-stage review: alternative; costs more, and the TDD gain is unproven (E14, E20).
- spec-kit or Kiro-style heavier spec ceremony: alternative; the worker rejected it for one-user effort (E21, E22, E26).
- RETRACE-style reconstruction verifier: alternative, spike only (E5).
- Second-family look on high-risk changes or at phase end: alternative, only if the auditor spike shows extra catches (E145, E148).
- backcheck (Apache-2.0, E152, E153) or Proof (MIT, E154) in place of a home-built claim checker: alternative after a spike under `claude -p`.
- Local `/code-review` or a fresh subagent for the PR diff: alternative. CodeRabbit Essentials at $24 per developer per month on annual billing is a paid fallback only if a spike shows extra catches (E157).
- GitHub App in place of a bot PAT (E82); a public repo or local-only enforcement in place of GitHub Pro; ntfy in place of Telegram (E102); OTel with SigNoz or Grafana if John wants charts (E88-E91); Renovate patch-only automerge later (E61, E75): alternatives.
- Multi-agent debate: rejected; the evidence was not opened (worker judgement).
- Same-agent self-review: rejected; models "struggle to self-correct" (E6).
- Mandatory agent-written tests: rejected; no significant change in outcomes (E1).
- TDD as a prompt ritual: rejected; regressions rose to 9.94% (E2).
- Prompt-only anti-cheat: rejected (E31).
- LLM-only completion judge: rejected; no judge exceeds AUROC 0.65 on tau2-bench (E137), and judges flip on confident rewrites (E139).
- An auditor that rewrites code: rejected (E146, E147).
- Mutation score as a hard gate: rejected (worker inference; its studies are unopened).
- Forced subagent delegation as an overclaiming fix: rejected; it raised misleading runs (E129).
- Proof-or-Stop's signed receipts: rejected; only the staleness rule is copied (E150).
- Paid review bots as the audit: rejected. Greptile is $30 per seat (E158); Qodo has no permanent free tier (E159); neutral recall is low (E164, E165).
- Managed Claude Code Review: rejected; Team or Enterprise only (E161), and it never blocks (E172).
- OverclaimBench as a test bed: rejected; its artifacts are not public (E131).
- Haiku as the claim auditor: rejected (E35).
- Superpowers' local merge to main: rejected; it bypasses PR checks (E41).
- Deny rules as the git boundary: rejected (E77).
- Merge queue: rejected (E60).
- Signed commits in v1: rejected (worker inference).
- Taiga as a product: rejected; its rules are copied (E63).
- Transcripts as the audit trail: rejected (E96, E97).
- Relying on usage-limit auto-continue: rejected (E117, E118).
- Channels as the only push: rejected (E104).
- Langfuse and Phoenix for v1: rejected; their setup pages were not opened.

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Claude Code hooks (PreToolUse deny, Stop/TaskCompleted gate, PostToolUse lint) | Protected oracle and deterministic done gate | Engineer VM | Included | E11, E15, E23 |
| `auditor` subagent (Sonnet-class or higher, Read/Glob/Grep/Bash) + `audit.sh` | Script layer then narrow claim judge | Engineer VM | Tokens; about 2-4x per gated task (worker inference from E151's 3.80x) | E32, E137, E144, E151 |
| backcheck | Deterministic claim-vs-transcript check, zero LLM calls (spike first) | Local CLI | Free (Apache-2.0) | E152, E153 |
| gitleaks, Semgrep | Secret scan; dependency/SAST scan at phase end or on risky diffs | Local | Not stated in findings | Q2 deterministic list (worker inference; tools not evaluated) |
| `claude --worktree`, `gh pr create`, `gh pr merge --auto` | Isolation, PR and Tier 1 auto-merge | VM + GitHub | Included | E37-E39, E54, E59 |
| GitHub branch protection, CODEOWNERS, required checks | Server-side merge stop | GitHub | Pro or Team for private repos; Pro price unverified | E50, E53, E56, E58 |
| Fine-grained PAT on a bot account | Repo-scoped agent credential | GitHub | Free | E80, E81 |
| Telegram Bot API (or ntfy) | Supervisor-side morning push by `curl` | Hosted | Free (not stated) | E103, E102 |
| systemd `Restart=on-failure` | Supervisor restart, reconcile, "supervisor died" ping | VM | Free | E124, E125 |
| statusline `rate_limits` | Pre-flight limit guard (spike under `-p`) | Claude Code (Pro/Max) | Included | E98 |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1. Pick the GitHub plan: Pro, a public repo, or local-only enforcement | John | Spike 5 in a throwaway private repo |
| 2. Create the bot account with write (not admin) access and a repo-scoped fine-grained PAT (Contents, Pull requests, Metadata) | John by hand (findings name no automated path) | Spike 5: bot push to main and force-push refused |
| 3. Enable branch protection, required checks, CODEOWNERS with "Require review from Code Owners", "Do not allow bypassing", and auto-merge | Automated once the plan allows it | Spike 5: auto-merge works with 0 approvals; a CODEOWNERS path blocks it |
| 4. Install the PreToolUse protected-path deny list and test-diff guard | Automated | Spikes 2 and 6 (Bash writes and `git -C`, `sh -c`, alias rewording) |
| 5. Add the Stop/TaskCompleted gate and the `auditor` agent with `audit.sh` | Automated | Spikes 4 and 9 |
| 6. Create `audit/waivers.md` | Automated file; John owns its content | John edits it; the auditor reads it |
| 7. Set up the Telegram bot or ntfy topic for the push | Not stated in findings | A test push arrives |
| 8. Install the supervisor systemd unit (`ExecStartPre` reconcile, `ExecStopPost` ping); keep `autoContinueAtUsageLimit` off | Automated | Spike 8 (deliberate usage-limit run) |
| 9. Two weeks of shadow mode: the engineer proposes the tier, John merges | John | Spike 7: tier agreement with John |

## Repo composition
- Agents: `auditor` (fresh context, same family, no Write/Edit on source; writes only `audit/AUDIT-<id>.md`, at most 15 lines, `PASS | FAIL | NEEDS-JOHN`) (Q3).
- Scripts: `audit.sh` (script layer); a test-diff guard; a pre-merge script refusing `gh pr merge` on protected paths; the supervisor's reset-time parser and reconcile; a `getUpdates` poller writing `decisions.json` (a new build item with no source) (Q3, Q5, Q6, Q7).
- Hooks: PreToolUse deny list (tests, `conftest.py`, CI and test config, hooks, `.claude/`, `audit/`, CODEOWNERS, the protected-path list); Stop/TaskCompleted gate; PostToolUse lint and typecheck; StopFailure and Notification as event taps (Implications, Q9).
- Files: `events.jsonl` (durable log), `RUN_STATUS.json`, `MORNING.md`, `audit/AUDIT-<id>.md`, `audit/waivers.md`, CODEOWNERS, systemd unit (Implications).
- Superpowers: keep verification-before-completion (E19), the two-part task review (E20) and the worktree skill (E40, E43). Drop the TDD iron law (E14 vs E1, E2). Replace the finishing menu with always-PR, and deny local merge to main (E41).
- Beads and Ralph: not addressed in this findings file. It builds on engineer-context's supervisor loop (Q8).
- From cwc-long-running-agents: copy the read-only evaluator and default-FAIL pattern; spike before use (E32-E34).

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| 1. Reviewer and plan A/B | 10 of John's tasks with and without the reviewer and the plan, via `claude plugin eval` | Metrics: first-try gate passes and a maintainer rubric; no threshold given |
| 2. Protected-path deny | Bash writes to tests, `conftest.py` and test config | Every write is blocked |
| 3. Reviewer tier | Same vs different model tier for the reviewer | Not stated |
| 4. Seeded-fault auditor | 20 planted faults (deleted test, skipped test, mocked function, phantom file, fake package, stale doc reference, missing test run); Sonnet vs Opus vs a second family; backcheck and Proof read-only under `claude -p` | Catch and false-positive rates measured; cost within the 2-4x budget (E151) |
| 5. GitHub plan | Throwaway private repo on John's plan: protection, required check, CODEOWNERS; bot push to main, force push, `gh pr merge --auto` | Auto-merge works at 0 approvals; a CODEOWNERS path blocks it; bot pushes refused |
| 6. Deny-list bypass | `git -C . push`, `sh -c`, alias rewording against deny list and hook | Shows which rewordings pass; the server rule must hold |
| 7. Shadow mode | Two weeks; the engineer's proposed tier vs John's decision | Agreement is measured; no threshold given |
| 8. Usage-limit run | Deliberate headless limit: output text, `api_error_status`, exit code, `result.subtype`, StopFailure, statusline under `-p`, `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` vs a verify-first prompt | Supervisor parses reset time and resumes |
| 9. TaskCompleted under `-p` | Whether it fires for subagent tasks; exit code vs JSON blocking | The hook fires and blocks |
| (carried) engineer-context 3 and 8 | Stop hook behaviour; completion honesty | As in the context digest |

## Requirements served
- R14: Tier 2 changes and `NEEDS-JOHN` verdicts become numbered decision lines in one morning push. Each line has a recommended default and a reply token (Q6; the layout is worker inference).
- R15: per-task `claude -p` under a systemd-supervised loop that resumes after limits and crashes (Q7).
- R16: Tier 1 self-merge through `gh pr merge --auto`, enforced server-side. It is off until the GitHub plan is chosen and shadow mode passes (Q5).
- R17: the `auditor` checks claims against evidence, reruns tests, runs the secret scan and the doc-manifest check, and binds its verdict to HEAD (Q3).
- R18: a FAIL blocks `done`. The same FAIL twice becomes NEEDS-JOHN. A weekly limit ends the night as `stopped_by_bound` (Q3, Q9).
- R20 (partly): SAST and dependency scans at phase end. A full security report is not designed here (Q2, Q9).
- Q3: `waiting_for_reset` plus reconcile, so a crash, reboot or limit still ends in a known state (Q7).
- Q4: the evidence command is rerun at HEAD with a test count above zero; implementer-written tests never count as evidence (Q2, Implications).
- Q6: the paid review bots are priced and rejected (CodeRabbit $24 or $30, Greptile $30) (E157, E158).

## GTM scenario
- Scan as-is: gap.
- Fix Attio tables and views, set up Clay workflows: gap for the mechanism. A UI or service task runs the real artifact through Playwright (E27). This applies to checking a change, not to making it.
- Clean data: deleting data is Tier 2 (NEEDS-JOHN) and never self-merged (Q5). A destructive or external action is a NEEDS-JOHN audit verdict (Q3).
- Finish tooling: per-task PRs on the Attio-Project repo under the Tier 1/Tier 2 rules. A repo where merging deploys is always Tier 2 (E64).

## Tensions
- This area replaces engineer-context's fresh-context reviewer with a script-first auditor (Q8). Engineer-models still describes a "fresh-context Claude reviewer subagent ... after each feature".
- The push moves from Channels (engineer-context Q7.5, engineer-runtime) to a supervisor `curl` to Telegram or ntfy (E104). The requirements leave the approval channel open, and replies need an unsourced `getUpdates` poller.
- R16 vs GitHub plans: protected branches for private repos are listed under Pro (E50). The protected-branches page states no plan (E55). The Pro price is unverified. A free private repo probably cannot enforce R16.
- Usage limits: Q7(f) keeps `autoContinueAtUsageLimit` off. After correction, the official page says the setting works with `-p` (E117), so relying on the supervisor alone is a choice, not a forced one.
- Reviewer cadence: per task vs phase end is unresolved (E9 vs E12; spike 1).
- Test-first value: positive sources were not opened, while opened studies show no gain or harm (E1, E2). The prompt-against-cheating results conflict: 92% to 1% (E134) vs "nearly negligible" (E31).
- Rests on unverified material: the AppWorld detector reading (E138) and the E144 quote wording (both from Verification). backcheck and Proof were not cloned or run. Transcript parsing "can break on any release" (E97).
- 45 claims remain excluded as search text only. They include the Opus 5.x false-completion numbers (Open questions).

## Open for John
- GitHub Pro, a public repo, or local-only enforcement for R16 (Q5).
- Whether lockfile bumps may self-merge (default: John-gated) (Q5 Contradictions 2).
- Whether R16 has further limits, such as production deploys. Repos that deploy on merge are Tier 2 by default (E64).
- Telegram or ntfy for the push; whether he wants an OTel dashboard (Q6).
- The content of `audit/waivers.md` (Q3).
