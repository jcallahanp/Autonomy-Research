# Self-improvement round 1: implementer report

Date: 2026-10-16. Branch `worktree-agent-a1bef18f4577b81b7`, fast-forwarded from 981a205 to
f938610 (the plan commit) before any change. Plan: `2026-10-16-round-1-plan.md`. Changes 1-7, 9
and 10 are implemented; change 8 (frozen-exam guard) was already in place and is untouched. No
file in `tests/frozen-exam.sha256` changed (`tests/rules/frozen-exam.sh` passes). No eval was
run; the controller measures.

## Test results

- `bash tests/check.sh`: all rules pass, at HEAD and at each of the five change commits
  (checked by `git archive` of each commit into a temp dir).
- `bash tests/test-fm.sh`: all pass.
- `bash tests/check-mermaid.sh`: ran with rendering (npx and local Chromium worked offline from
  cache): 6 diagrams ok.
- RED: the base tree f938610 with the new rule files copied in fails 61 checks. Every new rule
  line failed before its change. The ones the brief asked to show:

  ```
  FAIL citations: verifier tools lack mcp__plugin_research-agent_firecrawl__firecrawl_scrape
  FAIL citations: verifier tools lack mcp__firecrawl__firecrawl_scrape
  FAIL citations: note-schema.md Cited findings template line lacks Quote: "..."
  FAIL citations: researcher.md does not ask for a Quote: on every cited finding
  FAIL citations: synthesizer.md does not carry the Quote: field
  FAIL citations: findings-format.md Evidence bullet lacks Quote:
  FAIL context-rot: with jq: hook did not inject the active run's PLAN.md
  FAIL context-rot: with jq: hook cut PLAN.md before line 60
  FAIL context-rot: with jq: hook dropped the newest INDEX.md line
  FAIL context-rot: with jq: INDEX label does not say 'newest 30'
  FAIL context-rot: without jq: hook did not inject the active run's PLAN.md
  FAIL context-rot: without jq: hook dropped the newest INDEX.md line
  FAIL tool-skills: session-start carried more than 30 INDEX.md lines
  ```

  GREEN: the same rules pass after the change commits (`check.sh: all rules pass`).

## Per change

### 1. Verifier can open what researchers cite
- Files: `plugin/agents/verifier.md`, `plugin/skills/research/findings-format.md` (section 7),
  `plugin/skills/research/SKILL.md` (EARS line).
- What changed: tools add `mcp__plugin_research-agent_firecrawl__firecrawl_scrape`,
  `mcp__firecrawl__firecrawl_scrape` and `Write`. Repo `path:line` citations are read with Read;
  clone citations are fetched at the repo URL. The sample is never more than 20, taken in risk
  order (numbers and dates, quotes, single-source claims, summary claims, then the rest). The
  old "include every summary claim, number and high-confidence claim" rule, which could exceed
  20, is gone. Each claim is judged against its `Quote:`; "uncertain" is a fourth reason and
  counts as unverified. EARS lines rewritten.
- Rule: `tests/rules/citations.sh` (change 1 block); `tests/rules/tail-cases.sh` last check
  (verifier can reach the firecrawl mock).

### 2. Quote carry-through
- Files: `plugin/skills/research/note-schema.md`, `plugin/agents/researcher.md`,
  `plugin/agents/synthesizer.md`, `plugin/skills/research/findings-format.md`.
- What changed: every Cited findings line ends `— Quote: "<verbatim, at most 30 words>"`;
  the researcher copies the quote first, then writes a claim that says no more. Synthesizer
  rule 3 (new): copy claim, source and quote together into the Evidence bullet; no information
  not backed by a cited line; never drop a qualifier or narrow a citation; a merged sentence
  cites both notes. These last two come from hand-check patterns #45 and #80. Evidence is one
  bullet per cited claim, with its `Quote:`.
- Rule: `tests/rules/citations.sh` (change 2 block).

### 3. Repo citations are legal
- Files: `plugin/skills/research/note-schema.md`, `plugin/agents/researcher.md`,
  `plugin/agents/synthesizer.md`.
- What changed: an opened source is a URL or a repo `path:line` (local), or
  `<repo URL> <file>:<line> (commit <sha>)` for a clone. The synthesizer keeps them as written.
  Its old "a claim with no URL is excluded" became "no opened source".
- Rule: `tests/rules/citations.sh` (change 3 block).

### 4. Compaction re-injects the active run
- Files: `plugin/hooks/session-start.sh`, `plugin/skills/research/SKILL.md` (step 5 now
  rewrites both Outputs lines so neither says pending; EARS line), `docs/installation.md`.
- What changed: the hook picks the newest `research/runs/*/PLAN.md` (by mtime) whose
  `## Outputs` section contains `pending` or `running` (awk, scoped to that section). It
  injects the first 60 lines of that file under a label that names its path, then the newest
  30 INDEX.md lines (`tail -n 30`), labelled "newest 30 lines". It still needs no jq, still
  exits 0, and takes 20 ms on this repo. The fallback skill list gains `self-improve`.
- Rules: `tests/rules/context-rot.sh` runs the hook against a temp project with three runs:
  an older active one, the newest active one (68 lines) and a newer finished one (with a
  stray "pending" in Facets). The INDEX has 45 lines. The test runs with jq, and again with a
  PATH that holds only dirname, awk, head, tail, ls, cat, sed and tr (no jq). It checks that
  the right PLAN is chosen, the 60-line cut, the 30-line tail, the label and exit 0, and that
  nothing is injected when no run is active. `tests/rules/tool-skills.sh` moves its old
  first-30 check to tail semantics.

### 5. Workers expect compaction
- Files: `plugin/agents/researcher.md`, `plugin/skills/research/SKILL.md`.
- What changed: the researcher writes the note skeleton before its first search and fills it
  as it goes. It is told it may be compacted and must not wrap up early, and to re-read its
  brief and note after a summary. The dispatch template has its own `Rulings:` line, copied
  from PLAN.md verbatim. EARS lines added.
- Rule: `tests/rules/context-rot.sh` (last block).

### 6. Contradictions the run found
- Files: `plugin/skills/research/routing.md`, `plugin/skills/spike/SKILL.md`,
  `plugin/skills/repo-triage/SKILL.md`, `plugin/agents/synthesizer.md`,
  `plugin/skills/research/SKILL.md`.
- What changed: the routing verify fallback is now "Firecrawl scrape, then Parallel or Exa
  fetch with an objective" (no `full_content`, no subagent). In a spike, the lead copies each
  triage `ROW:` line into PLAN.md and writes no registry row; the synthesizer in Spike mode is
  the only writer of spike rows. repo-triage says the same. Findings-file references to
  "Gaps" now say "Open questions": the reply step, the report step, synthesizer rule 2 and
  both EARS lines.
- Rule: `tests/rules/consistency.sh`.

### 7. Pipeline-tail cases
- Files: `plugin/evals/verify-tail/` and `plugin/evals/quote-carry/`: prompt, agent mock, graders.
- verify-tail: a two-facet run (`quux-durability`, facets `wal` and `backup`, `.test` URLs).
  Graders: findings file exists; both notes exist; `^## Verification`; at least one claim
  verified; an INDEX.md line with the slug; PLAN.md exists; PLAN.md `## Outputs` contains
  neither pending nor running (`not_contains`); skill-fired indicator.
- quote-carry: one facet (`zorb-snapshots`). The mock says "The reaper wakes every 900 seconds
  and folds the oldest two generations into one." The prompt plants "AES-256 by default" from
  an unopened forum post. Graders: findings file exists; the literal "folds the oldest two
  generations into one" appears in the note and in the findings; AES-256 is absent from the
  findings `## Evidence` section and from the note's Cited findings; skill-fired indicator.
- Both are `tags: [tail]`, `max_turns: 60`, `timeout_seconds: 900`, with fast-case tools
  (WebFetch, WebSearch and Bash disallowed). Graders are free only: regex, file_exists,
  tool_used. The regexes were checked in Node against good and bad sample texts.
- Rule: `tests/rules/tail-cases.sh`. It checks tags, turns, timeout, disallowed tools, an
  agent mock, `.test`-only URLs, free grader types, absence from the frozen manifest, the
  required graders, that the quote pattern is a literal from the mock, and that the mock does
  not support the planted claim.

### 9. self-improve skill
- Files: `plugin/skills/self-improve/SKILL.md` (110 lines),
  `plugin/skills/using-research-agent/SKILL.md`, the hook fallback string, `README.md`, the
  self-test case notes, `CHANGELOG.md` (Unreleased).
- Content: the frozen exam and its hash manifest; tail cases reported separately; the
  research run on the plugin first; the verifier plus a 20-citation hand check; the keep rule;
  the paired re-measure (`--runs 3`, 5 when budget allows); the exact fast, paired, tail and
  live commands; 2 rounds per approval; the changelog in `docs/self-improvement/`; the pull
  request as the only sign-off; never edit frozen graders or mocks. EARS lines at the end.
- Rules: `tests/rules/self-improve.sh`. `tests/rules/self-test.sh` now requires
  `self-improve` in the index and the hook fallback, and `tests/rules/docs.sh` already requires
  it in the README table.

### 10. One-fact path with no fetch tool
- File: `plugin/skills/research/SKILL.md`. When neither the listed tools nor ToolSearch offer
  a search or fetch tool, the lead says so, names the page, spawns no worker ("a worker has
  the same tools") and suggests setup. EARS line added.
- Rule: `tests/rules/self-improve.sh` (last block).

### Docs
`CHANGELOG.md` gains an Unreleased entry. `README.md` lists the skill. `docs/installation.md`
describes the new hook. `docs/diagrams/c3-research-run.mmd`, `context-flow.mmd` and
`tool-routing.mmd` now show quotes, the verifier writing INDEX, PLAN.md Outputs and the hook.
`research/open-questions.md` gains one entry.

## Rulings

- Ruling: fast-forwarded the worktree from 981a205 to f938610 — the brief requires f938610 or
  later and the worktree started at 981a205 — none: a fast-forward to the named commit.
- Ruling: the verifier gets Write, used only to create a missing INDEX.md — eval workspaces
  start empty, and Edit is not a reliable way to create a file — a Haiku verifier could
  overwrite the findings file with Write (the prompt forbids it). If that shows up, move INDEX
  creation to the lead.
- Ruling: verifier fetch order is the tool the Evidence bullet names, then WebFetch,
  Firecrawl, Parallel, Exa — re-using the opening tool removes the reachability mismatch, and
  Firecrawl is bundled and is what the mocks shadow — in live runs Parallel might quote better
  than Firecrawl. Small effect.
- Ruling: no Playwright or Bash for the verifier — the plan names Firecrawl only, and clones
  are checked by fetching the repo URL — pages only Playwright can open still come back as
  "page did not open".
- Ruling: the quote sits on the citation line (`— Quote: "..."`), and Evidence is one bullet
  per cited claim instead of one per source — this keeps claim, source and quote on one line
  for copying and grading, and the frozen graders' patterns still match — Evidence sections get
  longer.
- Ruling: notes keep `### Gaps`; only findings-file wording changed to Open questions — the
  frozen graders (`url-under-gaps`) and the note schema rule depend on the note heading —
  none for the exam.
- Ruling: the routing.md verify fallback is replaced, not deleted — the table needs a fallback
  cell, and Firecrawl is what the verifier now has — none. The other "in a subagent" cells
  (Playwright, Mermaid) are left as they were, because plan item 6 names only line 13.
- Ruling: registry ownership is per context. A research run's rows stay with the synthesizer
  in normal mode; tool-scan and triage rows go to the lead; spike rows go to the synthesizer in
  Spike mode — this matches the plan's three named owners and leaves research runs unchanged —
  if the plan meant "lead only" for research runs too, synthesizer.md:65-66 still needs a
  change.
- Ruling: "newest" PLAN.md means newest by modification time (`ls -t`) — the lead edits the
  active plan at every step — if an old plan is touched by hand, it wins.
- Ruling: the lead now rewrites the Outputs lines to `written` and `<v> of <n> verified,
  <status>` — the hook's active-run test and the verify-tail grader both need a finished run to
  stop saying pending, and the old text only said "Update the Outputs lines" — a lead that
  skips it keeps re-injecting a finished plan until the next run.
- Ruling: the quote-carry planted claim must be absent from the findings Evidence section and
  from the note's Cited findings, not from the whole file — naming the claim as unconfirmed
  under Open questions is the correct behaviour — a findings file that asserts it in Q&A prose
  without citing it would pass.
- Ruling: verify-tail also grades "at least one claim verified" — this is the only grader
  that shows change 1 lets the verifier reach the mock — it depends on the verifier's own
  `Verified: <n>` line format.
- Ruling: "does not drop" means the paired after suite score is at least the before score, and
  any single case that dropped is named — the plan gives no tolerance — with 3 runs, noise can
  reject a good change.
- Ruling: the paired command is the self-test command plus `--runs 3`, with named JSON files
  — the plan asks for 3 runs — I could not check whether `--runs` overrides a case's `runs: 1`
  (recorded in `research/open-questions.md`). `--max-cost-usd 5` may also stop 48 sessions
  partway; the skill says a partial result is not scored and the ceiling is raised only with
  the user's yes.
- Ruling: no version bump; the CHANGELOG entry is Unreleased — the brief says not to bump, and
  CONTRIBUTING pairs a bump with a release entry — installed users get none of this until a
  release bumps the version.
- Ruling: self-improve asks the user to approve the round plan before implementing — this is
  the "approval" the 2-round cap counts from — one extra confirmation turn.

## Concerns for the controller

- The verifier (Haiku) now has more steps. In fast and tail cases WebFetch is withheld, so it
  should go straight to Firecrawl, but it may spend a turn on ToolSearch first.
- Researchers may cite less under the quote-first rule (claims without a quote become Gaps).
  This is intended, but watch `contradiction`'s llm citation grader and `cite-or-park`.
- The paired protocol's `--runs` precedence and cost ceiling are unverified (see Rulings).
