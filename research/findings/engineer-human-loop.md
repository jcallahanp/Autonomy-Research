# Engineer human loop: frontloading John's work into one setup session, then short batched approvals

John's work can be frontloaded into one sitting. For most services a human is needed only for the first
("parent") credential and for each OAuth consent click. After that, the engineer can mint narrower tokens by API
on Cloudflare (https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/) and Vercel
(https://vercel.com/docs/rest-api/reference/endpoints/authentication/create-an-auth-token,
https://vercel.com/docs/cli/tokens). On Supabase it drives the Management API with a PAT that John makes on his
account page (https://supabase.com/docs/reference/api/introduction). On Slack it creates apps through the
manifest API from a config token that John generates by hand (https://docs.slack.dev/authentication/tokens,
https://docs.slack.dev/reference/methods/apps.manifest.create). The docs read show GitHub PATs, Google OAuth
clients, n8n and Attio keys, the Outreach, WHOOP and Withings apps, and Anthropic API keys as UI steps
(https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens,
https://support.google.com/cloud/answer/15549257, https://docs.n8n.io/connect/n8n-api/authentication.md,
https://docs.attio.com/rest-api/guides/authentication, https://developers.outreach.io/api/oauth/,
https://developer.whoop.com/docs/developing/getting-started,
https://developer.withings.com/developer-guide/v3/get-access/create-your-app,
https://platform.claude.com/docs/en/manage-claude/authentication). GitHub's terms forbid accounts registered by
bots but permit machine accounts
(https://docs.github.com/en/site-policy/github-terms/github-terms-of-service). Anthropic's Claude Code legal page
says that developers building products or services, "including those using the Agent SDK", should use API-key
authentication (https://code.claude.com/docs/en/legal-and-compliance). The notes do not settle whether John's
own `claude -p` supervisor running under his Max login counts as such a product, so it is carried as a decision
for John.

For secrets, the workers recommend SOPS with age, readable only by a separate broker Unix user, plus an
allowlisted job runner (comparison article: https://www.ssdnodes.com/learn/self-hosted-secrets-manager; the tool
docs were not opened). The reason is that documented leaks get past every model-facing control: an ignored
memory rule (https://github.com/anthropics/claude-code/issues/59094), `pass show` printing a PAT
(https://github.com/anthropics/claude-code/issues/71654), the harness's "file changed" notice bypassing a hook
(https://github.com/anthropics/claude-code/issues/94082) and `cat .env` putting 31 secrets into a transcript
(https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/). Transcripts are plaintext JSONL that
hold every tool result (https://code.claude.com/docs/en/claude-directory).

For approvals: users approved about 93% of permission prompts, and a sandbox boundary cut prompts by 84%
(https://www.anthropic.com/engineering/how-we-contain-claude). The workers therefore design three tiers: work
handled automatically, a numbered daily digest with defaults, and immediate hard gates. They lean on the
Renovate and Dependabot patterns (https://docs.renovatebot.com/key-concepts/dashboard/,
https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file).
The digest goes out from the supervisor's own Telegram bot (https://core.telegram.org/bots/api). The Channels
relay carries live tool prompts during the day (https://code.claude.com/docs/en/channels-reference). Remote
Control is the phone view, and SMS is a fallback alert only (https://www.twilio.com/en-us/sms/pricing/us).
Permission prompts stay open until someone answers them (https://code.claude.com/docs/en/remote-control), so
overnight runs must not depend on the relay.

For permissions: run `claude -p` per task with `--permission-mode auto --permission-prompts none`, as a
dedicated non-root user on the VM (https://code.claude.com/docs/en/permission-modes,
https://code.claude.com/docs/en/headless). Keep the Bash sandbox on with the unsandboxed retry off. Put deny
rules and `disableBypassPermissionsMode` in a root-owned managed-settings file
(https://code.claude.com/docs/en/permissions, https://code.claude.com/docs/en/devcontainer). Add a fail-closed
PreToolUse guard and a kill switch, a host egress allowlist and server-side branch protection. Bash deny rules
are "not a security boundary" (https://code.claude.com/docs/en/permissions). Nothing was spiked, so overall
confidence is medium.

## Questions and answers

### Q1. Which service credentials can the engineer create itself, and which need John in a UI?

**Confidence: medium-high on the documented create paths; medium on the absence claims** ("no create-key API"
for n8n, Attio, GitHub PATs, Google OAuth clients and Supabase project keys comes from the docs read, not from
proof).

The services fall into three groups (key-creation note):

- **A parent token mints children.** Cloudflare: a token with Account API Tokens Edit creates account-owned
  tokens, and the "Create additional tokens" template covers user-owned ones
  (https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/). The first token is made in the
  dashboard (https://developers.cloudflare.com/fundamentals/api/get-started/create-token/). Vercel: a REST call
  creates tokens, and the bearer token is shown only once
  (https://vercel.com/docs/rest-api/reference/endpoints/authentication/create-an-auth-token); `vercel tokens`
  scopes them to the user and optionally to one project (https://vercel.com/docs/cli/tokens).
- **A parent token drives the API, but some keys stay UI-made.** Supabase: the Management API needs a PAT made
  on the account page (https://supabase.com/docs/reference/api/introduction); the CLI accepts
  `SUPABASE_ACCESS_TOKEN` (https://supabase.com/docs/reference/cli/supabase-login); project publishable and
  secret keys are created in the Dashboard if they are missing (https://supabase.com/docs/guides/api/api-keys).
  Slack: config tokens are generated on the app settings page (https://docs.slack.dev/authentication/tokens);
  `apps.manifest.create` returns client credentials and an `oauth_authorize_url`
  (https://docs.slack.dev/reference/methods/apps.manifest.create). Worker inference: installing the app is still
  an OAuth click by John.
- **Human-only registration and consent.** GitHub's app manifest flow redirects a person through GitHub
  (https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest). The PAT docs
  show URL-parameter pre-fill but no creation endpoint
  (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
  Device flow serves headless CLI logins
  (https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps). For Google, the app
  must be registered before a client is created (https://support.google.com/cloud/answer/15549257). For n8n,
  Settings > n8n API > Create an API key (https://docs.n8n.io/connect/n8n-api/authentication.md). For Attio, a
  workspace-level token needs an admin (https://docs.attio.com/rest-api/guides/authentication). Outreach
  (https://developers.outreach.io/api/oauth/), WHOOP (https://developer.whoop.com/docs/developing/getting-started)
  and Withings (https://developer.withings.com/developer-guide/v3/get-access/create-your-app) all need an app
  made in their consoles. Anthropic API keys are "generated in the Claude Console"
  (https://platform.claude.com/docs/en/manage-claude/authentication), and the Admin API lists "List API Keys,
  Retrieve API Key (Admin API), Update API Key" (https://platform.claude.com/docs/en/api/organization/api_keys/list).

**Per-service table.** Every cell comes from the cited quote unless it is marked as inference.

| Service | John's one-time step | What the engineer can then do | Scope and expiry in the docs | Terms note | Sources |
| --- | --- | --- | --- | --- | --- |
| Cloudflare | Make a dashboard token with Account > Account API Tokens > Edit, or use the "Create additional tokens" template | Mint further tokens by API; `wrangler login` has remote-machine, container and no-callback-server variants | `not_before` / `expires_on`; the creator token "can create tokens with access to any of a user's resources" | Website terms cover only abuse-report API tokens; no signup clause found | https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/ ; https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ ; https://developers.cloudflare.com/workers/wrangler/commands/general/ ; https://www.cloudflare.com/website-terms/ |
| Vercel | Account and first token (worker inference); `vercel signup` exists in the CLI | Mint tokens by REST or `vercel tokens` | `expiresAt`, `projectId`; optionally a single project | John is "legally bound by the actions taken on your behalf by those Third Party Tools" | https://vercel.com/docs/rest-api/reference/endpoints/authentication/create-an-auth-token ; https://vercel.com/docs/cli/tokens ; https://vercel.com/docs/cli/signup ; https://vercel.com/legal/terms |
| Supabase | Make a PAT on the account page; create project keys in the Dashboard if absent | Management API and CLI with `SUPABASE_ACCESS_TOKEN` | Scoped PAT limited to the chosen organizations, projects and permissions | Customer responsible for "the security and use of" credentials | https://supabase.com/docs/reference/api/introduction ; https://supabase.com/docs/reference/cli/supabase-login ; https://supabase.com/docs/guides/api/api-keys ; https://supabase.com/terms |
| Slack | Generate a config token on the app settings page; click the install (worker inference) | Create apps via the manifest API (returns credentials and an authorize URL); rotate the config token | Config token expires 12 hours after generation | API terms: no training an LLM on API Data, no bulk export | https://docs.slack.dev/authentication/tokens ; https://docs.slack.dev/reference/methods/apps.manifest.create ; https://docs.slack.dev/reference/methods/tooling.tokens.rotate ; https://slack.com/terms-of-service/api |
| GitHub | Create the PAT or App by hand; the manifest flow redirects a person | Device-flow CLI login | Infinite PAT lifetimes allowed unless a policy blocks them | "You must be a human to create an Account"; machine accounts permitted | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens ; https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest ; https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps ; https://docs.github.com/en/site-policy/github-terms/github-terms-of-service |
| Google Cloud | Register the app, then create the OAuth client in the console; `gcloud auth login --no-browser` | Service-account keys, unless the org-policy constraint blocks them | Device flow supports a limited set of scopes | Terms not readable (gap) | https://support.google.com/cloud/answer/15549257 ; https://cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts ; https://developers.google.com/identity/protocols/oauth2/limited-input-device ; https://cloud.google.com/sdk/gcloud/reference/auth/login |
| Telegram | Make the first bot with @BotFather `/newbot` | Managed bots: token via `getManagedBotToken` (unverified for a non-business bot; spike) | — | Bot terms: no harassing or spamming users | https://core.telegram.org/bots/tutorial ; https://core.telegram.org/bots/api ; https://telegram.org/tos/bot-developers |
| n8n | Settings > n8n API > Create an API key, with a label and an expiration | No create endpoint found | Expiration set at creation; scopes on Enterprise only | Not read | https://docs.n8n.io/connect/n8n-api/authentication.md |
| Attio | Key in the Developer console; a workspace-level OAuth token needs an admin | No create endpoint found | — | "Automated decision-making shall be used solely to support human decision-making" | https://docs.attio.com/rest-api/guides/authentication ; https://attio.com/legal/terms-and-conditions |
| Outreach | Create an app; development credentials are immediate | Per-user OAuth consent (worker inference) | `expires_in` 7200 | Not read | https://developers.outreach.io/api/oauth/ |
| WHOOP | Create an App in the Developer Dashboard | Per-member consent (worker inference) | New apps start on a Sandbox tier of up to 10 members | Not read | https://developer.whoop.com/docs/developing/getting-started ; https://developer.whoop.com/docs/developing/app-approval |
| Withings | Register in the Partner Hub | OAuth code flow (note claim) | "Withings+ becomes required on the Start for Free API plan from October 12, 2026" | Not read | https://developer.withings.com/developer-guide/v3/get-access/create-your-app |
| Anthropic | Max `/login` for the engine; any API key from the Console | Admin API lists List/Retrieve/Update for keys; no create is listed | Key type chosen at creation | API keys for products built on the Agent SDK; no sharing of credentials | https://platform.claude.com/docs/en/manage-claude/authentication ; https://platform.claude.com/docs/en/api/organization/api_keys/list ; https://code.claude.com/docs/en/legal-and-compliance ; https://www.anthropic.com/legal/consumer-terms |
| Clay | Not established | Not established | Not established | Not read | Gap (Open questions) |

Worker inferences (key-creation note):
- Only Cloudflare, Vercel and Supabase let a parent token mint narrower tokens by API. So John's first step per
  service is the parent token, and the engineer mints a child per task.
- Child tokens should be scoped to a project or zone and expire within days.
- The Cloudflare creator token is the most dangerous secret and belongs outside the engineer's reach. This
  matches the docs' warning to "safeguard the new token"
  (https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/).

Two further points:
- **Google service-account keys.** The org-policy constraint stops service-account credentials from being
  created when it is set
  (https://cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts). The page's
  "enforced by default" note for orgs created on or after May 3, 2024 sits under a different constraint (the
  default service account role grant), and the worker flags that it may not cover key creation (same URL).
- **Withings.** Worker inference: John's existing account is unaffected only if it was created before
  2026-10-12. Check the account date.

**Contradictions.** None between notes or sources. The brief mentioned "GitHub fine-grained PAT creation
limits", but no creation API exists; both GitHub pages show only UI creation (key-creation note).

### Q2. What do the services' terms say, and does Anthropic allow the engineer to run on John's Max login?

**Confidence: low-medium.** Terms were found for only some of the services.

**What the terms say:**
- **GitHub** permits only human-registered accounts but allows machine accounts: "Accounts registered by "bots"
  or other automated methods are not permitted. We do permit machine accounts"
  (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service).
- **Vercel** binds John to the actions of the third-party tools he authorises
  (https://vercel.com/legal/terms).
- **Supabase** holds the customer responsible for the "security and use" of access credentials
  (https://supabase.com/terms).
- **Telegram's** bot-developer terms bar harassing or spamming users (https://telegram.org/tos/bot-developers).
  Worker inference (not in the source): the same terms also bar making credentials public.
- **Slack's** API terms bar training an LLM on API Data and bulk export
  (https://slack.com/terms-of-service/api).
- **Attio** limits automated decision-making to supporting human decisions
  (https://attio.com/legal/terms-and-conditions).
- **Cloudflare's** website terms only address automated abuse-report tokens
  (https://www.cloudflare.com/website-terms/).
- No relevant terms were found for Clay, n8n, Outreach, WHOOP, Withings, Google Cloud or Cloudflare self-serve
  signup (Open questions).

**Anthropic and the Max login (the wave-3 open question).** The notes establish three things:

1. **The quoted rule.** The Claude Code legal page says: "Developers building products or services that
   interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication
   through Claude Console" (https://code.claude.com/docs/en/legal-and-compliance). The note's claim for that page
   adds that subscription OAuth is for ordinary native use and that Max credentials may not be used to route
   requests for others. Those two points are not in the quote; the verifier should check them on the page.
2. **The consumer terms.** "You may not share your Account login information, Anthropic API key, or Account
   credentials with anyone else" (https://www.anthropic.com/legal/consumer-terms).
3. **The engineer cannot mint an API key itself.** Keys are generated in the Console
   (https://platform.claude.com/docs/en/manage-claude/authentication).

The key-creation worker's inference is that Claude Code on John's Max login for his own work fits the
ordinary-use wording, and that building a service for others on that login does not. No opened source says
whether a supervisor script that starts `claude -p` under John's own login counts as a "product or service"
built with the Agent SDK. **So the notes do not settle the question.** The blueprint should carry it as a
decision for John, with the quote above. The safe fallbacks:
- A Console API key for the supervisor's runs. engineer-runtime.md already keeps an API key "as an overflow
  fallback" (/home/user/Autonomy-Research/research/findings/engineer-runtime.md:439-441).
- Its spike 11, re-reading Anthropic's support article on Agent SDK billing
  (/home/user/Autonomy-Research/research/findings/engineer-runtime.md:466-467).

Note that API-key auth as the VM's primary auth loses Remote Control, connectors and Chrome
(/home/user/Autonomy-Research/research/findings/engineer-runtime.md:439). Switching wholesale has a cost.

Worker inference (key-creation note): John himself registers every account and app. Nothing read bans an agent
from calling key-mint APIs with a parent token that a human created.

**Contradictions.** There is no contradiction between sources, but there is a tension with the earlier
runtime finding. engineer-runtime.md recommends Max `/login` as primary auth
(/home/user/Autonomy-Research/research/findings/engineer-runtime.md:408-411). The legal-page quote above
recommends API keys for products built on the Agent SDK. **Unresolved** (Open questions).

### Q3. Which secrets store fits one VM and one user?

**Confidence: medium.** The SOPS+age and systemd-creds facts come from a third-party comparison article; the
tool docs were not opened.

**Recommendation (secrets worker inference):** SOPS with age, read only by a separate broker Unix user.
Fallback: a 1Password service account with a low-risk "agent" vault, if John already pays for 1Password.

**The candidates:**
- **1Password service accounts.** Up to 100 per account; a usage report shows which items an account accessed
  (https://www.1password.dev/service-accounts/). The rate-limit table lists "1Password, 1Password Families, and
  1Password Teams | Read | 1,000 | 1 hour" (https://www.1password.dev/service-accounts/rate-limits), so service
  accounts are not limited to Business. Permissions are "immutable" once the account is created
  (https://www.1password.dev/service-accounts/get-started).
- **Bitwarden Secrets Manager.** Free covers "Up to 2 users - Up to 3 projects - Up to 3 machine accounts"; Teams
  includes up to 20 machine accounts (https://bitwarden.com/help/secrets-manager-plans/).
- **Infisical.** Free covers 5 identities; Secret Rotation and 30-day audit log retention are on Pro at
  $20/identity/month (https://infisical.com/pricing). The core is MIT and self-hostable, and `infisical run`
  injects secrets into a process without writing them to disk (https://infisical.com/llms-full.txt). Worker
  inference (not in the source): the free tier also has 3 environments and no audit log retention.
- **Doppler.** Free for 3 users with 3 days of activity logs; automatic rotation is on a paid tier
  (https://www.doppler.com/pricing). Worker inference (not in the source): the paid tier is Team at
  $21/user/month with 90-day logs.
- **OpenBao and Vault.** On a single VPS, "A restarted server is a sealed server", and "the Shamir split protects
  nothing" for one person (https://www.ssdnodes.com/learn/self-hosted-secrets-manager).
- **systemd-creds.** Needs no install on Ubuntu 24.04, which ships systemd 255 (same URL).

**Worker inferences (secrets note):**
- An audit log matters little for one user on one VM, because the transcript and the broker's own log serve as
  the audit trail.
- SOPS+age and systemd-creds work offline; the hosted stores need the network when fetching a secret.
- Only Infisical Pro and above and Doppler's paid tier rotate automatically. That suits a policy where John
  rotates secrets and the engineer proposes rotations.

**Contradictions.** None between the notes. There is a difference in emphasis with
engineer-browser.md, which takes TOTP codes from a 1Password vault wrapper
(/home/user/Autonomy-Research/research/findings/engineer-browser.md:661-663). The secrets note puts SOPS+age
first and 1Password second. Both are conditional on whether John already has 1Password, and its Families price
was not opened. So the store is unresolved until John answers (Open questions). TOTP for browser logins can stay
on the 1Password path if he has it.

### Q4. How does the engineer use a secret without the value entering model context or transcripts, and which leaks are documented?

**Confidence: medium-high on the facts; medium on the pattern** (no spike).

**Documented leaks.** Each one got past a model-facing control:
- **An ignored memory rule.** The agent read a `.env` despite a memory rule forbidding it, and the issue states
  that agents "can read secret-bearing files (`.env`, `*-creds*`, `*.pem`, etc.) via `Read`, `Get-Content`,
  `cat`" (https://github.com/anthropics/claude-code/issues/59094).
- **An unlocked password store.** `pass show ... | head -8` printed a live `ghp_` token because gpg was unlocked
  (https://github.com/anthropics/claude-code/issues/71654). Worker inference (not in the source): in the same
  issue a urllib exception serialised an Authorization header.
- **A harness notice.** The harness's "file changed on disk" notice bypassed a PreToolUse secret-file hook
  (https://github.com/anthropics/claude-code/issues/94082). Worker inference (not in the source): the issue
  dates are 2026-05-14 (#59094), 2026-06-26 (#71654) and 2026-09-14 (#94082), and the reporters revoked four
  brokerage keys (#59094) and rotated ten production credentials (#94082).
- **A `cat .env`.** On September 30 a session ran `cat .env` and all 31 credentials landed in the transcript.
  The author's first `op run` wrapper "doesn't mask its own credentials"
  (https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/).

**Where transcripts live.** Local transcripts are plaintext, and "Anything that passes through a tool is written
to a transcript on disk". They sit at `projects/<project>/<session>.jsonl`, and large outputs spill into
`tool-results/`. The default cleanup is 30 days and the minimum is 1 (https://code.claude.com/docs/en/claude-directory).
Server-side retention is 30 days, or 5 years for users who allow data use for model improvement. Transcripts
shared via `/feedback` are kept 5 years, and `DISABLE_FEEDBACK_COMMAND=1` opts out. Survey uploads redact only
"Known API key and token patterns" (https://code.claude.com/docs/en/data-usage).

**What Claude Code controls cover, and where they stop:**
- **Read deny rules** do not apply to "a command that reads files without naming them, such as `grep -r`". They
  are best-effort for Grep and Glob, and `.claudeignore` "has no effect" (https://code.claude.com/docs/en/permissions).
- **The settings page** gives `Read(./.env)` and `Read(./.env.*)` deny examples
  (https://code.claude.com/docs/en/settings).
- **PostToolUse `updatedToolOutput`** changes "only ... what Claude sees". OpenTelemetry spans and analytics keep
  the original output (https://code.claude.com/docs/en/hooks).
- **Anthropic's cloud sessions** keep GitHub credentials out of the VM entirely: they "never enter the VM"
  (https://code.claude.com/docs/en/data-usage).

**The pattern (secrets worker inference, built from the incidents and the docs):**
1. An `engineer` user. Secrets files and the age key are owned by `secretbroker`, mode 0600.
2. `sudoers` lets `engineer` run only `/usr/local/bin/agent-run <name>`, where `<name>` is a job defined in a
   root-owned allowlist file.
3. The broker decrypts with SOPS and execs the fixed command with only that job's variables. It pipes secrets to
   setters through stdin and returns only the exit code and scrubbed output.
4. Deny rules for `.env*`, `~/.config/sops` and `secrets/**`.
5. A PreToolUse Bash guard and PostToolUse masking as defence in depth.
6. The sandbox on.
7. Low-risk credentials only.

Supporting evidence:
- The stdin pipe (`op read ... | wrangler secret put NAME`) keeps the value in the shell pipe, "not through a
  tool result" (/home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:61).
- The blog's working design uses an agent-only vault plus a wrapper that "only runs commands from an allowlist,
  and never a shell, `env`, `printenv`, `echo`, or a path". The author admits it "can't stop an agent that is
  deliberately looking for secrets" (https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/).
- A forward-proxy broker (Infisical Agent Vault) means "A prompt-injected agent has nothing to leak", but it is
  "currently in preview" (https://infisical.com/llms-full.txt).

Further worker inferences:
- For HTTP APIs, prefer a wrapper that calls the API and returns only the result, because exception strings
  echo Authorization headers.
- Rules in CLAUDE.md or memory are advisory only (#59094).
- Set `cleanupPeriodDays` low (for example 7) and `DISABLE_FEEDBACK_COMMAND=1`. John should check his
  data-privacy toggle, which decides between 30 days and 5 years.

`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` (step 7 of the worker's own list) was seen only in a search highlight. It is
excluded here (Open questions).

**Rotation and scope:**
- Use one credential per service and environment. Production, billing and backup credentials live where the
  agent cannot read them: "If the agent leaks something, I rotate a low-risk credential instead of the
  production database" (https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/).
- Keep an inventory of each credential and its consumers (same URL).
- John seeds secrets once, and the engineer only references them
  (/home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:63).
- 1Password service accounts "can't be modified after they're created"
  (https://www.1password.dev/service-accounts/get-started).
- Worker inference: the engineer rotates only the values it generates itself (`openssl rand` piped to the
  setter through a broker job). Keys issued by third parties need John in a console. A 90-day cadence is the
  worker's unsourced default.

**Contradictions.** The permissions page says deny rules cover recognised Bash file commands
(https://code.claude.com/docs/en/permissions). Yet incidents #59094, #71654 and #94082 show leaks through
PowerShell `Get-Content`, `pass show` and harness notices
(https://github.com/anthropics/claude-code/issues/59094, https://github.com/anthropics/claude-code/issues/71654,
https://github.com/anthropics/claude-code/issues/94082). The secrets worker judges this "not strictly
contradictory": the docs list only the commands they recognise. The evidence favours OS separation over rule
text, and the exact commands should be spiked on the VM.

A separate claim, that "transcripts retain secrets for up to 5 years under default settings", was seen only in a
search highlight. It is excluded, and the opened data-usage page is followed (Open questions).

### Q5. What does the evidence say about approval fatigue and what reduces it?

**Confidence: high on the problem (Anthropic's own data); low on which remedy works best for one user.** The
academic and clinical studies the worker used came from search-result text only and are excluded (Open
questions).

Anthropic's evidence:
- "Our telemetry showed users approved roughly 93% of permission prompts."
- Sandboxing gave "an 84% reduction in permission prompts".
- "experienced users auto-approve roughly twice as often as new users".
- All three are at https://www.anthropic.com/engineering/how-we-contain-claude, which also says auto mode lets
  "~17% of overeager actions get through" (same URL).
- Anthropic defines "approval fatigue, where people stop paying close attention to what they're approving"
  (https://www.anthropic.com/engineering/claude-code-auto-mode). Worker inference (not in the source): that post
  gives a 0.4% false-positive rate, the classifier runs on Sonnet 4.6, and low-risk actions skip the classifier.

Worker inferences (approvals note):
- A 93% approve rate means the design goal is to make the rare "no" visible, not to ask more often.
- Track John's approve rate and response time per tier. A sustained rise towards 100%, or a falling response
  time, is the fatigue signal.
- Vary the form of the rare high-stakes ask, for example a typed word instead of "1 y". This idea rests on
  polymorphic-warning studies that this file excludes as search text, so it is an untested heuristic here.

**Contradictions.** The approvals worker recorded a disagreement between a clinical-alert preprint that tailors
alerts by severity and a meta-analysis where acceptance did not rise after alert volume fell. Both sources came
from search text only, so the disagreement is listed under Open questions, not resolved here.

### Q6. How should approvals be batched: hard gates versus digest, timeouts and audit trail?

**Confidence: medium.** The pattern evidence comes from dependency tools; the design is the worker's inference.

**Pattern evidence:**
- **Renovate's dashboard** keeps pending approvals visible "instead of updates being totally invisible", and
  "vulnerability remediation PRs will still get created immediately without requiring approval"
  (https://docs.renovatebot.com/key-concepts/dashboard/).
- **Dependabot** combines matching updates "in a single pull request" and caps open PRs: "no further pull
  requests are raised until some of those open requests are merged or closed"
  (https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file).
- **Claude Code** "keeps permission prompts and `AskUserQuestion` questions open until you answer them"
  (https://code.claude.com/docs/en/remote-control). There is no built-in timeout for those prompts. Worker
  inference (not in the source): other forwarded dialogs expire after five minutes to a no-action default.
- **The existing protocol design** already specifies "one numbered line per decision request, each with a
  recommended default and the reply token (`1 yes`)"
  (/home/user/Autonomy-Research/research/runs/engineer-protocol/notes/observability.md:87). Worker inference (not
  in the source): one Telegram message holds at most 4096 characters.

**Design (approvals worker inference):**
- **T0, automatic.** Work that stays in the repo, is reversible and passes tests. Logged only.
- **T1, the batched digest.** Each item carries a default. It expires to that default after 24 h only if the
  default is reversible; otherwise the task is parked.
- **T2, hard gates.** Money, deleting data, store submission, external mail and secrets. Each is sent as its own
  immediate message, never defaults on timeout, and parks its task while other tasks continue. A hard gate is
  never covered by "all y" and needs a typed confirmation such as `CONFIRM 4 SPEND $12`.
- **Digest format.** `DECISIONS (3) reply "1 y 2 n 3 y" or "all y"`, then one line per item: id, tier tag, a
  one-sentence ask, the default, the cost of waiting and a link. It is sent with the morning report, plus at
  most one more digest a day.
- **Reminders.** One reminder after 12 h, then the next morning report. No repeated pings.
- **Audit trail.** The supervisor appends every ask and answer to `decisions/approvals.jsonl` and commits it.
  Each entry holds the id, tier, text hash, default, reply, sender id, Telegram message id and timestamps.
- **A cap on open T1 items,** Dependabot-style (for example 5).
- **Parsing.** Deterministic code parses replies, not the model. An unknown format never counts as approval.

**Contradictions.** None found.

### Q7. Which mechanism carries approvals: supervisor Telegram digest, Channels relay, Remote Control or SMS?

**Confidence: medium-high.**

**The Channels relay:**
- Both the terminal and the phone stay live, and "Claude Code applies whichever answer arrives first"
  (https://code.claude.com/docs/en/channels-reference).
- It covers tool-use prompts only: "Project trust and MCP server consent dialogs don't relay" (same URL).
- Worker inference (not in the source): request IDs are five letters, a reply must match `yes <id>`, and a wrong
  ID is dropped silently.
- "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist
  senders you trust" (https://code.claude.com/docs/en/channels).
- "Events only arrive while the session is open" (same URL).
- In `-p`, interactive tools are disabled "so the session never stalls" (same URL).
- "If Claude hits a permission prompt while you're away from the terminal, the session pauses until you
  respond" (same URL).

**Remote Control** has a "Push when actions required" setting. Its server mode "gives up after roughly 10
minutes" offline (https://code.claude.com/docs/en/remote-control).

**The Telegram Bot API** supports long polling and a webhook secret token header
(https://core.telegram.org/bots/api).

**The alternatives:**
- **LangGraph** "restarts from the beginning of the node" on resume
  (https://docs.langchain.com/oss/python/langgraph/interrupts).
- **HumanLayer** says its code is "pretty much all deprecated" (https://github.com/humanlayer/humanlayer).
- **Twilio SMS** costs "$0.0083 per 160-character segment", and "US A2P 10DLC are subject to registration"
  (https://www.twilio.com/en-us/sms/pricing/us). Worker inference (not in the source): a long code costs
  $1.15/month, and the onboarding fee was not on the page.
- **n8n's** human-review and Telegram approval claims came from search text only and are excluded (Open
  questions).

**Recommendation (approvals worker inference):**
- **Live tool prompts:** the Channels relay over Telegram, daytime only.
- **Batched digest:** the supervisor's own plain Telegram bot: `sendMessage` out, long-poll in, and an allowlist
  on `from.id`. Relay covers only tool-use prompts, not product decisions.
- **Remote Control:** the phone window and a fallback.
- **SMS:** an optional dead-man alert only. Sender identity is weaker (general knowledge, not sourced), it has
  no buttons, and registration is real work.
- **Rejected:** LangGraph, n8n (unless n8n already runs) and Slack, because each adds a second runtime or a
  public endpoint for no gain.
- **Bot sharing:** the Telegram plugin owns its bot's polling. Use two bots, or have the supervisor only send
  and read the replies as Channel events. This is unverified; spike it.

**Contradictions.** engineer-runtime.md recommended "Channels (Telegram allowlist) plus Remote Control push for
approvals" (/home/user/Autonomy-Research/research/findings/engineer-runtime.md:412-413). The new approvals note
confirms that recommendation with two amendments: do not rely on live relay overnight, and the digest is owned
by the supervisor, not Channels. The new notes win. Permission prompts stay open until answered
(https://code.claude.com/docs/en/remote-control) and a session pauses at a prompt
(https://code.claude.com/docs/en/channels), so a stalled prompt blocks the overnight run. And the relay does not
carry product decisions (https://code.claude.com/docs/en/channels-reference).

### Q8. Which permission mode for unattended runs?

**Confidence: high on the documented behaviour; medium on the choice** (not spiked). Worker inference (not in
the source): the features cited need Claude Code v2.1.259+ (`--permission-prompts`), v2.1.285+ (sandbox `false`
precedence) and v2.1.295+ (`onFailure: "block"`).

**The modes:**
- **`dontAsk`** is for "Locked-down CI and scripts" (https://code.claude.com/docs/en/permission-modes).
- **`bypassPermissions`** is for "Isolated containers and VMs only" (same URL). It requires "a container, VM, or
  the sandbox runtime; on Linux and macOS, run it as a non-root user", and it "offers no protection against
  prompt injection or unintended actions" (same URL). In bypass `-p`, the few remaining prompts are denied, "so
  an unattended session keeps working" (same URL). Worker inference (not in the source): critical-path `rm`
  prompts time out after 2 minutes.
- **Deny rules** "block in every mode, including `bypassPermissions`" (same URL).

**Auto mode in `-p`:**
- "When repeated blocks reach a threshold, the action doesn't run and Claude keeps working. Claude Code doesn't
  stop the run."
- "The thresholds of 3 blocks in a row and 20 blocks total are not configurable."
- "Auto mode reduces permission prompts but does not guarantee safety."
- The classifier blocks `git remote set-url` and recursive forced deletes such as `rm -rf "$VAR"`.
- A prose boundary "can be lost if context compaction removes the message that stated it", so use deny rules
  for hard guarantees.
- Auto mode needs "Claude Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5".
- All of the above: https://code.claude.com/docs/en/permission-modes.

**Headless behaviour:**
- `--permission-prompts none` means "Anything that would prompt is denied unless a `PermissionRequest` hook
  allows it", and Claude is told not to retry (https://code.claude.com/docs/en/headless). Worker inference (not
  in the source): denials appear in `permission_denials` in stream-json.
- In `-p`, a bare `Bash` allow entry is dropped and auto mode evaluates each command (same URL).
- A run where nothing sets a mode can start in auto, "so pass the one you want" (same URL).
- `auto` or `bypassPermissions` set in project `.claude/settings.json` or `settings.local.json` does not take
  effect (https://code.claude.com/docs/en/permission-modes).

**Recommendation (permissions worker):**
- `--permission-mode auto --permission-prompts none` for `-p` runs inside the isolated, non-root,
  egress-limited VM. The devcontainer page pairs bypass with egress limits
  (https://code.claude.com/docs/en/devcontainer).
- Fallback: `dontAsk` with an exact allowlist.
- Second fallback: `bypassPermissions` in a container.

Worker inferences:
- Blocked actions are silently denied, so the supervisor must read `permission_denials` and stop at a threshold.
- Run many short `-p` sessions to reset the 20-block counter.

**Contradictions.** None. The sandbox-environments page calls the classifier not an isolation boundary, yet
isolation is "not required" for auto. The worker reads these as consistent: isolation is optional for auto and
mandatory for bypass.

### Q9. Allow and deny rules, their bypasses, managed settings and hooks

**Confidence: high** (primary docs; the hooks page was read to about 100k of 270k characters).

**Rules:**
- "Rules are evaluated in order: deny, then ask, then allow", and "An allow rule can't carve an exception out of
  a deny rule" (https://code.claude.com/docs/en/permissions).
- Documented rewordings get past a `git push *` deny: `git -C . push origin main`,
  `git -c push.default=current push origin main` and `git 'push' origin main`. So do `/usr/bin/curl` and
  `sh -c 'curl ...'` (same URL).
- The docs say a deny or ask rule "isn't a security boundary around the program" and point to sandboxing (same
  URL).
- Deny rules apply to nested subcommands (same URL).
- The list of wrappers that gets stripped is fixed, and `npx` and `docker exec` "are not in the list" (same URL).

**Managed settings:**
- "no other level, including command line arguments, can override a managed permission rule", and a managed
  deny "can't be overridden by `--allowedTools`" (same URL).
- `disableBypassPermissionsMode` and `disableAutoMode` "are most useful in managed settings" (same URL).
- Claude Code reads `/etc/claude-code/managed-settings.json` on Linux at the highest precedence
  (https://code.claude.com/docs/en/devcontainer).

**Hooks:**
- A hook that exits with code 2 "stops the tool call before permission rules are evaluated", and a hook's allow
  cannot override deny or ask rules (https://code.claude.com/docs/en/permissions).
- Exit 0 with no output means no decision (https://code.claude.com/docs/en/hooks).
- PermissionRequest ignores exit 2; deny "through the `decision` object" (same URL).
- MCP matchers need `.*` (same URL).
- A timed-out hook "doesn't block the tool call", and `onFailure: "block"` changes that (same URL).
- The default timeout is 600 s (same URL).
- The `if` filter is best-effort, so "use the permission system rather than a hook to enforce a hard allow or
  deny" (same URL).
- Command hooks run "with your full access", outside the sandbox (https://code.claude.com/docs/en/sandboxing).
- A `-p` session "shows no workspace trust dialog and no per-server approval prompt"
  (https://code.claude.com/docs/en/headless), so project hooks in cloned repos run.

**Anthropic's example kill switch:**
- "Halt every tool call while ./AGENT_STOP exists"
  (https://github.com/anthropics/cwc-long-running-agents claude-code-config/.claude/hooks/kill-switch.sh:3
  (commit ad107a9)).
- The repo is an "Event demo; not maintained" (https://github.com/anthropics/cwc-long-running-agents README.md
  (commit ad107a9)).

**Worker inferences (permissions note):**
- **Allow list:** Read/Edit/Write in the work dir, exact `git` subcommands, test, lint and build prefixes,
  `gh pr create`, and `WebFetch(domain:...)` for docs. Never bare `Bash`, `npx *`, `docker *` or `bash *`.
- **Managed deny list:** `Read(**/.env*)`, `Read(~/.ssh/**)`, `Read(~/.config/gh/**)`, force push, push to main,
  `gh pr merge` except `--auto`, `rm -rf *`, `curl *`, `wget *` and `sudo *`. Treat it as defence in depth.
- **Hooks:** a PreToolUse guard with `onFailure: "block"` that parses the whole command, plus a copy of the
  kill switch (not an install of the repo). Each kept under a second.
- **Third-party code:** use `--bare` or pinned `--settings` on third-party repos.
- **The real stop for pushes** is server-side branch protection.

**Contradictions.** None found.

### Q10. Sandbox limits, OS-level containment, and what others do overnight

**Confidence: high on the sandbox facts; medium on practice** (one blog and one issue).

**Sandbox limits:**
- "The sandboxed Bash tool on its own constrains only shell commands, so it is not sufficient for fully
  unattended runs in either mode" (https://code.claude.com/docs/en/sandbox-environments).
- "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it"
  (https://code.claude.com/docs/en/sandboxing).
- Allowed domains "start empty" (same URL).
- Set `"allowUnsandboxedCommands": false` to stop the unsandboxed retry; a matching allow rule otherwise
  "approves an unsandboxed retry" (same URL).
- If bubblewrap is missing, commands run unsandboxed by default (same URL).
- On Ubuntu 24.04 and later, the AppArmor policy blocks bubblewrap's user namespaces (same URL).
- Broad domains such as `github.com` "can create paths for data exfiltration" (same URL).
- "Sandboxing reduces risk but is not a complete isolation boundary" (same URL).

**Whole-process containment:**
- The other options put "the whole Claude Code process inside the isolation boundary" (https://code.claude.com/docs/en/sandbox-environments).
- sandbox-runtime "is a beta research preview" (same URL).
- "A dedicated virtual machine provides the strongest separation, with its own kernel" (same URL).
- Dev containers do not stop exfiltration of "the Claude Code credentials stored in `~/.claude`", and the
  firewall is "provided as a working example rather than a maintained base image"
  (https://code.claude.com/docs/en/devcontainer).

**What others do:**
- Anthropic's example: "Cap session length and have an outer script start the next one" and pair with
  `ralph-loop` (https://github.com/anthropics/cwc-long-running-agents README.md and claude-code-config/README.md:29
  (commit ad107a9)).
- A 24-hour skip-permissions run ends on "sandboxing, not vibes"
  (https://kenimoto.dev/blog/autonomous-agent-24-hours-security-lessons/). Worker inference (not in the source,
  from a WebFetch summary): the incidents were an empty-variable `rm -rf`, a POST from a typosquatted skill and
  a leaked key, at a cost of about $387.
- An open issue involves `bypassPermissions` (https://github.com/anthropics/claude-code/issues/99198). Worker
  inference (not in the source): a sub-agent ran `rm -rf` on a user directory through an 8.3 short name and kept
  running about 45 minutes after stop.

**Worker inferences (permissions note):**
- John's VM is already the "virtual machine" row. If it holds only the engineer's work, then VM + non-root user
  + Bash sandbox + host egress allowlist meets Anthropic's own unattended recipe without Docker.
- The OAuth credential in `~/.claude` is exfiltratable, so treat it as burnable.
- Add OS limits: no sudo; systemd `MemoryMax`, `TasksMax` and `CPUQuota`; a wall-clock `timeout`; an nftables
  egress allowlist; a disk quota.

**Contradictions.** None found.

### Q11. Recommendation: setup-frontloading protocol, approval design and permission posture; alternatives, rejected candidates, spike list

**Confidence: medium.** This merges the four facet recommendations, which do not conflict. Each element rests on
a claim cited above. Nothing was spiked.

**1. The setup-frontloading protocol: one sitting, worked from one ordered page.** The page shape comes from
engineer-feasibility.md: "long waits first, worked through in one local sitting ... with secrets by name only and
an agent verification table at the end" (/home/user/Autonomy-Research/research/findings/engineer-feasibility.md:301).

1. **Root steps on the VM (permissions and secrets notes).**
   - Create the dedicated non-root `engineer` user and a `secretbroker` user.
   - Install the root-owned `/etc/claude-code/managed-settings.json` (https://code.claude.com/docs/en/devcontainer).
   - Install the AppArmor profile for bubblewrap (https://code.claude.com/docs/en/sandboxing).
   - Add the sudoers line for `agent-run` and the host egress allowlist.
   - Choose what counts as a hard gate.
2. **Parent credentials, one per service, which the engineer later narrows** (key-creation note):
   - a Cloudflare token with Account API Tokens Edit
     (https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/), kept by the broker, never by
     the engineer;
   - a Vercel token (https://vercel.com/docs/cli/tokens);
   - a scoped Supabase PAT (https://supabase.com/docs/reference/api/introduction);
   - a Slack config token (https://docs.slack.dev/authentication/tokens).
3. **Human-only registrations.**
   - A GitHub machine account registered by John, a fine-grained PAT and branch protection
     (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service).
   - The Telegram bot or bots via @BotFather (https://core.telegram.org/bots/tutorial).
   - Google app registration and OAuth client (https://support.google.com/cloud/answer/15549257).
   - The Outreach, WHOOP and Withings apps, checking Withings+ on John's account
     (https://developer.withings.com/developer-guide/v3/get-access/create-your-app).
   - The Attio key and the n8n key with an expiry.
   - A Console API key only if John decides the Max-login question that way (Q2).
4. **Every consent click, in the same sitting:** Slack install, Google consent, Outreach, WHOOP and Withings.
   Then the browser logins by hand, as in engineer-browser.md
   (/home/user/Autonomy-Research/research/findings/engineer-browser.md:661-663).
5. **Seed the secrets.** John writes the values into the SOPS files himself. Production, billing and backup
   values go where the engineer's identity cannot read them
   (https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/,
   /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:63).
6. **Privacy settings.** Check the data-privacy toggle (30 days versus 5 years), set `DISABLE_FEEDBACK_COMMAND=1`,
   and set a low `cleanupPeriodDays` (https://code.claude.com/docs/en/data-usage,
   https://code.claude.com/docs/en/claude-directory).
7. **Verification.** The engineer runs the verification table through broker jobs and reports only pass or fail
   per credential.

**2. The approval design.** Use the T0/T1/T2 tiers from Q6:
- T1 items go in a numbered digest with defaults and `all y`.
- T2 items get their own message, a typed confirmation and no timeout-default.
- Every ask and answer goes into a committed JSONL audit file, and deterministic code parses the replies.
- The supervisor's plain Telegram bot carries the digest (https://core.telegram.org/bots/api).
- The Channels relay carries live tool prompts during the day
  (https://code.claude.com/docs/en/channels-reference).
- Remote Control is the phone view (https://code.claude.com/docs/en/remote-control).
- Login expiry goes into the digest as a re-login item
  (/home/user/Autonomy-Research/research/findings/engineer-browser.md:663).

**3. The permission posture.**
- The supervisor runs `claude -p` per task with `--permission-mode auto --permission-prompts none`, plus
  `--max-turns` and `--max-budget-usd` (https://code.claude.com/docs/en/permission-modes,
  https://code.claude.com/docs/en/headless).
- Bash sandbox on, with `allowUnsandboxedCommands: false` (https://code.claude.com/docs/en/sandboxing).
- Managed deny rules and `disableBypassPermissionsMode` (https://code.claude.com/docs/en/permissions).
- A fail-closed PreToolUse guard and the kill-switch file
  (https://github.com/anthropics/cwc-long-running-agents claude-code-config/.claude/hooks/kill-switch.sh:3
  (commit ad107a9)).
- OS limits and egress allowlist, and server-side branch protection.
- The supervisor stops the night after N denials of one kind.
- John reviews the denials each morning.

**Alternatives.**
- **Keys:** Playwright on dashboards for GitHub PAT pre-fill URLs; the GitHub App manifest flow
  (https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest).
- **Secrets:**
  - a 1Password service account with an agent-only vault, if John has 1Password
    (https://www.1password.dev/service-accounts/rate-limits);
  - Infisical Agent Vault or Claude cloud network secrets for HTTPS APIs (https://infisical.com/llms-full.txt);
  - systemd-creds for long-running services
    (https://www.ssdnodes.com/learn/self-hosted-secrets-manager).
- **Approvals:** n8n send-and-wait only if n8n already runs (claims unverified); a Slack app; Twilio SMS as a
  dead-man alert (https://www.twilio.com/en-us/sms/pricing/us).
- **Permissions:**
  - `dontAsk` with an exact allowlist;
  - `bypassPermissions` in a container with the firewall (https://code.claude.com/docs/en/permission-modes,
    https://code.claude.com/docs/en/devcontainer);
  - Docker Sandboxes (needs KVM);
  - sandbox-runtime, which is beta (https://code.claude.com/docs/en/sandbox-environments);
  - cloud sessions and Routines for jobs that touch only GitHub (engineer-runtime.md).

**Rejected, with reasons.**
- **Accounts created by bots.** GitHub bans them
  (https://docs.github.com/en/site-policy/github-terms/github-terms-of-service).
- **Scraping dashboards to mint keys.** Worker judgement.
- **OpenBao or Vault.** It seals on restart, and the Shamir split protects nothing for one person
  (https://www.ssdnodes.com/learn/self-hosted-secrets-manager).
- **Self-hosted Infisical.** Rotation and the audit log are on Pro (https://infisical.com/pricing). Worker
  inference: Postgres and Redis for one user.
- **Doppler.** 3-day logs on Free (https://www.doppler.com/pricing).
- **Bitwarden Secrets Manager as primary.** It has no strength here
  (https://bitwarden.com/help/secrets-manager-plans/).
- **`pass`.** An unlocked gpg printed a PAT (https://github.com/anthropics/claude-code/issues/71654).
- **A plain `.env` or direnv** (https://github.com/anthropics/claude-code/issues/59094,
  https://github.com/anthropics/claude-code/issues/94082).
- **Relying on CLAUDE.md or memory rules** (#59094).
- **HumanLayer.** Deprecated (https://github.com/humanlayer/humanlayer).
- **LangGraph interrupts.** A second runtime with node replay
  (https://docs.langchain.com/oss/python/langgraph/interrupts).
- **OpenClaw as channel host.** Per the registry and engineer-runtime.md.
- **SMS as the primary channel.** Weaker identity and registration overhead
  (https://www.twilio.com/en-us/sms/pricing/us).
- **`bypassPermissions` directly on the host VM under John's account**
  (https://code.claude.com/docs/en/permission-modes).
- **The Bash sandbox alone** (https://code.claude.com/docs/en/sandbox-environments).
- **Prose boundaries or deny rules alone** (https://code.claude.com/docs/en/permissions).
- **The Ralph loop as shipped.** Per the registry.

**Spike list (must be tried before building).**
1. Mint a Cloudflare child token with narrow permissions and a TTL.
2. Create a Slack app from a manifest, then install it.
3. Create a Google service-account key in a throwaway project (`gcloud iam service-accounts keys create`).
4. Create a Telegram managed bot.
5. Check the Withings+ requirement on John's account.
6. Look for n8n and Clay key-create endpoints.
7. Does `updatedToolOutput` change what is written to the transcript JSONL, and does it run on the harness
   "file changed" notice?
8. Does the sudoers broker boundary hold against `sudo -l`, `ps` and `/proc/*/environ` reads by `engineer`?
9. Test deny rules against `cat`, `python -c`, `grep -r` and equivalents on the VM.
10. After a full run, grep `~/.claude/projects/` for a canary secret.
11. Is Infisical Agent Vault's preview viable?
12. Does the Channels relay work under a headless tmux session with the Telegram plugin?
13. Can one bot be shared between the plugin and the supervisor?
14. Build and test the parser for `1 y 2 n`.
15. Measure John's reply latency to set the timeouts.
16. What does a stalled prompt cost overnight?
17. Run auto + `--permission-prompts none` on a task that triggers blocks: record the exit code,
    `permission_denials` and the behaviour past 20 blocks.
18. Test rewording bypasses (`git -C . push`) against deny rules, the hook and the server rule.
19. Run the sandbox with `allowUnsandboxedCommands: false` on Ubuntu 24.04; confirm `failIfUnavailable`.
20. Does a hook fail open on timeout, or block with `onFailure: "block"`?
21. Can a non-root user read the managed-settings file?
22. What does the classifier cost per action, in tokens and latency?
23. The Max-login versus API-key decision (Q2). Re-read Anthropic's support article on Agent SDK billing.

## Evidence

Key-creation note (research/runs/engineer-human-loop/notes/key-creation.md):

- **E1.** https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/ — opened 2026-10-16, curl. Claim: Cloudflare: a token with the right permission creates further tokens via API; the user-owned case needs a special template, account-owned needs Account API Tokens Edit. First human step is the dashboard token. Quote: "To create account-owned API tokens, create a token with Account > Account API Tokens > Edit. To create user-owned API tokens, use the Create additional tokens template."
- **E2.** https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ — opened 2026-10-16, curl. Claim: Cloudflare: the first token is made in the dashboard. Quote: "From the Cloudflare dashboard, go to My Profile > API Tokens for user tokens. For Account Tokens, go to Manage Account > API Tokens."
- **E3.** https://developers.cloudflare.com/workers/wrangler/commands/general/ — opened 2026-10-16, curl. Claim: Cloudflare: wrangler has a login OAuth command with remote-machine, container and no-callback-server variants. Quote: "Use wrangler login on a remote machine Use wrangler login in a container Use wrangler login without a local callback server"
- **E4.** https://vercel.com/docs/rest-api/reference/endpoints/authentication/create-an-auth-token — opened 2026-10-16, curl. Claim: Vercel: a token can mint tokens by REST, with an optional expiry and project. Quote: "Creates and returns a new authentication token for the currently authenticated User. The bearerToken property is only provided once, in the response body"
- **E5.** https://vercel.com/docs/cli/tokens — opened 2026-10-16, curl. Claim: Vercel CLI: `vercel tokens` creates, lists and revokes tokens, optionally project-scoped; `vercel signup` creates an account from the CLI. Quote: "Tokens authenticate Vercel CLI commands and Vercel REST API requests on your behalf. They are scoped to your user account, and optionally to a single project."
- **E6.** https://vercel.com/docs/cli/signup — opened 2026-10-16, curl. Claim: Vercel signup via CLI exists. Quote: "The vercel signup command allows you to create a new Vercel account through Vercel CLI."
- **E7.** https://supabase.com/docs/reference/api/introduction — opened 2026-10-16, curl. Claim: Supabase: Management API needs an access token (PAT or OAuth2); PATs are generated on the account page by hand. Quote: "To generate or manage your personal access tokens, visit your account page."
- **E8.** https://supabase.com/docs/reference/cli/supabase-login — opened 2026-10-16, curl. Claim: Supabase CLI login stores a PAT; CI skips login with an env var. Quote: "you may skip login by specifying the SUPABASE_ACCESS_TOKEN environment variable in other commands."
- **E9.** https://supabase.com/docs/guides/api/api-keys — opened 2026-10-16, curl. Claim: Supabase: project API keys (publishable/secret) are created in the Dashboard if absent; the docs list the Management API only as a way to read them. Quote: "If your project has no publishable or secret key yet, create them first in the Settings > API Keys section of the Dashboard."
- **E10.** https://docs.slack.dev/authentication/tokens — opened 2026-10-16, curl. Claim: Slack: config tokens are generated by hand on the app settings page; they drive the manifest API. Quote: "These tokens are created on the app settings page below the list of apps. Under Your App Configuration Tokens, click Generate Token to create one."
- **E11.** https://docs.slack.dev/reference/methods/apps.manifest.create — opened 2026-10-16, curl. Claim: Slack: apps.manifest.create returns client credentials and an authorize URL, not a bot token, so install is a separate OAuth step. Quote: "\"credentials\" : { \"client_id\" : \"...\" , \"client_secret\" : \"...\" , \"verification_token\" : \"...\" , \"signing_secret\" : \"...\" } , \"oauth_authorize_url\""
- **E12.** https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest — opened 2026-10-16, curl. Claim: GitHub App manifest flow registers an app but redirects a person through GitHub. Quote: "You redirect people to GitHub to register a new GitHub App."
- **E13.** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens — opened 2026-10-16, curl. Claim: GitHub PATs: the docs describe creating them in settings, plus URL-parameter pre-fill, but no creation endpoint. Quote: "Pre-filling fine-grained personal access token details using URL parameters"
- **E14.** https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps — opened 2026-10-16, curl. Claim: GitHub OAuth apps support a device flow for headless tools; `gh auth login` uses a device code. Quote: "device flow : Used for headless apps, such as CLI tools."
- **E15.** https://core.telegram.org/bots/tutorial — opened 2026-10-16, curl. Claim: Telegram: first bot comes from a chat with @BotFather. Quote: "Obtaining a token is as simple as contacting @BotFather , issuing the /newbot command and following the steps until you're given a new token."
- **E16.** https://core.telegram.org/bots/api — opened 2026-10-16, curl. Claim: Telegram Bot API now has managed bots whose token a bot can fetch. Quote: "Information about the bot. The bot's token can be fetched using the method getManagedBotToken ."
- **E17.** https://cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts — opened 2026-10-16, curl. Claim: Google: service-account key creation can be blocked by org policy. Quote: "When this constraint is set, user-managed credentials cannot be created for service accounts in projects affected by the constraint."
- **E18.** https://support.google.com/cloud/answer/15549257 — opened 2026-10-16, curl. Claim: Google: OAuth clients are created in the console (Google Auth Platform Clients page); registration of the app comes first. Quote: "You will be prompted to register your application to use Google Auth if you are yet to do so. This is required before creating a client."
- **E19.** https://developers.google.com/identity/protocols/oauth2/limited-input-device — opened 2026-10-16, curl. Claim: Google device flow supports only limited scopes. Quote: "This OAuth 2.0 flow supports a limited set of scopes ."
- **E20.** https://cloud.google.com/sdk/gcloud/reference/auth/login — opened 2026-10-16, curl. Claim: gcloud has a no-browser login. Quote: "command line, use the --no-browser flag."
- **E21.** https://docs.n8n.io/connect/n8n-api/authentication.md — opened 2026-10-16, curl. Claim: n8n: API keys are created in the UI; no creation endpoint is documented. Quote: "Go to **Settings** > **n8n API**. 3. Select **Create an API key**. 4. Choose a **Label** and set an **Expiration** time for the key."
- **E22.** https://docs.attio.com/rest-api/guides/authentication — opened 2026-10-16, curl. Claim: Attio: single-workspace key is generated in the Developer console; OAuth workspace-level token needs an admin. Quote: "Only workspace admins can grant a workspace-level token."
- **E23.** https://developers.outreach.io/api/oauth/ — opened 2026-10-16, curl. Claim: Outreach: an app must be created, development credentials are immediate, production after review. Quote: "Development credentials are provisioned immediately and are intended to be used during application development and testing."
- **E24.** https://developer.whoop.com/docs/developing/getting-started — opened 2026-10-16, curl. Claim: WHOOP: a dashboard app comes first. Quote: "To start developing with WHOOP, you first need to create an App in the WHOOP Developer Dashboard ."
- **E25.** https://developer.withings.com/developer-guide/v3/get-access/create-your-app — opened 2026-10-16, curl. Claim: Withings: app registered in Partner Hub; OAuth code flow. Quote: "Step 1 Create your application Register in the Partner Hub to get your client credentials."
- **E26.** https://platform.claude.com/docs/en/manage-claude/authentication — opened 2026-10-16, curl. Claim: Anthropic: API keys are generated in the Console; the Admin API list covers List, Retrieve and Update of keys, not create. Quote: "API keys are static secrets that you generate in the Claude Console and send on every request as a bearer token"
- **E27.** https://platform.claude.com/docs/en/api/organization/api_keys/list — opened 2026-10-16, curl. Claim: Anthropic Admin API: lists "List API Keys, Retrieve API Key (Admin API), Update API Key" under API Keys; also Service Accounts and WIF for non-interactive tokens. Quote: "API Keys   List API Keys  Retrieve API Key (Admin API)  Update API Key"
- **E28.** https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/ — opened 2026-10-16, curl. Claim: Cloudflare tokens take a TTL window, and a "roll tokens" page exists. Quote: "you can set the time at which a token becomes active with not_before and the time when it expires with expires_on ."
- **E29.** https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/ — opened 2026-10-16, curl. Claim: Cloudflare: safeguard the creator token. Quote: "Make sure you safeguard the new token because it can create tokens with access to any of a user's resources."
- **E30.** https://docs.slack.dev/reference/methods/tooling.tokens.rotate — opened 2026-10-16, curl. Claim: Slack config tokens expire in 12 hours and rotate by API with a single refresh token. Quote: "Each app configuration token will expire 12 hours after it has been generated."
- **E31.** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens — opened 2026-10-16, curl. Claim: GitHub PATs: automatic removal after a year unused, expiry strongly advised; infinite allowed unless policy blocks. Quote: "Infinite lifetimes are allowed but may be blocked by a maximum lifetime policy set by your organization or enterprise owner."
- **E32.** https://supabase.com/docs/reference/api/introduction — opened 2026-10-16, curl. Claim: Supabase: PATs have custom expiry and a scoped form. Quote: "A scoped PAT can only reach the organizations, projects, and permissions you choose when creating it."
- **E33.** https://docs.n8n.io/connect/n8n-api/authentication.md — opened 2026-10-16, curl. Claim: n8n: expiry set at creation; scopes only on Enterprise. Quote: "If you're on an Enterprise plan, choose the **Scopes** to give the key."
- **E34.** https://vercel.com/docs/rest-api/reference/endpoints/authentication/create-an-auth-token — opened 2026-10-16, curl. Claim: Vercel token body takes expiresAt and projectId. Quote: "\"name\" : \"Example Name\" , \"expiresAt\" : \"123\" , \"projectId\" : \"example_id\""
- **E35.** https://developers.outreach.io/api/oauth/ — opened 2026-10-16, curl. Claim: Outreach access tokens last 7200 s and dev grants are expired periodically. Quote: "\"expires_in\" : 7200"
- **E36.** https://developer.whoop.com/docs/developing/app-approval — opened 2026-10-16, curl. Claim: WHOOP new apps start in a sandbox tier of 10 members. Quote: "Every new app starts on the Sandbox tier, which allows up to 10 WHOOP members to connect."
- **E37.** https://developer.withings.com/developer-guide/v3/get-access/create-your-app — opened 2026-10-16, curl. Claim: Withings change dated 2026-10-12: new accounts need a membership for free-plan apps. Quote: "Withings+ becomes required on the Start for Free API plan from October 12, 2026."
- **E38.** https://cloud.google.com/resource-manager/docs/organization-policy/restricting-service-accounts — opened 2026-10-16, curl. Claim: Google: newer orgs enforce a default-service-account role-grant constraint by default (key-creation default not shown by this quote). (The page prints that note under the default-service-account role-grant constraint; confirm it also covers key creation before relying on it. See Gaps.) Quote: "Note : If your organization was created on or after May 3, 2024, this constraint is enforced by default."
- **E39.** https://platform.claude.com/docs/en/manage-claude/authentication — opened 2026-10-16, curl. Claim: Anthropic key types: personal, service account, legacy workspace. Quote: "When you create a key, you choose its type, which determines what the key can do, where it works, and when it stops working"
- **E40.** https://docs.github.com/en/site-policy/github-terms/github-terms-of-service — opened 2026-10-16, curl. Claim: GitHub: no bot-created accounts; machine accounts allowed if a human registers them. Quote: "You must be a human to create an Account. Accounts registered by \"bots\" or other automated methods are not permitted. We do permit machine accounts:"
- **E41.** https://vercel.com/legal/terms — opened 2026-10-16, curl. Claim: Vercel: authorising AI tools with credentials makes John responsible. Quote: "you authorize and agree to be legally bound by the actions taken on your behalf by those Third Party Tools."
- **E42.** https://code.claude.com/docs/en/legal-and-compliance — opened 2026-10-16, curl. Claim: Anthropic (Claude Code legal page): subscription OAuth is for ordinary native use; products built on the Agent SDK should use API keys; no routing via Max credentials for others. Quote: "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication through Claude Console"
- **E43.** https://www.anthropic.com/legal/consumer-terms — opened 2026-10-16, curl. Claim: Anthropic consumer terms: no sharing credentials. Quote: "You may not share your Account login information, Anthropic API key, or Account credentials with anyone else."
- **E44.** https://telegram.org/tos/bot-developers — opened 2026-10-16, curl. Claim: Telegram bot-developer terms: credentials may not be made public; no spam. Quote: "Your TPA must not harass or spam users with unsolicited messages;"
- **E45.** https://www.cloudflare.com/website-terms/ — opened 2026-10-16, curl. Claim: Cloudflare website terms only cover automated abuse-report tokens, not account signup. Quote: "If you intend to automate the process by which you submit abuse reports , you will need to request access to an abuse API token."
- **E46.** https://slack.com/terms-of-service/api — opened 2026-10-16, curl. Claim: Slack API terms restrict API data use by apps offered outside the org. Quote: "you may not: (A) use API Data to train a large language model; (B) bulk export Slack message and file data"
- **E47.** https://attio.com/legal/terms-and-conditions — opened 2026-10-16, curl. Claim: Attio customer agreement limits automated decisions about people. Quote: "Automated decision-making shall be used solely to support human decision-making"
- **E48.** https://supabase.com/terms — opened 2026-10-16, curl. Claim: Supabase terms hold the customer responsible for credential use. Quote: "the security and use of Customer's and its Authorized Users' access credentials"

Secrets note (research/runs/engineer-human-loop/notes/secrets.md):

- **E49.** https://www.1password.dev/service-accounts/ — opened 2026-10-16, Exa fetch. Claim: 1Password service accounts: up to 100 per account, vault-scoped, usage report available. Quote: "You can create up to 100 service accounts." and "you can see what items a service account accesses by creating a usage report."
- **E50.** https://www.1password.dev/service-accounts/rate-limits — opened 2026-10-16, Exa fetch. Claim: Service accounts are not limited to Business: the rate-limit table lists them for Individual, Families, Teams and Business. Quote: "1Password, 1Password Families, and 1Password Teams | Read | 1,000 | 1 hour | Per service account token"
- **E51.** https://www.1password.dev/service-accounts/get-started — opened 2026-10-16, Exa fetch. Claim: 1Password service account limits: cannot reach Personal/Private vault; permissions immutable after creation (rotate by creating a new account). Quote: "Service account permissions, vault access, and Environment access are immutable."
- **E52.** https://bitwarden.com/help/secrets-manager-plans/ — opened 2026-10-16, Exa fetch. Claim: Bitwarden Secrets Manager Free: 2 users, 3 projects, 3 machine accounts; Families plan holders create a separate Free organization. Quote: "Up to 2 users - Up to 3 projects - Up to 3 machine accounts"
- **E53.** https://bitwarden.com/help/secrets-manager-plans/ — opened 2026-10-16, Exa fetch. Claim: Bitwarden Teams Secrets Manager: event logs and 20 machine accounts, priced per user. Quote: "Up to 20 machine accounts included, with extra accounts billed per account"
- **E54.** https://infisical.com/pricing — opened 2026-10-16, Exa fetch. Claim: Infisical: free tier is 5 identities, 3 environments, no audit log retention; Secret Rotation and 30-day audit log start at Pro $20/identity/month. Quote: "Free $ 0 forever ... 5 identities, unlimited projects"; "Pro ... $ 2 0 /identity/month ... Secret Rotation ... 30-day Audit log retention"
- **E55.** https://infisical.com/llms-full.txt — opened 2026-10-16, Exa fetch. Claim: Infisical core is MIT and self-hostable; some features paid. Quote: "The core platform is MIT licensed and fully self-hostable. Some features (SSO enforcement, LDAP, SCIM, KMIP, HSM, audit streaming) are paid."
- **E56.** https://infisical.com/llms-full.txt — opened 2026-10-16. Claim: Infisical `infisical run -- <cmd>` injects into a process without writing to disk; machine identity via `INFISICAL_TOKEN`. Quote: "`infisical run -- ` injects secrets into a process without writing them to disk."
- **E57.** https://www.doppler.com/pricing — opened 2026-10-16, Exa fetch. Claim: Doppler Developer plan: free for 3 users, 3 days of activity logs; automatic rotation and 90-day logs on Team at $21/user/month. Quote: "Free for 3 users $8/mo per additional user"; "3 days of activity logs"; "Automatic secret rotation"
- **E58.** https://www.ssdnodes.com/learn/self-hosted-secrets-manager — opened 2026-10-16, Exa fetch. Claim: Single-VPS comparison (Oct 2026): OpenBao is MPL 2.0 and seals on every restart; file-based options need no extra service. Quote: "A restarted server is a sealed server."
- **E59.** https://www.ssdnodes.com/learn/self-hosted-secrets-manager — opened 2026-10-16, Exa fetch. Claim: Same source on single-box choice. Quote: "On a one person VPS the Shamir split protects nothing, because all five shares end up in the same password manager belonging to the same person."
- **E60.** https://www.ssdnodes.com/learn/self-hosted-secrets-manager — opened 2026-10-16, Exa fetch. Claim: Same source: SOPS+age and systemd-creds details (Ubuntu 24.04 ships systemd 255; no TPM2 on most VPS so host key only; back up `/var/lib/systemd/credential.secret`). Quote: "Ubuntu 24.04 ships systemd 255, so this needs no install."
- **E61.** https://code.claude.com/docs/en/permissions — opened 2026-10-16, WebFetch (saved output). Claim: Read/Edit deny rules apply to built-in file tools and recognised Bash file commands, not to scripts or `grep -r`; sandbox gives OS enforcement. Quote: "They don't apply to a command that reads files without naming them, such as `grep -r pattern .` run from the directory that holds the file"
- **E62.** https://code.claude.com/docs/en/permissions — opened 2026-10-16, WebFetch. Claim: Same page: Read rules are best-effort for Grep/Glob; `.claudeignore` has no effect. Quote: "Claude makes a best-effort attempt to apply `Read` rules to all built-in tools that read files like Grep and Glob"
- **E63.** https://code.claude.com/docs/en/permissions — opened 2026-10-16, WebFetch. Claim: Same page: `.claudeignore`. Quote: "If your project has a `.claudeignore` file, it has no effect, so move its entries into `Read` deny rules."
- **E64.** https://code.claude.com/docs/en/settings — opened 2026-10-16, WebFetch. Claim: Settings page gives a paste-ready deny example. Quote: "Read(./.env)" and "Read(./.env.*)" under `"deny"`.
- **E65.** https://code.claude.com/docs/en/hooks — opened 2026-10-16, WebFetch. Claim: PreToolUse hooks: exit 2 blocks even with JSON; timeouts do not block unless `onFailure: "block"`. Quote: "To block the call when a `command` or `http` hook times out, set `onFailure: \"block\"`."
- **E66.** https://code.claude.com/docs/en/hooks — opened 2026-10-16, WebFetch. Claim: PostToolUse can replace tool output for all tools before Claude sees it, but telemetry captures the original. Quote: "`updatedToolOutput` only changes what Claude sees. The tool has already run by the time the hook fires"
- **E67.** https://code.claude.com/docs/en/hooks — opened 2026-10-16, WebFetch. Claim: Same page, telemetry caveat. Quote: "Telemetry such as OpenTelemetry tool spans and analytics events also captures the original output before the hook runs."
- **E68.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Anthropic's own cloud sessions keep credentials out of the VM via a proxy. Quote: "GitHub credentials are stored encrypted on Anthropic's servers and never enter the VM."
- **E69.** https://github.com/anthropics/claude-code/issues/59094 — opened 2026-10-16, Exa fetch. Claim: Incident 2026-05-14: agent ran `Get-Content ...\.env | Select-String` despite a memory rule forbidding it; four live brokerage keys revoked. Quote: "Claude Code agents can read secret-bearing files (`.env`, `*-creds*`, `*.pem`, etc.) via `Read`, `Get-Content`, `cat`, etc."
- **E70.** https://github.com/anthropics/claude-code/issues/71654 — opened 2026-10-16, Exa fetch. Claim: Incident 2026-06-26: `pass show ... | head -8` printed a live GitHub PAT because gpg was unlocked; a urllib exception serialised an Authorization header. Quote: "agent ran pass show GH-YOLO/api-key 2>&1 | head -8 expecting a decrypt error, but gpg was unlocked so the live ghp_… printed to stdout"
- **E71.** https://github.com/anthropics/claude-code/issues/94082 — opened 2026-10-16, Exa fetch. Claim: Incident 2026-09-14: harness "file changed on disk" notice dumped a full secrets file, bypassing a PreToolUse secret-file hook; ten production credentials rotated. Quote: "can be silently bypassed by a **different, unguarded surface**: the harness's own \"this file changed on disk since you last read it\" notification."
- **E72.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Incident 2026-09-30 (blog 2026-10-05): `cat .env` where `.env` was a 1Password-backed named pipe; 31 secrets in the transcript. Quote: "On September 30th a Claude Code agent session ran cat .env. The file held every credential I use to work on CertWatch, my certificate monitoring product, and all 31 of them landed in the session transcript."
- **E73.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Same post: first `op run` wrapper would have leaked the service-account token. Quote: "`op run` masks secret values it injects, but it doesn’t mask its own credentials."
- **E74.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Same post: working design is two vaults plus an allowlist wrapper that strips the token. Quote: "A “master” vault holds production, billing, backup, and CI, and the agent’s service account can’t read it at all."
- **E75.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Same post, wrapper rule. Quote: "It only runs commands from an allowlist, and never a shell, `env`, `printenv`, `echo`, or a path."
- **E76.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Same post, honest limit. Quote: "It can’t stop an agent that is deliberately looking for secrets"
- **E77.** /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:61 — read 2026-10-16. Claim: Earlier operations note found the stdin pattern: `op read ... | wrangler secret put NAME`. Quote: "The value passes through the shell pipe, not through a tool result."
- **E78.** /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:61 — read 2026-10-16. Claim: Same note, `op run` caveat. Quote: "Caveat: with `op run` the value sits in the child process environment."
- **E79.** https://infisical.com/llms-full.txt — opened 2026-10-16, Exa fetch. Claim: Infisical Agent Vault (preview): forward proxy attaches the credential outside the agent; self-hostable. Quote: "A prompt-injected agent has nothing to leak, because the credential was never in its environment, files, or context."
- **E80.** https://infisical.com/llms-full.txt — opened 2026-10-16, Exa fetch. Claim: Same source on status. Quote: "It is currently in preview, so features and pricing may change."
- **E81.** https://code.claude.com/docs/en/claude-directory — opened 2026-10-16, WebFetch (saved). Claim: Local transcripts plaintext, include tool results. Quote: "These files are plaintext. Anything that passes through a tool is written to a transcript on disk: file contents, command output, pasted text."
- **E82.** https://code.claude.com/docs/en/claude-directory — opened 2026-10-16, WebFetch. Claim: Location and content. Quote: "projects/<project>/<session>.jsonl | Full conversation transcript: every message, tool call, and tool result"
- **E83.** https://code.claude.com/docs/en/claude-directory — opened 2026-10-16, WebFetch. Claim: Large tool outputs spill to separate files. Quote: "projects/<project>/<session>/tool-results/ | Large tool outputs spilled to separate files"
- **E84.** https://code.claude.com/docs/en/claude-directory — opened 2026-10-16, WebFetch. Claim: Default cleanup 30 days, minimum 1. Quote: "The default is 30 days and the minimum is 1; setting `0` fails with a validation error."
- **E85.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Consumer retention 5 years or 30 days; commercial 30 days. Quote: "Users who don't allow data use for model improvement: 30-day retention period"
- **E86.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Same page. Quote: "Users who allow data use for model improvement: 5-year retention period to support model development and safety improvements"
- **E87.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Cloud sessions store the transcript; deletable. Quote: "Anthropic stores the session transcript so you can return to the session later."
- **E88.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Same page on deletion. Quote: "Deleting a session permanently removes the session's event data."
- **E89.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Transcripts shared with `/feedback` retained 5 years. Quote: "Transcripts shared via `/feedback`, or via `/bug` and `/share`, which report through the same path, are retained for 5 years."
- **E90.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: Survey transcript upload redacts only known patterns. Quote: "Known API key and token patterns are redacted before upload. Source code, file contents, and other conversation content are uploaded as-is."
- **E91.** https://code.claude.com/docs/en/data-usage — opened 2026-10-16, WebFetch. Claim: `/feedback` can be disabled. Quote: "To opt out, set the `DISABLE_FEEDBACK_COMMAND` environment variable to `1`."
- **E92.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Rule from the field: a value that reached a transcript is compromised. Quote: "Once a value reaches a transcript, a log, a screenshot, or a chat message, it is compromised."
- **E93.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16, Exa fetch. Claim: Rotation of the leaked set took about a day, mostly verification. Quote: "The rotation took about a day. Most of that was verification, and I would do it the same way again."
- **E94.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16. Claim: Two-vault split limits blast radius. Quote: "If the agent leaks something, I rotate a low-risk credential instead of the production database."
- **E95.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16. Claim: Inventory of every credential, consumers and what else changes. Quote: "Keep an inventory of every credential, where it lives, and what else changes when you rotate it."
- **E96.** https://zerofaultlabs.io/i-printed-31-secrets-into-an-ai-transcript/ — opened 2026-10-16. Claim: Rotation touches every paired copy. Quote: "Every secret had a consumer somewhere: a Fly app secret, a GitHub Actions secret, or a Terraform Cloud variable."
- **E97.** https://www.1password.dev/service-accounts/get-started — opened 2026-10-16, Exa fetch. Claim: 1Password service accounts cannot be edited; revoke and recreate. Quote: "Service accounts can’t be modified after they’re created. If you need to make changes, revoke the service account and create a new one."
- **E98.** /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:63 — read 2026-10-16. Claim: Prior note: John seeds secrets the model must never see; the engineer references them. Quote: "John seeds them once in the vault; the engineer only references them."
- **E99.** /home/user/Autonomy-Research/research/runs/engineer-deploy/notes/operations.md:50 — read 2026-10-16. Claim: Prior note: GitHub OIDC replaces stored cloud keys. Quote: "request a short-lived access token directly from the cloud provider."

Approvals note (research/runs/engineer-human-loop/notes/approvals.md):

- **E100.** https://www.anthropic.com/engineering/how-we-contain-claude — opened 2026-10-16, WebFetch. Claim: Anthropic telemetry: users approved roughly 93% of prompts; more approvals means less attention per approval (2026-05-25 post). Quote: "Our telemetry showed users approved roughly 93% of permission prompts."
- **E101.** https://www.anthropic.com/engineering/how-we-contain-claude — opened 2026-10-16, WebFetch. Claim: Sandboxing, a boundary instead of per-action prompts, cut prompts 84%. Quote: "an 84% reduction in permission prompts"
- **E102.** https://www.anthropic.com/engineering/how-we-contain-claude — opened 2026-10-16, WebFetch. Claim: Experienced users auto-approve about twice as often as new users (they supervise only when it goes off track). Quote: "experienced users auto-approve roughly twice as often as new users"
- **E103.** https://www.anthropic.com/engineering/claude-code-auto-mode — opened 2026-10-16, WebFetch. Claim: Auto mode (classifier on Sonnet 4.6) exists to reduce fatigue: Anthropic defines approval fatigue and publishes 0.4% false positive and 17% miss on real overeager actions for the full pipeline; low-risk actions skip the classifier. Quote: "approval fatigue, where people stop paying close attention to what they're approving"
- **E104.** https://www.anthropic.com/engineering/how-we-contain-claude — opened 2026-10-16, WebFetch. Claim: Auto mode miss rate stated as a footnote caveat: one layer inside a sandbox, not a substitute. Quote: "~17% of overeager actions get through"
- **E105.** https://docs.renovatebot.com/key-concepts/dashboard/ — opened 2026-10-16, WebFetch. Claim: Renovate dashboard: approval for major updates via a checkbox list; the docs prefer it to disabling updates because pending work stays visible. Quote: "you can fully see what's pending on the dashboard, instead of updates being totally invisible."
- **E106.** https://docs.renovatebot.com/key-concepts/dashboard/ — opened 2026-10-16, WebFetch. Claim: Renovate: security fixes bypass the approval queue. Quote: "But vulnerability remediation PRs will still get created immediately without requiring approval."
- **E107.** https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file — opened 2026-10-16, WebFetch. Claim: Dependabot grouping and cap: related updates combine into one PR, and a default cap of five open PRs stops pile-up. Quote: "All updates for dependencies that match a rule are combined in a single pull request."
- **E108.** https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file — opened 2026-10-16, WebFetch. Claim: Dependabot cap. Quote: "no further pull requests are raised until some of those open requests are merged or closed."
- **E109.** https://code.claude.com/docs/en/remote-control — opened 2026-10-16, WebFetch (saved page, grep). Claim: Claude Code's remote prompts have no timeout: permission prompts stay open until answered; other forwarded dialogs expire after five minutes to a no-action default. Quote: "Claude Code keeps permission prompts and `AskUserQuestion` questions open until you answer them."
- **E110.** /home/user/Autonomy-Research/research/runs/engineer-protocol/notes/observability.md:87 — read 2026-10-16. Claim: Existing protocol design already has the shape: numbered lines with recommended default and reply token, pushed in one Telegram message at most 4096 characters. Quote: "Approvals needed: one numbered line per decision request, each with a recommended default and the reply token (`1 yes`)"
- **E111.** https://code.claude.com/docs/en/channels-reference — opened 2026-10-16, WebFetch. Claim: Channels permission relay: both terminal and phone stay live, first answer wins; request ID is five letters; reply must match `yes <id>`; wrong ID dropped silently. Quote: "Both stay live: you can answer in the terminal or on your phone, and Claude Code applies whichever answer arrives first and closes the other."
- **E112.** https://code.claude.com/docs/en/channels-reference — opened 2026-10-16, WebFetch. Claim: Relay covers tool-use only, not trust or MCP consent dialogs. Quote: "Project trust and MCP server consent dialogs don't relay; those only appear in the local terminal."
- **E113.** https://code.claude.com/docs/en/channels — opened 2026-10-16, WebFetch. Claim: Sender allowlist and spoofing: allowlist gates relay too; pairing bootstraps it. Quote: "Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."
- **E114.** https://code.claude.com/docs/en/channels — opened 2026-10-16, WebFetch. Claim: Channels need a running local session and are research preview; Telegram plugin polls, no URL to expose. Quote: "Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal."
- **E115.** https://code.claude.com/docs/en/channels — opened 2026-10-16, WebFetch. Claim: Channels in `-p` mode disable interactive tools. Quote: "tools that need terminal input, such as multiple-choice questions and plan mode approval, are disabled so the session never stalls waiting for input."
- **E116.** https://code.claude.com/docs/en/remote-control — opened 2026-10-16, WebFetch (saved page). Claim: Remote Control push for permission prompts is a setting; server mode gives up after roughly 10 minutes offline. Quote: "Claude Code gives up after roughly 10 minutes and the `claude remote-control` process exits."
- **E117.** https://code.claude.com/docs/en/remote-control — opened 2026-10-16, WebFetch. Claim: Remote Control push setting. Quote: "enable **Push when actions required** for permission prompts and questions"
- **E118.** https://core.telegram.org/bots/api — opened 2026-10-16, WebFetch (first 100k of 582k chars). Claim: Telegram Bot API: long polling and webhook secret token exist; sender is the `from` field. Quote: "A secret token to be sent in a header “X-Telegram-Bot-Api-Secret-Token” in every webhook request"
- **E119.** https://docs.langchain.com/oss/python/langgraph/interrupts — opened 2026-10-16, WebFetch. Claim: LangGraph interrupts need a checkpointer, resume on the same thread id, and re-run the node from its start on resume. Quote: "The node restarts from the beginning of the node where the interrupt was called when resumed"
- **E120.** https://github.com/humanlayer/humanlayer — opened 2026-10-16, WebFetch. Claim: HumanLayer repo is deprecated. Quote: "the code here is pretty much all deprecated."
- **E121.** https://www.twilio.com/en-us/sms/pricing/us — opened 2026-10-16, WebFetch. Claim: Twilio US SMS: $0.0083 per segment plus carrier fees, long code $1.15/month, A2P 10DLC registration required. Quote: "$0.0083 per 160-character segment across long codes, toll-free numbers, and short codes."
- **E122.** https://www.twilio.com/en-us/sms/pricing/us — opened 2026-10-16, WebFetch. Claim: Twilio registration. Quote: "US A2P 10DLC are subject to registration"
- **E123.** https://code.claude.com/docs/en/channels — opened 2026-10-16, WebFetch. Claim: both unattended sessions stall at a prompt until answered. Quote: "If Claude hits a permission prompt while you're away from the terminal, the session pauses until you respond."

Permissions note (research/runs/engineer-human-loop/notes/permissions.md). All docs pages were opened 2026-10-16 with WebFetch:

- **E124.** https://code.claude.com/docs/en/permission-modes. Claim: Mode table: `dontAsk` denies anything that would prompt, aimed at CI; `bypassPermissions` is for isolated containers and VMs only. Quote: "Locked-down CI and scripts" / "Isolated containers and VMs only"
- **E125.** https://code.claude.com/docs/en/permission-modes. Claim: Deny rules hold in every mode including bypass. Quote: "Deny rules block in every mode, including `bypassPermissions`."
- **E126.** https://code.claude.com/docs/en/permission-modes. Claim: Auto mode in `-p`: thresholds 3 in a row / 20 total are fixed; with no prompt to fall back to, the action is not run and the run continues. Quote: "When repeated blocks reach a threshold, the action doesn't run and Claude keeps working. Claude Code doesn't stop the run."
- **E127.** https://code.claude.com/docs/en/permission-modes. Claim: The block counters are not configurable. Quote: "The thresholds of 3 blocks in a row and 20 blocks total are not configurable."
- **E128.** https://code.claude.com/docs/en/permission-modes. Claim: Anthropic's own caveat on auto mode. Quote: "Auto mode reduces permission prompts but does not guarantee safety."
- **E129.** https://code.claude.com/docs/en/headless. Claim: `--permission-prompts none` (v2.1.259+) denies anything that would prompt and tells Claude not to retry, so nothing waits on a human; denials are listed in `permission_denials` in stream-json. Quote: "Anything that would prompt is denied unless a `PermissionRequest` hook allows it, Claude is told that nobody can approve the request and not to retry it"
- **E130.** https://code.claude.com/docs/en/headless. Claim: In `-p` a bare `Bash` allow entry is dropped in auto mode. Quote: "Claude Code drops a bare `Bash` entry as a broad allow rule and auto mode evaluates each command instead."
- **E131.** https://code.claude.com/docs/en/headless. Claim: A `-p` run with nothing set takes the built-in start mode, which can be auto, so pass the mode explicitly. Quote: "A run where nothing sets a permission mode takes the built-in starting permission mode, which can be `auto`, so pass the one you want"
- **E132.** https://code.claude.com/docs/en/permission-modes. Claim: `auto` or `bypassPermissions` set in project `.claude/settings.json` or `settings.local.json` is ignored; use the CLI flag or user/managed settings. Quote: "If you set `\"bypassPermissions\"` in those two files, it doesn't take effect either, and the session starts in Manual mode."
- **E133.** https://code.claude.com/docs/en/permission-modes. Claim: Bypass refuses to run as root; Anthropic's unattended recipe requires a container, VM or sandbox runtime and a non-root user. Quote: "Required: a container, VM, or the sandbox runtime; on Linux and macOS, run it as a non-root user"
- **E134.** https://code.claude.com/docs/en/permission-modes. Claim: Bypass warning. Quote: "`bypassPermissions` offers no protection against prompt injection or unintended actions."
- **E135.** https://code.claude.com/docs/en/permission-modes. Claim: In bypass `-p`, the few things that still prompt are denied; critical-path `rm` prompts time out after 2 minutes and are denied so the session keeps going. Quote: "Claude Code denies the command and tells Claude what to do instead, so an unattended session keeps working."
- **E136.** https://code.claude.com/docs/en/permission-modes. Claim: Classifier blocks by default include force-push-type and exfil actions, pushing to a third-party repo, `git remote set-url`, and launching agent loops without a sandbox. Quote: "Changing where pushes go with `git remote set-url` or `git remote add`, unless you named the new remote"
- **E137.** https://code.claude.com/docs/en/permission-modes. Claim: Prose boundaries ("don't push") are read by the classifier but can be lost on compaction; use deny rules for hard guarantees. Quote: "a boundary can be lost if context compaction removes the message that stated it. For a hard guarantee, add a deny rule instead."
- **E138.** https://code.claude.com/docs/en/permission-modes. Claim: Auto mode needs a supported model (Opus 4.6+, Sonnet 4.6+, Haiku 5.5 on the Anthropic API). Quote: "Claude Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5"
- **E139.** https://code.claude.com/docs/en/devcontainer. Claim: Dev-container page endorses bypass for unattended work only with non-root plus egress limits. Quote: "Pair this flag with the network egress restrictions above to limit what a bypassed session can reach."
- **E140.** https://code.claude.com/docs/en/permissions. Claim: Order. Quote: "Rules are evaluated in order: deny, then ask, then allow. The first match in that order determines the outcome"
- **E141.** https://code.claude.com/docs/en/permissions. Claim: Deny cannot be carved out by allow. Quote: "An allow rule can't carve an exception out of a deny rule."
- **E142.** https://code.claude.com/docs/en/permissions. Claim: Documented bypass of `git push` deny. Quote: "`git push *` | `git push origin main` | `git -C . push origin main`, `git -c push.default=current push origin main`, `git 'push' origin main`" (table row)
- **E143.** https://code.claude.com/docs/en/permissions. Claim: Same for `curl`/`rm` via full path or `sh -c`. Quote: "`/usr/bin/curl https://example.com`, `sh -c 'curl https://example.com'`"
- **E144.** https://code.claude.com/docs/en/permissions. Claim: Anthropic's stance. Quote: "a deny or ask rule covers the invocation Claude usually produces and isn't a security boundary around the program."
- **E145.** https://code.claude.com/docs/en/permissions. Claim: Remedy named by the docs. Quote: "For filesystem and network enforcement that doesn't depend on the command text, use sandboxing."
- **E146.** https://code.claude.com/docs/en/permissions. Claim: Compound commands are split and deny applies to any subcommand, including nested ones. Quote: "Deny and ask rules apply when any subcommand matches them, including a command nested inside a subshell, a command substitution, or a control-flow body"
- **E147.** https://code.claude.com/docs/en/permissions. Claim: Wrapper list is fixed; `npx`, `docker exec` are not stripped. Quote: "Development environment runners such as `direnv exec`, `devbox run`, `mise exec`, `npx`, and `docker exec` are not in the list."
- **E148.** https://code.claude.com/docs/en/permissions. Claim: Managed settings beat everything including CLI flags. Quote: "no other level, including command line arguments, can override a managed permission rule."
- **E149.** https://code.claude.com/docs/en/permissions. Claim: Deny at any level is final. Quote: "a managed settings deny can't be overridden by `--allowedTools`"
- **E150.** https://code.claude.com/docs/en/permissions. Claim: `disableBypassPermissionsMode`/`disableAutoMode` work from any scope; most useful in managed. Quote: "These are most useful in managed settings where they can't be overridden."
- **E151.** https://code.claude.com/docs/en/devcontainer. Claim: Linux managed file path. Quote: "Claude Code reads `/etc/claude-code/managed-settings.json` on Linux and applies it at the highest precedence in the settings hierarchy"
- **E152.** https://code.claude.com/docs/en/permissions. Claim: A PreToolUse deny cannot be overridden by allow, and exit 2 beats allow rules. Quote: "A hook that exits with code 2 stops the tool call before permission rules are evaluated, so the block applies even when an allow rule would otherwise let the call proceed."
- **E153.** https://code.claude.com/docs/en/permissions. Claim: A hook "allow" cannot override deny/ask rules. Quote: "Claude Code evaluates deny and ask rules regardless of what a PreToolUse hook returns"
- **E154.** https://code.claude.com/docs/en/headless. Claim: A `-p` session runs the project's hooks and `.mcp.json` servers without any trust dialog unless `--bare`. Quote: "A `-p` session shows no workspace trust dialog and no per-server approval prompt."
- **E155.** https://code.claude.com/docs/en/hooks. Claim: Exit 2 and JSON decisions. Quote: "Exit code 0 with no output means the hook has no decision to report, so the tool call continues through the normal permission flow."
- **E156.** https://code.claude.com/docs/en/hooks. Claim: PermissionRequest cannot use exit 2. Quote: "Exit code 2 isn't honored for this event and the permission flow proceeds unchanged. Deny through the `decision` object instead."
- **E157.** https://code.claude.com/docs/en/hooks. Claim: MCP matchers need `.*`. Quote: "The `.*` is required: a matcher like `mcp__memory` or `mcp__brave-search` contains only exact-match characters"
- **E158.** https://code.claude.com/docs/en/hooks. Claim: Fail-open on timeout. Quote: "A timed-out `command`, `http`, or `mcp_tool` hook doesn't block the tool call"
- **E159.** https://code.claude.com/docs/en/hooks. Claim: `if` filter best-effort. Quote: "Because the `if` filter is best-effort, use the permission system rather than a hook to enforce a hard allow or deny."
- **E160.** https://code.claude.com/docs/en/hooks. Claim: Defaults: command hook timeout 600 s. Quote: "600s for `command`, `http`, and `mcp_tool`"
- **E161.** https://code.claude.com/docs/en/sandboxing. Claim: Hooks run with full access outside the Bash sandbox. Quote: "command hooks, local MCP servers, plugin monitors, LSP servers, and helper commands such as your status line command and `apiKeyHelper` run with your full access"
- **E162.** https://code.claude.com/docs/en/headless. Claim: `--permission-prompts none` still lets a PermissionRequest hook allow a call (route to a human, see human-loop facet). Quote: "Anything that would prompt is denied unless a `PermissionRequest` hook allows it"
- **E163.** https://github.com/anthropics/cwc-long-running-agents claude-code-config/.claude/hooks/kill-switch.sh:3 (commit ad107a9) — read 2026-10-16, git clone + sed. Claim: Anthropic's cwc example uses PreToolUse `*` kill-switch hook that blocks every call while a file exists. Quote: "# Halt every tool call while ./AGENT_STOP exists. `touch AGENT_STOP` to engage; `rm AGENT_STOP` to resume."
- **E164.** https://github.com/anthropics/cwc-long-running-agents README.md (commit ad107a9) — read 2026-10-16. Claim: That repo is explicitly an example, not maintained. Quote: "These are example ingredients, not a turnkey harness. Event demo; not maintained and not accepting contributions."
- **E165.** https://code.claude.com/docs/en/sandbox-environments. Claim: Not sufficient alone. Quote: "The sandboxed Bash tool on its own constrains only shell commands, so it is not sufficient for fully unattended runs in either mode."
- **E166.** https://code.claude.com/docs/en/sandboxing. Claim: Coverage. Quote: "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it."
- **E167.** https://code.claude.com/docs/en/sandboxing. Claim: Network allowlist starts empty. Quote: "Connections go through a proxy on your machine that checks each host against your allowed domains, which start empty."
- **E168.** https://code.claude.com/docs/en/sandboxing. Claim: Escape hatch: disable it for unattended runs. Quote: "You can disable the unsandboxed retry by setting `\"allowUnsandboxedCommands\": false`"
- **E169.** https://code.claude.com/docs/en/sandboxing. Claim: A matching allow rule also approves unsandboxed retry. Quote: "An allow rule that matches a command also approves an unsandboxed retry of it, so the command can run outside the sandbox with no prompt."
- **E170.** https://code.claude.com/docs/en/sandboxing. Claim: Fails open if bubblewrap missing. Quote: "By default, if the sandbox can't start because a dependency is missing or the platform is unsupported, Claude Code runs commands without sandboxing."
- **E171.** https://code.claude.com/docs/en/sandboxing. Claim: Ubuntu 24.04 needs an AppArmor profile for bwrap. Quote: "On Ubuntu 24.04 and later, the default AppArmor policy prevents bubblewrap from creating the user namespaces it needs for isolation."
- **E172.** https://code.claude.com/docs/en/sandboxing. Claim: Exfiltration residual risk. Quote: "Allowing broad domains such as `github.com` can create paths for data exfiltration."
- **E173.** https://code.claude.com/docs/en/sandboxing. Claim: Limits. Quote: "Sandboxing reduces risk but is not a complete isolation boundary."
- **E174.** https://code.claude.com/docs/en/sandbox-environments. Claim: Whole-process options. Quote: "Every other approach in the table puts the whole Claude Code process inside the isolation boundary, so file tools, MCP servers, and hooks are restricted too."
- **E175.** https://code.claude.com/docs/en/sandbox-environments. Claim: sandbox-runtime is beta. Quote: "The runtime is a beta research preview, and its configuration format may change as the package evolves."
- **E176.** https://code.claude.com/docs/en/devcontainer. Claim: Devcontainer caveat. Quote: "dev containers do not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in `~/.claude`."
- **E177.** https://code.claude.com/docs/en/devcontainer. Claim: Firewall is example only; needs NET_ADMIN. Quote: "It is provided as a working example rather than a maintained base image"
- **E178.** https://code.claude.com/docs/en/sandbox-environments. Claim: VM is strongest isolation. Quote: "A dedicated virtual machine provides the strongest separation, with its own kernel"
- **E179.** https://github.com/anthropics/cwc-long-running-agents README.md (commit ad107a9) — read 2026-10-16. Claim: cwc README: unattended loop is an outer script with capped sessions. Quote: "Cap session length and have an outer script start the next one (pick next feature, build, evaluate, reset)"
- **E180.** https://github.com/anthropics/cwc-long-running-agents claude-code-config/README.md:29 (commit ad107a9) — read 2026-10-16. Claim: cwc suggests pairing with ralph-loop or `claude -p "continue from PROGRESS.md"`. Quote: "For unattended multi-session runs, pair this config with the [`ralph-loop`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop) plugin"
- **E181.** https://github.com/anthropics/cwc-long-running-agents README.md (commit ad107a9) — read 2026-10-16. Claim: cwc README contains an agent-addressed instruction: "In your project, run `claude` and paste: Clone github.com/anthropics/cwc-long-running-agents into /tmp, copy its `claude-code-config/.claude/` directory..." — page contains instructions addressed to agents; not followed. Quote (kept as data): "In your project, run `claude` and paste: Clone github.com/anthropics/cwc-long-running-agents into /tmp, copy its `claude-code-config/.claude/` directory..."
- **E182.** https://kenimoto.dev/blog/autonomous-agent-24-hours-security-lessons/ — opened 2026-10-16, WebFetch (summary; verbatim quote from page: "sandboxing, not vibes"). Claim: Incident (24 h, skip-permissions): empty-variable `rm -rf`, a typosquatted skill POST, a leaked key; cost ~$387. Quote: "sandboxing, not vibes"
- **E183.** https://github.com/anthropics/claude-code/issues/99198 — opened 2026-10-16, WebFetch. Claim: Incident, issue #99198 (open 2026-10): sub-agent in `bypassPermissions` ran `rm -rf C:/Users/<USER~1>` via 8.3 short name; kept running ~45 min after stop; no maintainer reply; page also has a commenter promoting their own interception layer (unrelated promotion, not followed). Quote: "bypassPermissions"
- **E184.** https://code.claude.com/docs/en/permission-modes. Claim: Classifier now blocks the unresolved-variable `rm -rf "$VAR"` case that bit the 24 h run. Quote: "A recursive forced delete such as `rm -rf \"$VAR\"`"

Earlier findings files built on (read 2026-10-16 with Read; their own sources are cited inside them):

- **E185.** /home/user/Autonomy-Research/research/findings/engineer-runtime.md:408-413 — read 2026-10-16, Read. Claim: The runtime recommendation signs the VM in with John's Max subscription by `/login` and uses Channels plus Remote Control push for approvals. Quote: "background process with a watchdog, with Channels (Telegram allowlist) plus Remote Control push for approvals"
- **E186.** /home/user/Autonomy-Research/research/findings/engineer-runtime.md:439-441 — read 2026-10-16, Read. Claim: API-key or setup-token auth as primary loses Remote Control, connectors and Chrome; an API key is kept only as an overflow fallback (worker inference in that file). Quote: "`setup-token` or API-key auth as the VM's primary auth: loses Remote Control, connectors and Chrome"
- **E187.** /home/user/Autonomy-Research/research/findings/engineer-feasibility.md:301 — read 2026-10-16, Read. Claim: The setup list is one ordered page worked through in one sitting. Quote: "One ordered page from the integration cards, long waits first, worked through in one local sitting with Claude in Chrome, with secrets by name only and an agent verification table at the end"
- **E188.** /home/user/Autonomy-Research/research/findings/engineer-browser.md:661-663 — read 2026-10-16, Read. Claim: John logs in by hand; TOTP from a vault wrapper; a re-login item goes into the approval digest. Quote: "John logs in by hand, Google included" and "a re-login item in the approval digest"

## Implications for the autonomous engineer (and the researcher plugin)

- **Two artefacts for the setup page.** The frontloaded sitting needs two artefacts:
  - the ordered setup page from engineer-feasibility.md, extended with the Q1 table as a "parent credential"
    column and a "consent click" column;
  - a root-run `setup-root.sh` for the VM steps (managed settings, AppArmor profile, broker user, sudoers,
    egress rules).
  The engineer must never receive a value through chat. Its verification table checks each credential only
  through a broker job.
- **Requirement R14 (batched gated approvals)** maps to the T0/T1/T2 tiers. Suggested EARS wording:
  - "When an action is irreversible, spends money, deletes data, publishes, sends external mail or touches a
    secret, the engineer shall park the task and send one immediate hard-gate message that needs a typed
    confirmation, and shall not proceed on timeout."
  - "When a decision is reversible, the engineer shall queue it in the next digest with a default."
- **Requirement R15 (unattended runs)** maps to `claude -p` per task with auto mode and
  `--permission-prompts none`, managed settings and a supervisor that reads `permission_denials`. Suggested EARS
  wording: "When an unattended run records N denials of one kind, the supervisor shall stop the run and add the
  denials to the morning digest."
- **A secret's value never passes through the model.** The broker user, SOPS+age and generate-and-pipe rotation
  replace every "read the .env" path. CLAUDE.md rules about secrets are documentation only, not enforcement
  (#59094).
- **The supervisor owns the audit trail** (`decisions/approvals.jsonl`) and the reply parser. The model never
  interprets an approval.
- **The Max-login question blocks the auth design** (Q2). The blueprint should present it to John as a decision,
  with the legal-page quote.
- **For the researcher plugin:** this run found that workers label Exa search-result text as "opened". The
  worker brief should say plainly that text from a search-result page counts as a snippet, so that workers fetch
  the page or put it under Gaps.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Cloudflare create tokens via API | https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/ | Parent token with Account API Tokens Edit mints scoped TTL child tokens | hosted API | 2026-10-16 | Use: John makes one parent token, held by the broker |
| Vercel tokens (REST + `vercel tokens`) | https://vercel.com/docs/cli/tokens | Mint, list, revoke tokens, optionally project-scoped; `vercel signup` exists | hosted, CLI | 2026-10-16 | Use |
| Supabase Management API + PAT | https://supabase.com/docs/reference/api/introduction | PAT-driven project management; scoped PAT; project keys made in the Dashboard | hosted, CLI | 2026-10-16 | Use; PAT is a John step |
| Slack manifest API + config tokens | https://docs.slack.dev/reference/methods/apps.manifest.create | Config token (12 h) creates apps; returns client credentials and an authorize URL | hosted | 2026-10-16 | Use; John does the install click |
| GitHub App manifest flow / device flow | https://docs.github.com/en/apps/sharing-github-apps/registering-a-github-app-from-a-manifest | Human-redirected app registration; device flow for CLI logins; no PAT-create API found | hosted | 2026-10-16 | Fallback; John creates the PAT or App |
| Telegram managed bots | https://core.telegram.org/bots/api | A bot fetches a managed bot's token via getManagedBotToken; first bot via @BotFather | hosted | 2026-10-16 | Spike |
| Anthropic Admin API (keys) | https://platform.claude.com/docs/en/build-with-claude/administration-api | Key list/retrieve/update; keys made in the Console | hosted, org only | 2026-10-16 | Skip for solo; keys from the Console |
| 1Password service accounts | https://www.1password.dev/service-accounts/rate-limits | Service accounts listed for 1Password, Families and Teams in the rate-limit table; vault-scoped; immutable | VM | 2026-10-16 | Fallback store with an agent-only vault; `op run` does not mask its own token; confirm price |
| Bitwarden Secrets Manager | https://bitwarden.com/help/secrets-manager-plans/ | Free: 2 users, 3 projects, 3 machine accounts | hosted | 2026-10-16 | Fallback; no advantage over SOPS here |
| Infisical (cloud + self-host) | https://infisical.com/pricing | MIT core; Free 5 identities; rotation and 30-day audit log on Pro $20/identity/month; `infisical run` | hosted / self-host | 2026-10-16 | Skip self-host for one VM |
| Infisical Agent Vault | https://infisical.com/llms-full.txt | Forward proxy attaches credentials outside the agent; preview | cloud or self-host | 2026-10-16 | Spike for HTTPS APIs |
| Doppler | https://www.doppler.com/pricing | Free for 3 users, 3 days of activity logs; automatic rotation on a paid tier | hosted | 2026-10-16 | Skip |
| OpenBao / Vault | https://www.ssdnodes.com/learn/self-hosted-secrets-manager | Seals on restart; Shamir split protects nothing for one person | self-host | 2026-10-16 (comparison article) | Reject for one VM |
| SOPS + age, systemd-creds | https://www.ssdnodes.com/learn/self-hosted-secrets-manager | Encrypted files, no service; systemd 255 on Ubuntu 24.04 | VM | 2026-10-16 (article; tool docs not opened) | **Recommended** (SOPS+age behind a broker Unix user); systemd-creds for services |
| PostToolUse `updatedToolOutput` | https://code.claude.com/docs/en/hooks | Replaces tool output before Claude sees it; telemetry keeps the original | Claude Code | 2026-10-16 | Defence in depth; spike the transcript effect |
| pass (gpg) | https://github.com/anthropics/claude-code/issues/71654 | GPG password store | local | 2026-10-16 (issue only) | Reject: an unlocked gpg printed a PAT |
| Channels permission relay (Telegram plugin) | https://code.claude.com/docs/en/channels-reference | Forwards tool-use prompts to chat; first answer wins; sender allowlist; no trust or MCP consent dialogs | John's machine/VM | 2026-10-16 | Use for live daytime prompts; not for overnight reliance |
| Supervisor Telegram digest (plain bot) | https://core.telegram.org/bots/api | sendMessage out, long poll in, allowlist on sender id; numbered batch with defaults | supervisor | 2026-10-16 | Use for batched approvals |
| LangGraph interrupt | https://docs.langchain.com/oss/python/langgraph/interrupts | Pause and resume graph state; node restarts on resume | Python | 2026-10-16 | Skip; second runtime |
| HumanLayer | https://github.com/humanlayer/humanlayer | Approval SDK; repo says the code is deprecated | - | 2026-10-16 | Reject |
| n8n human review / Send and Wait | https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools | Tool-call approval via a chat channel (description from search text only) | n8n | not opened (search text only) | Alternative only if n8n already runs; verify first |
| Twilio SMS | https://www.twilio.com/en-us/sms/pricing/us | $0.0083 per segment; A2P 10DLC registration | hosted, paid | 2026-10-16 | Fallback dead-man alert only, not the approval path |
| Renovate Dependency Dashboard / Dependabot groups | https://docs.renovatebot.com/key-concepts/dashboard/ | Visible approval queue; security fixes bypass it; grouped PRs; open-PR cap | hosted | 2026-10-16 | Pattern reference for batch design |
| Auto mode + `--permission-prompts none` | https://code.claude.com/docs/en/permission-modes ; https://code.claude.com/docs/en/headless | Classifier reviews actions; in `-p` repeated blocks deny the action and the run continues; flag denies all prompts | Claude Code `-p` | 2026-10-16 | Use inside the isolated VM; supervisor watches denials; spike exit behaviour |
| dontAsk / bypassPermissions | https://code.claude.com/docs/en/permission-modes | dontAsk for locked-down CI; bypass needs container/VM/sandbox runtime and non-root | Claude Code | 2026-10-16 | dontAsk = strict fallback; bypass = container-only fallback |
| Managed settings file `/etc/claude-code/managed-settings.json` | https://code.claude.com/docs/en/devcontainer | Highest precedence; not overridable by CLI flags; holds deny rules and `disableBypassPermissionsMode` | Linux | 2026-10-16 | Use; spike reading by a non-root agent user |
| PreToolUse / PermissionRequest hooks (guard, kill switch) | https://code.claude.com/docs/en/hooks | Exit 2 blocks before permission rules; fail-open on timeout unless `onFailure: "block"`; run outside the sandbox | Claude Code | 2026-10-16 | Use for a command-aware guard and a kill switch; spike fail-closed behaviour |
| Claude Code Bash sandbox (unattended use) | https://code.claude.com/docs/en/sandboxing | bubblewrap-based shell sandbox; empty domain allowlist; `allowUnsandboxedCommands: false`; AppArmor profile needed on Ubuntu 24.04 | Claude Code on Linux | 2026-10-16 | Use inside the VM; not sufficient alone for unattended runs |
| anthropics/cwc-long-running-agents | https://github.com/anthropics/cwc-long-running-agents | Kill-switch, verify-gate and other hooks, evaluator subagent; unmaintained event demo | clone read only (commit ad107a9) | 2026-10-16 | Reference; copy the kill-switch idea, do not install |
| Bash deny rules as a boundary | https://code.claude.com/docs/en/permissions | Matched on command text; documented rewordings get past them | Claude Code | 2026-10-16 | Defence in depth only |

## Open questions

**Excluded claims (DROPPED: 17).** These had only a search snippet or search-result text behind them, or no URL
opened in this run:
1. Slack token rotation is irreversible. Taken from engineer-feasibility.md Q7 and not re-opened in this run.
2. 1Password Business price of $8.99 per user per month. Search result only; https://1password.com/pricing/business
   was not opened.
3. The OpenBao + Claude Code home-lab pattern (wrapper scripts, short-lived SSH certs, manual unseal). The dev.to
   page was seen in search highlights only.
4. `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials from child-process environments. Release note seen as
   a search highlight only; not on the env-vars page that was opened.
5. Infisical's local-development guide warns against launching the editor through `infisical run`. Search
   highlight only.
6. OpenBao separate policies per capability with short-lived tokens. Same dev.to page, search highlight only.
7. Bitwarden machine accounts with per-project read or read-write. Search highlight only.
8. "Transcripts retain secrets for up to 5 years under default settings"
   (https://github.com/anthropics/claude-code/issues/38417). Search highlight only. The opened data-usage page
   says 30 days unless the user allows data use for model improvement (5 years). John must check his privacy
   toggle.
9. Warning habituation and polymorphic warnings (https://dl.acm.org/doi/10.25300/MISQ/2018/14124,
   https://doi.org/10.1145/3025453.3025896). Abstracts read through Exa search-result pages.
10. "Habituation is neural, not carelessness" (https://doi.org/10.1145/3025453.3025896). Search-result text only.
11. A pooled drug-interaction alert override rate of 79.8% (https://doi.org/10.2196/preprints.88578). Search-result
    text only.
12. Cutting alert volume did not raise acceptance
    (https://journals.sagepub.com/doi/10.1177/14604582241263242). Search-result text only.
13. Measure alert fatigue as a sustained fall from baseline
    (https://academic.oup.com/jamia/article/33/8/1523/8684938). Search-result text only.
14. n8n's chat node "Limit Wait Time" auto-resume
    (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chat). Exa search text only.
15. n8n human review through a Slack, Telegram or chat channel
    (https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools). Exa search text only.
16. n8n Telegram in-chat approval buttons sit behind the `ENHANCED_HITL_TELEGRAM` flag
    (https://github.com/n8n-io/n8n/issues/34009). Exa search text only.
17. Further deletion incidents: issue #32938, plus nope.net and Docker `rm -rf ~/` write-ups. Titles only, not
    opened.

**Unresolved contradictions:**
- **Fatigue remedy.** Severity tailoring (preprint 88578) versus "volume fell but acceptance did not rise"
  (Sagepub meta-analysis). Both sources are excluded above. Settle it by measuring John's approve rate per tier.
- **Max login versus API key** (Q2). Does a supervisor running `claude -p` under John's own Max login count as a
  "product or service" built with the Agent SDK
  (https://code.claude.com/docs/en/legal-and-compliance)? This is a decision for John. Also check the note's
  "ordinary native use" and "routing for others" wording on the page.
- **Secrets store** (Q3). SOPS+age first (secrets note) versus a 1Password vault wrapper (engineer-browser.md).
  This depends on whether John has 1Password and on the Families price, which was not opened.

**Gaps from the notes:**
- **Keys:** Clay key creation and terms (the page text held no auth content; the terms fetch returned only nav
  text); n8n Cloud versus self-hosted key creation and the n8n terms; the Telegram managed-bot path for a
  non-business bot; a Google OAuth-client create API (not proven absent); a Supabase API-key create endpoint;
  default token lifetimes for Cloudflare, Vercel and Attio; Attio's key-scope UI; whether the Google org-policy
  default applies to John's org; terms for Clay, n8n, Outreach, WHOOP, Withings, Google Cloud (the terms fetch
  returned only nav text) and Cloudflare signup.
- **Secrets:**
  - the 1Password Families or Individual price (seen only in a search highlight, in CAD); `bws run` semantics
    and the Bitwarden Free audit log;
  - Infisical self-host resource needs; the age and SOPS licences;
  - whether the transcript JSONL stores the original output or the `updatedToolOutput` replacement;
  - whether `updatedToolOutput` fires on the harness "file changed" notice;
  - whether any built-in Anthropic redaction of tool output exists;
  - other secret-redaction hook projects (cc-safe-setup, Prismor), not evaluated;
  - cloud-session transcript retention in backups after deletion; whether editing the JSONL is supported;
  - per-service rotation APIs; honey tokens.
- **Approvals:** change-advisory (ITIL) practice; HumanLayer's format and new product; Slack interactive
  messages; OpenClaw messaging; the Twilio onboarding fee; any study on batched approvals for AI agents
  specifically; timeout lengths (need John's real response times); whether the supervisor and the Telegram
  plugin can share one bot; whether the relay works under background tmux.
- **Permissions:**
  - the exit code and result subtype when auto mode hits the 20-block limit in `-p`;
  - classifier cost and latency;
  - whether `allowManagedPermissionRulesOnly` and the `/etc/claude-code` file are honoured for a non-root user
    without MDM;
  - whether PermissionRequest hooks fire for classifier denials under `--permission-prompts none`;
  - about 170k characters of the hooks page left unread; hook latency numbers;
  - whether the VM has KVM, and whether `kernel.apparmor_restrict_unprivileged_userns` is 1;
  - the Claude Code version on John's VM;
  - Ralph posts from 2026 and Anthropic's long-run harness post, not opened.

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 cited claims.
Verified: 18. Unverified: 2.
- Unverified: Four brokerage keys were revoked (#59094 incident, Evidence E69) — https://github.com/anthropics/claude-code/issues/59094 — page says the issue lists steps the reporter "now must" take but "never confirms that any of these were completed"; the quoted sentence itself is verified, the revocation is not.
- Unverified: Withings+ becomes required on the Start for Free API plan from October 12, 2026 (E37) — https://developers.withings.com/developer-guide/v3/get-access/create-your-app — page did not open: WebFetch "getaddrinfo ENOTFOUND developers.withings.com", Parallel "connect_error", Exa "CRAWL_UNKNOWN_ERROR".

Verified in sample: E42, E129, E133, E150, E126, E138 (Anthropic API model list), E70, E71, E72 (page opened via Exa after WebFetch returned HTTP 404), E116, E111, E115, E16, E118, E100, E101, E30. E168 is verified on substance (the page states that `allowUnsandboxedCommands: false` makes Claude Code ignore the `dangerouslyDisableSandbox` retry), but the page's wording differs from the quote in the note. Telegram's `getManagedBotToken` sentence sits in the second 100k characters of a 582k-character page.
