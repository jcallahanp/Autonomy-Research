# Plan formats agents follow best, the plan set and its approval

Brief: Decide which plan files an autonomous Claude Code engineer writes before code (formats, sizes, machine-readable versus prose), and how a non-technical owner approves them.
Run: research/runs/engineer-planning/PLAN.md

Clones (read only, mktemp dir, not run): github/spec-kit f6e72bc, Fission-AI/OpenSpec f80d860, obra/superpowers bb92a77.

## Spec-driven tools and formats

### Takeaway
Every SDD tool converges on the same three layers (what/why, how, tasks) in Markdown; none gives strong evidence that more spec files make agents follow them better. The evidence supports a short human-confirmed intent plus testable criteria and explicit contracts, not volume. Confidence: medium (evidence is mostly small, automated-spec studies).

### Cited findings
- Kiro writes three files per spec: requirements.md (or bugfix.md), design.md, tasks.md. — https://kiro.dev/docs/specs/, opened 2026-10-16, WebFetch — Quote: "Every spec generates three key files that form the foundation of your specification:"
- Kiro's Quick Spec skips approval gates; the normal flow has a Review button for comments on exact passages. — https://kiro.dev/docs/specs/, opened 2026-10-16, WebFetch — Quote: "Generate requirements, design, and tasks in one pass without approval gates."
- Kiro requirements use EARS ("WHEN ... THE SYSTEM SHALL ..."); this is from the search-excerpt of kiro.dev/docs/specs/feature-specs/requirements-first, which I did not open (registry row from an earlier run opened it). Not cited here.
- spec-kit: spec template uses numbered "System MUST" functional requirements, Given/When/Then scenarios and a marker for unresolved items; templates are spec 131, plan 113, tasks 252, constitution 50, checklist 45 lines. — https://github.com/github/spec-kit templates/spec-template.md:98 (commit f6e72bc), read 2026-10-16, git clone — Quote: "- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]"
- spec-kit's tasks template groups tasks by user story with exact file paths and parallel markers. — https://github.com/github/spec-kit templates/tasks-template.md:20 (commit f6e72bc), read 2026-10-16, git clone — Quote: "- Include exact file paths in descriptions"
- spec-kit treats checklist boxes as a read-only gate in /implement. — https://github.com/github/spec-kit templates/commands/implement.md:57 (commit f6e72bc), read 2026-10-16, git clone — Quote: "Treat checklist markers as a read-only gate: scan checkbox state, report status, and ask before proceeding when needed"
- Fowler site (Birgitta Boeckeler, 2025-10-15): spec-kit made too many repetitive files; Kiro's three files easier but still too verbose for a small bug. — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html, opened 2026-10-16, WebFetch — Quote: "Overall they were just very verbose and tedious to review."
- Same article: agents do not reliably follow all spec instructions. — same URL — Quote: "I frequently saw the agent ultimately not follow all the instructions."
- Thoughtworks Radar, SDD in Assess, 2025-11-05: lengthy spec files are hard to review. — https://www.thoughtworks.com/radar/techniques/spec-driven-development, opened 2026-10-16, WebFetch — Quote: "lengthy spec files"; "hard to review" (page text: some tools "generate lengthy spec files that are hard to review"; the fetch tool paraphrased around these phrases)
- Thoughtworks Radar vol. 33 (Nov 2025) warns of heavy up-front specification. — https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2025/11/tr_technology_radar_vol_33_en.pdf, seen only as a search excerpt (not opened); not cited. The Nov 2025 blip page above is opened.
- Thoughtworks Radar April 2026 puts OpenSpec in Assess: propose, apply, archive; spec deltas; says Spec Kit and Superpowers suit greenfield better than brownfield. — https://www.thoughtworks.com/radar/tools/openspec, opened 2026-10-16, WebFetch — Quote: "better suited to greenfield projects than brownfield ones" (as quoted by the fetch tool from the page)
- OpenSpec's default schema makes proposal.md "1-2 pages", then per-capability specs/<capability>/spec.md behaviour contracts, design.md, tasks.md. — https://github.com/Fission-AI/OpenSpec schemas/spec-driven/schema.yaml:44 and :57 (commit f80d860), read 2026-10-16, git clone — Quote: "Keep it concise (1-2 pages). Focus on the \"why\" not the \"how\" -"; ":57 A spec is a behavior contract, not an implementation plan."
- Superpowers writing-plans: a plan holds only decisions the implementer cannot make alone; no placeholders; length bounded by the code. Plans saved to docs/superpowers/plans/YYYY-MM-DD-<feature>.md. — https://github.com/obra/superpowers skills/writing-plans/SKILL.md:157 (commit bb92a77), read 2026-10-16, git clone — Quote: "A plan is the set of decisions the implementer cannot make alone."
- Superpowers brainstorming saves a committed design doc at docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md with goals, non-goals, constraints, decided parts. — https://github.com/obra/superpowers skills/brainstorming/SKILL.md:157 (commit bb92a77), read 2026-10-16, git clone — Quote: "`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, committed."
- Agent OS (Builder Methods) phases: plan-product (mission, roadmap, tech stack), shape-spec, write-spec, create-tasks, implement/orchestrate. — https://buildermethods.com/agent-os/v2/workflow, opened 2026-10-16, WebFetch — Quote: "define the strategic product mission, its projected feature development roadmap, and its technology stack"
- Controlled study (ISCAP 2026): a Spec-Kit-style generated spec/plan/task list raised weighted test pass rate 78.2% to 87.4% on 296 matched BigCodeBench comparisons, at roughly 28x tokens and 15x wall-clock. — https://iscap.us/proceedings/2026/pdf/6729.pdf (PDF text via pdftotext), opened 2026-10-16 — Quote: "The method used roughly 28 times the tokens and 15 times as much wall-clock time of the free-prompting baseline."
- Master's thesis (mskre.no, automated Spec Kit vs vibe, 240 backends): more scaffolding did not consistently raise requirement coverage; best-run code organisation was clearer with more scaffolding. — https://mskre.no/thesis.pdf (pdftotext), opened 2026-10-16 — Quote: "adding more automated scaffolding before implementation did not consistently improve FR coverage."
- ASE 2026 study: fine-grained structured pseudocode specs beat natural language; module-level granularity is the best balance. — https://conf.researchr.org/details/ase-2026/ase-2026-research-track/219/From-Vibe-to-Spec-An-Empirical-Study-to-Demystify-Specifications-in-Code-Generation, opened 2026-10-16, WebFetch — Quote: "organizing specifications at the module level provides the best overall balance"
- AGENTS.md study (ETH SRI Lab, arXiv 2602.11988, Feb 2026): context files raise cost over 20% with no reliable success gain; instructions are followed, so unnecessary requirements make tasks harder. — https://arxiv.org/abs/2602.11988, opened 2026-10-16, WebFetch — Quote: "increasing inference cost by over 20% on average" (fetch tool's quote of the abstract)

### Contradictions
- ISCAP: spec step improved pass rate 9.2 points — https://iscap.us/proceedings/2026/pdf/6729.pdf; disagrees with thesis: more automated scaffolding did not consistently improve coverage and cost more — https://mskre.no/thesis.pdf. Likely cause: ISCAP used single-function tasks with no SRS; thesis started from an SRS plus fixed API contract. Both use LLM-generated specs; neither tests human-confirmed intent.
- The thesis cites Hill (large PR study) finding no support for SDD reducing defects; I did not open Hill. Treat as a Gap.

### Inferences
- (Mine, from ISCAP + thesis) A spec helps most when it supplies what the task lacks (intent, constraints, success criteria); regenerating prose from a prompt the agent already has adds cost, not signal. The human-confirmed parts are where the value is.
- (Mine, from Boeckeler, Thoughtworks, AGENTS.md study) Size should scale with the decision count, not the template. Spec-kit's roughly 590 lines of templates are the ceiling; Kiro's three files and OpenSpec's "1-2 pages" proposal are the reference for a small project.
- (Mine) Do not adopt any SDD tool wholesale. Copy: Kiro's three-layer split, EARS, spec-kit's NEEDS CLARIFICATION marker and read-only checklist gate, OpenSpec's behaviour-contract-not-implementation rule, Superpowers' "plan = decisions only" rule.

### Gaps
- Tessl, Traycer and BMAD file sizes: not opened this run (BMAD and OpenSpec already in registry). Tessl is described only through the Fowler article (private beta Sept 2025).
- No maintainer data from spec-kit/Kiro on adherence rates; Hill PR study not opened.
- Parallel Search returned "Too Many Requests"; Exa used throughout.
- Thoughtworks radar vol. 33 PDF seen only as search excerpt.

## Plan set for a small project

### Takeaway
Essential: one intent brief (prose, 1-2 pages, EARS requirements with acceptance criteria), one architecture sketch (Mermaid/C4 container level), one integrations and keys map (YAML), one task list (YAML/JSON with ids, files, acceptance test refs), and executable acceptance tests. Recommended when needed: data schema (SQL/JSON Schema/OpenAPI as the source file, not prose), ADRs (MADR, one per real decision). Prose for why, YAML/JSON for anything a script checks. Confidence: medium (sizes are my inference from the cited limits).

### Cited findings
- Kiro's design file carries architecture, sequence diagrams and data models; requirements carry EARS and acceptance criteria. — https://kiro.dev/docs/specs/, opened 2026-10-16, WebFetch — Quote: "Build design docs with sequence diagrams and architecture plans" (page bullet list; requirements bullet: "Break down requirements into user stories with acceptance criteria")
- OpenSpec: a spec is externally observable behaviour; internals go in design.md. — https://github.com/Fission-AI/OpenSpec schemas/spec-driven/schema.yaml:57 (commit f80d860), read 2026-10-16, git clone — Quote: "A spec is a behavior contract, not an implementation plan."
- Superpowers: split a multi-subsystem spec into per-subsystem plans, each producing working testable software; steps with checkable results. — https://github.com/obra/superpowers skills/writing-plans/SKILL.md, read 2026-10-16, git clone — Quote: "Each plan should produce working, testable software on its own."
- Superpowers plan hygiene: ban vague lines. — https://github.com/obra/superpowers skills/writing-plans/SKILL.md:159 (commit bb92a77), read 2026-10-16 — Quote: "Lines that decide nothing (\"TBD\", \"handle edge cases\", \"add appropriate validation\","
- Agent OS keeps a product-level layer (mission, roadmap, tech stack) once per project, separate from per-feature specs. — https://buildermethods.com/agent-os/v2/workflow, opened 2026-10-16, WebFetch — Quote: "It is typically run only once at the beginning a new project" (fetch-tool paraphrase of page; treat as paraphrase)
- Structured, module-level specs gave the best quality/stability/token balance. — ASE 2026 page above — Quote: "using fine-grained, structured pseudocode specifications significantly enhances generation stability and quality."
- Registry (earlier runs): C4 context + container levels, MADR for decisions, EARS, Volere fit criterion already adopted. — /home/user/Autonomy-Research/research/tool-registry.md:132 — Quote: "Use context + container levels for the as-is map"

### Contradictions
- None found. (Thesis result that less scaffolding scored as well on a clear SRS + fixed API contract is consistent with: the contract is the essential file, extra prose is not.)

### Inferences
Proposed set, John-sized project (all under `docs/plan/` in the repo, committed):
1. `brief.md` (prose, 1-2 pages): goal, non-goals, users, success measures, costs and risks in plain words. This is the owner-facing file.
2. `requirements.md` (prose in EARS, 15-40 lines of "When X, the system shall Y", each with an ID and a Given/When/Then acceptance line). Prose, but one statement per line so IDs are greppable.
3. `architecture.md` (one Mermaid C4 container diagram plus 10-20 lines; plain flowchart if no C4 skill). Diagram source, not an image.
4. `integrations.yaml` (YAML): per service name, purpose, auth type, env var name only (never values), free/paid and price, owner action needed, fallback. Checkable by a script against `.env.example`.
5. `contracts/` (OpenAPI YAML / JSON Schema / SQL DDL): only where two parts talk to each other. Machine-readable as the single source; no prose copy.
6. `tasks.yaml` (YAML): id, title, requirement IDs, files, depends_on, acceptance test path, status. Splitting rules belong to another facet.
7. `tests/acceptance/` (executable): one test per requirement ID; the done-gate runs these.
8. `decisions/NNNN-*.md` (MADR, 10-25 lines each) only for choices with real alternatives (database, host, auth).
Total reviewed-by-human text: about 150-250 lines excluding contracts. Prose for the why and the owner-facing parts; YAML/JSON for integrations, tasks, contracts, and status, because a hook or script can validate them (Tessl/MDD concern from Fowler: parseable structure gives tool support).
Dropped from spec-kit/Kiro: separate research.md, quickstart.md, per-story checklists, constitution (use CLAUDE.md for rules).

### Gaps
- Sizes above are not benchmarked; spike: generate the set for one real John project and measure review time and agent adherence versus a 1-page brief.
- No source found comparing YAML tasks versus Markdown checklists on agent adherence.
- Agent OS file names not confirmed from an opened page (the search excerpt named mission.md, roadmap.md, tech-stack.md under agent-os/product/; I did not open that file).

## Plan approval for a non-technical owner

### Takeaway
Show the owner only brief.md (plus a visual brief from another run) with goals, scope, costs, risks and the gates; he signs off the brief, integrations/costs and acceptance criteria, not the architecture. Record approval as a committed `APPROVAL.md`/`approval.json` that stores the content hash of the approved files plus a signed git tag or a merged PR with a required approving review and "dismiss stale approvals" on; the agent's start-up check compares hashes and refuses to build if they differ. Confidence: medium (pattern assembled from tools I read; not tested).

### Cited findings
- Superpowers makes approval a hard gate and says approval is limited to what was shown. — https://github.com/obra/superpowers skills/brainstorming/SKILL.md:180 and :202 (commit bb92a77), read 2026-10-16, git clone — Quote: "Approval covers what you showed them. A description you haven't written isn't approved."
- Same file: gate wording. — skills/brainstorming/SKILL.md:180 — Quote: "Nothing gets built until your human partner approves the full"
- Plannotator (local plan reviewer, last reviewed 2026-07-18): in-session Approve records no identity; keep an authorizing record in Git, issue or PR. — https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution, opened 2026-10-16, WebFetch — Quote: "does not record reviewer identity or authorization."
- Same page: what a plan must state before approval. — same URL — Quote: "the intended outcome, boundaries, important implementation choices, risks, and validation" (fetch-tool quote)
- Spec Guard (jpstone, MCP, small repo): three human gates (approve plan, authorize, complete), approval hash-bound to exactly what was reviewed and stale on edit, packet stored as JSON in git. — https://github.com/jpstone/spec-guard, opened 2026-10-16, WebFetch — Quote: "Approval binds a hash of exactly what was reviewed; edit a Spec afterward and the approval goes stale"
- Same repo: agent cannot approve itself. — same URL — Quote: "The agent literally cannot stamp its own approval."
- Enact blog (2026-10-14, vendor): approval needs a named approver, authority to say no, and a record tied to the exact spec version; stale-approval problem as with PRs. — https://www.enactapp.io/blog/spec-approval-workflow-ai-coding-agents, seen as search excerpt only, not opened; not cited as evidence (vendor).
- GitHub protected branches: required approving reviews, dismiss stale approvals when the diff changes, CODEOWNERS review. — https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches, opened 2026-10-16, WebFetch — Quote: "dismiss stale pull request approvals when commits are pushed that affect the diff in the pull request."
- Same page: code-owner approval. — same URL — Quote: "any pull request that affects code with a code owner must be approved by that code owner"
- Lodestar (builder-seoro, harness for non-developers, small repo): non-coder approves decision cards, a UX preview before code, spec amendments, final handoff; agents decide mechanics. Search excerpt only, not opened; not cited. Registry-style note: pattern matches the split below.
- Kiro: approval gates exist per phase except Quick Spec; Markdown Review for comments. — https://kiro.dev/docs/specs/, opened 2026-10-16, WebFetch — Quote: "select the floating **Review** button"

### Contradictions
- None found.

### Inferences
- (Mine) What John signs: (a) goals and non-goals, (b) scope list in plain words, (c) acceptance criteria as observable outcomes ("when I do X I see Y"), (d) gates: which actions need him later (spend, publish, delete, login), (e) costs: monthly total and each paid service with price, (f) risks and what the agent will do if blocked. Architecture, schema, contracts and task list he does not sign; the agent's fresh-context reviewer checks them against the signed brief.
- (Mine) Record: `docs/plan/approval.json` = {approved_by, date, files:{path: sha256}, scope_version, gates:[...]}. Written only when John's own message (or a PR approval by his account) says yes; a PreToolUse/start hook recomputes hashes of brief.md, requirements.md, integrations.yaml and stops code edits on mismatch. Hash binding follows Spec Guard; the GitHub protected-branch rules (stale-approval dismissal, code-owner review on `docs/plan/`) give an identity-bearing record he can do from a phone. A signed or annotated git tag `plan-approved-N` marks the version. In-session ExitPlanMode approval alone is insufficient (registry notes issues #50176, #30090; Plannotator says Approve records no identity).
- (Mine) Any change to a hashed file after approval means re-approval of the diff only, shown as a plain-language change summary (change control is another facet).
- (Mine) Two-step to limit John's effort: Express path for low-risk defaults (agent says defaults aloud, per Superpowers' "A default they never heard is one they couldn't reject"), full path for anything touching money, data deletion, outbound messages.

### Gaps
- Not tested: whether a hook can reliably block edits on hash mismatch in a cloud session; spike required.
- Whether John can approve a PR from the GitHub mobile app with branch rules on a single-user repo (self-approval is not allowed by GitHub on own PRs unless a second account or bypass); not verified. A hash file plus a message-based approval may be the practical single-user route.
- Enact blog and Lodestar not opened.

## Recommendation, alternatives, rejected, spikes

Recommendation: a custom lean plan set (brief.md, requirements.md in EARS, architecture.md Mermaid, integrations.yaml, contracts/, tasks.yaml, acceptance tests, MADR for real decisions), written by the engineer after a Superpowers-style brainstorm, approved by a hash-bound approval.json plus a git tag. Free; no new tool installed.
Alternatives: OpenSpec (lighter, delta-based; fallback if a CLI-managed structure is wanted; Thoughtworks Assess Apr 2026); Kiro-style three files by hand; spec-spec-kit only as prompt patterns.
Rejected: spec-kit wholesale (verbose per Fowler and Thoughtworks), BMAD (heavy), Kiro IDE (not Claude Code), Tessl (spec-as-source, beta), Spec Guard / drft / Plannotator as dependencies (small or paid third parties; copy the hash-binding idea only). Traycer: not researched.
Spike before building: (1) write the set for one real project and time John's review; (2) hash-mismatch hook in the cloud runtime; (3) compare agent adherence with 1-page brief vs full set on one task.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Spec spec-kit (re-look) | https://github.com/github/spec-kit | Templates spec 131 / plan 113 / tasks 252 lines, NEEDS CLARIFICATION marker, read-only checklist gate | agent commands, Python CLI | 2026-10-16 | Copy marker and gate; reject wholesale (verbose) |
| OpenSpec (re-look) | https://github.com/Fission-AI/OpenSpec | proposal (1-2 pages), per-capability behaviour specs, design, tasks; Thoughtworks Assess Apr 2026 | npm CLI | 2026-10-16 | Fallback framework; behaviour-contract rule worth copying |
| Superpowers brainstorming + writing-plans (re-look) | https://github.com/obra/superpowers | Hard-gate brainstorm, committed design doc, decisions-only plans | plugin | 2026-10-16 | Use; process layer already in registry |
| Agent OS (Builder Methods) | https://buildermethods.com/agent-os/v2/workflow | Six phases: plan-product, shape-spec, write-spec, create-tasks, implement, orchestrate | agent commands | 2026-10-16 (workflow page; file names unconfirmed) | Reference only |
| Spec Guard | https://github.com/jpstone/spec-guard | MCP governance: three human gates, hash-bound approval, JSON packet in git | MCP server | 2026-10-16 (README only, not run) | Reference: copy hash-bound approval; do not install (small project) |
| Plannotator | https://docs.plannotator.ai/learn/code-context/approve-ai-coding-plan-before-execution | Local browser plan reviewer, Plan Diff; Approve records no identity | local | 2026-10-16 (docs page only) | Optional viewer; not a record of approval |
| GitHub protected-branch rules | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | Required reviews, stale-approval dismissal, code-owner review | GitHub | 2026-10-16 | Use as identity-bearing approval route; single-user self-approval caveat unverified |
| Evaluating AGENTS.md (arXiv 2602.11988) | https://arxiv.org/abs/2602.11988 | Study: context files raise cost 20%+, no reliable gain | paper | 2026-10-16 | Evidence: keep plan and rules files minimal |
| ISCAP 2026 SDD vs vibe study | https://iscap.us/proceedings/2026/pdf/6729.pdf | Spec-kit-style matched comparison: +9.2 points at ~28x tokens | paper | 2026-10-16 | Evidence |
| Thoughtworks Radar SDD / OpenSpec blips | https://www.thoughtworks.com/radar/techniques/spec-driven-development | Assess-ring critiques (lengthy specs, bitter lesson) | web | 2026-10-16 | Evidence |
| Kiro specs (re-look) | https://kiro.dev/docs/specs/ | Three files, Review comments, Quick Spec without gates | IDE | 2026-10-16 | Borrow format only |
