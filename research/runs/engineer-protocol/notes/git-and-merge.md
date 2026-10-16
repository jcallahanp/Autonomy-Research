# Git discipline and self-merge without a human reviewer

Brief: Define the git workflow and merge policy for an autonomous Claude Code engineer that merges routine changes itself (R16, awaiting John's confirmation) while keeping risky changes for John.
Run: research/runs/engineer-protocol/PLAN.md

Recommendation (one): trunk-based, one worktree + one branch + one small PR per task; Conventional Commit titles; squash merge; the engineer self-merges only Tier 1 PRs (docs, tests, notes, deterministic small changes) via `gh pr merge --auto` after required checks pass; everything on a protected-path list is owned by John through CODEOWNERS plus a branch rule, and enforcement lives on GitHub, not in prompts. The load-bearing prerequisite: a free personal private repo cannot enforce any of this (see Q2), so John must pick (a) GitHub Pro, (b) a public repo, or (c) local-only enforcement with weaker guarantees. Spike before building is listed at the end of Q4.

## Branching and PR conventions
### Takeaway
Branch per task in its own worktree, small PRs, Conventional Commit titles, squash merge to keep main one-commit-per-task and revert-friendly. Claude Code and Superpowers both support worktrees natively and Superpowers' finishing skill defaults to asking the human, which the engineer must override with a written policy. Confidence: medium-high (conventions are well documented; "squash vs merge" is a preference, only one precedent set found).

### Cited findings
- Claude Code has a native worktree flag for parallel sessions, each a separate checkout on its own branch — https://code.claude.com/docs/en/common-workflows, opened 2026-10-16, WebFetch — Quote: "Each git worktree is a separate checkout on its own branch, created from an existing commit"
- Same page: `claude --worktree <name>` starts a parallel session; second terminal with another name gives isolation — https://code.claude.com/docs/en/common-workflows, opened 2026-10-16, WebFetch — Quote: "claude --worktree feature-auth"
- Claude Code links a session to the PR it creates, so `claude --from-pr N` resumes it — https://code.claude.com/docs/en/common-workflows, opened 2026-10-16, WebFetch — Quote: "Claude Code links the session to the PR when Claude creates it with `gh pr create`"
- Superpowers using-git-worktrees: detect existing isolation, prefer native tools, never fight the harness, verify worktree dir is git-ignored — https://github.com/obra/superpowers skills/using-git-worktrees/SKILL.md:12 (commit bb92a77), read 2026-10-16, git clone — Quote: "Detect existing isolation first. Then use native tools. Then fall back to git. Never fight the harness."
- Superpowers finishing skill: tests green first, then a menu (merge locally / push+PR / keep) and "the integration decision is theirs" — i.e. it asks a human by design — skills/finishing-a-development-branch/SKILL.md:81-82 (commit bb92a77), read 2026-10-16, git clone — Quote: "Wait for their answer; the integration decision is theirs."
- Superpowers refuses force-push and force worktree removal on its own initiative — skills/finishing-a-development-branch/SKILL.md:225 (commit bb92a77), read 2026-10-16, git clone — Quote: "A rejected push means the remote moved. Investigate; force-push only on your human partner's explicit request."
- Superpowers never starts implementation on main — skills/executing-plans/SKILL.md:112 (commit bb92a77), read 2026-10-16, git clone — Quote: "Never start implementation on a main/master branch without your human"
- Conventional Commits 1.0.0 gives a parsable title and maps fix/feat/BREAKING to PATCH/MINOR/MAJOR, which lets a gate read the type from the title — https://www.conventionalcommits.org/en/v1.0.0/, opened 2026-10-16, WebFetch — Quote: "`<type>[optional scope]: <description>`"
- Same: breaking-change marker — https://www.conventionalcommits.org/en/v1.0.0/, opened 2026-10-16, WebFetch — Quote: "a commit that has a footer `BREAKING CHANGE:`, or appends a `!` after the type/scope, introduces a breaking API change"
- A governance method for AI self-merge sets self-merge preconditions: squash only, delete branch, checks pass, reviewer different from author — https://github.com/shiyamaz/qorum-method examples/qorum.yml:61-67 (commit fbcfa2c), read 2026-10-16, git clone — Quote: "merge_method: squash"
- A commercial agent product prefers merge commit > rebase > squash but squashes when only squash is allowed, using the PR description as the commit message — https://docs.tai.ga/deliver/auto-merge/, opened 2026-10-16, WebFetch — Quote: "Taiga prefers a merge commit, then a rebase, then a squash, in that order"
- Claude Code docs advise reviewing the generated PR and asking for risks — https://code.claude.com/docs/en/common-workflows, opened 2026-10-16, WebFetch — Quote: "Review Claude's generated PR before submitting and ask Claude to highlight potential risks or considerations."

### Contradictions
- Squash (Qorum, qorum.yml:65) versus merge commit first (Taiga docs). Preference, not fact; I recommend squash because one task = one revertable commit (inference below).

### Inferences
- Squash merge plus Conventional Commit PR title gives one revert target per task and a title a CI check can lint. Rests on GitHub revert-PR behaviour (Q4) and the Conventional Commits spec.
- Superpowers' finishing menu must be replaced for the engineer by a policy that picks option 2 (push + PR) always and then runs the merge gate; option 1 (local merge to main) must be denied because it bypasses PR checks.
- "Small PR" has no hard number from an Anthropic source; use the Qorum Low/Medium limits (5 / 20 files, 1000 diff lines) as a starting point.

### Gaps
- No Anthropic engineering post on commit/PR size or squash vs merge was opened; the Claude Code docs pages opened say nothing on it. Parallel Search was rate limited (Too Many Requests); not retried.
- Worktree cleanup details page (https://code.claude.com/docs/en/worktrees) not opened.

## Merge policy without a human
### Takeaway
Use GitHub auto-merge, which merges only after required checks pass, on a branch protected so that the agent's credential cannot push to main or bypass rules; guard human-owned paths with CODEOWNERS. Critical constraint: on a free personal account these features are listed under GitHub Pro for private repos, so R16 as designed needs a paid plan ($ price not verified) or a public repo. Confidence: medium (plan table read via docs summary; rulesets/merge queue availability on Free not confirmed).

### Cited findings
- Free personal accounts get private repos with a limited feature set; Pro adds protected branches, required reviewers and code owners for private repos — https://docs.github.com/en/get-started/learning-about-github/githubs-plans, opened 2026-10-16, WebFetch — Quote: "Advanced tools and insights in private repositories:"
- Same page, Pro list items — https://docs.github.com/en/get-started/learning-about-github/githubs-plans, opened 2026-10-16, WebFetch — Quote: "Protected branches"
- Pricing page marks repository rules as public-only on Free and code owners as a Team feature — https://github.com/pricing, opened 2026-10-16, WebFetch — Quote: "Ensure that pull requests have a specific number of approving reviews."
- Rulesets are documented for Team and Enterprise plans — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets, opened 2026-10-16, WebFetch — Quote: "for customers on GitHub Team and GitHub Enterprise plans"
- Bypass lists need an organisation-owned repo; a personal repo cannot grant GitHub Apps a bypass — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches, opened 2026-10-16, WebFetch — Quote: "Actors may only be added to bypass lists when the repository belongs to an organization."
- Auto-merge must be enabled per repo and merges once reviews and checks pass — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request, opened 2026-10-16, WebFetch — Quote: "Before you use auto-merge, it must be enabled for the repository."
- Branch protection defaults: force pushes blocked, status checks must pass, signed commits and linear history optional — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches, opened 2026-10-16, WebFetch — Quote: "By default, GitHub blocks force pushes on all protected branches."
- Branch rule options include "Do not allow bypassing the above settings" and "Require branches to be up to date before merging" — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule, opened 2026-10-16, WebFetch — Quote: "Do not allow bypassing the above settings"
- Merge queue is enabled in branch protection by repo admins; plan availability not stated on that page — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue, opened 2026-10-16, WebFetch — Quote: "Require merge queue"
- CODEOWNERS: file in .github/, root or docs/; last match wins; owners need write access; an approval from any owner suffices — https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners, opened 2026-10-16, WebFetch — Quote: "Order is important; the last matching pattern takes the most precedence."
- Dependabot auto-merge pattern: `gh pr merge --auto`, gate on `update-type` (patch), and require status checks — https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions, opened 2026-10-16, WebFetch — Quote: "you should enable **Require status checks to pass before merging** for the target branch for Dependabot pull requests."
- Same page: with a merge queue the built-in token cannot enqueue — https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions, opened 2026-10-16, WebFetch — Quote: "If the target branch uses a merge queue, the built-in `GITHUB_TOKEN` cannot add pull requests to the queue."
- Renovate: does not automerge without passing checks; recommends tests; automerge by minor/patch only and excludes 0.x — https://docs.renovatebot.com/key-concepts/automerge/, opened 2026-10-16, WebFetch — Quote: "By default, Renovate will not automerge until it sees passing status checks / check runs for the branch."
- Renovate no-tests escape hatch is explicit opt-in — https://docs.renovatebot.com/key-concepts/automerge/, opened 2026-10-16, WebFetch — Quote: "If you have no tests but still want Renovate to automerge, you need to add `"ignoreTests": true` to your configuration."
- A merging agent product never asks to be a bypass actor and stops if its fix commits changed what decides whether checks pass — https://docs.tai.ga/deliver/auto-merge/, opened 2026-10-16, WebFetch — Quote: "a green reached that way is not evidence the code works, and Taiga does not merge on it."
- Same page: merge does not equal ship if main deploys — https://docs.tai.ga/deliver/auto-merge/, opened 2026-10-16, WebFetch — Quote: "If merging to your main branch deploys, then auto-merge inherits that"
- A 2026 risk-tier write-up (swarmz.net, 2026-08-21, third-party blog) scopes auto-merge to paths and credentials — https://swarmz.net/blog/should-you-let-ai-agents-merge-their-own-pull-requests, opened 2026-10-16, WebFetch — Quote: "Two conditions both have to hold: the diff is scoped entirely to low-risk paths, and CI is green"

### Contradictions
- Branch protection page states no plan requirement for protected branches (WebFetch of about-protected-branches), while the plans page lists "Protected branches" under Pro for private repos. The plans page is the specific one; settle by a 10-minute spike creating a rule in a throwaway free private repo.

### Inferences
- With a personal-account repo, no bypass list exists, so the agent's PAT (owned by John, admin) is subject to rules only if "Do not allow bypassing" is on. Hence either use a separate bot account/GitHub App with write (not admin) access or enable that option. Rests on the bypass-list and "Do not allow bypassing" findings.
- Required approvals can be 0 for routine PRs: auto-merge then depends on required status checks only; John's approval is demanded only on CODEOWNERS paths ("Require review from Code Owners"). A bot account sharing John's identity cannot approve for him; a separate bot identity is needed so John remains the code owner (CODEOWNERS owners need write access, so John as owner works).
- Merge queue is not needed for a single-agent repo; skip. (Dependabot caveat about GITHUB_TOKEN makes it extra friction.)
- Self-edit lock: .github/CODEOWNERS, workflows and the protected-path list must be John-owned (Fullsend: below).

### Gaps
- GitHub Pro price not verified (pricing page opened lists Free, Team $4 user/month first 12 months only). Pro was not found on that page.
- Whether rulesets and auto-merge work on Free private repos: not stated by any opened page; spike.
- Required-reviewer-by-path GA Feb 2026 (swarmz blog claim) not verified at GitHub. runcycles.io and thinqit.io were seen in search only, not opened. Taiga and swarmz are vendor/blog sources; no Anthropic engineering post on agent self-merge was found or opened.

## Routine versus needs John
### Takeaway
Classify by paths and mechanical size limits, not by the agent's opinion: Tier 1 self-merge = docs/notes/tests/small code in non-protected paths with green required checks; Tier 2 needs John = protected paths, new or changed dependencies, CI or deploy config, auth/secrets, migrations, public API, anything irreversible or user-visible, and diffs over the size limit. Confidence: medium-high (three independent precedents agree on the core list; thresholds are tunable defaults, not standards).

### Cited findings
- Qorum default protected paths: workflows, .gitignore, env/key/pem/secrets, dependency manifests and lockfiles, migrations, IaC, and the gate config itself — https://github.com/shiyamaz/qorum-method examples/qorum.yml:12-35 (commit fbcfa2c), read 2026-10-16, git clone — Quote: "\".github/workflows/**\"   # CI/CD — can exfiltrate secrets or ship anything"
- Qorum tier limits: Low <=5 files, no deletions, <=1000 diff lines; Medium <=20 files, <=3 deletions plus cooldown and notify — examples/qorum.yml:42-54 (commit fbcfa2c), read 2026-10-16, git clone — Quote: "cooldown_seconds: 60            # your STOP window before merge"
- Qorum bias rule: round up, never down — examples/qorum.yml:58 (commit fbcfa2c), read 2026-10-16, git clone — Quote: "if a PR doesn't clearly satisfy a lower tier, it belongs to the next higher one — never downgrade."
- Qorum invariant: reviewer clears low/medium, only the human clears high — https://github.com/shiyamaz/qorum-method README.md (commit fbcfa2c), read 2026-10-16, git clone — Quote: "the Reviewer may clear Low and Medium, but only the human Approver clears High"
- Fullsend: autonomy per repo with CODEOWNERS as the escape hatch; agent config, system prompts and CODEOWNERS itself human-owned — https://fullsend.sh/docs/problems/autonomy-spectrum, opened 2026-10-16, WebFetch — Quote: "Agent configuration and system prompts"
- Fullsend: runtime escalation dimensions reversibility, blast radius, visibility — https://fullsend.sh/docs/problems/autonomy-spectrum, opened 2026-10-16, WebFetch — Quote: "if any dimension is high, escalate"
- swarmz Tier 2 never auto-merge: schema, auth, payments, public API — https://swarmz.net/blog/should-you-let-ai-agents-merge-their-own-pull-requests, opened 2026-10-16, WebFetch — Quote: "everything that changes what the system does or who can do what inside it"
- Claude Code's auto-mode classifier already blocks by default: production deploys and migrations, force push, granting repo permissions — https://code.claude.com/docs/en/permission-modes (saved copy line 360-368), opened 2026-10-16, WebFetch — Quote: "Production deploys and migrations"
- Same: classifier blocks pushing secrets or widening deploy exposure through CI/deploy config — https://code.claude.com/docs/en/permission-modes, opened 2026-10-16, WebFetch — Quote: "Force push"
- Renovate precedent for dependency risk: only minor/patch, exclude 0.x — https://docs.renovatebot.com/key-concepts/automerge/, opened 2026-10-16, WebFetch — Quote: "Non-major updates in SemVer ecosystems shouldn't have breaking changes (if they follow the spec)."

### Contradictions
- Qorum places dependency lockfiles under protected (High); swarmz Tier 1 allows "lockfile-only dependency bumps where the update tool is trusted". Resolution is John's: I recommend John-gated by default for the engineer (new dependency = supply-chain decision), with Renovate-style patch-only lockfile bumps as an opt-in later.

### Inferences
- Proposed rule set for John to confirm (R16): SELF-MERGE only if ALL hold: PR title is Conventional Commit type in {docs, test, chore (non-config), style, fix, feat, refactor}; no path matches the protected list; <=20 files, <=1000 diff lines, deletions small; no dependency manifest change; no workflow, hook, CLAUDE.md/settings/permissions or CODEOWNERS change; required checks green on the final head SHA and no CI/test config edited in the PR; PR carries the verification evidence; a cooldown of e.g. 60 s with notification (Qorum Medium) before merge. NEEDS JOHN: anything else, plus `!`/BREAKING titles, migrations, auth/secrets, deploy/infra, data deletion, anything touching a repo that auto-deploys on merge, and any change to the engineer's own guardrails.
- The path rule is enforced twice: CODEOWNERS + "Require review from Code Owners" on GitHub (hard), and a Claude Code pre-merge script that refuses `gh pr merge` when the diff touches the list (soft, defence in depth).
- Tests that cover protected code should be protected too (Fullsend states this; included here as inference from its reasoning I did not quote).

### Gaps
- No empirical data on false-merge rates for the thresholds; spike with shadow mode (Fullsend suggests agents recommend while humans merge, then compare) for the first two weeks.
- Merge-to-main deploy behaviour of John's targets (Vercel, Supabase) unchecked: if main auto-deploys, merge equals ship and Tier 1 must narrow.

## Safety rails and recovery
### Takeaway
Layer it: GitHub rules on the server (no force push, no deletion, required checks, no bypass), a scoped credential (fine-grained PAT or GitHub App, repo-limited, Contents+Pull requests only, no admin), Claude Code deny rules and a PreToolUse hook for local history-rewriting commands, and revert PRs plus pre-risk tags for recovery. Server-side rules are the only layer that does not depend on command text matching. Confidence: medium-high.

### Cited findings
- Claude Code permission rules are enforced by the harness, not the model, and a CLAUDE.md instruction does not change what is allowed — https://code.claude.com/docs/en/permissions, opened 2026-10-16, WebFetch — Quote: "Permission rules are enforced by Claude Code, not by the model."
- Deny rules on `git push` can be bypassed by rewording the command, so they are not a boundary — https://code.claude.com/docs/en/permissions (saved copy line 156), opened 2026-10-16, WebFetch — Quote: "A push written another way, such as `git -C . push`, isn't matched"
- Same page: PreToolUse hooks cannot override a deny rule — https://code.claude.com/docs/en/permissions, opened 2026-10-16, WebFetch — Quote: "a matching deny rule blocks the call"
- The classifier lets Claude push to any branch including default, and relies on remote branch protection — https://code.claude.com/docs/en/permission-modes (saved copy line 425), opened 2026-10-16, WebFetch — Quote: "the remote's own branch protection still applies"
- Fine-grained PATs: repo-limited, per-permission, default 30-day expiry, cannot exceed owner's access, max 50 — https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens, opened 2026-10-16, WebFetch — Quote: "Each token can be further limited to only access specific repositories for that user or organization."
- Same page: token cannot exceed its owner — https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens, opened 2026-10-16, WebFetch — Quote: "A token cannot grant additional access capabilities to a user."
- GitHub Apps have narrow permissions and act independently of a user — https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps, opened 2026-10-16, WebFetch — Quote: "Unlike OAuth apps, GitHub Apps can also act independently of a user."
- Branch protection can require signed commits — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches, opened 2026-10-16, WebFetch — Quote: "can only push commits that have been signed and verified to the branch."
- Revert via GitHub creates a new PR, needs write access — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/reverting-a-pull-request, opened 2026-10-16, WebFetch — Quote: "Reverting a merged pull request creates a new pull request that reverts the original merge commit."
- Superpowers refuses `--force` worktree removal and requires typed confirmation for discarding work — skills/finishing-a-development-branch/SKILL.md:179 (commit bb92a77), read 2026-10-16, git clone — Quote: "Never `--force` on your own initiative."
- Merge credential scoping — https://swarmz.net/blog/should-you-let-ai-agents-merge-their-own-pull-requests, opened 2026-10-16, WebFetch — Quote: "scope the agent's merge credential to only those"

### Contradictions
- None found.

### Inferences
- Credential choice for a single user on a personal account: a GitHub App needs John to create and install it (one-time, ~15 min) and mints 1-hour tokens, but a personal repo has no bypass lists and no org-level controls anyway; a fine-grained PAT on a separate bot account (collaborator with write, not admin) is simplest and keeps John's own account out of the agent's reach. I could not verify installation-token lifetime from an opened page (Gaps). Recommend: bot account + fine-grained PAT (repo-scoped; Contents, Pull requests, Metadata read; Workflows permission withheld so the agent cannot edit workflow files) now; GitHub App later. "Workflows" permission name is from my knowledge, not from an opened page.
- A deny list for `git push --force*`, `git push -f*`, `git reset --hard origin`, `git branch -D`, `gh pr merge` without `--auto`, plus a PreToolUse hook that parses the full command is defence in depth only, given the documented rewording bypass; the server-side rule is the real stop.
- Recovery: (1) tag `pre-<task>` before any Tier 2 merge John approves and before schema/deploy-affecting merges; (2) revert PR on red post-merge CI on main, created automatically by a small script and itself Tier 1; (3) protect tags with a rule if the plan allows (not verified); (4) squash merge so one revert undoes one task.
- Signed commits are optional for a single-user setup; they add a key-management burden for little protection against the main threat (the agent itself). Skip in v1.

### Gaps
- Fine-grained PAT behaviour against branch protection (does an admin PAT bypass?) not stated on the opened page; spike.
- Whether "Workflows" permission exists and blocks edits to `.github/workflows` for fine-grained PATs: not opened.
- GitHub App installation-token lifetime: page opened did not state it.
- Rules for tags (tag protection / rulesets) on personal private repos: not checked.
- Qorum is a method/method sources; read-only repo clone of Qorum only; none run.

### Spike before building
1. In a throwaway private repo on John's actual plan: create branch protection, required check, CODEOWNERS and `Require review from Code Owners`; confirm Free refuses or accepts, and what Pro adds.
2. With a bot collaborator PAT: try `git push origin main`, `git push --force`, `gh pr merge --auto` on a Tier 1 PR and on a PR touching a CODEOWNERS path; confirm each result.
3. Confirm whether auto-merge works with 0 required approvals and that a CODEOWNERS path blocks it.
4. Test the Claude Code deny list plus hook against `git -C . push`, `sh -c`, and alias rewording.
5. Run two weeks in shadow mode (engineer opens PRs, John merges) and compare the engineer's tier to John's decision before enabling R16.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| GitHub branch protection + CODEOWNERS (private repo, plan matrix) | https://docs.github.com/en/get-started/learning-about-github/githubs-plans | Server-side merge gate; listed under Pro for private repos, repository rules public-only on Free | GitHub | 2026-10-16 | Use; needs Pro/Team or a public repo; Pro price unverified |
| GitHub rulesets | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | Rule layers, bypass lists; documented for Team/Enterprise | GitHub | 2026-10-16 | Fallback; org plan needed, bypass lists need an org repo |
| GitHub auto-merge (`gh pr merge --auto`) | https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request | Merges when required checks pass | GitHub | 2026-10-16 | Use for Tier 1 |
| GitHub merge queue | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue | Serialises merges; plan not stated | GitHub | 2026-10-16 | Skip; single agent, extra token friction |
| Fine-grained PAT / GitHub App | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens | Repo-scoped least-privilege agent credential | GitHub | 2026-10-16 | Use PAT on a bot account now; App later |
| Qorum Method | https://github.com/shiyamaz/qorum-method | Convention: three-tier risk gate, protected paths, optional classifier script; not run | repo files / agent prompts | 2026-10-16 (clone commit fbcfa2c) | Reference; copy tier limits and protected-path list, do not adopt wholesale |
| Fullsend autonomy spectrum | https://fullsend.sh/docs/problems/autonomy-spectrum | Design doc: CODEOWNERS as autonomy escape hatch, shadow mode, escalation dimensions | docs | 2026-10-16 | Reference; use shadow mode and dimensions |
| Taiga autonomous merge | https://docs.tai.ga/deliver/auto-merge/ | Hosted agent product that merges only what branch protection allows | hosted, paid/unknown | 2026-10-16 | Reject as product (not needed); copy "no bypass actor" and "changed check config is not green" rules |
| Renovate / Dependabot automerge | https://docs.renovatebot.com/key-concepts/automerge/ | Dependency bot automerge by update type with required checks | GitHub app / Action | 2026-10-16 | Later, optional for patch bumps |
| Conventional Commits | https://www.conventionalcommits.org/en/v1.0.0/ | Commit/PR title format | convention | 2026-10-16 | Use |
