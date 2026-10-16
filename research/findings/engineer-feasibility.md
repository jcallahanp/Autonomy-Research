# Engineer feasibility: mapping integrations and testing a bounded set of candidate paths

Before the autonomous Claude Code engineer commits to a stack, it should run a fixed feasibility protocol made of files. The protocol has five parts. (1) **Map.** Three small artifacts written from facts rather than memory: a plain Mermaid context-plus-container map with one sequence diagram per critical flow, gated by a parser check because LLM-written Mermaid is about 70% valid unchecked and 95% with a render-and-repair loop (https://llm-enabled-development-41d6d8.pages.cms.hu-berlin.de/en/archiv/experiments/diagram/diagram-long/, https://github.com/jasonworden/mermaid-lint); an integration matrix with one row per edge; and one integration card per service from a 12-point edge-case checklist built on Stripe's and Google's rules (https://docs.stripe.com/webhooks, https://developers.google.com/identity/protocols/oauth2, https://google.aip.dev/194). (2) **Bound.** Look up dead ends and do a desk check first. Run a real trial only for behavioural claims (auth, rate limits, webhooks, pagination, UI-only, go/no-go), because "Real APIs diverge from documentation" (https://qapractices.com/checklists/third-party-integration-testing-checklist/). Then test at most three paths, one question each, with the pass line fixed before the run (https://builderscamp.com/guides/other/riskiest-assumption-test), a box in turns, wall-clock time and USD, and a forced decision when the box ends (https://agilesm.net/spike-enabler-story.html, https://code.claude.com/docs/en/best-practices). (3) **Sandbox.** One worktree and one `claude -p` process per trial, run as a non-root user inside a `--network none` container that reaches a host proxy. The proxy allowlists hosts and injects a scoped test credential. The built-in Bash sandbox stays on as an inner layer only, because Anthropic says it alone "is not sufficient for fully unattended runs" (https://code.claude.com/docs/en/sandbox-environments, https://code.claude.com/docs/en/agent-sdk/secure-deployment). The supervisor, not the agent, writes `result.json` and tears the trial down (https://code.claude.com/docs/en/headless). (4) **Decide.** Pass/fail gates first, then coarse High/Medium/Low ratings against a datum, each with an evidence tag, under criteria John ranks and freezes before scoring. Near-ties count as ties and are settled by reversibility (https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/, https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model, https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf). The decision is recorded as a MADR ADR whose status John edits (https://adr.github.io/madr/). (5) **Record and hand off.** Negative results go to a greppable dead-ends file with the version tested and a retry-when condition (https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md, https://pypi.org/project/epitaph/). The chosen path becomes one setup list in dependency order, which John works through in one local sitting with Claude in Chrome; Chrome pauses at login and CAPTCHA for him (https://code.claude.com/docs/en/chrome). The research agent's spike skill blocks every build-time need: three user-named paths, no credentials, an isolation recipe the agent is only told to follow, the worker cleaning up after itself, and a prose-only result (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14,16,28-29). It needs a separate "trial" mode, not looser rules. Overall confidence: medium. The mechanics are primary-sourced. The rubric, bounding numbers, checklist and setup-list format are worker syntheses, and none has been run on John's systems.

## Questions and answers

### Q1. Which mapping artifacts should the engineer produce, and how do they stay valid?

**Confidence: medium.** The 70% and 95% validity figures come from one student project. No opened source measured whether diagrams stay current across design changes.

C4's own guidance is that "the system context and container diagrams are sufficient for most software development teams" (https://c4model.com/diagrams). Mermaid's own C4 diagram type is "experimental" and its syntax "can change" (https://mermaid.js.org/syntax/c4.html). The Structurizr DSL is a text model of the same architecture (https://docs.structurizr.com/dsl). Worker inference (not in the source quote): it exports to PlantUML and Mermaid; D2 export is not confirmed. Measured once, LLM-generated Mermaid rose "from an initial 70% to 95%" with a validation pipeline, and the model's own repair of invalid code "is only successful in about 80-85% of cases" (https://llm-enabled-development-41d6d8.pages.cms.hu-berlin.de/en/archiv/experiments/diagram/diagram-long/). mermaid-lint uses "the official `mermaid.parse()` API" (https://github.com/jasonworden/mermaid-lint). Worker inference (not in the source quote): it is MIT-licensed, runs through `npx` on Node 22+, and exits 1 on failure, so it can serve as a hook or CI gate. One agent-driven repo found that "Agents cannot \"see\" a broken diagram" and added a render gate in CI (https://github.com/juliusz-cwiakalski/agentic-delivery-os/pull/123). OpenAPI (https://learn.openapis.org/) and AsyncAPI (https://www.asyncapi.com/docs/tutorials/getting-started) are the machine-readable contracts for REST and for events. EventStorming is "a flexible workshop format" for people, not something an agent outputs (https://www.eventstorming.com/). A Claude Code plan "is a review gate, not a committed document, unless you explicitly save it" (https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/), so every artifact must be written to a file.

**Minimum set (worker synthesis).** Three files:
1. `docs/map/integration-map.md`: a plain Mermaid `flowchart` at context-plus-container level, labelled with the C4 level, plus one `sequenceDiagram` per critical flow, only for the flow being built.
2. `docs/map/integration-matrix.md`: one row per edge, with columns for direction, protocol, auth, data moved, contract source, evidence/status and failure mode.
3. One integration card per service (Q7).

OpenAPI and AsyncAPI files are inputs the matrix points to, not separate deliverables. This extends the earlier as-is pack: "C4 context-plus-container Mermaid, system-of-record table, credential inventory", with each row marked observed, inferred or asserted (/home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:83). It also extends the intake rule to offer a diagram only after John picks an option (/home/user/Autonomy-Research/research/findings/engineer-intake.md:51). Worker inference: the matrix carries the most value because a table is reliable for an LLM to write, diffs cleanly in git, can be checked by script for empty cells, and holds the evidence column that path comparison needs. For John's GTM system, the edges come from config snapshots rather than a code graph. AWS lists "Interfaces (APIs and published contracts)" as a decision area worth an ADR (https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html), so matrix rows map onto ADR triggers.

**Staying valid (worker inference, untested).** Generate the map from facts (config snapshots, OpenAPI files), not memory. Put a parse gate (mermaid-lint) in a Stop or PostToolUse hook. Give each diagram a source-of-truth pointer and a last-verified date, and have a check flag the diagram when the pointed-to file changes. No opened source shows this done for integration maps.

**Contradictions.** One page holds both sides of this. The PR text at https://github.com/juliusz-cwiakalski/agentic-delivery-os/pull/123 says "AVOID Mermaid C4 (renders in tooling, not on GitHub)". A later comment in the same PR, as reported by the fetch tool (commits 98e4f73, 87ef6bb, no verbatim quote), says GitHub now renders C4 and the restriction was removed. Mermaid still labels C4 experimental (https://mermaid.js.org/syntax/c4.html). Unresolved: default to plain flowchart and sequence diagrams, and spike a C4 render on John's viewer. Listed under Open questions.

### Q2. How are paths represented and compared on evidence, and how is the decision recorded?

**Confidence: medium-high on the method, medium on the criterion list, which is a synthesis.**

A path is one combination of tool choices. Represent it as one row-set in a matrix:

- **Gates first.** Pass or fail, with evidence. A mandatory requirement "belongs in a pass/fail gate before scoring, not blended into a percentage" (https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model).
- **Then coarse ratings.** Stakeholders "cannot reliably and repeatably make finer distinctions than High, Medium, and Low" (SEI, https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf). A Pugh matrix is a "non-numeric and iterative tool for concept selection" that compares each option to a datum (https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/).
- **Weights frozen, ties declared.** Weights are defensible "only when the criteria and weights are locked before anyone scores", and "A 6.75 versus 7.00 result is a tie that deserves a conversation, not a verdict" (https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model).
- **Reversibility.** The rune-kit rubric scores it 1-5 by "how expensive is it to change your mind later?" (https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md).

**Proposed rubric (worker synthesis).**
- Gates: works with the accounts and permissions John actually has; no secret leaves its allowed boundary; health data goes to no unapproved processor; free, or priced within John's limit.
- Ratings, each H/M/L with a separate evidence tag (spiked = ran it; documented = vendor page opened; asserted = unverified): feasibility evidence, John's effort, cost, maintenance, reversibility, lock-in, privacy risk.
- Order of judgement, per the ruling: outcome quality first, then John's effort, then cost. The rest break ties.
- John ranks 3 or 4 criteria once (rank order, not percentages). The ranking is frozen in the decision file, and a sensitivity check asks whether swapping the top two changes the winner. If it does, the result is reported as a tie.
- The datum is the cheapest or current path.
- Worker inference: for the riskiest choice, 3 to 5 concrete mini-ATAM scenarios.

**Recording.** MADR is "a streamlined template for recording architectural significant decisions", with drivers, considered options, pros and cons, and a confirmation field: "Describe how the implementation of/compliance with the ADR can/will be confirmed" (https://adr.github.io/madr/). Further rules for the record:
- An ADR should be "one or two pages long". A reversed one is kept "but mark it as superseded" (https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions).
- Accepted ADRs are immutable, and approval adds "a timestamp, version, and list of stakeholders" (https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html).
- ADRs belong "close to your application code" and are written when there are "two or more engineering options" (https://docs.cloud.google.com/architecture/architecture-decision-records).
- "Agents like Claude Code don't know past team decisions", so a CLAUDE.md rule should force an ADR scan before design changes (https://zenn.dev/kosk_t/articles/adr-lightweight-decision-records-for-ai?locale=en).
- Kiro's `design.md` "map[s] cleanly onto Architecture Decision Records" (https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/).
- Write an ADR only when a decision is hard to reverse and a real trade-off. "Conventions are choices everyone makes the same way" (https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md).
- The earlier intake protocol already requires "approval recorded in a file, not via ExitPlanMode alone" (/home/user/Autonomy-Research/research/findings/engineer-intake.md:77).

**Proposed ADR (worker design).** MADR sections plus: the gate table, the rated matrix with evidence tags, John's frozen criterion order and date, a sensitivity note and tie flag, "what would change this decision" triggers, links to spike results, a status line (`proposed -> accepted by John <date>` or `accepted over objection`), and a plain-language summary at the top: "We chose X because Y; the cost is Z; you can undo it by W". The matrix lives in a linked file. No opened source shows a tool that compares integration paths on gathered evidence, so this part is custom.

**Contradictions.** The weighted-scoring page treats a frozen-weight sum as defensible (https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model). Jacqui Read argues weightings are a workaround: "These need to be reassessed when criteria are added and removed", so criteria should be split to the same level of abstraction instead (https://jacquiread.com/posts/2024-09-11-decision-making-adrs-weightings-are-a-workaround/). The evidence favours gates plus coarse ratings with no summed decimals, because the SEI three-level limit (https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf) and the weighted-scoring page's own tie warning both undercut fine-grained sums. Frozen weights remain an alternative if John wants a single number. A third view, that summed weighted scores should be "avoided entirely" (an engmanage substack post), was seen only in a search result and is excluded (see Open questions).

### Q3. Spike practice and the bounding rule

**Confidence: medium.** Definitions are high confidence. No source sets agent-scale boxes, the turn number is a worker proposal, and the desk-vs-trial rule is the worker's own.

**Definitions.**
- A spike or prototype is disposable: "Prototyping generates disposable code", while "Tracer code is not disposable: you write it for keeps" (https://flylib.com/books/en/1.315.1.25/1/).
- A walking skeleton is a "tiny implementation of the system that performs a small end-to-end function" and is "production code", not a prototype (https://codeclimate.com/legacy/kickstart-your-next-project-with-a-walking-skeleton).
- Set-based design "considers a broader range of possible designs and delays certain decisions longer" (https://sloanreview.mit.edu/article/toyotas-principles-of-setbased-concurrent-engineering/).

Worker inference: the feasibility trial is a spike. A passing spike hands the build a walking-skeleton task, not its own code. The part of set-based design worth borrowing is "eliminate infeasible or dominated options and write down why", not "carry many options long".

**Boxes and kill rules.**
- Spikes "should be time-boxed in short increments (1-3 days)", and "Batching learning is worse than batching other kinds of work" (https://dojoconsortium.org/docs/work-decomposition/spikes/).
- Integration spikes take "One to two weeks for a team that already has access, environments, and a clear vertical slice" (https://baaz.pro/blog/how-to-estimate-api-integration-work).
- A spike succeeds "when it leads to a clear choice (proceed, pivot, reduce scope, or drop the approach)". Without a box, "It runs until someone feels finished" (https://agilesm.net/spike-enabler-story.html).
- One assumption per test: "One per test." "The pass line is set before the test runs." "feasibility needs an engineering spike." (https://builderscamp.com/guides/other/riskiest-assumption-test)
- Claude Code docs: "After two failed corrections, `/clear` and write a better initial prompt". Fan out only after testing on "the first 2-3 files". They name "The infinite exploration" as a failure mode (https://code.claude.com/docs/en/best-practices).
- The earlier context protocol already gives each task "two attempts per task, then a blocked note" under supervisor caps (/home/user/Autonomy-Research/research/findings/engineer-context.md:119).

**Candidate count.** "Simple fact-finding requires just 1 agent with 3-10 tool calls", and "multi-agent systems use about 15× more tokens than chats" (https://www.anthropic.com/engineering/multi-agent-research-system). When the verifier is imperfect, "optimal sampling attempts are often fewer than 10" (https://arxiv.org/abs/2411.17501). Parallel runs cost about linearly: "Three models on one task is roughly three times the tokens of one run" (https://docs.arantic.com/cursor/parallel-agents). Worker inference: keep the cap of 3. No opened source supports more than 5 for feasibility trials.

**Proposed bounding rule (worker inference, unvalidated):**
1. Dead-end lookup and desk check before any worker is dispatched.
2. Run the cheapest probe that could kill the riskiest assumption first.
3. At most 3 paths, one question, pass line written first.
4. Per-worker box in turns, wall-clock time and `--max-budget-usd`. The suggested box of one working session or about 60 turns is the worker's own unvalidated number.
5. When the box ends, report "inconclusive" and stop.
6. Two failed fix attempts on the same blocker: record and stop.
7. Each parallel worker varies the path and keeps the probe fixed, with a deterministic pass condition.

**Desk research vs trial.** No standard heuristic was found. "Real APIs diverge from documentation. Validate every behavior empirically" (https://qapractices.com/checklists/third-party-integration-testing-checklist/). "Sandboxes that diverge from production teach you the wrong lessons" (https://baaz.pro/blog/how-to-estimate-api-integration-work). Worker inference: a trial is required when the claim is behavioural rather than documented; concerns auth, rate limits, quota, webhooks or pagination; is UI-only; comes from a sandbox or from docs older than the last vendor release; or is a go/no-go dependency. Desk research is enough when the fact is documented, versioned, reversible and cited with a date. Only "observed" evidence counts for dependency decisions.

**Contradictions.**
- **Box length.** Dojo sets 1-3 days (https://dojoconsortium.org/docs/work-decomposition/spikes/); Baaz sets 1-2 weeks for third-party integrations once access exists (https://baaz.pro/blog/how-to-estimate-api-integration-work). The worker reads this as a difference of domain, not an error. Neither source gives an agent-scale box in turns, so the agent box is unresolved and listed under Open questions.
- **Is a spike disposable?** Baaz says "A spike is not a scrappy prototype you throw away by default" (https://baaz.pro/blog/how-to-estimate-api-integration-work). The Pragmatic Programmer says "Prototyping generates disposable code" (https://flylib.com/books/en/1.315.1.25/1/). Worker reconciliation: keep the spike's evidence and decision, throw away its code, and build the skeleton fresh. The evidence favours this because Baaz's point concerns evidence, not code.
- **Parallelism.** Anthropic says "most coding tasks involve fewer truly parallelizable tasks than research" (https://www.anthropic.com/engineering/multi-agent-research-system). Claude Code docs promote `/batch` across "5 to 30 subagents" (https://code.claude.com/docs/en/best-practices). The worker reconciles these by task type: `/batch` suits independent, same-shaped edits, and competing-path trials are independent candidates, which fits parallel work.
- **Workers disagree on the cap.** The spike-practice note recommends keeping the fixed 3-worker cap; the trial-sandboxes note recommends a configurable cap tied to John's quota in trial mode. Both are inferences. The cited evidence (sub-10 sampling returns, linear cost, 2-3-first fan-out) supports 3 as the default. Making the cap configurable is not contradicted, but no source supports a number.

### Q4. Recording negative results so they are not retried

**Confidence: medium.** The agent-era tools are young and unvetted.

Three working formats exist:
1. **ADR "Considered Options".** Each rejected option gets a "Bad, because" line (https://adr.github.io/madr/decisions/adr-template.html).
2. **Dated negative-results registry.** Its purpose: "A list of experiments that lost, so the next session skips a known-dead path." It ends each entry with "**Decision**: rejected | deferred | revisit-if <condition>" and requires "Evidence must be a location (`file:line`, eval path, PR #, or `learning.db topic/key`), not a claim" (https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md).
3. **Machine-checkable ledger.** epitaph is "the **repo-scoped attempt ledger**: one JSON file per rejected attempt, committed to the repo, queryable by machine before the retry happens", with a `--retry-when` condition (https://pypi.org/project/epitaph/).

A scratchpad gist adds two rules: "record only approaches that were actually attempted and explain concretely why they failed", and "Before performing any task, read .ai_scratchpad.md." (https://gist.github.com/corpulent/f7fbad0a4d9cdb6a5d4f31d249a2341c). Two warnings apply:
- Auto-capture without a recurrence check wastes tokens: "74% of the corpus (1,849 of 2,490 rows) was one-off" (https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md).
- Failed attempts left in context hurt: "the context is cluttered with failed approaches" (https://code.claude.com/docs/en/best-practices).

Spike write-ups must say "what options were ruled in or out" (https://agilesm.net/spike-enabler-story.html).

**Proposed record (worker inference).** A flat, greppable `dead-ends.md` with these fields: path, date, version or commit tested, probe, result, evidence location (command and output), `retry-when` condition, and an expiry hint for fast-moving tools. Rejections made on paper are labelled `desk-rejected` so they are not mistaken for observed failures. The first step of spike, intake and engineer planning greps this file and the tool registry before dispatching a worker. On a match, the prior result is stated and the `retry-when` condition must hold before a retry. Copy the record shape, not the tools: epitaph and dsh-negative-ledger are v0.x and unvetted. The worker infers that a hook will enforce this better than prose; this is untested and is a spike item.

### Q5. Sandboxing parallel trials that need credentials and network

**Confidence: medium.** The Claude Code mechanics are high confidence. Whether John's VM exposes KVM, and the Podman specifics, are unknown.

**What Claude Code provides.**
- File isolation: `--worktree` creates "an isolated worktree" (https://code.claude.com/docs/en/worktrees). Subagents get "a temporary worktree that Claude Code removes automatically when the subagent finishes without changes".
- Limits of worktrees: "Non-interactive runs with `-p` have no exit prompt, so Claude doesn't clean up their worktrees"; "None of them tracks which files a shell command writes"; and `.worktreeinclude` is the one path by which `.env` files reach a worktree (same page).
- "Agent teams don't isolate teammates in worktrees". Agent view is a "Research preview" (https://code.claude.com/docs/en/agents).
- The Bash sandbox "covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it". Its domain allowlist starts "empty". On Ubuntu 24.04+ it needs an AppArmor change for bubblewrap. It can mask credentials with a placeholder "sentinel", but "There is no built-in credential deny list" (https://code.claude.com/docs/en/sandboxing).
- The allowlist checks "the client-supplied hostname and does not terminate or inspect encrypted traffic" (https://code.claude.com/docs/en/agent-sdk/secure-deployment).
- Anthropic's verdict: the sandbox "on its own constrains only shell commands, so it is not sufficient for fully unattended runs in either mode". Skip-permissions refuses to run as root (https://code.claude.com/docs/en/sandbox-environments).

**Local boundary (recommended).** Anthropic documents a hardened container that "Removes all network interfaces; the agent communicates through the mounted Unix socket". "The recommended approach is to run a proxy outside the agent's security boundary that injects credentials into outgoing requests" (https://code.claude.com/docs/en/agent-sdk/secure-deployment). The same page warns:
- "Even read-only access to a code directory can expose credentials."
- "Node.js `fetch()` ignores these variables by default", so the network must fail closed rather than rely on proxy variables.
- gVisor is "Up to 10-200× slower for heavy open/close patterns".
- Firecracker can "boot VMs in under 125ms with less than 5 MiB memory overhead".

Anthropic's reference devcontainer firewall "supports running Claude Code with `--dangerously-skip-permissions` for unattended work". Unprivileged containers need `enableWeakerNestedSandbox`, and Anthropic rates a full VM's effort "High" (https://code.claude.com/docs/en/sandbox-environments). Rootless Podman needs UID ranges in "/etc/subuid and /etc/subgid" (https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md).

Worker inference: each trial gets its own allowlist file for the host proxy and a short-lived test-account token the proxy injects, never an environment variable in the worker. Setup is roughly one day of one-off work, starting from Anthropic's reference devcontainer.

**Docker Sandboxes (sbx) alternative.** "The raw credential values never enter the VM" (https://docs.docker.com/ai/sandboxes/security/). Requirements: "KVM hardware virtualization" and the `kvm` group, "Ubuntu 24.04 or later" (https://docs.docker.com/ai/sandboxes/install/). Behaviour: "Removing a sandbox deletes everything inside it" (https://docs.docker.com/ai/sandboxes/get-started/); "Sandboxes don't pick up user-level configuration from your host, such as `~/.claude`" (https://docs.docker.com/ai/sandboxes/agents/claude-code/); and in clone mode "Your repository is mounted read-only" (https://docs.docker.com/ai/sandboxes/security/). Worker inference: if John's VM is a cloud VM, nested KVM may be missing, which would rule out sbx and Firecracker. `ls /dev/kvm` decides.

**Hosted options are the exception path.**
- E2B: a "pre-built `claude` template", but "sandboxes can reach the open internet by default" (https://docs.e2b.dev/agents/claude-code). It offers "One-time $100 in usage credits", "Up to 1 hour per sandbox session", "Up to 20 concurrently running sandboxes", and a "$150 monthly plan fee, plus usage" tier (https://e2b.dev/pricing). Worker inference (not in the source quote): E2B's example passes the API key as an env var inside the sandbox.
- Daytona: "$200 in free compute included" and "Sub 90ms sandbox creation" (vendor claim) (https://www.daytona.io/pricing).
- Vercel Sandbox: Hobby sessions of 45 minutes against 24 hours on Pro, 10 concurrent sandboxes on Hobby, creation "paused" when the quota is used, a 30-minute 4-vCPU build-and-test costing "$0.1104", downloads free, and snapshots expiring "30 days after their last use" (https://vercel.com/docs/vercel-sandbox/pricing).
- Modal: "$30 / month free credits" and "$0.00003942 / core / sec" (https://modal.com/pricing). Worker inference (not in the source quote): about 3x the container price.
- Cloudflare Sandbox SDK: runs "coding agents such as Claude Code" per task, "Available on Workers Paid plan" (https://developers.cloudflare.com/sandbox/).

Worker inference: every hosted option puts the repo and any injected token on a third party, and no hosted page opened documents a credential-injecting egress proxy. So hosted wins on effort only for one-off probes of public code.

**Contradictions.**
- **Docker on the VM.** The earlier runtime recommendation says "no Docker is required for this route" (/home/user/Autonomy-Research/research/findings/engineer-runtime.md:418-419, citing https://code.claude.com/docs/en/sandbox-environments). The new notes put trials inside Docker or Podman because the Bash sandbox alone "is not sufficient for fully unattended runs" (https://code.claude.com/docs/en/sandbox-environments). These apply to different scopes. The engineer's main process can stay Docker-free, but trials holding network and credentials need a container or microVM. The new evidence wins for trials, and this adds Docker or Podman to the VM bootstrap.
- **`--bare` vs subscription login.** `--bare` is recommended for scripts, yet "In bare mode, Claude Code never reads OAuth credentials" (https://code.claude.com/docs/en/headless). The runtime recommendation keeps `/login` subscription auth and an API key "only as an overflow fallback with `--max-budget-usd`" (/home/user/Autonomy-Research/research/findings/engineer-runtime.md:439-441). Without `--bare`, a `-p` run "runs the hooks in a project's `.claude/settings.json` and connects the servers in its `.mcp.json`" (https://code.claude.com/docs/en/headless). This is unresolved until spiked: either use `--bare` with a trial-only API key and budget cap, or run non-bare in a directory with a clean settings file.

### Q6. Result capture and teardown

**Confidence: medium.** The record schema is the worker's design.

`--output-format json` returns "structured JSON with result, session ID, and metadata", including `total_cost_usd`. With a schema, the answer lands in "the `structured_output` field". The process "exits with code 0 on success and a non-zero code when the run fails". Denials appear in `permission_denials` (https://code.claude.com/docs/en/headless). The same page sets limits on these signals:
- Cost figures are "client-side estimates".
- SIGTERM gives "exit code 143" and no result for the in-flight turn.
- Idle background work is dropped "after 10 minutes".
- Hitting `--max-budget-usd` "stops the remaining background work".

For teardown, Anthropic recommends an overlay filesystem so "the agent [can] write without modifying underlying files", and a tmpfs "cleared when the container stops" (https://code.claude.com/docs/en/agent-sdk/secure-deployment). After unattended runs, "Review the paths you kept writable" (https://code.claude.com/docs/en/sandbox-environments). On hosted Vercel, "Call `sandbox.stop()` when done" and use Spend Management to "pause projects" (https://vercel.com/docs/vercel-sandbox/pricing).

**Proposed (worker inference).** The supervisor writes `result.json`, never the agent: `{trial_id, path, question, probe, verdict, exit_code, duration_s, cost_usd, network_hosts_denied, creds_used (names only), artifacts[], log_path, teardown: ok|failed, started, ended}`. A failed teardown blocks the verdict. Caps come in three layers: `--max-budget-usd` and `--max-turns` per run, a wall-clock `timeout` (exit 143), and a per-night total. The container or VM lifecycle guarantees teardown (`--rm`, `sbx rm`, `git worktree remove`), backed by a sweep at engineer start (`git worktree list`, labelled containers, old temp dirs). Prose notes are kept for negative results.

### Q7. The integration edge-case checklist, applied to John's services

**Confidence: medium.** Stripe and Google are primary sources. Several per-service values are not in the quoted text and are marked below.

**Checklist (worker synthesis, 12 points):**
1. Auth type.
2. Token lifetime and rotation (store the new refresh token atomically).
3. Scopes, and who may grant them.
4. Rate limit, window, 429 handling and Retry-After.
5. Pagination and offset caps.
6. Webhook signature and timestamp.
7. Webhook retries, ordering and duplicates, plus a reconciliation poll.
8. Idempotency for every write.
9. Sandbox or test mode vs production.
10. API version pinning and deprecations.
11. Plan or role gating.
12. Data residency, ToS and rules on automated accounts.

Rule (worker inference): any "no" on points 2, 3 or 11 becomes a human setup step, and a "no" on point 7 means designing a polling reconciler.

**Sources for the generic points.**
- Stripe webhooks: return `2xx` quickly "before any complex logic"; "Any manipulation to the raw body of the request causes the verification to fail"; ordering is not guaranteed; "the same event more than once" can arrive; replay tolerance is "5 minutes"; delivery retries run "for up to three days" live but "three times over the course of a few hours" in a sandbox; the payload version follows the account's API version; secret rotation can overlap "up to 24 hours" (https://docs.stripe.com/webhooks).
- Stripe idempotency: keys are pruned after "at least 24 hours", and reusing a key with different parameters "errors" (https://docs.stripe.com/api/idempotent_requests).
- Google OAuth: an app in Testing status "is issued a refresh token expiring in 7 days"; tokens expire after "six months" unused; the cap is "100 refresh tokens per Google Account per OAuth 2.0 client ID" (https://developers.google.com/identity/protocols/oauth2); Testing apps are limited to "100 test users" (https://support.google.com/cloud/answer/15549945).
- Retries: "Clients should not automatically retry requests in which repeated runs would cause unintended state changes". UNAVAILABLE is "generally transient" (https://google.aip.dev/194).

**Per-service facts, quoted.** Values marked "worker inference (not in the source quote)" come from the worker's reading of the page, not from the quoted line.
- **Attio.** Rate-limit responses are "always" 429 (https://docs.attio.com/rest-api/guides/rate-limiting). Worker inference (not in the source quote): 100 reads/s, 25 writes/s, Retry-After. Webhooks retry "up to 10 times with an exponential back-off" with "a 5 second timeout" (https://docs.attio.com/rest-api/guides/webhooks). Worker inference (not in the source quote): `Attio-Signature` header. "Only workspace admins can grant a workspace-level token" (https://docs.attio.com/rest-api/guides/authentication).
- **Clay.** "Webhook sources are limited to 50,000 submissions, and this limit persists even after deleting rows" (https://university.clay.com/docs/webhook-integration-guide). "Tables are Enterprise only." (https://developers.clay.com/). Clay's API auth and rate limit are unconfirmed.
- **n8n.** The API "isn't available on the free trial" (https://docs.n8n.io/connect/n8n-api). "Non-Enterprise API keys have full access to all the account's resources and capabilities", and the key is created in Settings and copied (https://docs.n8n.io/connect/n8n-api/authentication.md).
- **Outreach.** "10,000 requests per hour" per user (https://developers.outreach.io/api/getting-started). Building against it requires that "you need to create an Outreach app" (https://developers.outreach.io/api/oauth/). Worker inference (not in the source quote; the tool paraphrased the page): development credentials are immediate, production credentials follow a review, and the access token `expires_in` is 7200.
- **WHOOP.** "Existing access tokens are invalidated once your app uses the refresh token" (https://developer.whoop.com/docs/developing/oauth). The limit is "100 requests per minute." (https://developer.whoop.com/docs/developing/rate-limiting). Worker inference (not in the source quote): `offline` scope, 10,000 requests/day. Webhooks retry "five times over the course of about one hour", and "It is possible that a webhook may be missed." (https://developer.whoop.com/docs/developing/webhooks).
- **Withings.** "Do not poll more than once every 10 minutes per user". "Add `&mode=demo` to test without a real device". "No contract required" (https://developer.withings.com/llms.md). Worker inference (not in the source quote): access token 3 h, refresh token 1 year with rotation, old token valid 8 h, auth code valid 30 s. Webhook retry and signing are unconfirmed.
- **Slack.** Existing installs of non-Marketplace apps keep the old limits (https://docs.slack.dev/apis/web-api/rate-limits). Request timestamps must be within "five minutes" (https://docs.slack.dev/authentication/verifying-requests-from-slack). "Token rotation may not be turned off once it's turned on." (https://docs.slack.dev/authentication/tokens). Worker inference (not in the source quote): 12 h token expiry. `apps.manifest.create` needs "An app configuration access token." (https://docs.slack.dev/reference/methods/apps.manifest.create).
- **Cloudflare.** "1,200 requests per five minute period per user" (https://developers.cloudflare.com/fundamentals/api/reference/limits/). "The token secret is only shown once." (https://developers.cloudflare.com/fundamentals/api/get-started/create-token/). Worker inference (not in the source quote): the same page names a `/user/tokens/verify` check. "Account-owned API tokens cannot create accounts." (https://developers.cloudflare.com/fundamentals/account/create-account/).
- **Vercel.** "Account Webhooks are available on Enterprise and Pro plans" (https://vercel.com/docs/webhooks). Rate limits reset "after the **Duration** has expired" (https://vercel.com/docs/limits). Worker inference (not in the source quote): `x-vercel-signature`, secret shown once, 60 domain deletes/min.
- **Supabase.** "PATs are tokens with a custom expiry" (https://supabase.com/docs/reference/api/introduction). Worker inference (not in the source quote): 120 Management API calls/min. Supabase "is deprecating the `anon` and `service_role` keys by the end of 2026", and the secret key "bypasses Row Level Security" (https://supabase.com/docs/guides/api/api-keys). Database webhooks are "asynchronous" (https://supabase.com/docs/guides/database/webhooks).
- **Google OAuth.** See the generic sources above.

**Applied to John (worker inference).**
- WHOOP, Withings, and Slack with rotation on need a token store that is written on every refresh. The engineer should state this as a requirement.
- Google: move the consent screen to "In production", or the refresh token dies weekly. Whether sensitive scopes need verification was not tested.
- Withings and WHOOP: plan a poll-based reconciler.

### Q8. Turning results into an ordered human setup list

**Confidence: low-medium.** The pause points rest on a primary source. The order and row format are worker design, and no source gives time estimates.

**Pause points and human-only facts.**
- Claude in Chrome: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually". It refuses to upload credential-named files such as `.env`, `.pem` or `.key`. Chrome integration stays off under API-key or setup-token auth (https://code.claude.com/docs/en/chrome).
- A practitioner handoff "records a handoff with four parts: what it saw, the one action you take, where you take it, and the signal that lets it continue". Some platform terms state "Accounts registered by \"bots\" or other automated methods are not permitted." (https://launchrepo.dev/guides/ai-agent-captcha-2fa-handoffs/, a secondary source).
- Cloudflare: adding accounts needs "the Super Administrator role on an existing account" (https://developers.cloudflare.com/fundamentals/account/create-account/).
- Supabase on the Vercel marketplace: one install will "create a Supabase project and sync" environment variables (https://supabase.com/docs/guides/integrations/vercel-marketplace).
- Attio: workspace tokens need an admin (https://docs.attio.com/rest-api/guides/authentication).
- n8n: the key is copied from the UI (https://docs.n8n.io/connect/n8n-api/authentication.md).
- Requirement R11: "When the plan is approved, the engineer shall produce one ordered setup list" (/home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:105-110). G4 asks for "Minimal manual setup." (/home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:29).

**Proposed list (worker inference).**

Order by dependency:
1. Human identity and billing accounts.
2. Workspace roles and plan tier.
3. App registration (the agent can prefill; Slack apps can be created from a manifest).
4. Consent clicks as the data owner.
5. Secrets pasted by John into the vault (names only reach the agent).
6. An automated verification call per service.

Who does what:
- **Human only:** first account per vendor, billing or plan upgrades (n8n API needs paid cloud or self-host, Vercel webhooks need Pro, Clay Tables need Enterprise), OAuth consent, 2FA, and copy-once secrets.
- **Agent, in a local session with Claude in Chrome open:** navigate, prefill forms, create apps from a manifest, run verification calls. Cloud sessions cannot do this.

How the page looks:
- One page, grouped by service.
- Long waits first, as "start now, finish later", for example Outreach production review and Google verification if needed.
- Each row gives: what you do, where (URL), how long (labelled an estimate), what you hand back (secret name, never the value), and the one-command check the agent runs afterwards.
- The page ends with an "agent verifies all" pass/fail table that names the first failing row.

Example row: `[ ] 4. Slack -- create app from manifest (agent prepares) -- you click Install as workspace admin -- 3 min -- paste SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET into vault -- verify: auth.test returns ok`.

Example order for John: Google Cloud project → consent screen to production → OAuth client → consent → token; Cloudflare account → scoped token → verify; Vercel team (Pro if webhooks) → token; Supabase via marketplace or own org → PAT; Slack admin → manifest app → install → bot token and signing secret; Attio admin → key; n8n self-host → key; WHOOP and Withings developer apps → redirect URI → consent; Outreach dev app → production review (start first); Clay → check plan.

The whole sitting is estimated at about 45-90 minutes across 11 services. This is the worker's own unsourced estimate.

### Q9. Concrete gaps in the research agent's spike skill

**Confidence: high on the gaps**, which are read directly from the files. **Medium on the fixes.**

The skill's rules today:
- "The skill shall test only paths the user named, and shall not add a path of its own." (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14)
- "at most three workers in parallel" (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:16)
- "no credentials beyond read-only search keys" (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:28)
- a path that needs an account, a write token or a payment is reported "blocked" (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:28-29)
- the network recipe passes "only the proxy variables" (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:40-44)
- step 1 says "Confirm ... with the user in one message" (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:52)
- relaxing isolation needs "the user's own message" quoted (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:34-35)
- output goes to `research/spikes/<slug>.md` via the synthesizer (/home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:64,68)

The worker's rules today:
- isolation is a temp-dir recipe: "Every install, clone or run of the candidate happens in a fresh temp dir outside the project" (spike-worker.md:26-27)
- no `sudo`, no global installs, no `curl | sh` (spike-worker.md:52-53)
- the worker holds Read, Write and Bash, which are not bound to `$T` (spike-worker.md:8)
- caps are "maxTurns: 40" and "Stop at about 15 tool calls." (spike-worker.md:6,79)
- "do not retry with changed flags" (spike-worker.md:79-80)
- cleanup is the worker's own `rm -rf` (spike-worker.md:79)
- the result is a one-word prose verdict (spike-worker.md:87-93)
- the worker runs with `omitClaudeMd: true` (spike-worker.md:7-9)

**The 13 gaps and the change each implies (worker inference):**
1. Path cap and source: make the cap configurable and use a pre-authorised path list written at intake.
2. Credentials: a per-trial credential manifest (names, scope, expiry, test account only), injected by the host proxy or Claude Code's credential mask.
3. Network: replace `env -i` with a boundary (`--network none` plus an allowlisting proxy) and a per-trial domain list.
4. Isolation is advisory: run each trial as `claude -p` in a rootless container or under a dedicated OS user, not as an in-session subagent.
5. Longer probes: a wall-clock timeout, `--max-budget-usd`, and a rule for what counts as progress.
6. Retry: bounded retries in trial mode, where fixing configuration is the work.
7. Install rules: relax per trial inside a container, and record the relaxation in the result.
8. Result capture: a JSON result record per trial (Q6), with the prose note kept for negatives.
9. Cleanup: the supervisor tears down, with a startup sweep and `teardown` recorded in the result.
10. Human gate: for unattended runs, a written authorisation record or a Channels/Remote Control approval.
11. Outputs: decide where trial records live in the engineer's repo, as opposed to `research/spikes/`.
12. `claude -p` auth: `--bare` with a trial-only key, or non-bare with clean settings (Q5 Contradictions).
13. Resource contention: per-trial CPU, memory and pids limits, and a concurrency cap tied to quota.

From the spike-practice note (worker inference), add: a dead-end lookup and desk check before dispatch; riskiest-assumption-first ordering; a box in turns, wall-clock time and USD with an "inconclusive at box end" kill rule; and a `retry-when` field plus the version tested on every negative result.

**Contradictions.** Retrying: spike-worker.md:79-80 forbids retries ("A path that fails is a result"). The Claude Code docs allow two failed corrections before a restart (https://code.claude.com/docs/en/best-practices). The context protocol allows two attempts per task (/home/user/Autonomy-Research/research/findings/engineer-context.md:119). These are reconciled by mode. For a feasibility spike, no retry is correct, because the probe tests the path. For a build-time trial, allow at most two attempts on the same blocker, then record and stop.

### Q10. Recommended feasibility protocol, alternatives, rejected candidates and spike list

**Confidence: medium.** This merges the four workers' facet recommendations. They agree on the shape (files for state, deterministic gates, supervisor-owned boundaries) and differ only on the cap (Q3 Contradictions).

**One recommendation: the feasibility protocol.**
1. **Look up first.** Grep `dead-ends.md`, `docs/adr/` and the tool registry for every candidate (https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md, https://zenn.dev/kosk_t/articles/adr-lightweight-decision-records-for-ai?locale=en).
2. **Map.** Write `docs/map/integration-map.md` (plain Mermaid flowchart plus one sequence diagram per critical flow, parse-gated by mermaid-lint in a hook), `docs/map/integration-matrix.md` (one row per edge, with an evidence tag), and one integration card per service from the 12-point checklist. Build them from config snapshots and OpenAPI files, with a source pointer and a last-verified date (https://c4model.com/diagrams, https://github.com/jasonworden/mermaid-lint, /home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:83). John reviews the map and the matrix.
3. **Desk check, then pick what to trial.** Claims about auth, rate limits, webhooks, pagination, UI-only behaviour or go/no-go dependencies need "observed" evidence. Documented, versioned, reversible facts can stay desk-checked (https://qapractices.com/checklists/third-party-integration-testing-checklist/, worker rule).
4. **Bounded trials.** At most 3 paths. One question and a pass line per path, written before the run. The cheapest killing probe on the riskiest assumption goes first. Each trial has a box in `--max-turns`, wall-clock `timeout` and `--max-budget-usd`. At box end the result is "inconclusive"; after two failed fixes on one blocker, record and stop (https://builderscamp.com/guides/other/riskiest-assumption-test, https://agilesm.net/spike-enabler-story.html, https://code.claude.com/docs/en/best-practices, https://code.claude.com/docs/en/headless).
5. **Sandbox.** One worktree per trial and one `claude -p --output-format json --json-schema` process per trial, run as non-root in a hardened rootless container (`--network none`, `--rm`, pids and memory limits). A host proxy allowlists hosts and injects that trial's scoped test credential, and the Bash sandbox stays on inside (https://code.claude.com/docs/en/agent-sdk/secure-deployment, https://code.claude.com/docs/en/sandbox-environments, https://code.claude.com/docs/en/worktrees).
6. **Capture and teardown.** The supervisor writes `result.json`, tears down by lifecycle, and sweeps orphans at start (https://code.claude.com/docs/en/headless).
7. **Compare and decide.** Gates, then H/M/L ratings against a datum with separate evidence tags, under John's frozen rank order. A sensitivity check and a tie rule fall back to reversibility. Record a MADR ADR with a plain-language summary and a confirmation line; John flips the status (https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/, https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf, https://adr.github.io/madr/).
8. **Record negatives** in `dead-ends.md` with the version tested, evidence location and `retry-when` (https://pypi.org/project/epitaph/).
9. **Setup list.** One ordered page from the integration cards, long waits first, worked through in one local sitting with Claude in Chrome, with secrets by name only and an agent verification table at the end (https://code.claude.com/docs/en/chrome, https://launchrepo.dev/guides/ai-agent-captcha-2fa-handoffs/).
10. **Build.** The first build step is a walking skeleton of the chosen path, not the spike code (https://codeclimate.com/legacy/kickstart-your-next-project-with-a-walking-skeleton).

Everything is free: Markdown, Mermaid, mermaid-lint, Docker or Podman, and Claude Code features.

**Alternatives.**
- Docker Sandboxes `sbx` as the trial boundary, if `/dev/kvm` exists (https://docs.docker.com/ai/sandboxes/install/).
- Claude Code's sandbox runtime (beta) for low-risk trials (https://code.claude.com/docs/en/sandbox-environments).
- Hosted Vercel Sandbox or E2B for one-off probes of public code (https://vercel.com/docs/vercel-sandbox/pricing, https://e2b.dev/pricing).
- Structurizr DSL when several views must come from one model (https://docs.structurizr.com/dsl).
- Weighted scoring with frozen weights and a sensitivity check, if John wants one number (https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model).
- Mini-ATAM scenarios for the one or two riskiest choices (https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf).
- An epitaph-style JSON ledger with a hook (https://pypi.org/project/epitaph/).
- A `setup.sh` with prompts, for the final verification step only (worker inference).

**Rejected, with reasons.**
- **Full ATAM.** Too heavy for one user. Worker inference (not in a quoted source): multi-day with 8-20 people.
- **EventStorming as agent output.** It is a human workshop (https://www.eventstorming.com/).
- **Mermaid C4 as default.** Experimental (https://mermaid.js.org/syntax/c4.html).
- **Summed unfrozen weights.** False precision (https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model).
- **Adopting Kiro, BMAD or Spec Kit for this.** None adds evidence-based path comparison (worker inference).
- **Carrying many alternatives long-term.** Set-based design's cost without a Toyota-scale team (worker inference).
- **Auto-captured negative memory without a recurrence check.** vexjoy retired theirs at 74% one-off rows (https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md).
- **LLM-judged winner selection without a deterministic probe** (https://arxiv.org/abs/2411.17501).
- **Agent teams as trial runners.** No worktree isolation (https://code.claude.com/docs/en/agents).
- **Agent view as trial runner.** Research preview (https://code.claude.com/docs/en/agents).
- **The Bash sandbox alone.** "not sufficient for fully unattended runs" (https://code.claude.com/docs/en/sandbox-environments).
- **gVisor and self-hosted Firecracker for v1.** I/O cost, KVM requirement, and no untrusted code in scope (https://code.claude.com/docs/en/agent-sdk/secure-deployment; scope is worker inference).
- **Hobby hosted tiers as the main path.** 1 hour on E2B, 45 minutes on Vercel, with creation paused at quota (https://e2b.dev/pricing, https://vercel.com/docs/vercel-sandbox/pricing).
- **Modal.** No advantage seen (https://modal.com/pricing).
- **Cloudflare Sandbox SDK unless already on Workers Paid** (https://developers.cloudflare.com/sandbox/).
- **Cursor `/best-of-n`.** Different engine, and it varies the model, not the path (https://cursor.com/docs/configuration/worktrees).
- **Fully browser-driven account creation.** It pauses at login and CAPTCHA by design (https://code.claude.com/docs/en/chrome), and some terms ban bot accounts (https://launchrepo.dev/guides/ai-agent-captcha-2fa-handoffs/).
- **Having the model solve CAPTCHA or 2FA, or storing secrets in chat** (worker inference).
- **Supabase `anon`/`service_role` keys for new work.** Deprecated by end of 2026 (https://supabase.com/docs/guides/api/api-keys).
- **Piecemeal per-service setup asks.** Requirement R11 asks for one ordered list (/home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:105-110).

**Spike list (must be tried for real before building).**
1. `ls /dev/kvm` on John's VM, and sbx if KVM is present.
2. A hardened container running `claude -p` under subscription login and under a trial-only API key: prove `--bare`, exit codes 0 and 143, and budget-stop exits.
3. The host proxy injecting a test token with TLS termination, and a tool that ignores `HTTP_PROXY` failing closed.
4. The AppArmor bubblewrap profile on Ubuntu 24.04.
5. Three trials in parallel, with leaked-secret and orphan-worktree checks after a forced kill.
6. Which turn and wall-clock box fits one trial worker.
7. Whether a `PreToolUse` or `SessionStart` hook that greps `dead-ends.md` changes agent behaviour.
8. Whether John can provide test accounts for auth and rate-limit probes.
9. Generate the integration map and matrix for John's GTM system from config snapshots: validity rate, and correctness against a hand-made version.
10. mermaid-lint as a hook on 20 generated diagrams: failures and repair rounds.
11. Score 3 candidate paths 5 times each: rating stability.
12. Show John 3 ADRs: can he state the decision and its undo path?
13. Change one design input: does the stale-diagram check flag the map?
14. Render a Mermaid C4 block where John views docs.
15. Google OAuth publishing status with John's real scopes (the 7-day Testing refresh token).
16. Outreach development vs production credentials.
17. Clay API surface on John's plan.
18. n8n API on John's plan or self-host.
19. WHOOP and Withings refresh-token rotation store.
20. Actual minutes per setup step in John's first sitting, fed back into the list.

## Evidence

All web sources opened 2026-10-16. Local files read 2026-10-16. Where a note's claim holds a value that its quote does not, the bullet ends with "Not in quote".

Mapping and rubric (notes/mapping-and-rubric.md):
- A1. https://c4model.com/diagrams — 2026-10-16, WebFetch — C4 itself says two levels are enough for most teams — Quote: "only those that add value - the system context and container diagrams are sufficient for most software development teams."
- A2. https://docs.structurizr.com/dsl — 2026-10-16, WebFetch — Structurizr DSL is a text model of C4 and exports to PlantUML and Mermaid (D2 export not confirmed on the page) — Quote: "The Structurizr DSL provides a way to define a software architecture model." Not in quote: the export targets.
- A3. https://mermaid.js.org/syntax/c4.html — 2026-10-16, WebFetch — Mermaid's own C4 type is experimental — Quote: "This is an experimental diagram for now. The syntax and properties can change in future releases."
- A4. https://llm-enabled-development-41d6d8.pages.cms.hu-berlin.de/en/archiv/experiments/diagram/diagram-long/ — 2026-10-16, WebFetch — LLM Mermaid reliability measured once: about 70% valid at first, 95% with a render check, repair loop and a long syntax reference; repair loop fixes only 80-85% of broken diagrams — Quote: "This pipeline increased the success rate from an initial 70% to 95% after the final iteration."
- A5. same URL — 2026-10-16, WebFetch — Same project: repair by the LLM is the weak point — Quote: "the repair of invalid code is only successful in about 80-85% of cases."
- A6. https://github.com/jasonworden/mermaid-lint — 2026-10-16, WebFetch — A free MIT Mermaid linter exists that uses the official parser, runs via npx, and returns exit code 1 on failure, so it works as a CI gate or hook (Node 22+) — Quote: "Uses the official `mermaid.parse()` API — catches real syntax errors, not just missing diagram-type keywords." Not in quote: MIT, npx, exit code, Node 22+.
- A7. https://github.com/juliusz-cwiakalski/agentic-delivery-os/pull/123 — 2026-10-16, WebFetch — A real agent-driven repo found that nothing checked its docs' diagrams, so it added a render gate in CI — Quote: "Agents cannot \"see\" a broken diagram; a human only notices by rendering."
- A8. https://learn.openapis.org/ — 2026-10-16, WebFetch — OpenAPI is the machine-readable contract format for REST — Quote: "A format readable by both machines and humans"
- A9. https://www.asyncapi.com/docs/tutorials/getting-started — 2026-10-16, WebFetch — AsyncAPI is the equivalent for event-driven APIs (webhooks, queues) — Quote: "Much like OpenAPI (aka Swagger) does for REST APIs"
- A10. https://www.eventstorming.com/ — 2026-10-16, WebFetch — Event storming is a human workshop format, not an agent output — Quote: "EventStorming is a flexible workshop format for collaborative exploration of complex business domains."
- A11. https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/ (post dated 2026-06-16) — 2026-10-16, WebFetch — The Claude Code plan is not kept by default, so any mapping artifact must be saved as a file; Claude Code plan mode plan is a review gate, not committed — Quote: "The plan itself is a review gate, not a committed document, unless you explicitly save it."
- A12. /home/user/Autonomy-Research/research/findings/engineer-existing-systems.md:83 — read 2026-10-16, Read/grep — The earlier existing-systems recommendation already prescribes "C4 context-plus-container Mermaid, system-of-record table, credential inventory" with each row marked observed, inferred or asserted, and John reviewing the context diagram and system-of-record table — Quote: "John reviews the context diagram and the system-of-record table, and the pack feeds the intake explore branch"
- A13. /home/user/Autonomy-Research/research/findings/engineer-intake.md:51 — read 2026-10-16, grep — The earlier intake recommendation already shows John a comparison table of at most 5 options, not a diagram, and offers a diagram after he picks (worker inference there) — Quote: "offer a diagram only after he picks (judgement, no source)."
- A14. https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html — 2026-10-16, WebFetch — AWS lists "Interfaces (APIs and published contracts)" and "Dependencies" as ADR-worthy decision areas, so the matrix rows map onto ADR triggers — Quote: "Interfaces (APIs and published contracts)"
- A15. https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/ — 2026-10-16, WebFetch — Pugh matrix is non-numeric, compares each option to a datum with +, S, - — Quote: "non-numeric and iterative tool for concept selection"
- A16. https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model — 2026-10-16, WebFetch — Weighted scoring is defensible only if weights are frozen before scoring — Quote: "The model produces a defensible decision only when the criteria and weights are locked before anyone scores"
- A17. same URL — 2026-10-16, WebFetch — Near-ties are not verdicts — Quote: "A 6.75 versus 7.00 result is a tie that deserves a conversation, not a verdict."
- A18. same URL — 2026-10-16, WebFetch — Mandatory requirements belong in a gate, not in the weights — Quote: "it belongs in a pass/fail gate before scoring, not blended into a percentage."
- A19. SEI CMU/SEI-2000-TR-004 https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf (pdftotext of the fetched file, line 1151) — 2026-10-16, WebFetch + pdftotext — SEI says stakeholders cannot rate finer than three levels — Quote: "stakeholders cannot reliably and repeatably make finer distinctions than High, Medium, and Low."
- A20. https://jacquiread.com/posts/2024-09-11-decision-making-adrs-weightings-are-a-workaround/ — 2026-10-16, WebFetch — Weightings add upkeep and error risk; prefer splitting criteria to the same level of abstraction — Quote: "These need to be reassessed when criteria are added and removed"
- A21. https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md — 2026-10-16, WebFetch — A rune-kit rubric scores reversibility 1-5 on cost to change one's mind and demands a named rejected alternative — Quote: "Score 1–5: how expensive is it to change your mind later?"
- A22. https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/ — 2026-10-16, WebFetch — Kiro design.md already holds alternatives considered and maps to ADRs — Quote: "Design decisions captured in `design.md` map cleanly onto Architecture Decision Records."
- A23. https://zenn.dev/kosk_t/articles/adr-lightweight-decision-records-for-ai?locale=en (2026-04-20) — 2026-10-16, WebFetch — Agents do not know past decisions and may reverse them unless ADRs are scanned; a CLAUDE.md rule can force the check — Quote: "Agents like Claude Code don’t know past team decisions."
- A24. https://docs.cloud.google.com/architecture/architecture-decision-records — 2026-10-16, WebFetch — Google Cloud advises ADRs be kept with code and written when options compete — Quote: "Store your ADRs close to your application code, ideally in the same version control system."
- A25. https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html — 2026-10-16, WebFetch — AWS Prescriptive Guidance treats accepted ADRs as immutable — Quote: "When the team accepts an ADR, it becomes immutable."
- A26. https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md — 2026-10-16, WebFetch — A recorded ADR criteria gate: only log a decision if hard to reverse, surprising and a real trade-off; conventions go in CLAUDE.md — Quote: "Conventions are choices everyone makes the same way."
- A27. https://adr.github.io/madr/ — 2026-10-16, WebFetch — MADR template sections: decision drivers, considered options, pros and cons, confirmation — Quote: "a streamlined template for recording architectural significant decisions in a structured manner."
- A28. same URL — 2026-10-16, WebFetch — MADR has a confirmation field — Quote: "Describe how the implementation of/compliance with the ADR can/will be confirmed."
- A29. https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — 2026-10-16, WebFetch — ADR is short and keeps status — Quote: "The whole document should be one or two pages long."
- A30. same URL — 2026-10-16, WebFetch — Reversal keeps history — Quote: "If a decision is reversed, we will keep the old one around, but mark it as superseded."
- A31. https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html — 2026-10-16, WebFetch — AWS lifecycle Proposed, Accepted, Rejected, Superseded with timestamp and stakeholders — Quote: "If the team approves the ADR, the owner adds a timestamp, version, and list of stakeholders."
- A32. https://docs.cloud.google.com/architecture/architecture-decision-records — 2026-10-16, WebFetch — Google's outline includes key options and reasons for the accepted choice — Quote: "When there are two or more engineering options and you want to document your thoughts and reasons behind the selection."
- A33. /home/user/Autonomy-Research/research/findings/engineer-intake.md:77 — read 2026-10-16, grep — The earlier intake recommendation already prescribes an "accepted over objection" ADR and a file-based approval record — Quote: "approval recorded in a file, not via ExitPlanMode alone"

Spike practice and negative results (notes/spike-practice.md):
- B1. https://dojoconsortium.org/docs/work-decomposition/spikes/ — 2026-10-16, WebFetch — Modern spike guidance sets short boxes: spikes "should be time-boxed in short increments (1-3 days)" and "used sparingly" — Quote: "They should be time-boxed in short increments (1-3 days)."
- B2. https://agilesm.net/spike-enabler-story.html — 2026-10-16, WebFetch — Success is a decision, not a document: a spike is judged by whether it ends in proceed, pivot, reduce scope or drop — Quote: "A spike is successful when it leads to a clear choice (proceed, pivot, reduce scope, or drop the approach)"
- B3. same URL — 2026-10-16, WebFetch — Spike write-up must record what was ruled out — Quote: "Record what was tried, what was learned, what constraints were discovered, and what options were ruled in or out."
- B4. same URL — 2026-10-16, WebFetch — Anti-pattern of no box — Quote: "It runs until someone feels finished, so uncertainty expands and decisions drift;"
- B5. https://codeclimate.com/legacy/kickstart-your-next-project-with-a-walking-skeleton — 2026-10-16, WebFetch — Walking skeleton (Cockburn) vs prototype — Quote: "tiny implementation of the system that performs a small end-to-end function. It need not use the final architecture, but it should link together the main architectural components."
- B6. same URL — 2026-10-16, WebFetch — Same page: skeleton is kept code — Quote: "it's not a prototype and not a proof of concept — it's production code"
- B7. https://flylib.com/books/en/1.315.1.25/1/ — 2026-10-16, WebFetch — Tracer bullets (Pragmatic Programmer) — Quote: "Tracer code is not disposable: you write it for keeps." and "Prototyping generates disposable code."
- B8. https://sloanreview.mit.edu/article/toyotas-principles-of-setbased-concurrent-engineering/ — 2026-10-16, WebFetch — The Sloan page does confirm the contrast with point-based design (page itself returned only footnotes otherwise) — Quote: "Toyota considers a broader range of possible designs and delays certain decisions longer than other automotive companies do."
- B9. https://builderscamp.com/guides/other/riskiest-assumption-test — 2026-10-16, WebFetch — Riskiest assumption first, one per test, pass line fixed beforehand, feasibility maps to a spike — Quote: "One per test." / "feasibility needs an engineering spike." / "The pass line is set before the test runs."
- B10. https://dojoconsortium.org/docs/work-decomposition/spikes/ — 2026-10-16, WebFetch — Batch learning is worse than batching work (supports trial early, not research everything first) — Quote: "Batching learning is worse than batching other kinds of work"
- B11. https://baaz.pro/blog/how-to-estimate-api-integration-work — 2026-10-16, WebFetch — Integration spikes run longer but only once access exists — Quote: "One to two weeks for a team that already has access, environments, and a clear vertical slice."
- B12. same URL — 2026-10-16, WebFetch — Same page: spike is evidence, not scrap code — Quote: "A spike is not a scrappy prototype you throw away by default."
- B13. https://www.anthropic.com/engineering/multi-agent-research-system — 2026-10-16, WebFetch — Anthropic scales effort to complexity and had an overspend failure mode — Quote: "Simple fact-finding requires just 1 agent with 3-10 tool calls"
- B14. same URL — 2026-10-16, WebFetch — Multi-agent token cost and fit — Quote: "multi-agent systems use about 15× more tokens than chats."
- B15. same URL — 2026-10-16, WebFetch — Anthropic: most coding tasks are poorly parallelisable — Quote: "most coding tasks involve fewer truly parallelizable tasks than research"
- B16. https://arxiv.org/abs/2411.17501 — 2026-10-16, WebFetch — Resampling returns diminish fast when the verifier is imperfect — Quote: "Empirical results show that optimal sampling attempts are often fewer than 10"
- B17. https://code.claude.com/docs/en/best-practices — 2026-10-16, WebFetch — Claude Code docs: after two failed corrections, restart with a better prompt — Quote: "After two failed corrections, `/clear` and write a better initial prompt incorporating what you learned."
- B18. same URL — 2026-10-16, WebFetch — Same docs: fan-out gate — Quote: "Refine your prompt based on what goes wrong with the first 2-3 files, then run on the full set."
- B19. same URL — 2026-10-16, WebFetch — Same docs name the unbounded-exploration failure — Quote: "The infinite exploration."
- B20. https://qapractices.com/checklists/third-party-integration-testing-checklist/ — 2026-10-16, WebFetch — "Real APIs diverge from documentation" — Quote: "Real APIs diverge from documentation. Validate every behavior empirically,"
- B21. https://baaz.pro/blog/how-to-estimate-api-integration-work — 2026-10-16, WebFetch — Sandbox is not production — Quote: "Sandboxes that diverge from production teach you the wrong lessons."
- B22. https://code.claude.com/docs/en/best-practices — 2026-10-16, WebFetch — Claude Code parallel options — Quote: "Run multiple Claude sessions in parallel to speed up development, run isolated experiments, or start complex workflows."
- B23. same URL — 2026-10-16, WebFetch — Fan-out size — Quote: "Run `/batch <instruction>` to have Claude split the change across 5 to 30 subagents."
- B24. same URL — 2026-10-16, WebFetch — Cheap rollback for risky tries — Quote: "Instead of carefully planning every move, you can tell Claude to try something risky. If it doesn't work, rewind and try a different approach."
- B25. same URL — 2026-10-16, WebFetch — Fresh-context reviewer — Quote: "A fresh context improves code review since Claude won't be biased toward code it just wrote."
- B26. https://cursor.com/docs/configuration/worktrees — 2026-10-16, WebFetch — Cursor best-of-N — Quote: "`/best-of-n` runs the same task across multiple models at once." and "Try multiple approaches for a hard change"
- B27. https://docs.arantic.com/cursor/parallel-agents — 2026-10-16, WebFetch — Cost of best-of-N (third-party doc mirror, not Cursor) — Quote: "Best-of-N multiplies cost by the number of models. Three models on one task is roughly three times the tokens of one run."
- B28. https://adr.github.io/madr/decisions/adr-template.html — 2026-10-16, WebFetch — ADR rejected options template — Quote: "Considered Options" and "Bad, because {argument d}"
- B29. https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md — 2026-10-16, Exa web_fetch_exa — Dated registry with four fields, evidence must be a location, "check before re-running" — Quote: "Negative-results registry. A list of experiments that lost, so the next session skips a known-dead path."
- B30. same URL — 2026-10-16, Exa web_fetch_exa — Same file: field list — Quote: "- **Decision**: rejected | deferred | revisit-if <condition>."
- B31. same URL — 2026-10-16, Exa web_fetch_exa — Same file: evidence discipline — Quote: "Evidence must be a location (`file:line`, eval path, PR #, or `learning.db topic/key`), not a claim."
- B32. same URL — 2026-10-16, Exa web_fetch_exa — Same file also shows a retired auto-capture loop: 74 percent of rows were one-off and injected hints were truncated (author's own measurement; page contains no instructions to agents). Lesson: auto-captured negative memory without recurrence check wasted tokens — Quote: "74% of the corpus (1,849 of 2,490 rows) was one-off."
- B33. https://pypi.org/project/epitaph/ (v0.2.0, uploaded 2026-09-05) — 2026-10-16, Exa web_fetch_exa — Tombstone ledger with refutation condition and pre-flight rule — Quote: "epitaph is the **repo-scoped attempt ledger**: one JSON file per rejected attempt, committed to the repo, queryable by machine before the retry happens."
- B34. same URL — 2026-10-16, Exa web_fetch_exa — Same page: example record flag — Quote: "--retry-when \"once a fencing token sits in front of the lock\""
- B35. https://gist.github.com/corpulent/f7fbad0a4d9cdb6a5d4f31d249a2341c — 2026-10-16, WebFetch — Scratchpad dead-ends section and read-first rule — Quote: "record only approaches that were actually attempted and explain concretely why they failed" and "Before performing any task, read .ai_scratchpad.md."
- B36. https://code.claude.com/docs/en/best-practices — 2026-10-16, WebFetch — Claude Code docs on failed approaches polluting context — Quote: "the context is cluttered with failed approaches."

Trial sandboxes and the spike skill (notes/trial-sandboxes.md):
- C1. https://code.claude.com/docs/en/worktrees — 2026-10-16, WebFetch — Worktrees are the first-party parallel-edit primitive; one flag creates an isolated checkout and branch — Quote: "Pass `--worktree` or `-w` with a name to create an isolated worktree and start Claude in it."
- C2. same URL — 2026-10-16, WebFetch — Subagents can be pinned to a worktree in frontmatter and are removed when they finish without changes — Quote: "Each subagent gets a temporary worktree that Claude Code removes automatically when the subagent finishes without changes"
- C3. same URL — 2026-10-16, WebFetch — Headless `-p` worktrees are not cleaned up automatically, so the engineer's supervisor must sweep them — Quote: "Non-interactive runs with `-p` have no exit prompt, so Claude doesn't clean up their worktrees"
- C4. same URL — 2026-10-16, WebFetch — Worktree checks guard git and edit targets only, not arbitrary writes — Quote: "None of them tracks which files a shell command writes"
- C5. same URL — 2026-10-16, WebFetch — A worktree does not carry gitignored files such as `.env` unless `.worktreeinclude` lists them; that file is the one place a trial would receive local secrets, so it must stay empty or hold test values only — Quote: "To carry gitignored files such as `.env` into every new worktree automatically, add a [`.worktreeinclude` file]"
- C6. https://code.claude.com/docs/en/agents — 2026-10-16, WebFetch — Five parallel approaches exist; worktrees isolate files; agent teams do not — Quote: "Agent teams don't isolate teammates in worktrees"
- C7. same URL — 2026-10-16, WebFetch — Agent view dispatches background sessions (research preview) — Quote: "One screen to dispatch and monitor sessions running in the background, opened with `claude agents`. Research preview"
- C8. same URL — 2026-10-16, WebFetch — `/batch` is a packaged worktree fan-out of 5 to 30 subagents — Quote: "has Claude split one large change into 5 to 30 worktree-isolated subagents"
- C9. same URL — 2026-10-16, WebFetch — Parallel runs multiply token use — Quote: "Running several sessions or subagents at once multiplies token usage."
- C10. https://code.claude.com/docs/en/sandboxing — 2026-10-16, WebFetch — The Bash sandbox covers shell commands only — Quote: "The sandbox covers shell commands only. Claude's file tools, MCP servers, and hooks run outside it."
- C11. same URL — 2026-10-16, WebFetch — Network default is deny with an empty allowlist — Quote: "No direct route out. Connections go through a proxy on your machine that checks each host against your allowed domains, which start empty."
- C12. same URL — 2026-10-16, WebFetch — Linux needs bubblewrap and socat; Ubuntu 24.04+ needs an AppArmor profile for bwrap (a one-off sudo step on John's VM) — Quote: "On Ubuntu 24.04 and later, the default AppArmor policy prevents bubblewrap from creating the user namespaces it needs for isolation."
- C13. same URL — 2026-10-16, WebFetch — Credentials can be masked: the sandboxed command sees a placeholder and the proxy substitutes the real value (needs TLS termination, which is experimental) — Quote: "Claude Code shows sandboxed commands a per-session placeholder called the sentinel" and "the proxy substitutes the real value inside request contents, so it has to see them."
- C14. same URL — 2026-10-16, WebFetch — Built-in credential deny list is empty — Quote: "There is no built-in credential deny list, so only the files and variables you list are restricted."
- C15. https://code.claude.com/docs/en/agent-sdk/secure-deployment — 2026-10-16, WebFetch — Allowlist is by hostname, so a leaky allowed domain defeats it — Quote: "The proxy allowlists domains based on the client-supplied hostname and does not terminate or inspect encrypted traffic."
- C16. https://code.claude.com/docs/en/sandbox-environments — 2026-10-16, WebFetch — Anthropic's own verdict on the Bash sandbox for unattended work — Quote: "on its own constrains only shell commands, so it is not sufficient for fully unattended runs in either mode."
- C17. same URL — 2026-10-16, WebFetch — Skip-permissions needs a non-root user — Quote: "On Linux and macOS, Claude Code refuses to start with this flag when running as root, so run the container, VM, or sandbox runtime as a non-root user."
- C18. same URL — 2026-10-16, WebFetch — Sandbox runtime wraps the whole process (file tools, MCP, hooks), beta — Quote: "The runtime is a beta research preview, and its configuration format may change as the package evolves."
- C19. https://code.claude.com/docs/en/headless — 2026-10-16, WebFetch — Headless: structured result, cost and exit code per run — Quote: "With `--output-format json`, the response payload includes `total_cost_usd` and a per-model cost breakdown"
- C20. same URL — 2026-10-16, WebFetch — `--bare` is recommended for scripts but cannot use the subscription login — Quote: "In bare mode, Claude Code never reads OAuth credentials or the system keychain."
- C21. same URL — 2026-10-16, WebFetch — Without `--bare`, a `-p` run in a trial directory executes that directory's hooks and MCP servers — Quote: "Without `--bare`, a `-p` session runs the hooks in a project's `.claude/settings.json` and connects the servers in its `.mcp.json`, even in a folder you've never trusted."
- C22. same URL — 2026-10-16, WebFetch — Kill behaviour: SIGTERM gives exit 143 and no result for the in-flight turn — Quote: "Claude Code exits with code 143."
- C23. https://code.claude.com/docs/en/agent-sdk/secure-deployment — 2026-10-16, WebFetch — Hardened container recipe with no network and a proxy socket is documented by Anthropic — Quote: "Removes all network interfaces; the agent communicates through the mounted Unix socket below"
- C24. same URL — 2026-10-16, WebFetch — Credentials stay outside the boundary — Quote: "The recommended approach is to run a proxy outside the agent's security boundary that injects credentials into outgoing requests."
- C25. same URL — 2026-10-16, WebFetch — Mounted code can leak secrets even read-only — Quote: "Even read-only access to a code directory can expose credentials."
- C26. same URL — 2026-10-16, WebFetch — Tools that ignore proxy variables exist — Quote: "Node.js `fetch()` ignores these variables by default; in Node 24+ you can set `NODE_USE_ENV_PROXY=1` to enable support."
- C27. same URL — 2026-10-16, WebFetch — gVisor: strong isolation, I/O cost — Quote: "Up to 10-200× slower for heavy open/close patterns"
- C28. same URL — 2026-10-16, WebFetch — Firecracker microVM numbers — Quote: "It can boot VMs in under 125ms with less than 5 MiB memory overhead"
- C29. https://code.claude.com/docs/en/sandbox-environments — 2026-10-16, WebFetch — Anthropic's isolation table lists effort: dev container medium, custom container medium to high, VM high — Quote: "| [Virtual machine](#virtual-machine) | Full operating system | No | High |"
- C30. same URL — 2026-10-16, WebFetch — Reference devcontainer has a default-deny firewall and is meant for unattended runs — Quote: "Because the firewall blocks unapproved egress, a configuration like this supports running Claude Code with `--dangerously-skip-permissions` for unattended work."
- C31. same URL — 2026-10-16, WebFetch — Unprivileged containers break nested bubblewrap — Quote: "Unprivileged containers need `enableWeakerNestedSandbox`"
- C32. https://docs.docker.com/ai/sandboxes/security/ — 2026-10-16, WebFetch — Docker Sandboxes (`sbx`) runs agents in microVMs with host-side credential injection and deny-by-default egress — Quote: "The raw credential values never enter the VM."
- C33. https://docs.docker.com/ai/sandboxes/install/ — 2026-10-16, WebFetch — sbx Linux requirements — Quote: "KVM hardware virtualization supported and turned on by the CPU, and your user account in the `kvm` group."
- C34. same URL — 2026-10-16, WebFetch — sbx Ubuntu support is 24.04+ and its documented install is a `curl | sh` (page text, not an instruction to this agent; not run) — Quote: "Ubuntu 24.04 or later."
- C35. https://docs.docker.com/ai/sandboxes/get-started/ and https://docs.docker.com/ai/sandboxes/agents/claude-code/ — 2026-10-16, WebFetch — sbx teardown and Claude Code launch — Quote: "Removing a sandbox deletes everything inside it." and "Launch Claude Code in a sandbox by pointing it at a project directory:"
- C36. https://docs.docker.com/ai/sandboxes/agents/claude-code/ — 2026-10-16, WebFetch — sbx does not import host Claude config — Quote: "Sandboxes don't pick up user-level configuration from your host, such as `~/.claude`."
- C37. https://docs.docker.com/ai/sandboxes/security/ — 2026-10-16, WebFetch — sbx clone mode keeps the host tree read-only — Quote: "Clone mode: Your repository is mounted read-only, and the agent works on a private clone."
- C38. https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md — 2026-10-16, WebFetch — Rootless Podman prerequisites are small but real — Quote: "Rootless Podman requires the user running it to have a range of UIDs listed in the files /etc/subuid and /etc/subgid."
- C39. https://docs.e2b.dev/agents/claude-code — 2026-10-16, WebFetch — E2B: ready-made Claude Code template, headless flags, open internet by default — Quote: "E2B provides a pre-built `claude` template with Claude Code already installed."
- C40. same URL — 2026-10-16, WebFetch — E2B egress is open unless set — Quote: "The sandbox isolates the agent from your host machine, but sandboxes can reach the open internet by default."
- C41. same URL — 2026-10-16, WebFetch — E2B passes the API key as a sandbox env var, so the credential is inside the boundary — Quote: "Use `-p` for non-interactive mode and `--dangerously-skip-permissions` to auto-approve all tool calls." Not in quote: the API-key env var.
- C42. https://e2b.dev/pricing — 2026-10-16, WebFetch — E2B price and limits — Quote: "One-time $100 in usage credits." / "Up to 1 hour per sandbox session." / "Up to 20 concurrently running sandboxes." / "$150 monthly plan fee, plus usage"
- C43. https://www.daytona.io/pricing — 2026-10-16, WebFetch — Daytona: free credit and startup claim — Quote: "$200 in free compute included." / "Sub 90ms sandbox creation from code to execution."
- C44. https://vercel.com/docs/vercel-sandbox/pricing (served as /docs/sandbox/pricing; page last_updated 2026-09-10) — 2026-10-16, WebFetch — Vercel Sandbox quotas — Quote: "| Max Session Duration | 45 minutes | 24 hours | 24 hours |" and "| Concurrent Sandboxes | 10 | 10,000 | 10,000 |"
- C45. same URL — 2026-10-16, WebFetch — Vercel Hobby hard-stops rather than bills — Quote: "Once you exceed the quotas, sandbox creation is paused until 30 days have passed since you first used the feature."
- C46. same URL — 2026-10-16, WebFetch — Vercel cost example for a 30-minute 4 vCPU build and test — Quote: "| Build and test | 30 min | 4 | 8 GB | $0.0256 | $0.0848 | $0.1104 |"
- C47. same URL — 2026-10-16, WebFetch — Vercel egress cost, downloads free — Quote: "Data your sandbox downloads from the internet, such as packages, Git repositories, artifacts, and datasets, is free."
- C48. same URL — 2026-10-16, WebFetch — Vercel persistence: snapshots expire by default — Quote: "Snapshots expire **30 days after their last use by default**."
- C49. https://modal.com/pricing — 2026-10-16, WebFetch — Modal sandbox price is about 3x container price; Starter has monthly credit — Quote: "$30 / month free credits" and "$0.00003942 / core / sec" Not in quote: the 3x ratio.
- C50. https://developers.cloudflare.com/sandbox/ — 2026-10-16, WebFetch — Cloudflare Sandbox SDK runs coding agents per task, needs a paid Workers plan — Quote: "Run coding agents such as Claude Code, Codex, and Devin in a sandbox that belongs to one task."
- C51. same URL — 2026-10-16, WebFetch — Cloudflare plan gate — Quote: "Available on Workers Paid plan"
- C52. https://code.claude.com/docs/en/sandbox-environments — 2026-10-16, WebFetch — Anthropic itself says managed services can host the container — Quote: "Several managed sandbox and remote execution services can host the container for you."
- C53. https://code.claude.com/docs/en/headless — 2026-10-16, WebFetch — JSON output carries result, session id and metadata, and a schema can force a structured field — Quote: "`json`: structured JSON with result, session ID, and metadata"
- C54. same URL — 2026-10-16, WebFetch — Schema-validated output — Quote: "The response includes metadata about the request (session ID, usage, etc.) with the structured output in the `structured_output` field."
- C55. same URL — 2026-10-16, WebFetch — Cost figures are estimates — Quote: "Both figures are [client-side estimates](/docs/en/agent-sdk/cost-tracking) and can differ from your actual bill."
- C56. same URL — 2026-10-16, WebFetch — Exit status — Quote: "Claude Code exits with code 0 on success and a non-zero code when the run fails, so your scripts can branch on the exit status."
- C57. same URL — 2026-10-16, WebFetch — Permission denials are reported in the final stream message — Quote: "the final result message lists them in `permission_denials`."
- C58. same URL — 2026-10-16, WebFetch — Background work can hold a run open for 10 minutes — Quote: "Claude Code stops whatever is still running after 10 minutes of continuous idle waiting by default and drops its partial result."
- C59. same URL — 2026-10-16, WebFetch — Budget cap stops background work — Quote: "If the run reaches its [`--max-budget-usd`](/docs/en/cli-reference#cli-flags) cap, Claude Code stops the remaining background work instead of waiting."
- C60. https://code.claude.com/docs/en/agent-sdk/secure-deployment — 2026-10-16, WebFetch — Ephemeral writable locations and review before persist — Quote: "an overlay filesystem lets the agent write without modifying underlying files."
- C61. same URL — 2026-10-16, WebFetch — Container tmpfs clears on stop — Quote: "Provides a writable temporary directory that's cleared when the container stops"
- C62. https://code.claude.com/docs/en/sandbox-environments — 2026-10-16, WebFetch — Sandbox runtime review step after unattended runs — Quote: "Review the paths you kept writable. On Linux and WSL2, also review anything the session created."
- C63. https://vercel.com/docs/vercel-sandbox/pricing — 2026-10-16, WebFetch — Vercel cost control: stop promptly, spend management — Quote: "Stop sandboxes promptly: Call `sandbox.stop()` when done rather than waiting for timeout"
- C64. same URL — 2026-10-16, WebFetch — Pro tier spend alerts — Quote: "configure [Spend Management](/docs/spend-management) to receive alerts or pause projects when you reach a specified amount."
- C65. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:16 — read 2026-10-16, Read — Path count cap — Quote: "The skill shall run at most three workers in parallel, each testing exactly one path."
- C66. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14 — read 2026-10-16, Read — User must name paths; skill adds none — Quote: "The skill shall test only paths the user named, and shall not add a path of its own."
- C67. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:28 — read 2026-10-16, Read — No credentials — Quote: "The skill shall give a worker no credentials beyond read-only search keys."
- C68. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:28-29 — read 2026-10-16, Read — Account needs equal blocked — Quote: "If a path needs an account, a write token or a payment, the worker shall stop and report it as blocked."
- C69. spike-worker.md:26-27 — read 2026-10-16, Read — Isolation is a shell recipe, not an enforced boundary — Quote: "Every install, clone or run of the candidate happens in a fresh temp dir outside the project"
- C70. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:40-44 — read 2026-10-16, Read — Recipe passes proxy variables but allows any host — Quote: "passing only the proxy variables (`HTTPS_PROXY`,"
- C71. spike-worker.md:52-53 — read 2026-10-16, Read — Install limits — Quote: "No `sudo`, no global installs (`npm -g`, `pip` without a venv in `$T`), no `curl | sh`"
- C72. spike-worker.md:8 — read 2026-10-16, Read — Worker has Bash and Write but no sandbox setting, and Read/Write are not bound to `$T` — Quote: "tools: Read, Write, Grep, Glob, Bash, ToolSearch, WebFetch"
- C73. spike-worker.md:6 and :79 — read 2026-10-16, Read — Turn and call caps sized for short probes — Quote: "maxTurns: 40" and "Stop at about 15 tool calls."
- C74. spike-worker.md:79-80 — read 2026-10-16, Read — Worker may never retry — Quote: "A path that fails is a result: do not retry with changed flags to make it pass."
- C75. spike-worker.md:79 — read 2026-10-16, Read — Cleanup is the worker's own last step — Quote: "When done, `rm -rf` the literal temp path."
- C76. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:52 — read 2026-10-16, Read — Step 1 needs the user in the loop — Quote: "Confirm the question, the named paths (one to three) and the probe with the user in one message."
- C77. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:34-35 — read 2026-10-16, Read — Overrides need the user's own message — Quote: "If an isolation rule is to be relaxed, then the lead shall quote the user's own message in the brief."
- C78. /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:64 and :68 — read 2026-10-16, Read — Output location and writer — Quote: "Spawn one `synthesizer` to read the spike notes and write `research/spikes/<slug>.md`"
- C79. spike-worker.md:87-93 — read 2026-10-16, Read — Result format is prose headings — Quote: "`Verdict: works | fails | blocked` (keep one word)"
- C80. spike-worker.md:7-9 — read 2026-10-16, Read — Worker model and omitted context — Quote: "omitClaudeMd: true"

Edge cases and setup list (notes/edge-cases-and-setup-list.md):
- D1. https://docs.stripe.com/webhooks — 2026-10-16, WebFetch — Webhooks: verify signature on the raw body, return 2xx fast — Quote: "Quickly returns a successful status code (`2xx`) before any complex logic that might cause a timeout."
- D2. same URL — 2026-10-16, WebFetch — Raw-body trap — Quote: "Any manipulation to the raw body of the request causes the verification to fail."
- D3. same URL — 2026-10-16, WebFetch — Ordering not guaranteed — Quote: "Stripe doesn’t guarantee the delivery of events in the order that they’re generated."
- D4. same URL — 2026-10-16, WebFetch — Duplicates: dedupe on event ID — Quote: "Webhook endpoints might occasionally receive the same event more than once."
- D5. same URL — 2026-10-16, WebFetch — Replay protection via signed timestamp, default tolerance 5 minutes — Quote: "Our libraries have a default tolerance of 5 minutes between the timestamp and the current time."
- D6. same URL — 2026-10-16, WebFetch — Retry horizon differs live vs sandbox — Quote: "Stripe attempts to deliver events to your destination for up to three days with an exponential back off in live mode."
- D7. same URL — 2026-10-16, WebFetch — Sandbox retries are shorter — Quote: "We retry event deliveries created in a sandbox three times over the course of a few hours."
- D8. same URL — 2026-10-16, WebFetch — Webhook payload version pinned to account API version at event time — Quote: "The API version in your account settings when the event occurs dictates the API version, and therefore the structure of an"
- D9. same URL — 2026-10-16, WebFetch — Secret rotation overlap up to 24 h — Quote: "You can choose to immediately expire the current secret or delay its expiration for up to 24 hours"
- D10. https://docs.stripe.com/api/idempotent_requests — 2026-10-16, WebFetch — Idempotency keys: saved result incl. errors, 24 h pruning, all POSTs — Quote: "you can remove keys from the system automatically after they’re at least 24 hours old."
- D11. same URL — 2026-10-16, WebFetch — Idempotency key reuse with different params errors — Quote: "The idempotency layer compares incoming parameters to those of the original request and errors if they’re not the same"
- D12. https://developers.google.com/identity/protocols/oauth2 — 2026-10-16, WebFetch — Google refresh-token traps: Testing status 7 days; unused 6 months; 100 per client — Quote: "is issued a refresh token expiring in 7 days"; "The refresh token has not been used for six months."; "100 refresh tokens per Google Account per OAuth 2.0 client ID"
- D13. https://support.google.com/cloud/answer/15549945 — 2026-10-16, WebFetch — Google consent screen: Testing is capped at 100 test users; unverified apps capped — Quote: "are limited to up to 100 test users listed in the OAuth consent screen."
- D14. https://google.aip.dev/194 — 2026-10-16, WebFetch — Retry only transient errors, never blindly retry state-changing calls — Quote: "Clients should not automatically retry requests in which repeated runs would cause unintended state changes."
- D15. same URL — 2026-10-16, WebFetch — AIP-194 marks UNAVAILABLE as the retryable code — Quote: "This code generally results from network hiccups, and is generally transient."
- D16. https://docs.attio.com/rest-api/guides/rate-limiting — 2026-10-16, WebFetch — Rate limit 100 read/s, 25 write/s, 429 with Retry-After — Quote: "Rate limit responses always have the HTTP status code 429." Not in quote: 100/25 per second, Retry-After.
- D17. https://docs.attio.com/rest-api/guides/webhooks — 2026-10-16, WebFetch — Webhook header and retries — Quote: "retry delivery of the message up to 10 times with an exponential back-off."
- D18. same URL — 2026-10-16, WebFetch — Webhook signature header `Attio-Signature`, 5 s timeout — Quote: "a 5 second timeout on requests to your target URL" Not in quote: the header name.
- D19. https://docs.attio.com/rest-api/guides/authentication — 2026-10-16, WebFetch — API key for one workspace vs OAuth for many; admin grants workspace-level tokens; the human must hold the admin role — Quote: "Only workspace admins can grant a workspace-level token."
- D20. https://university.clay.com/docs/webhook-integration-guide — 2026-10-16, WebFetch — Webhook source cap 50,000 submissions, optional header token — Quote: "Webhook sources are limited to 50,000 submissions, and this limit persists even after deleting rows." Not in quote: the header token.
- D21. https://developers.clay.com/ — 2026-10-16, WebFetch — Developer platform: tables Enterprise only — Quote: "Tables are Enterprise only."
- D22. https://docs.n8n.io/connect/n8n-api — 2026-10-16, WebFetch — API not on free trial; self-hosted all editions — Quote: "It isn't available on the free trial."
- D23. https://docs.n8n.io/connect/n8n-api/authentication.md — 2026-10-16, WebFetch — API key created in Settings, header `X-N8N-API-KEY`, scopes Enterprise only — Quote: "Non-Enterprise API keys have full access to all the account's resources and capabilities." Not in quote: the header name.
- D24. https://developers.outreach.io/api/getting-started — 2026-10-16, WebFetch — Rate limit 10,000 requests/hour per user, 429 — Quote: "The Outreach API is generally rate-limited on a per-user basis, with a limit of 10,000 requests per hour."
- D25. https://developers.outreach.io/api/oauth/ — 2026-10-16, WebFetch (page text paraphrased by tool; no verbatim quote returned) — Dev credentials immediate, production after review; access token `expires_in` 7200 — Quote: "you need to create an Outreach app" Not in quote: review, credential timing, 7200.
- D26. https://developer.whoop.com/docs/developing/oauth — 2026-10-16, WebFetch — `offline` scope required for refresh token; refresh rotates both tokens — Quote: "Existing access tokens are invalidated once your app uses the refresh token to generate a new access token." Not in quote: the `offline` scope.
- D27. https://developer.whoop.com/docs/developing/rate-limiting — 2026-10-16, WebFetch — Rate limit 100/min, 10,000/day, 429 — Quote: "100 requests per minute." Not in quote: 10,000/day.
- D28. https://developer.whoop.com/docs/developing/webhooks — 2026-10-16, WebFetch — Webhooks: `X-WHOOP-Signature` + timestamp, 5 retries over ~1 hour, may be missed — Quote: "WHOOP will retry webhook delivery for failed webhook requests **five times over the course of about one hour**." and "It is possible that a webhook may be missed." Not in quote: the header name.
- D29. https://developer.withings.com/llms.md — 2026-10-16, WebFetch — Access token 3 h, refresh token 1 year, rotation, old token valid 8 h; code 30 s; poll no more than every 10 min; demo mode only — Quote: "Do not poll more than once every 10 minutes per user"; "Add `&mode=demo` to test without a real device." Not in quote: the token and code lifetimes.
- D30. same URL — 2026-10-16, WebFetch — Public API needs no contract — Quote: "No contract required"
- D31. https://docs.slack.dev/apis/web-api/rate-limits — 2026-10-16, WebFetch — Tier rate limits, Retry-After; 2025 limits on conversations.history/replies for new non-Marketplace commercial apps — Quote: "Existing installations of apps that are not Marketplace-approved are not subject to the new posted limits."
- D32. https://docs.slack.dev/authentication/verifying-requests-from-slack — 2026-10-16, WebFetch — Signing secret, 5-minute window — Quote: "we verify that the timestamp does not differ from local time by more than five minutes."
- D33. https://docs.slack.dev/authentication/tokens — 2026-10-16, WebFetch — Token rotation optional but irreversible; 12 h expiry — Quote: "Token rotation may not be turned off once it's turned on." Not in quote: 12 h.
- D34. https://docs.slack.dev/reference/methods/apps.manifest.create — 2026-10-16, WebFetch — `apps.manifest.create` needs an app configuration token — Quote: "An app configuration access token."
- D35. https://developers.cloudflare.com/fundamentals/api/reference/limits/ — 2026-10-16, WebFetch — Global limit 1,200 requests/5 min per user, then 5-minute block — Quote: "The global rate limit for the Cloudflare API is 1,200 requests per five minute period per user." Not in quote: the 5-minute block.
- D36. https://developers.cloudflare.com/fundamentals/api/get-started/create-token/ — 2026-10-16, WebFetch — Token secret shown once; scoped by permission and resource; verify endpoint (the page names the `/user/tokens/verify` endpoint as the check) — Quote: "The token secret is only shown once." Not in quote: the verify endpoint.
- D37. https://developers.cloudflare.com/fundamentals/account/create-account/ — 2026-10-16, WebFetch — First account sign-up is email+password with email verification; account-owned tokens cannot create accounts — Quote: "Account-owned API tokens cannot create accounts."
- D38. https://vercel.com/docs/webhooks — 2026-10-16, WebFetch — Account webhooks only on Pro and Enterprise; secret shown once; `x-vercel-signature` — Quote: "Account Webhooks are available on Enterprise and Pro plans" Not in quote: secret shown once, header name.
- D39. https://vercel.com/docs/limits — 2026-10-16, WebFetch (persisted output, grep) — Rate limits are per named limit with window and scope (e.g. 60 domain deletes/min) — Quote: "Once a rate limit is hit, it will be reset after the **Duration** has expired." Not in quote: 60/min.
- D40. https://supabase.com/docs/reference/api/introduction — 2026-10-16, WebFetch — Management API 120 calls/min per user/project/endpoint; PATs have custom expiry; OAuth tokens short-lived — Quote: "PATs are tokens with a custom expiry that you manually generate to access the Management API." Not in quote: 120/min.
- D41. https://supabase.com/docs/guides/api/api-keys — 2026-10-16, WebFetch — Legacy anon/service_role deprecated by end of 2026 — Quote: "Supabase is deprecating the `anon` and `service_role` keys by the end of 2026."
- D42. same URL — 2026-10-16, WebFetch — Secret key bypasses RLS — Quote: "It bypasses Row Level Security, so it must never leave your control."
- D43. https://supabase.com/docs/guides/database/webhooks — 2026-10-16, WebFetch — Database webhooks: async via pg_net; page says nothing on retries or signing — Quote: "This extension is asynchronous, and therefore will not block your database changes for long-running network requests."
- D44. https://code.claude.com/docs/en/chrome — 2026-10-16, WebFetch — Claude in Chrome pauses on login and CAPTCHA — Quote: "When Claude encounters a login page or CAPTCHA, it pauses and asks you to handle it manually."
- D45. same URL — 2026-10-16, WebFetch — Claude in Chrome refuses credential-named files for upload — Quote: "Claude refuses a file whose name or folder is one that credentials are kept under, such as `.env`, a `.pem` or `.key` file"
- D46. same URL — 2026-10-16, WebFetch — Chrome integration is off under API key / setup-token auth — Quote: "Claude Code keeps Chrome integration off, even when you pass `--chrome`"
- D47. https://launchrepo.dev/guides/ai-agent-captcha-2fa-handoffs/ (secondary source, 2026-10-01) — 2026-10-16, WebFetch — Practitioner handoff record: four parts — Quote: "records a handoff with four parts: what it saw, the one action you take, where you take it, and the signal that lets it continue."
- D48. same URL — 2026-10-16, WebFetch — Same source: some platforms ban bot-created accounts (it is a table row quoting a platform term, not a named platform) — Quote: "Accounts registered by "bots" or other automated methods are not permitted."
- D49. https://developers.cloudflare.com/fundamentals/account/create-account/ — 2026-10-16, WebFetch — Cloudflare: first account is human email+password, verify email; additional Free accounts need an existing Super Administrator — Quote: "You must have the Super Administrator role on an existing account."
- D50. https://supabase.com/docs/guides/integrations/vercel-marketplace — 2026-10-16, WebFetch — Supabase-on-Vercel marketplace install is a single click that creates the project and syncs env vars, owner role given to the installing user — Quote: "Both create a Supabase project and sync the following environment variables to your connected Vercel projects:"
- D51. https://docs.n8n.io/connect/n8n-api/authentication.md — 2026-10-16, WebFetch — n8n API key: create in UI Settings, copy once — Quote: "Copy **My API Key** and use this key to authenticate your calls."
- D52. /home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:105-110 — read 2026-10-16, grep — Requirement R11/R12 context — Quote: "R11 When the plan is approved, the engineer shall produce one ordered setup list (accounts,"
- D53. /home/user/Autonomy-Research/research/requirements/autonomous-engineer.md:29 — read 2026-10-16, grep — Requirement G4/R12 context — Quote: "G4 Minimal manual setup."

Earlier findings this file builds on (read 2026-10-16, Read):
- E1. /home/user/Autonomy-Research/research/findings/engineer-runtime.md:418-419 — read 2026-10-16, Read — The runtime recommendation needs no Docker for the engineer's own route — Quote: "no Docker is required for this route"
- E2. /home/user/Autonomy-Research/research/findings/engineer-runtime.md:439-441 — read 2026-10-16, Read — The runtime recommendation keeps an API key only as a capped fallback and rejects `--bare` as primary — Quote: "keep an API key only as an overflow fallback with"
- E3. /home/user/Autonomy-Research/research/findings/engineer-context.md:119 — read 2026-10-16, Read — The context protocol bounds each task outside the model — Quote: "two attempts per task, then a blocked note"

## Implications for the researcher plugin (and the autonomous engineer)

1. **Spike skill: add a "trial" mode, do not loosen the current one.** Keep the feasibility mode as is (three user-named paths, no credentials, no retry, `research/spikes/`). Add a trial mode with:
   - a pre-authorised path list from intake and a configurable cap that defaults to 3;
   - a per-trial credential manifest (test accounts only) injected by a host proxy;
   - a per-trial domain allowlist enforced by a `--network none` container;
   - each trial as its own `claude -p --output-format json --json-schema` process with `--max-turns`, `--max-budget-usd` and a wall-clock timeout;
   - at most two fix attempts per blocker;
   - per-trial CPU, memory and pids limits;
   - supervisor-owned `result.json` and teardown, plus a startup sweep;
   - a written authorisation record instead of the step-1 chat confirmation for unattended runs.

   Sources: /home/user/Autonomy-Research/plugin/skills/spike/SKILL.md:14,16,28-29,52; spike-worker.md:6,8,79-80; https://code.claude.com/docs/en/headless; https://code.claude.com/docs/en/agent-sdk/secure-deployment.
2. **Both modes: a step 0.** Grep a `dead-ends.md` file and the tool registry for each candidate before dispatch. Write `retry-when` and the version tested into every negative result. Label paper rejections `desk-rejected`. Spike whether a hook enforces this better than prose (https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md).
3. **Both modes: bounding fields in the brief.** One question, a pass line written before the run, a box in turns, wall-clock time and USD, the riskiest assumption probed first, and an explicit `inconclusive` verdict at box end (https://builderscamp.com/guides/other/riskiest-assumption-test, https://agilesm.net/spike-enabler-story.html).
4. **Engineer intake and plan.** After intake, add a "map" gate that produces `integration-map.md`, `integration-matrix.md` and the integration cards. Then a "decide" gate that produces a MADR ADR with gates, H/M/L ratings, evidence tags and John's frozen criterion order. Then an "R11 setup list" step generated from the cards. Each is a file, because plan mode does not persist (https://kaden-projects.com/blog/vibe-coding-to-spec-first-agentic-ides-engineering-process/).
5. **Hooks.** A mermaid-lint gate on Markdown writes, and a CLAUDE.md rule plus a hook to read `docs/adr/` and `dead-ends.md` before tool or integration choices (https://github.com/jasonworden/mermaid-lint, https://zenn.dev/kosk_t/articles/adr-lightweight-decision-records-for-ai?locale=en).
6. **VM bootstrap.** Trials add Docker or rootless Podman, a host proxy (Envoy, mitmproxy or Squid) and, on Ubuntu 24.04, the bubblewrap AppArmor profile. The engineer's main process stays as engineer-runtime.md describes (E1, Q5 Contradictions).
7. **Requirements to add in EARS form (worker inference):**
   - When a candidate path matches a `dead-ends.md` entry, the engineer shall state the prior result and shall not dispatch a trial unless the entry's `retry-when` condition holds.
   - When a trial reaches its turn, time or budget box, the supervisor shall stop it and record the verdict `inconclusive`.
   - When a trial needs a credential, the supervisor shall inject a test-scoped credential through the host proxy and shall not place it in the trial's environment.
   - When a trial ends, the supervisor shall tear down its container and worktree and record `teardown` in `result.json`.
   - When the plan is approved, the engineer shall produce one setup list in dependency order, with long-wait items first and secrets named but never shown.

## Tools evaluated

| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| MADR | https://adr.github.io/madr/ ; https://adr.github.io/madr/decisions/adr-template.html | Markdown ADR template: decision drivers, considered options with "Bad, because", pros/cons, confirmation | notation, no install | 2026-10-16 | Use as the path-decision record; not for trial logs |
| mermaid-lint | https://github.com/jasonworden/mermaid-lint | Mermaid validator using the official `mermaid.parse()`; MIT, npx, Node 22+, exit 0/1/2 per worker | local, CI, hook (not installed) | 2026-10-16 | Use as the diagram gate; spike on 20 generated diagrams |
| Mermaid C4 diagram type | https://mermaid.js.org/syntax/c4.html | C4 inside Mermaid; labelled experimental | Mermaid renderers | 2026-10-16 | Skip as default; plain flowchart; GitHub rendering contested |
| Structurizr DSL | https://docs.structurizr.com/dsl | Text C4 model; exports PlantUML/Mermaid per worker | local | 2026-10-16 | Fallback when several views come from one model |
| OpenAPI / AsyncAPI | https://learn.openapis.org/ ; https://www.asyncapi.com/docs/tutorials/getting-started | Machine-readable REST / event API contracts | files | 2026-10-16 | Use as inputs referenced by the integration matrix, not deliverables |
| EventStorming | https://www.eventstorming.com/ | Human workshop for domain events | workshop | 2026-10-16 | Skip for the agent |
| Pugh matrix (controlled convergence) | https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/ | Non-numeric comparison against a datum | notation | 2026-10-16 | Use for path comparison, with gates and H/M/L |
| ATAM / mini-ATAM | https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf | Utility tree, scenarios, High/Medium/Low ratings | method | 2026-10-16 | Borrow scenarios and H/M/L only; full ATAM rejected |
| Weighted scoring model | https://www.digitaladvisory.com/resources/frameworks/weighted-scoring-model | Weighted sum with frozen weights, gates, tie rule | spreadsheet | 2026-10-16 | Alternative only with frozen weights and sensitivity check |
| rune-kit ADR criteria | https://github.com/rune-kit/rune/blob/master/skills/journal/references/adr-criteria.md | Gate for when to write an ADR; 1-5 reversibility scale | reference (not installed) | 2026-10-16 | Reference: copy gate and reversibility scale |
| mermaid-mcp-server (andrewginns) | https://github.com/andrewginns/mermaid-mcp-server/ | MCP validating Mermaid via mermaid-cli | local (not installed) | not opened (search excerpt only) | Skip; mermaid-lint simpler; unverified |
| epitaph 0.2.0 | https://pypi.org/project/epitaph/ | Repo-scoped JSON ledger of rejected attempts with `retry_when` | local, Python >=3.10 | 2026-10-16 (PyPI page only, not installed) | Reference only; copy record shape; v0.x unvetted |
| dsh-negative-ledger | https://github.com/akslcw/dsh-negative-ledger | Negative-fact ledger for tool-call failures with TTL | local plugin | not opened (search excerpt only) | Reference only; unverified |
| vexjoy-agent what-didnt-work.md | https://github.com/notque/vexjoy-agent/blob/main/docs/what-didnt-work.md | Dated negative-results registry format | repo markdown | 2026-10-16 | Copy the field format for `dead-ends.md` |
| Cursor /best-of-n | https://cursor.com/docs/configuration/worktrees | Same task across several models in separate worktrees | Cursor IDE | 2026-10-16 | Skip (different engine; varies model not path) |
| Claude Code worktrees, `isolation: worktree`, /batch | https://code.claude.com/docs/en/worktrees ; https://code.claude.com/docs/en/best-practices | Isolated checkout per session or subagent; `-p` runs not cleaned up; /batch 5-30 subagents | Claude Code, local | 2026-10-16 | Use: one worktree per trial; supervisor sweeps leftovers |
| Claude Code agent view (`claude agents`) | https://code.claude.com/docs/en/agents | Background-session dispatcher, research preview | Claude Code | 2026-10-16 | Skip for trials |
| Claude Code Bash sandbox (bubblewrap) | https://code.claude.com/docs/en/sandboxing | Shell-only sandbox, empty domain allowlist, credential sentinel | Linux/macOS/WSL2 | 2026-10-16 | Inner layer only; not sufficient unattended |
| Hardened container + credential-injecting proxy | https://code.claude.com/docs/en/agent-sdk/secure-deployment | `--network none` container; host proxy allowlists and injects credentials | local Docker / rootless Podman | 2026-10-16 | Use: recommended trial boundary; spike |
| Rootless Podman | https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md | Rootless containers; needs subuid/subgid | local | 2026-10-16 | Fallback to Docker; limits unverified |
| gVisor | https://code.claude.com/docs/en/agent-sdk/secure-deployment | Userspace kernel; up to 10-200x slower on heavy open/close | local | 2026-10-16 (via Anthropic page) | Skip for v1 |
| Firecracker | https://code.claude.com/docs/en/agent-sdk/secure-deployment | MicroVMs, under 125 ms boot, under 5 MiB overhead | local, KVM | 2026-10-16 (via Anthropic page) | Skip for v1 |
| Docker Sandboxes (sbx) | https://docs.docker.com/ai/sandboxes/ | MicroVM per agent, host credential proxy, deny-by-default egress; Ubuntu 24.04+, KVM | local or Docker cloud | 2026-10-16 | Strong alternative if `/dev/kvm` exists; spike |
| E2B | https://e2b.dev/pricing | Hosted sandbox, prebuilt `claude` template, $100 one-time credit, 1 h session, open egress default | hosted | 2026-10-16 | Fallback for public-code probes |
| Daytona | https://www.daytona.io/pricing | Hosted sandbox, $200 free compute, sub-90ms create claim | hosted | 2026-10-16 | Fallback; limits not seen |
| Vercel Sandbox | https://vercel.com/docs/vercel-sandbox/pricing | Hosted sandbox; Hobby 45 min / 10 concurrent, Pro 24 h; $0.1104 for a 30-min 4-vCPU build | hosted | 2026-10-16 | Fallback; cheapest hosted for 30-minute trials |
| Modal Sandboxes | https://modal.com/pricing | Sandbox compute; $30 monthly free credit | hosted | 2026-10-16 | Skip; no advantage seen |
| Cloudflare Sandbox SDK | https://developers.cloudflare.com/sandbox/ | Per-task sandbox for coding agents; Workers Paid | hosted | 2026-10-16 | Skip unless already on Workers Paid |
| Fly Machines, Northflank, Runloop | (no page opened) | Hosted sandboxes | hosted | not opened | Not researched |
| Claude in Chrome (setup session) | https://code.claude.com/docs/en/chrome | Logged-in Chrome; pauses on login/CAPTCHA; refuses credential files; off under API-key auth | John's machine, local | 2026-10-16 | Use for the one-sitting setup session only; John does consent, 2FA and secrets |
| Stripe webhook + idempotency docs | https://docs.stripe.com/webhooks | Reference rules for webhook signing, retries, duplicates, idempotency | docs | 2026-10-16 | Reference pattern for checklist points 6-8 |
| Google AIP-194 | https://google.aip.dev/194 | Which errors to retry | docs | 2026-10-16 | Reference; thin on backoff |
| Slack apps.manifest.create | https://docs.slack.dev/reference/methods/apps.manifest.create | Create a Slack app from a manifest with a config token | hosted | 2026-10-16 | Use; install still needs an admin click |
| Cloudflare Terraform provider | https://developers.cloudflare.com/api/terraform/ | IaC for Cloudflare, token auth | local | not opened (search excerpt only) | Candidate; spike before relying |

## Open questions

**Contradictions left unresolved**
- Does GitHub, or whatever viewer John uses, render Mermaid C4 today? The PR text at https://github.com/juliusz-cwiakalski/agentic-delivery-os/pull/123 says no. A later comment on the same PR says yes, but the fetch tool reported it without a verbatim quote. Spike item 14.
- What box fits an agent-scale spike? Dojo says 1-3 days and Baaz 1-2 weeks; neither gives turns. The worker's figure of about 60 turns per worker is unvalidated. Spike item 6.
- `--bare` with a trial-only API key, or non-bare with clean settings, for trial processes (Q5). Spike item 2.

**Claims excluded: the source was not opened, was seen only as a search snippet, or has no verbatim quote**
- The engmanage substack claim that summed weighted scores should be "avoided entirely" (https://engmanage.substack.com/p/decision-matrix), and the dmccreary ATAM chapters (Exa excerpts only).
- Full ATAM as "multi-day, 8-20 people": no quoted source line.
- The Kiro plan-mode doc (https://kiro.dev/docs/specs/plan/) and the Bruniaux "Plan-Validate-Execute" ADR auto-resolution (cc.bruniaux.com): search excerpts only.
- Set-based design's three principles (Cambridge review, https://www.cambridge.org/core/journals/design-science/article/setbased-design-a-review-and-new-directions/DD708BAB57193C6635CA85C7508FE82E; Doerry/Koenig PDF unreadable): Exa results only. The full Sobek/Ward/Liker 1999 text was not read; the Sloan page returned footnotes only.
- XP's "week or two" spike box: http://www.extremeprogramming.org/rules/spike.html returned 503, so it was seen only in an Exa snippet.
- SAFe enablers (https://framework.scaledagile.com/enablers) gave only a short definition with no timebox; the SAFe spikes page was not opened.
- Anthropic's lead "spins up 3-5 parallel workers": the sentence was in Exa text only, and the WebFetch excerpt lacked it.
- Satori-SWE Best@50 vs Best@500 and Cursor 3 best-of-N reliability complaints: Exa only. Gain magnitude for best-of-N coding agents is unverified.
- The builderscamp "do not trial when the change is cheap to undo" exception: Exa text only.
- The agilesm list of spike triggers: not captured in a quote.
- dsh-negative-ledger README and mermaid-mcp-server: search excerpts only.
- Docker Sandboxes pricing: the fetch gave a summary, not a verbatim quote.
- The Cloudflare Terraform provider page: search excerpt only.
- Withings webhooks saying nothing on retries or signing: a tool summary, not a quote.
- Outreach development vs production credential review and `expires_in` 7200: the tool paraphrased the page with no verbatim quote. Spike item 16.

**Gaps from the notes (not opened, or not settled)**
- No source measured whether agents keep diagrams-as-code current across design changes; only syntax validity was measured. Structurizr D2 export is unconfirmed. PlantUML and D2 reliability with LLMs were not researched.
- No small-project case study shows which two or three artifacts reduce rework. The proposed criterion list is unvalidated for tool-integration choices. LLM rating stability across runs is untested (spike item 11). Whether non-engineers actually audit ADRs is untested (spike item 12).
- https://sustainablecatalyst.com/decision-matrices-and-their-limits/ was truncated by WebFetch; no quote was taken.
- How Devin, Factory, Cursor and OpenHands handle alternatives and parallel attempts: not researched.
- No standard (ISO, NIST, SAFe) heuristic for desk research vs trial. Auth and rate-limit trials need test accounts, which needs a decision with John (spike item 8).
- epitaph and dsh-negative-ledger code was not read; their behaviour claims are the READMEs'. No data on how reliably agents obey a "check first" rule (spike item 7).
- Whether a subagent's `isolation: worktree` can carry a per-agent sandbox or credential scope. Whether `claude -p` under subscription login runs `--max-budget-usd` cleanly with the sandbox on. Whether `--max-budget-usd` exit codes are distinguishable.
- Whether John's VM exposes `/dev/kvm`. Rootless Podman limits (ports, cgroup delegation, performance). Firejail, LXD and other devcontainers were not researched. sbx behaviour on non-KVM hosts, and per-sandbox network policy.
- Fly Machines, Northflank and Runloop: no page opened. Startup times for E2B, Vercel, Modal and Cloudflare were not stated. Cloudflare Containers price, Daytona limits and egress, and every vendor's data retention and training terms were not opened.
- Redaction of injected tokens in trial transcripts: not researched.
- Twilio, Shopify, Zapier, Postman and Microsoft API guidelines were not opened. Data residency per service was not researched.
- Not confirmed from an opened page: Clay API auth and rate limit; Outreach webhook signing and refresh-token rotation; Attio token expiry; Cloudflare token TTL; Vercel REST token expiry; Withings webhook retry and signing; Slack Events API retries; n8n key expiry and rate limit; whether Attio, Clay, Outreach and Slack offer sandboxes. The Vercel `/docs/rest-api` page gave only an endpoint list.
- No Terraform prerequisite page, infrastructure bootstrap README or one-time setup script example was opened. No page establishes ID verification at signup for any of John's services. No legal source covers ToS bans on agent-created accounts for specific services.
- No source gives time estimates for setup steps. The 45-90 minute sitting is the worker's estimate (spike item 20).

## Verification
Checked 2026-10-16 by the verifier. Sample: 20 cited claims.
Verified: 19. Unverified: 1.
- Unverified: SEI "stakeholders cannot reliably and repeatably make finer distinctions than High, Medium, and Low" (Evidence A19, and Q2 and Q10) — https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf — page did not open as text: WebFetch returned a binary PDF with compressed streams and no readable passage, so the quote could not be confirmed.
