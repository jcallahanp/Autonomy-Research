# Autonomous engineer requirements

What a fully autonomous Claude Code engineer must do for John, written from his prompt and his
interview answers (2026-10-16) so that research and the later build can be checked against it.

## Stakeholders and users

- John: the only user in version 1. He designs and approves; the engineer does the rest.
- Later users: people John may hand the engineer to once it works. Designed for one, documented
  for many; multi-user security is out of scope for version 1.
- The research agent in this repo: a component the engineer folds into its research phase.
- The systems the engineer works on: John's GTM stack (Clay, Attio, n8n, Outreach, Slack, a
  Claude Code artifact), his health app (Whoop, Withings, Slack, blood work, Docker, Cloudflare),
  and new web apps, websites, GTM systems and Android apps.

## Goals

Each goal with the need the five whys reached.

- G1 Hands-off execution, overnight included. Need: John's time. He spends about 12 hours a day
  clicking yes, merging pull requests and making API keys, none of it cognitively demanding; he
  wants that time for designing. He stays in the loop only where his expertise matters.
- G2 A front-loaded plan with feasibility tested up front. Need: projects need him today because
  they start on a weak framework and change course midway, which breaks docs and creates the
  babysitting in G1. A strong, pre-tested start removes the reason he has to be there.
- G3 Intake that narrows the search space. Need: he does not know what he does not know; he
  names the tools he knows to get better output, and an agent that clings to those words builds
  the wrong thing.
- G4 Minimal manual setup. Need: making accounts and keys and waiting for them is hours of his
  day; it must be done once, up front, and automated wherever a service allows.
- G5 Visual briefs instead of long documents. Need: he must understand and explain the system
  without reading hundreds of pages, and a plan nobody reads is not a plan.
- G6 Context and memory discipline. Need: long sessions drift out of scope, forget to update
  documents and hallucinate; Superpowers helped but needed him at every phase.
- G7 Security testing with professional reports. Need: trust in what gets built without him
  auditing it, and without "is this secure? yes".
- G8 A packaged, repeatable setup. Need: reuse across his projects and, later, for other people.
- G9 Taking over existing systems. Need: finish half-built projects such as the GTM system
  without manual clicks.

## Anti-goals and out of scope

- No 630-page briefs. Nothing for John longer than three pages.
- No human at every phase. No check-in that a gate or a batch could have replaced.
- No endless loops. A stuck run stops and says so.
- No clinging to a bad plan or to the user's named tools when the goal says otherwise.
- Not for other users in version 1; not iOS in version 1 (no Apple developer account).
- This research pass installs or runs nothing and changes nothing in the research agent.

## Constraints

- Claude Code is the engine. Other models, harnesses and tools attach to it.
- Where the engineer runs (VPS, VM, John's computer, cloud sessions, or a mix) is decided by
  research on outcomes and portability.
- Hard gates in every project: spending money, deleting data, submitting to an app store.
  Projects may add gates.
- Approvals reach John as one batched, concise list over a light channel (SMS or similar), not
  as individual check-ins inside Claude.
- Free tiers and self-hosted first. Paid only when significantly better, with the price stated.
- Web deploys first, Android second, iOS deferred.
- Outreach is a company account with limits John does not control. Attio's App SDK is blocked at
  his organisation. Attio's API and MCP cannot create some tables and views (John's report; to
  verify), so some configuration is UI-only.
- John is on the Claude Max plan.
- His GTM repo (jcallahanp/Attio-Project) and health repo (jcallahanp/Health-Management) may be
  read; his Attio, Clay and n8n accounts are not touched in this research pass.

## Functional requirements

Intake
- R1 When the user gives a brief of any length, spoken or written, the engineer shall play back
  the goal, the constraints, the anti-goals and the parts of the brief that conflict or do not
  fit the goal before it proposes a design.
- R2 When the brief names a tool or technique, the engineer shall record the intent behind it
  and present alternatives in the same direction before adopting the named one.
- R3 When the brief asks for something that does not fit the goal, the engineer shall say so,
  explain briefly, and offer the fitting option; it shall not build the misfit silently.
- R4 When intake needs more from the user, the engineer shall ask one open question per turn
  that the user can answer by talking, and shall not ask chains of yes/no questions.
- R5 When the user does not know the options, the engineer shall present the main approaches
  with their trade-offs in a form a non-technical reader understands, then ask the user to
  choose or accept its recommendation.

Existing systems
- R6 When a project involves an existing system, the engineer shall produce an as-is map (code,
  workflows, SaaS configuration, data flows, credentials in use, known breakages) before it
  proposes changes.

Feasibility and planning
- R7 When a design has more than one viable path, the engineer shall map dependencies, keys and
  integration points for each, keep the number of candidates bounded, test candidates in
  isolated sandboxes in parallel where documentation cannot settle feasibility, and record
  negative results so they are not retried.
- R8 Before building, the engineer shall produce the plan set (requirements, architecture, data
  schema, key map, task breakdown, acceptance scenarios) and shall treat it as the single source
  of truth.
- R9 When a change of course is needed mid-build, the engineer shall record the change, update
  every dependent document in the same change, and seek re-approval when the change alters what
  the user will see or do.
- R10 When planning a project, the engineer shall list where data will flow (vendors, models,
  hosted services, logs) and the privacy risks, and shall ask the user for that project's
  limits. John's current projects default to permissive.

Setup and the human in the loop
- R11 When the plan is approved, the engineer shall produce one ordered setup list (accounts,
  keys, permissions) for a single session, verify each item automatically, and shall not ask for
  setup items piecemeal later.
- R12 Where a service allows a key or configuration to be created through an API, a CLI or
  browser automation, the engineer shall do it itself; where it cannot (two-factor, CAPTCHA,
  terms of service), the setup list shall say so and why.
- R13 Where a configuration has no API (for example Attio tables and Kanban views), the engineer
  shall perform it through browser or computer control and shall confirm the result through an
  API when one exists.
- R14 When an action is gated, the engineer shall pause that action only, add it to a batch,
  send the batch as one concise list over the configured channel, and continue other work.
- R15 While no gated action is pending, the engineer shall run without human input, overnight
  included.
- R16 When a change passes its checks and touches nothing gated, the engineer shall merge it
  itself; John shall not have to click merge for routine changes.

Execution and oversight
- R17 When a task or phase completes, a separate audit agent shall check claims against
  evidence, that tests actually ran, that documents were updated, that no secret was committed,
  and that the plan was not drifted from, and shall report what it found.
- R18 If a run makes no progress within its bound, then the engineer shall stop the loop,
  record its state and notify, instead of retrying indefinitely.
- R19 When it needs a tool it does not know, the engineer shall run a bounded discovery pass and
  log every candidate with a verdict and a reason.
- R20 When it builds software, the engineer shall run concrete security tests with pass/fail
  criteria, patch what fails, and produce a report with scope, method, findings, severity,
  remediation and retest, stating what it does not assure.
- R21 When it deploys, the engineer shall deploy web targets with no human step beyond the
  gates, Android after web, and shall not attempt iOS in version 1.

Communication
- R22 Before and after each project, the engineer shall produce a brief of at most three pages,
  mostly diagrams, dark theme, covering how the system works, the stack and where keys live,
  and what the user must do, plus a machine-oriented plan for the agent.

Packaging
- R23 The engineer shall be installable from a repeatable setup with plain-language steps for
  anything manual, so the same setup can be reproduced every time.

## Quality requirements

- Q1 When a cheaper model tier or tool is chosen for a task, the engineer shall keep it only
  while the outcome quality holds; outcome comes before cost.
- Q2 While a session runs, it shall keep its state (plan, tasks, decisions) in files so that a
  fresh session can resume it, and after a compaction it shall re-read those files before acting.
- Q3 When an overnight run ends, it shall end in a known state (done, blocked with a reason, or
  stopped by a bound), never silently.
- Q4 When the engineer reports something as done, it shall carry the evidence (test output, a
  run, a diff).
- Q5 The user-facing brief shall be at most three pages; agent-facing documents shall be sized
  to what a model reads reliably.
- Q6 Where a paid service is recommended, the recommendation shall state the price and why it is
  significantly better than the free option.
- Q7 While the engineer runs for John alone in an environment he controls, broad permissions are
  acceptable with a disclosure of the risks; this does not loosen R20 for the software it builds.
- Q8 The engineer passes acceptance when it takes John's GTM system as it stands, maps it,
  fixes the Attio tables and views, sets up the Clay workflows, cleans the data and finishes the
  tooling with no manual clicks from John after one setup session.

## Assumptions and risks

- Claude Code as the engine is a decision, not a finding; the research does not revisit it.
- "Argon 4" is Gemini's newest model with a 1M-token window per John; unverified until the
  research opens a source.
- Attio's API and MCP limits on creating tables and views are John's report; to verify.
- Terms of service of some services may forbid automated signup or key creation; R12 depends on
  what the research finds per service.
- Whether a Max subscription may run Claude Code unattended on a server is unverified.
- John's view that outcomes would be about the same with stronger direction up front is the
  hypothesis the whole design rests on; Q8 is its test.
- Superpowers, Beads and Ralph are sources of ideas, not components; which ideas survive is a
  research outcome.

## Audit

Missing
- No time budget or deadline was stated. Listed as a gap.
- The approval channel is "SMS or similar"; the channel is not fixed. Listed as a gap.
- The cap on candidate paths in R7 is unset. Listed as a gap.
- Per-project gates beyond the three in Constraints are handled by R10 and R14 but no template
  for stating them exists yet. Listed as a gap.

Inconsistent
- G1 (hands-off) against John's "I do need to be in the loop": resolved by his own words, he
  stays in at design and approval level; R14 and R15 together carry it.
- His "immutable plan" against R9 (update docs on a change of course): resolved as a
  change-controlled plan in the readback, and he did not object.
- Broad permissions (Q7) against rigorous security testing (R20): two different subjects, kept
  as separate statements.
- R16 (the engineer merges routine changes itself) against the current project practice where
  John merges pull requests himself. For the engineer he asked for exactly this, so R16 stands
  as the default; John confirms or narrows it.

Redundant or untestable
- "Cutting edge" and "maximum capability" are intent, recorded under G1 and R2, not as
  requirements, because they cannot be tested.
- R15 and Q3 overlap on overnight runs; kept, one states behaviour and the other the end state.

Count: 23 functional requirements, 8 quality requirements.

## Gaps

- Time budget or deadline for the engineer project. None stated.
- The approval channel: SMS, Slack, Telegram or another; John said "SMS or similar".
- The number of candidate paths the engineer may keep in R7.
- A template for per-project gates and privacy limits (R10, R14).
- Whether R16 (self-merge of routine changes) has limits, for example production deploys.
