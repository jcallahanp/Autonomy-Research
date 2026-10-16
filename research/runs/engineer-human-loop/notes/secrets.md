# Secrets store and keeping secrets out of model context

Brief: Choose the secrets store for an autonomous Claude Code engineer on one Ubuntu VM, and the exact pattern by which the engineer uses a secret without its value entering model context, transcripts or logs.
Run: research/runs/engineer-human-loop/PLAN.md

## Which secrets store (candidates, price, licence, setup, audit, offline)

### Takeaway
For one VM and one person, the file-based options (SOPS with age, systemd credentials) beat a secrets service on setup effort and offline behaviour; the paid-or-hosted stores only win on audit log and rotation. Recommendation (mine, medium confidence): SOPS+age (free, offline) read only by a separate broker Unix user; fallback 1Password service account with a low-risk "agent" vault if John already pays for 1Password (service accounts work on Families, not only Business). Reject Vault/OpenBao, self-hosted Infisical, pass and plain `.env` for this case.

### Cited findings
- 1Password service accounts: up to 100 per account, vault-scoped, usage report available — https://www.1password.dev/service-accounts/, opened 2026-10-16, Exa fetch — Quote: "You can create up to 100 service accounts." and "you can see what items a service account accesses by creating a usage report."
- Service accounts are not limited to Business: the rate-limit table lists them for Individual, Families, Teams and Business — https://www.1password.dev/service-accounts/rate-limits, opened 2026-10-16, Exa fetch — Quote: "1Password, 1Password Families, and 1Password Teams | Read | 1,000 | 1 hour | Per service account token"
- 1Password service account limits: cannot reach Personal/Private vault; permissions immutable after creation (rotate by creating a new account) — https://www.1password.dev/service-accounts/get-started, opened 2026-10-16, Exa fetch — Quote: "Service account permissions, vault access, and Environment access are immutable."
- 1Password Business price: $8.99 per user per month billed yearly (search result page, https://1password.com/pricing/business, not opened; price only a search highlight, see Gaps).
- Bitwarden Secrets Manager Free: 2 users, 3 projects, 3 machine accounts; Families plan holders create a separate Free organization — https://bitwarden.com/help/secrets-manager-plans/, opened 2026-10-16, Exa fetch — Quote: "Up to 2 users - Up to 3 projects - Up to 3 machine accounts"
- Bitwarden Teams Secrets Manager: event logs and 20 machine accounts, priced per user — same page — Quote: "Up to 20 machine accounts included, with extra accounts billed per account"
- Infisical: free tier is 5 identities, 3 environments, no audit log retention; Secret Rotation and 30-day audit log start at Pro $20/identity/month — https://infisical.com/pricing, opened 2026-10-16, Exa fetch — Quote: "Free $ 0 forever ... 5 identities, unlimited projects"; "Pro ... $ 2 0 /identity/month ... Secret Rotation ... 30-day Audit log retention"
- Infisical core is MIT and self-hostable; some features paid — https://infisical.com/llms-full.txt, opened 2026-10-16, Exa fetch — Quote: "The core platform is MIT licensed and fully self-hostable. Some features (SSO enforcement, LDAP, SCIM, KMIP, HSM, audit streaming) are paid."
- Infisical `infisical run -- <cmd>` injects into a process without writing to disk; machine identity via `INFISICAL_TOKEN` — https://infisical.com/llms-full.txt, opened 2026-10-16 — Quote: "`infisical run -- ` injects secrets into a process without writing them to disk."
- Doppler Developer plan: free for 3 users, 3 days of activity logs; automatic rotation and 90-day logs on Team at $21/user/month — https://www.doppler.com/pricing, opened 2026-10-16, Exa fetch — Quote: "Free for 3 users $8/mo per additional user"; "3 days of activity logs"; "Automatic secret rotation"
- Single-VPS comparison (Oct 2026): OpenBao is MPL 2.0 and seals on every restart; file-based options need no extra service — https://www.ssdnodes.com/learn/self-hosted-secrets-manager, opened 2026-10-16, Exa fetch — Quote: "A restarted server is a sealed server."
- Same source on single-box choice — Quote: "On a one person VPS the Shamir split protects nothing, because all five shares end up in the same password manager belonging to the same person."
- Same source: SOPS+age and systemd-creds details (Ubuntu 24.04 ships systemd 255; no TPM2 on most VPS so host key only; back up `/var/lib/systemd/credential.secret`) — Quote: "Ubuntu 24.04 ships systemd 255, so this needs no install."
- OpenBao with Claude Code home-lab pattern: wrapper scripts are what the agent calls; short-lived SSH certs and KV reads; manual unseal after restart — https://dev.to/kseitter/why-ai-agents-need-a-vault-building-openbao-for-claude-code-a-home-lab-walkthrough-idn, opened (search highlights only; not opened, see Gaps).

### Contradictions
- None found. (1Password Business is not required for service accounts per the rate-limit page; the earlier registry row only said "if John has 1Password".)

### Inferences
- Audit log matters little for a single user on one VM; the transcript and the broker's own log are the audit trail. So the paid features of Infisical Pro and Doppler Team do not earn their price here (mine, from the pricing pages).
- Offline behaviour: SOPS+age and systemd-creds work with no network; 1Password, Bitwarden, Infisical Cloud and Doppler need the network at fetch time (mine; docs describe online fetch via token).
- Rotation support: only Infisical Pro+ and Doppler Team list automatic rotation; 1Password, Bitwarden Free and SOPS rotate by hand or by script, which suits a "John rotates, engineer proposes" policy.

### Gaps
- 1Password Families / Individual current price: only seen in a search highlight (https://1password.com/pricing?currency=cad showed $4.99 Families in CAD); not opened. Confirm before recommending.
- `bws run` (Bitwarden) injection semantics and Bitwarden audit log on Free: not opened.
- OpenBao dev.to page and Infisical self-host resource needs (Postgres, Redis) not opened.
- age/SOPS licences (MPL-2.0 for SOPS, BSD-3 for age) not verified from an opened page.

## Use without exposure (injection patterns, Claude Code controls, leaks)

### Takeaway
No single control suffices: Read deny rules cover built-in file tools and recognised Bash file commands but not scripts that open files themselves; hooks cover tool calls but not harness-injected "file changed" notices; `op run` masks injected values but not its own token. Pattern: the engineer never holds a vault token or a secret file; it calls an allowlisted broker as a different Unix user, the broker injects secrets into one child process, and only exit code plus filtered output returns. Layer deny rules, a PreToolUse Bash guard, a sandbox, PostToolUse `updatedToolOutput` redaction, and scoped low-risk credentials. Confidence: medium-high on the facts, medium on the pattern (needs a spike).

### Cited findings
- Read/Edit deny rules apply to built-in file tools and recognised Bash file commands, not to scripts or `grep -r`; sandbox gives OS enforcement — https://code.claude.com/docs/en/permissions, opened 2026-10-16, WebFetch (saved output) — Quote: "They don't apply to a command that reads files without naming them, such as `grep -r pattern .` run from the directory that holds the file"
- Same page: Read rules are best-effort for Grep/Glob; `.claudeignore` has no effect — Quote: "Claude makes a best-effort attempt to apply `Read` rules to all built-in tools that read files like Grep and Glob"
- Same page: `.claudeignore` — Quote: "If your project has a `.claudeignore` file, it has no effect, so move its entries into `Read` deny rules."
- Settings page gives a paste-ready deny example — https://code.claude.com/docs/en/settings, opened 2026-10-16, WebFetch — Quote: "Read(./.env)" and "Read(./.env.*)" under `"deny"`.
- PreToolUse hooks: exit 2 blocks even with JSON; timeouts do not block unless `onFailure: "block"` — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch — Quote: "To block the call when a `command` or `http` hook times out, set `onFailure: \"block\"`."
- PostToolUse can replace tool output for all tools before Claude sees it, but telemetry captures the original — https://code.claude.com/docs/en/hooks, opened 2026-10-16, WebFetch — Quote: "`updatedToolOutput` only changes what Claude sees. The tool has already run by the time the hook fires"
- Same page, telemetry caveat — Quote: "Telemetry such as OpenTelemetry tool spans and analytics events also captures the original output before the hook runs."
- Claude Code can strip Anthropic and cloud credentials from child process env (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`) — https://github.com/anthropics/claude-code-action/releases/tag/v1.0.77 (2026-03-23), opened as search highlight only; not cited (see Gaps).
- Anthropic's own cloud sessions keep credentials out of the VM via a proxy — https://code.claude.com/docs/en/data-usage, opened 2026-10-16, WebFetch — Quote: "GitHub credentials are stored encrypted on Anthropic's servers and never enter the VM."
- Incident 2026-05-14: agent ran `Get-Content ...\.env | Select-String` despite a memory rule forbidding it; four live brokerage keys revoked — https://github.com/anthropics/claude-code/issues/59094, opened 2026-10-16, Exa fetch — Quote: "Claude Code agents can read secret-bearing files (`.env`, `*-creds*`, `*.pem`, etc.) via `Read`, `Get-Content`, `cat`, etc."
- Incident 2026-06-26: `pass show ... | head -8` printed a live GitHub PAT because gpg was unlocked; a urllib exception serialised an Authorization header — https://github.com/anthropics/claude-code/issues/71654, opened 2026-10-16, Exa fetch — Quote: "agent ran pass show GH-YOLO/api-key 2>&1 | head -8 expecting a decrypt error, but gpg was unlocked so the live ghp_… printed to stdout"
- Incident 2026-09-14: harness "file changed on disk" notice dumped a full secrets file, bypassing a PreToolUse secret-file hook; ten production credentials rotated — https://github.com/anthropics/claude-code/issues/94082, opened 2026-10-16, Exa fetch — Quote: "can be silently bypassed by a **different, unguarded surface**: the harness's own \"this file changed on disk since you last read it\" notification."
- Incident 2026-09-30 (blog 2026-10-05): `cat .env` where `.env` was a 1Password-backed named pipe; 31 secrets in the transcript — https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/, opened 2026-10-16, Exa fetch — Quote: "On September 30th a Claude Code agent session ran cat .env. The file held every credential I use to work on CertWatch, my certificate monitoring product, and all 31 of them landed in the session transcript."
- Same post: first `op run` wrapper would have leaked the service-account token — Quote: "`op run` masks secret values it injects, but it doesn’t mask its own credentials."
- Same post: working design is two vaults plus an allowlist wrapper that strips the token — Quote: "A “master” vault holds production, billing, backup, and CI, and the agent’s service account can’t read it at all."
- Same post, wrapper rule — Quote: "It only runs commands from an allowlist, and never a shell, `env`, `printenv`, `echo`, or a path."
- Same post, honest limit — Quote: "It can’t stop an agent that is deliberately looking for secrets"
- Earlier operations note found the stdin pattern: `op read ... | wrangler secret put NAME` — /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:61, read 2026-10-16 — Quote: "The value passes through the shell pipe, not through a tool result."
- Same note, `op run` caveat — /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:61 — Quote: "Caveat: with `op run` the value sits in the child process environment."
- Infisical Agent Vault (preview): forward proxy attaches the credential outside the agent; self-hostable — https://infisical.com/llms-full.txt, opened 2026-10-16, Exa fetch — Quote: "A prompt-injected agent has nothing to leak, because the credential was never in its environment, files, or context."
- Same source on status — Quote: "It is currently in preview, so features and pricing may change."
- Infisical `run` doc warns about child inheritance: do not launch the editor itself through the run command — https://infisical.com/docs/documentation/guides/local-development, opened as search highlight only (not cited).

### Contradictions
- Anthropic docs say deny rules cover `cat`, `head`, `tail`, `sed` in Bash (permissions page), while incidents #59094 and #94082 show leaks via PowerShell `Get-Content`, `pass show`, and harness notices. Not strictly contradictory: the docs list only recognised commands. A spike should test the exact commands on the VM.

### Inferences
- Rules in CLAUDE.md or memory are advisory: #59094 shows the agent violating an explicit memory rule. Enforcement must be a deny rule, hook or OS permission (mine, from #59094).
- Strongest control is OS separation: the engineer's Unix user cannot read the age key or vault token, so no tool path (Read, Bash, a Python one-liner, harness notice) can reach them (mine; consistent with the docs' statement that only the sandbox gives OS-level enforcement).
- Exact pattern: (1) `engineer` user; secrets files and age key owned by `secretbroker`, mode 0600; (2) `sudoers` lets `engineer` run only `/usr/local/bin/agent-run <name>` as `secretbroker`, where `<name>` is an allowlisted job (deploy, setter, API call) defined in a root-owned file; (3) broker decrypts with SOPS, execs the fixed command with only that job's variables, pipes secrets to setters via stdin, drops its own token, returns exit code and output passed through a scrubber that masks the job's secret values; (4) `permissions.deny` for Read of `.env*`, `~/.config/sops`, `secrets/**`; deny Bash `printenv`/`env`/`cat` on those paths; (5) PreToolUse Bash guard plus PostToolUse `updatedToolOutput` secret-shape masking as defence in depth; (6) sandbox on; (7) `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` for the Anthropic token.
- Prefer "wrapper that calls the API and returns only the result" for HTTP APIs, because debug flags and exception strings echo Authorization headers (#71654).
- A forward-proxy broker (Infisical Agent Vault, or the Claude cloud network-secrets proxy already in the registry) is the stronger design for HTTPS APIs, because no env or file ever holds the value; it is preview, so spike.

### Gaps
- Whether the on-disk transcript JSONL stores the original or the `updatedToolOutput`-replaced result: docs fetched say only "changes what Claude sees"; not settled. Spike it.
- Whether `updatedToolOutput` fires for the harness "file changed" notice: no source; #94082 is open.
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` not confirmed on the official env-vars page (only a release note and a third-party page seen in search highlights).
- No Anthropic doc found that lists built-in secret redaction of tool output; absence not proven. Data-usage page mentions redaction only for feedback uploads and error reports.
- Search found other secret-redaction hook projects (cc-safe-setup, Prismor, per #71654 comments); not opened or evaluated.

## Transcripts (location, retention, secrets in tool output)

### Takeaway
Local transcripts are plaintext JSONL under `~/.claude/projects/` containing every tool result, kept 30 days by default (`cleanupPeriodDays`, minimum 1). Anything printed by a tool is therefore both sent to the API and persisted on disk; deleting the file does not un-leak it. Server-side retention depends on account: Max/Pro 30 days or 5 years (training opt-in), commercial 30 days. Cloud sessions store the transcript at Anthropic. Confidence: high.

### Cited findings
- Local transcripts plaintext, include tool results — https://code.claude.com/docs/en/claude-directory, opened 2026-10-16, WebFetch (saved) — Quote: "These files are plaintext. Anything that passes through a tool is written to a transcript on disk: file contents, command output, pasted text."
- Location and content — same page — Quote: "projects/<project>/<session>.jsonl | Full conversation transcript: every message, tool call, and tool result"
- Large tool outputs spill to separate files — same page — Quote: "projects/<project>/<session>/tool-results/ | Large tool outputs spilled to separate files"
- Default cleanup 30 days, minimum 1 — same page — Quote: "The default is 30 days and the minimum is 1; setting `0` fails with a validation error."
- Consumer retention 5 years or 30 days; commercial 30 days — https://code.claude.com/docs/en/data-usage, opened 2026-10-16, WebFetch — Quote: "Users who don't allow data use for model improvement: 30-day retention period"
- Same page: — Quote: "Users who allow data use for model improvement: 5-year retention period to support model development and safety improvements"
- Cloud sessions store the transcript; deletable — same page — Quote: "Anthropic stores the session transcript so you can return to the session later."
- Same page on deletion — Quote: "Deleting a session permanently removes the session's event data."
- Transcripts shared with `/feedback` retained 5 years — same page — Quote: "Transcripts shared via `/feedback`, or via `/bug` and `/share`, which report through the same path, are retained for 5 years."
- Survey transcript upload redacts only known patterns — same page — Quote: "Known API key and token patterns are redacted before upload. Source code, file contents, and other conversation content are uploaded as-is."
- `/feedback` can be disabled — same page — Quote: "To opt out, set the `DISABLE_FEEDBACK_COMMAND` environment variable to `1`."
- Rule from the field: a value that reached a transcript is compromised — zerofaultlabs post above — Quote: "Once a value reaches a transcript, a log, a screenshot, or a chat message, it is compromised."
- Rotation of the leaked set took about a day, mostly verification — same post — Quote: "The rotation took about a day. Most of that was verification, and I would do it the same way again."

### Contradictions
- A user-filed issue (#38417, https://github.com/anthropics/claude-code/issues/38417, search highlight only) says "Transcripts retain secrets for up to 5 years under default settings"; the data-usage page says 5 years applies only to consumer accounts that allow model improvement, else 30 days. Treat the doc as authoritative; John must check his privacy toggle.

### Inferences
- John is the single user, likely on a Max (consumer) plan: check claude.ai/settings/data-privacy-controls, because the toggle decides 30 days vs 5 years for any leaked value (mine; the toggle location is on the data-usage page).
- Set `cleanupPeriodDays` low (for example 7) on the VM and set `DISABLE_FEEDBACK_COMMAND=1` for unattended runs; this limits local exposure only (mine).

### Gaps
- Retention of a cloud session's transcript after deletion in Anthropic backups: not stated on the pages opened.
- Whether local scrub tools (editing JSONL) are supported: not documented in sources opened.

## Scoping and rotation

### Takeaway
One credential per service and per environment, held in a vault the engineer's identity can read only for staging/sandbox/read-only values; production, billing and backup credentials live in a vault the engineer cannot read, and John seeds or rotates them. The engineer may rotate only credentials it generated itself (random app keys, via `openssl rand` piped to the setter) and propose, not perform, rotation of anything else. Confidence: medium (practice-based).

### Cited findings
- Two-vault split limits blast radius — https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/, opened 2026-10-16 — Quote: "If the agent leaks something, I rotate a low-risk credential instead of the production database."
- Inventory of every credential, consumers and what else changes — same post — Quote: "Keep an inventory of every credential, where it lives, and what else changes when you rotate it."
- Rotation touches every paired copy — same post — Quote: "Every secret had a consumer somewhere: a Fly app secret, a GitHub Actions secret, or a Terraform Cloud variable."
- OpenBao pattern: separate policies per capability, short-lived tokens — dev.to page (search highlight only; see Gaps).
- 1Password service accounts cannot be edited; revoke and recreate — get-started page above — Quote: "Service accounts can’t be modified after they’re created. If you need to make changes, revoke the service account and create a new one."
- Bitwarden machine accounts: per-project read or read-write — https://bitwarden.com/help/secrets-manager-quick-start/, search highlight only; not cited.
- Prior note: John seeds secrets the model must never see; the engineer references them — /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:63, read 2026-10-16 — Quote: "John seeds them once in the vault; the engineer only references them."
- Prior note: GitHub OIDC replaces stored cloud keys — operations.md:50 — Quote: "request a short-lived access token directly from the cloud provider."

### Contradictions
- None found.

### Inferences
- Rotation cadence (mine, not sourced): rotate immediately on any exposure; otherwise a long-lived static key every 90 days is a common default, short-lived OIDC or signed certs need none; set per credential in the inventory.
- Rotation of the leaked or aged token requires the new value to reach the setter without passing through the engineer's context: the generate-and-pipe pattern (`openssl rand -hex 32 | <setter> NAME` via broker job) meets this; third-party-issued keys (Stripe, Attio, Clay) need John in a console, which sits with the key-creation facet.
- Keep an `inventory.md` with name, service, env, scope, owner, consumers, last-rotated; contains no values, safe to read (mine, from the blog post).

### Gaps
- Per-service rotation APIs (which allow programmatic rotation with a scoped admin key) not researched.
- Honey tokens / canary credentials (Infisical Pro lists them) not evaluated as a leak detector.

## Recommendation, alternatives, rejects, spikes

- Recommend: SOPS+age secrets, broker user and allowlisted `agent-run` job script, deny rules + PreToolUse/PostToolUse guards + sandbox, `agent`-grade (low-risk) credentials only, inventory file, John owns production secrets. Free, offline, about half a day to build.
- Alternatives: (a) 1Password service account with an "agent" vault, if John already has 1Password (Families works; paid); (b) Infisical Agent Vault proxy or Claude cloud network secrets for HTTPS APIs (no value in env); (c) systemd-creds for secrets consumed by long-running services.
- Rejected: OpenBao/Vault (seals on restart, ops burden for one VM); self-hosted Infisical (Postgres and Redis for one user; audit and rotation are paid tiers); Doppler (cloud, 3-day logs on free, rotation paid); Bitwarden Secrets Manager (3 machine accounts, fine as fallback but no strengths here); `pass` (unlocked gpg agent printed a PAT, #71654); plain `.env` with direnv (file readable by the engineer, #59094, #94082); relying on CLAUDE.md rules (#59094).
- Spike before building: (1) does `updatedToolOutput` change what is written to the JSONL, and does it run on the file-changed notice; (2) that the sudoers-broker boundary survives `sudo -l`, `ps`, `/proc/*/environ` reads by the engineer user; (3) deny rules vs `cat`, `python -c`, `grep -r`, `Get-Content` equivalents on the VM; (4) a canary secret ("CANARY-xyz") grep over `~/.claude/projects/` after a full run; (5) Agent Vault preview viability.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1Password CLI service accounts (price check) | https://www.1password.dev/service-accounts/rate-limits | Service accounts on Individual/Families/Teams/Business; hourly limits 1,000 reads (non-Business) | VM | 2026-10-16 | Fallback store with an agent-only vault; confirm price |
| Bitwarden Secrets Manager | https://bitwarden.com/help/secrets-manager-plans/ | Free: 2 users, 3 projects, 3 machine accounts; Teams per user | hosted | 2026-10-16 | Fallback; no advantage over SOPS here |
| Infisical (cloud + self-host) | https://infisical.com/pricing | MIT core; Free 5 identities/3 envs; rotation and audit log on Pro $20/identity/month; `infisical run` | hosted / self-host | 2026-10-16 | Skip self-host for one VM; watch Agent Vault |
| Infisical Agent Vault | https://infisical.com/llms-full.txt | Forward proxy attaches credentials outside the agent; preview | cloud or self-host, proxy on own infra | 2026-10-16 | Spike for HTTPS APIs |
| Doppler | https://www.doppler.com/pricing | Free 3 users, 3-day activity logs; rotation on Team $21/user/month | hosted | 2026-10-16 | Skip |
| OpenBao / Vault | https://www.ssdnodes.com/learn/self-hosted-secrets-manager | MPL 2.0 Vault fork; seals on restart | self-host | 2026-10-16 (comparison article) | Reject for one VM |
| SOPS + age | https://www.ssdnodes.com/learn/self-hosted-secrets-manager | Encrypted files in git, no service | local | 2026-10-16 (comparison article; tool docs not opened) | **Recommended** with broker user |
| systemd-creds | https://www.ssdnodes.com/learn/self-hosted-secrets-manager | Per-service encrypted credentials in `$CREDENTIALS_DIRECTORY` | Ubuntu 24.04 (systemd 255) | 2026-10-16 (article) | Use for long-running services |
| Claude Code PostToolUse `updatedToolOutput` | https://code.claude.com/docs/en/hooks | Replaces tool output before Claude sees it; telemetry keeps original | Claude Code | 2026-10-16 | Use as defence in depth; spike transcript effect |
| `pass` | https://dev.to (no page) / issue 71654 | GPG password store | local | 2026-10-16 (issue only) | Reject: unlocked gpg printed a PAT |
