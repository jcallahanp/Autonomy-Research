# John's two systems as they stand

Brief: Describe, from the two read-only clones, what John's GTM and health systems do today, what each depends on, where workflow and SaaS configuration lives, what is known to break, and what an engineer taking over would need that the repos do not contain.
Run: research/runs/engineer-existing-systems/PLAN.md

Commits read: GTM repo `2d294ad` (1 commit, "Add Superpowers engineering skills and CLAUDE.md working rules"); health repo `46e6364` (1 commit, "S05 Voice parser (#11)"). Both read 2026-10-16 with Read/Bash (cat, grep, git). No repo code was run. No secret values were opened or copied.

## GTM repo: what is in it and what it says the system does

### Takeaway
The GTM repo (Attio-Project) contains no GTM system at all: no Clay, Attio, n8n, Outreach, Slack or artifact configuration, only a vendored Superpowers skill library, a CLAUDE.md of working rules and a one-line README. The whole GTM system therefore lives only in the Attio, Clay, n8n and Outreach accounts, and the repo says nothing about breakages or manual steps. Confidence: high (full file list read; grep for the tool names finds only the README title).

### Cited findings
- The repo holds exactly 2 non-skill files, CLAUDE.md and README.md, plus `.claude/skills/` — https://github.com/jcallahanp/Attio-Project README.md:1 (commit 2d294ad), read 2026-10-16, Bash — Quote: "# Attio-Project"
- A case-insensitive grep for attio, clay, n8n and outreach across the repo (excluding .git) matched only README.md, and that match is the title above — https://github.com/jcallahanp/Attio-Project README.md:1 (commit 2d294ad), read 2026-10-16, Bash — Quote: "# Attio-Project"
- The repo's CLAUDE.md is about how Claude behaves, not about the system — https://github.com/jcallahanp/Attio-Project CLAUDE.md:1-4 (commit 2d294ad), read 2026-10-16, Bash — Quote: "John owns this project and wants Claude to work like a strong senior engineer who is also a good mentor"
- Skills are vendored from Superpowers (plugin v7.0.0) so they load in cloud sessions — https://github.com/jcallahanp/Attio-Project CLAUDE.md:8-11 (commit 2d294ad), read 2026-10-16, Bash — Quote: "vendored from commit `bb92a77`, plugin v7.0.0"
- The skills directory lists 17 skills (brainstorming, diagnosing-superpowers, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving/requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills) — `git ls-files` of the clone (commit 2d294ad), read 2026-10-16, Bash — Quote: ".claude/skills/brainstorming/SKILL.md"
- The repo has no workflow exports, SQL, schema, JSON, Clay table definitions, Attio object/attribute lists or n8n JSON — `git ls-files` of the clone (commit 2d294ad), read 2026-10-16, Bash — Quote: "CLAUDE.md README.md"  (the only non-skill tracked files)

### Contradictions
- None found. (The task brief says the GTM system uses Clay, Attio, n8n, Outreach, Slack and a Claude Code artifact; the repo neither confirms nor denies it. Treated as a Gap, not a contradiction.)

### Inferences
- Inference: the brief's description of the GTM stack comes from John, not from the repo; an engineer cloning it learns nothing about the pipeline. Rests on the single-commit file list and the empty README.
- Inference: Attio-Project looks like a freshly created shell prepared for Claude Code work (commit message "Add Superpowers engineering skills and CLAUDE.md working rules"), so the as-is map must be built by inspecting the live accounts.
- Inference: a separate repo `jcallahanp/Varonis` ("SDR OS") exists and may hold the real sales tooling; it is named in the health repo (see health section) and was not in this task's clones.

### Gaps
- Everything about Clay enrichment tables and credits, Attio objects/lists/views/attributes, n8n workflows and credentials, Outreach sequences and mappings, Slack channels and the Claude Code artifact — not in the repo; needs account access (or exports) from John.
- Known breakages and manual steps in the GTM system — repo mentions none; must be elicited from John or read from account run histories (n8n execution errors, Clay failed rows, Attio duplicates).
- Whether `jcallahanp/Varonis` (SDR OS) holds GTM code — not cloned or opened here.

## Health repo: what it does, tooling, unfinished and known broken, credentials by name

### Takeaway
Health-Management is a substantial, well-documented, single-user Python/FastAPI + Postgres + React PWA project built for a Google Cloud VM behind Cloudflare Tunnel and Access. Only the foundation, data core, hosting code, quick-log app and voice parser are merged as code; the live server does not exist yet, Slack logging, reminders, nutrition and WHOOP/Withings sync are unbuilt, and the first deploy needs a sitting by John. Confidence: high.

### Cited findings
- Intended product — https://github.com/jcallahanp/Health-Management CLAUDE.md:7-9 (commit 46e6364), read 2026-10-16, Bash — Quote: "voice logging (Slack and a home-screen mic), reminders, device sync (WHOOP, Withings), adherence charts and a web app with Claude built in."
- Hosting shape — https://github.com/jcallahanp/Health-Management CLAUDE.md:8-9 (commit 46e6364), read 2026-10-16, Bash — Quote: "One small Google Cloud VM, reachable only through Cloudflare Access. It only suggests; John approves every change."
- Cloudflare Tunnel plus Access, no inbound ports — https://github.com/jcallahanp/Health-Management docs/adr/0018-cloudflare-access.md:7 (commit 46e6364), read 2026-10-16, Bash — Quote: "The VM has no inbound ports. A Cloudflare Tunnel serves `app.<domain>`; an Access policy allows only John's Google account"
- Current phase: the live server does not exist — https://github.com/jcallahanp/Health-Management docs/status.md:6-7 (commit 46e6364), read 2026-10-16, Bash — Quote: "The live server does not exist until John runs `deploy/SETUP.md`."
- Nothing is formally "blocked" but progress waits on John — https://github.com/jcallahanp/Health-Management docs/status.md:14-15 (commit 46e6364), read 2026-10-16, Bash — Quote: "Waiting on John's one computer sitting for `deploy/SETUP.md` (Cloud Shell build, secrets"
- Live checks for S05 and S03 are pending, only proven with fakes — https://github.com/jcallahanp/Health-Management docs/status.md:10-13 (commit 46e6364), read 2026-10-16, Bash — Quote: "proven by tests with a fake Claude and a fake FoodData Central; the live checks (a real Sonnet 5.5 call"
- Next work: Slack logging then Reminders, Nutrition — https://github.com/jcallahanp/Health-Management docs/status.md:16 (commit 46e6364), read 2026-10-16, Bash — Quote: "Next:** S06 Slack logging, then S07 Reminders and S08 Nutrition, on John's yes."
- Feature state: 31 lines `failing`, 24 `passing` (grep count on docs/features.md); Slack logging F-23 is failing — https://github.com/jcallahanp/Health-Management docs/features.md:37 (commit 46e6364), read 2026-10-16, Bash — Quote: "| F-23 | Slack logging | S06 | capture §1"
- Device sync (WHOOP, Withings) is slice S10, not started — https://github.com/jcallahanp/Health-Management docs/plan.md:49 (commit 46e6364), read 2026-10-16, Bash — Quote: "| S10 | WHOOP and Withings | Weigh-ins, BP, HRV and sleep arrive on their own within about 20 minutes"
- Integrations are designed as one adapter per source — https://github.com/jcallahanp/Health-Management docs/adr/0020-integration-adapters.md:7 (commit 46e6364), read 2026-10-16, Bash — Quote: "Each source is a module in `backend/app/integrations/<source>/`"  (no `integrations/` directory is tracked in the clone)
- Stack layout: backend (Alembic migrations v0001-v0007, jobs worker, capture, quick_log, today), web (Vite PWA, Playwright e2e, 44 tracked files), deploy (Dockerfile, compose, Terraform, backup/restore scripts), 22 ADRs, design docs per area — `git ls-files` of the clone (commit 46e6364), read 2026-10-16, Bash — Quote: "deploy/terraform/secrets.tf"
- Secret names (values never in Git; John adds each by `gcloud secrets versions add`) — https://github.com/jcallahanp/Health-Management deploy/terraform/secrets.tf:7-26 (commit 46e6364), read 2026-10-16, Bash — Quote: "CLOUDFLARE_TUNNEL_TOKEN" ... "ANTHROPIC_API_KEY" ... "SLACK_BOT_TOKEN" ... "WHOOP_CLIENT_SECRET" ... "WITHINGS_CLIENT_SECRET" ... "PUSHOVER_APP_TOKEN" ... "GMAIL_APP_PASSWORD"
- Full named list from the same file: CF_ACCESS_TEAM_DOMAIN, CF_ACCESS_AUD, CF_ACCESS_SERVICE_TOKEN_ID, ALLOWED_EMAIL, DB_PASSWORD, DB_ADMIN_PASSWORD, TOKEN_ENCRYPTION_KEY, FDC_API_KEY, SLACK_APP_TOKEN, WHOOP_CLIENT_ID, WITHINGS_CLIENT_ID, PUSHOVER_USER_KEY — https://github.com/jcallahanp/Health-Management deploy/terraform/secrets.tf:7-26 (commit 46e6364), read 2026-10-16, Bash — Quote: "John adds each value himself with `gcloud secrets versions add NAME --data-file=-` (SETUP.md)"
- Deploy uses GitHub Actions with OIDC and Workload Identity Federation, project and VM named in the workflow — https://github.com/jcallahanp/Health-Management .github/workflows/deploy.yml:7 and :23-26 (commit 46e6364), read 2026-10-16, Bash — Quote: "Google credentials are short-lived (OIDC + Workload Identity Federation); no key is stored."
- Account/service inventory John created by hand (Google Cloud project, $55 budget, domain via Cloudflare Registrar, Slack workspace, Pushover, Withings dev app) — https://github.com/jcallahanp/Health-Management docs/status.md:53-57 (commit 46e6364), read 2026-10-16, Bash — Quote: "John set up Google Cloud project `life-os-jc` with billing and the $55 budget"
- Cloudflare Zero Trust set up in the dashboard, not in the repo — https://github.com/jcallahanp/Health-Management docs/status.md:58-59 (commit 46e6364), read 2026-10-16, Bash — Quote: "Cloudflare Zero Trust team `late-art-3c0d`, Google login method"
- SETUP.md has 22 numbered manual steps (Cloud Shell, secrets, Cloudflare Access app and tunnel by dashboard, Slack app creation, GitHub variables, first deploy) — https://github.com/jcallahanp/Health-Management deploy/SETUP.md:100 (commit 46e6364), read 2026-10-16, Bash — Quote: "The \"Life OS\" Slack app (in your Life OS workspace), with the scopes S06 uses"
- WHOOP/Withings design: polling, no webhooks, no Rythm API — https://github.com/jcallahanp/Health-Management docs/status.md:28-29 (commit 46e6364), read 2026-10-16, Bash — Quote: "no Rythm API (CSV download instead), no official Boostcamp export, WHOOP/Withings sign-in works behind Cloudflare Access with polling instead of webhooks."
- Process and tooling: single Build master with helpers, at most 2 slices, Checker comment and CI green before merge — https://github.com/jcallahanp/Health-Management docs/status.md:42-43 (commit 46e6364), read 2026-10-16, Bash — Quote: "one Build master with helpers, at most 2 slices, only the Build master writes the shared status files"
- Docs-as-memory convention: status, TODO, decisions, ADRs, glossary, history — https://github.com/jcallahanp/Health-Management CLAUDE.md:11-31 (commit 46e6364), read 2026-10-16, Bash — Quote: "Read these and nothing else at startup (under 5k tokens)"
- CI has three workflows (ci, deploy, guards) and dependabot — `git ls-files` of the clone (commit 46e6364), read 2026-10-16, Bash — Quote: ".github/workflows/guards.yml"

### Contradictions
- None found. (status.md:14 says "Blocked: nothing" while also saying the work waits on John's sitting; I read that as "no technical blocker", not a conflict.)

### Inferences
- Inference: "Known broken" for health is mostly "not yet built or not yet live-tested", not bugs: status.md lists no open defects, and the Checker found and fixed issues before each merge (status.md:61-63, 68-69). Rests on status.md and features.md counts.
- Inference: the health repo is the better of the two to hand to an engineer because infrastructure is code (Terraform, Compose, Actions); the only account-only pieces are Cloudflare Access/tunnel dashboard config, Slack app config, secret values and developer-app registrations.
- Inference: the home-screen mic, backend and PWA are code-complete for logging; reminders (S07), Slack (S06), nutrition (S08) and device sync (S10) are the open build scope.

### Gaps
- Contents of backend/web code and design docs beyond status, plan, features and secrets lists were not read line by line; I did not verify that the code matches status.md.
- Whether the VM or Cloudflare tunnel actually exist today — status.md says no live server as of its last log line (2026-10-11); status as of 2026-10-16 unknown.
- Whoop and Withings API behaviour was not researched (outside brief).

## Readable from the repo alone vs needs account access, and what the as-is map would still miss

### Takeaway
GTM: almost nothing is readable from the repo; every system (Attio, Clay, n8n, Outreach, Slack) needs account access or exports. Health: code, schema, Terraform, workflows, docs and decisions are all readable; the live state of Google Cloud, Cloudflare Zero Trust, Slack app, WHOOP and Withings developer apps, GitHub variables and Secret Manager values needs account access. Confidence: high for health, medium for GTM (absence of evidence in a thin repo).

### Cited findings
- Health infrastructure is declared in Terraform for Secret Manager, VM, storage, monitoring and GitHub — `git ls-files` of the clone, deploy/terraform/ (commit 46e6364), read 2026-10-16, Bash — Quote: "deploy/terraform/monitoring.tf"
- The Cloudflare tunnel and Access app are created in the dashboard, not by Terraform (no cloudflare file in deploy/terraform; steps are manual) — https://github.com/jcallahanp/Health-Management deploy/SETUP.md:73 (commit 46e6364), read 2026-10-16, Bash — Quote: "Access application, **before** the tunnel route, so the address is never open without a login:"
- Secret values are intentionally absent from Git — https://github.com/jcallahanp/Health-Management TODO.md:3 (commit 46e6364), read 2026-10-16, Bash — Quote: "Never paste keys, tokens or passwords into chat or Git."
- Rule that no health data may be in Git — https://github.com/jcallahanp/Health-Management CLAUDE.md:47 (commit 46e6364), read 2026-10-16, Bash — Quote: "No health data, names, secrets or tokens in Git. Tests use synthetic data only."
- Thread notes and summaries live outside the repo at /mnt/project-files — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:36-37 (commit 46e6364), read 2026-10-16, Bash — Quote: "One notes file per thread (`/mnt/project-files/notes/<thread>.md`"

### Contradictions
- None found.

### Inferences
- Access an engineer needs that repos lack. Health: Google Cloud project `life-os-jc` (IAM, Cloud Shell, Secret Manager write), Cloudflare account (Registrar domain, Zero Trust, tunnel), Slack "Life OS" workspace admin, Anthropic console key, WHOOP developer account, Withings developer app and the physical devices, Pushover, GitHub repo Variables/Actions, the Claude.ai project "Health Bot" and /mnt/project-files notes. GTM: Attio workspace admin, Clay workspace and credits, n8n instance and credential store, Outreach admin, Slack workspace/app, plus the Claude Code artifact. All inferred from the named services above and the brief.
- Missing from a repo-only as-is map: GTM everything; health live infra state, Terraform remote state bucket contents, GitHub repo variables, Cloudflare dashboard config, Slack scopes actually granted, developer-app callback registrations, and the notes in /mnt/project-files.
- Inference: the GTM acceptance scenario cannot be proved from the repo; it needs a read-only export step (Attio API schema dump, Clay table export, n8n workflow JSON export, Outreach sequence list) as the first engineer task.

### Gaps
- Whether John has MCP connectors to these accounts: this session's tool list shows Clay and n8n MCP servers connected, which could read account state, but I was told not to use them in this facet and did not call them.

## How John already works with Claude Code (data about habits)

### Takeaway
John wants a disciplined, mentoring, plan-first Claude with explicit approval, tiny reviewable plans, subagent roles and hook-enforced guardrails; he vendors Superpowers into repos as plain files so cloud sessions get it. Confidence: high.

### Cited findings
- GTM repo asks for senior engineer plus mentor — https://github.com/jcallahanp/Attio-Project CLAUDE.md:3-4 (commit 2d294ad), read 2026-10-16, Bash — Quote: "disciplined about process, and explaining the \"why\" as it goes."
- Superpowers core loop mandated (brainstorm, plan, TDD, debug, verify, review) — https://github.com/jcallahanp/Attio-Project CLAUDE.md:14-23 (commit 2d294ad), read 2026-10-16, Bash — Quote: "Before any task, check whether a skill applies and use it."
- Explain alternatives and recommend one — https://github.com/jcallahanp/Attio-Project CLAUDE.md:29-31 (commit 2d294ad), read 2026-10-16, Bash — Quote: "which alternatives you considered. Recommend one."
- Evidence before claims of done — https://github.com/jcallahanp/Attio-Project CLAUDE.md:34 (commit 2d294ad), read 2026-10-16, Bash — Quote: "Never claim something is done or working without evidence (test output, a run)."
- Corner-cutting rule — https://github.com/jcallahanp/Attio-Project CLAUDE.md:35-36 (commit 2d294ad), read 2026-10-16, Bash — Quote: "say so once, suggest the better path, and then do what he decides."
- Health repo has a protected rules file that outranks all others — https://github.com/jcallahanp/Health-Management CLAUDE.md:4 (commit 46e6364), read 2026-10-16, Bash — Quote: "Read `docs/agent_rules.md` first. It is protected and wins over everything else, including this file."
- Hard rule: step tracker at top of every reply — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:9-11 (commit 46e6364), read 2026-10-16, Bash — Quote: "Every reply to John, in every chat, starts with all of that chat's steps as a short bulleted list"
- Hard rule: plans stay simple, and why — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:15-16 (commit 46e6364), read 2026-10-16, Bash — Quote: "Oftentimes, I approve things without really considering them because it's too much to parse."
- Approval before every action — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:22 (commit 46e6364), read 2026-10-16, Bash — Quote: "For an action, summarize it and ask \"Do I have approval?\" first."
- No standing pre-approvals — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:24 (commit 46e6364), read 2026-10-16, Bash — Quote: "No standing pre-approvals in docs, settings or memory."
- Scope discipline — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:27-29 (commit 46e6364), read 2026-10-16, Bash — Quote: "Every session states its scope in one line at the start."
- Roles and model tiers — https://github.com/jcallahanp/Health-Management docs/agent_rules.md (Models and effort rule, section 4.6) (commit 46e6364), read 2026-10-16, Bash — Quote: "verifier Opus 5.5 high with fresh context; helpers low to medium. Never max by default."
- Two subagents defined: checker (read-only verifier, model opus) and reviewer — https://github.com/jcallahanp/Health-Management .claude/agents/checker.md:2-5 (commit 46e6364), read 2026-10-16, Bash — Quote: "Verifies a finished slice against its feature lines with a fresh memory, before John sees it."
- Hooks configured in settings.json: PreToolUse protected-files and privacy guards, PostToolUse lint, Stop test gate and autosave, PreCompact autosave, SessionStart context reload — https://github.com/jcallahanp/Health-Management .claude/settings.json (commit 46e6364), read 2026-10-16, Bash — Quote: "\"command\": \"python3 \\\"$CLAUDE_PROJECT_DIR/scripts/hooks/protected_files.py\\\" --claude\""
- Rules are adapted across repos (SDR OS in `jcallahanp/Varonis`) — https://github.com/jcallahanp/Health-Management docs/agent_rules.md:5 (commit 46e6364), read 2026-10-16, Bash — Quote: "Adapted from the SDR OS rules (repo `jcallahanp/Varonis`, `docs/agent_rules.md`)"
- Build process is a Build master with helpers, max 2 slices, one writer for shared files — https://github.com/jcallahanp/Health-Management CLAUDE.md:52-53 (commit 46e6364), read 2026-10-16, Bash — Quote: "Only the Build master writes `docs/status.md`, `docs/features.md`,"
- Work is driven from claude.ai projects and threads, not only CLI — https://github.com/jcallahanp/Health-Management docs/status.md:10-11 (commit 46e6364), read 2026-10-16, Bash — Quote: "Revamp planned in the Health Bot project and approved by John"

### Contradictions
- None found. Note a tension to be aware of, not a source conflict: the GTM CLAUDE.md says brainstorm, ask questions and "get John's OK" before code, while the campaign wants a fully autonomous engineer; the health agent_rules.md approval rules are stricter (approval for every action).

### Inferences
- Inference: John approves what he can read in two minutes; the autonomous engineer's output must be a short numbered plan plus a checkable outcome, and approval gates should be few and explicit. Rests on agent_rules.md:15-16, 22-24.
- Inference: John already uses subagent verification (checker/reviewer), hooks and TDD; the engineer should extend those rather than replace them.
- Inference: the autonomy campaign must reconcile "no standing pre-approvals" with autonomous operation, probably by per-task scoped approval; this is a design question for synthesis.

### Gaps
- Health reviewer.md and the hooks' code were not read in full; the 17 vendored skills were not read (they are upstream Superpowers).
- User-level CLAUDE.md or memory files on John's machine are not in the clones.

## Manual steps John still does that the scenario must remove

### Takeaway
The GTM repo documents none (Attio tables and views, Clay workflows, data cleanup, merges are not mentioned anywhere in it), so those manual steps can only come from John or the live accounts. The health repo lists explicit manual steps in TODO.md and deploy/SETUP.md. Confidence: high for health, low for GTM.

### Cited findings
- GTM: no mention of tables, views, Clay workflows, cleanup or merges in the repo — https://github.com/jcallahanp/Attio-Project README.md:1 (commit 2d294ad), read 2026-10-16, Bash — Quote: "# Attio-Project"
- Health: one sitting to run the setup list — https://github.com/jcallahanp/Health-Management TODO.md:8 (commit 46e6364), read 2026-10-16, Bash — Quote: "`deploy/SETUP.md` is the numbered list for the one remaining computer sitting"
- Health: create Anthropic key and store in Secret Manager — https://github.com/jcallahanp/Health-Management TODO.md:12 (commit 46e6364), read 2026-10-16, Bash — Quote: "Create a key at console.anthropic.com during the post-merge sitting in `deploy/SETUP.md` (step 14)"
- Health: optional FoodData Central key (demo key rate-limited) — https://github.com/jcallahanp/Health-Management TODO.md:13 (commit 46e6364), read 2026-10-16, Bash — Quote: "allows about 30 lookups an hour"
- Health: upload training program and workout history — https://github.com/jcallahanp/Health-Management TODO.md:14 (commit 46e6364), read 2026-10-16, Bash — Quote: "Upload your Boostcamp program (screenshots or a written copy) and your workout history"
- Health: create WHOOP developer app, parked until S10 — https://github.com/jcallahanp/Health-Management TODO.md:15 (commit 46e6364), read 2026-10-16, Bash — Quote: "Parked by John until device sync (S10) is near"
- Health: turn off old LifeOS WHOOP sync — https://github.com/jcallahanp/Health-Management TODO.md:16 (commit 46e6364), read 2026-10-16, Bash — Quote: "Ask Life OS HQ to turn off the old LifeOS app's WHOOP sync"
- Health: pair Withings devices at home on Wi-Fi — https://github.com/jcallahanp/Health-Management TODO.md:17 (commit 46e6364), read 2026-10-16, Bash — Quote: "pair them with the Withings app on home Wi-Fi (needs you at home)"
- Health: upload old Rythm results, lab PDF and food logs (deferred) — https://github.com/jcallahanp/Health-Management TODO.md:18 (commit 46e6364), read 2026-10-16, Bash — Quote: "Upload old Rythm results (CSV download from app.rythmhealth.com/account/orders, or PDFs)"
- Health: Cloudflare Access app, tunnel, service token, Slack app and GitHub variables are dashboard steps — https://github.com/jcallahanp/Health-Management deploy/SETUP.md:85 (commit 46e6364), read 2026-10-16, Bash — Quote: "Tunnel and its route: Networking > Tunnels > Create a tunnel > Cloudflared, name `life-os`."

### Contradictions
- None found.

### Inferences
- Inference: the health scenario that removes John's labour is "engineer runs SETUP.md end to end given scoped access", with irreducible human steps being those needing his identity or physical presence (Google login, Withings pairing, entering secret values he must not paste into chat).
- Inference: the GTM manual steps named in the brief (Attio tables/views, Clay workflows, cleanup, merges) have no repo evidence and must be captured by an interview plus account export before the scenario is written.

### Gaps
- Concrete GTM manual steps with where they are mentioned — no repo source; ask John or read his chat/project history.
- Any breakage list for GTM — none in repo.

## Tools evaluated
None.
