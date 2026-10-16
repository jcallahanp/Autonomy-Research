# Internal audit of the plugin's own evidence

Brief: From this repo's own files only, rank the plugin's weaknesses that most threaten research quality or context hygiene, so improvement rounds start from evidence rather than guesses.
Run: research/runs/research-agent-self-improvement/PLAN.md

Citation form: `path:line, read 2026-10-16, Read` (Read tool, or Bash `jq` for the eval JSON). All paths are relative to /home/user/Autonomy-Research except the build report, which is at /mnt/project-files/research-agent/2026-10-16-build-report.md (shortened to BR below).

## What does the v0.1 self-test record show about weak or untested areas?

### Takeaway
The 0.97 score measures the lead's routing and the output-shape rules on canned pages. It does not exercise the verifier, the synthesizer's registry writes, the gap round, the 8-worker cap, the lead's "never open a note" rule, the compaction hook, tool-scan or spike. Four cases are weak discriminators, because the no-plugin baseline passes some of their graders. Confidence: high on the facts, medium on the ranking.

### Cited findings
- Result: 0.97 suite score against a 0.8 bar, delta 0.76 against 0.3, 7 of 8 cases at 1.0, one run per case per arm — docs/self-test/2026-10-16-v0.1.md:7-8, read 2026-10-16, Read
- The one failing grader (injection-resist `no-beacon`) was a broken grader. It was fixed afterwards and "has not been re-run" — docs/self-test/2026-10-16-v0.1.md:23-29, read 2026-10-16, Read
- Stated limits: one run per case, the two live cases not run, mocked pages only ("measures the workflow and output rules, not live search quality") — docs/self-test/2026-10-16-v0.1.md:31-38, read 2026-10-16, Read
- The no-plugin baseline scored 1.0 on one-fact-inline. Its four scored graders (answer, cites-url, no-files, no-workers) all passed without the plugin — plugin/evals/results/2026-10-16T02-20-47-488Z/aggregate-result.json (jq over `.cases[].arms`), read 2026-10-16, Bash
- The injection-resist baseline passed `no-pwned-file` (a negative check) and failed `answer`, `flagged` and `no-beacon`. The baseline cannot fetch the mocked page, so the delta there measures tool availability, not injection resistance — aggregate-result.json (same file), read 2026-10-16, Bash
- Weak or vacuous baseline passes: system-map-diagrams `two-mmd-files` passes in the baseline. cite-or-park `reply-says-gap` passes in the baseline. Its regex accepts `403|blocked|unreachable` anywhere in the reply — plugin/evals/cite-or-park/graders/reply-says-gap.md:5-7 and aggregate-result.json, read 2026-10-16, Read/Bash
- one-fact-inline `cites-url` only needs the pattern `https?://\S+` in the reply. It never checks that the URL was opened. The only open-page check, `content-calls`, is `arm: with-only` and reported as `scored: false` in the second run — plugin/evals/one-fact-inline/graders/cites-url.md:3-5, content-calls.md:5-9, aggregate-result.json, read 2026-10-16, Read/Bash
- The `contradiction` case checks both values and both URLs in the findings file. No grader in any case checks a `## Verification` section, an INDEX line, PLAN.md, the worker-count cap, the return-contract line limit, or that the lead did not open notes. Searching all `plugin/evals/*/graders/*.md` for "Verification|INDEX|PLAN" finds nothing. The case list (8 fast + 2 live) has no spike, tool-scan, gap-round or compaction case — plugin/skills/self-test/SKILL.md:127-138, read 2026-10-16, Read, with a Grep over plugin/evals/*/graders
- The cite-or-park and contradiction prompts ask for "a single facet" or give two URLs, so they never test multi-facet fan-out, overlapping facets or the gap round — plugin/evals/cite-or-park/prompt.md:10, plugin/evals/contradiction/prompt.md:10, read 2026-10-16, Read
- The live cases (`triage-real-repo`, `scorecard-lookup`) are the only ones that exercise real tools. They were not run. The scorecard score grader requires "/10" or "out of 10", which BR lists as a known fragility — plugin/evals/scorecard-lookup/graders/score.md:5-6, BR:67, read 2026-10-16, Read
- Fast-case graders for `interview-ears` grade the output file only, not one-question-per-turn (BR:67). The interview prompt answers all questions up front — plugin/evals/interview-ears/prompt.md:10-14, read 2026-10-16, Read

### Contradictions
- None found. The self-test record and the build report agree on the limits (docs/self-test/2026-10-16-v0.1.md:31-38; BR:13-17).

### Inferences
- Most of the 0.76 delta comes from file-existence and presence checks (the baseline cannot write to the plugin's paths or call its mocks). It shows that the plugin's procedures are followed. It does not show that the research is better. Rests on aggregate-result.json (baseline failures are almost all file or mock graders) and docs/self-test/2026-10-16-v0.1.md:34-35.
- The pipeline's tail (synthesizer, verifier, INDEX write) has never been graded in any run. The synthesizer is only indirectly graded through the findings-file regex in contradiction and cite-or-park. This is the largest untested area that affects research quality.
- An `injection-resist` pass rests on one run and one mock page. The `no-beacon` fix is unproven, so injection resistance has no clean passing record yet.

### Gaps
- Whether the 02:01 first run and the 02:20 run differ for cases other than one-fact-inline — only one-fact-inline appears in the 02:01 aggregate. I did not open the HTML reports (the skill says not to).
- Per-run traces (did the lead spawn workers, how many tool calls) were not read, so I cannot say how the lead behaved inside the 7 passing cases.

## What does the build report list as decisions and deferred items, and which bear on quality or context rot?

### Takeaway
Of 26 decisions and about 20 deferred items, roughly a third affect research quality or context hygiene. The ones to act on are: the researcher's shell access with prompt-only injection defence (decision 2), the unproven fix and one-run noise (20, 17), the verifier's capped sample and weak model, the Firecrawl 403 fallback being "a prompt rule only", the spike/repo-triage duplicate registry row, and the session-start index that cannot show setup status. The rest (punctuation, SECURITY.md wording, case-sensitive secret scan, "run from the repo root") is cosmetic. Confidence: medium-high.

### Cited findings
- Decision 2: the researcher keeps Bash, "only prompt rules stop an injected page from turning into a command. This is the main Phase 2 security item" — BR:26, read 2026-10-16, Read
- Decision 9: registry rows are written by one writer. In tool-scan and repo-triage the lead writes them. A terse row line may under-describe install surface — BR:34, read 2026-10-16, Read
- Decision 10: the skill index and findings index are re-injected after /compact and /clear ("the context rot you ranked first") — BR:35, read 2026-10-16, Read
- Decisions 17 and 20: one run per case makes the score noisy, and the grader fix is unproven — BR:47-49, read 2026-10-16, Read
- Decision 22: a research case that writes no findings file fails one more check. The report treats this as a double count — BR:51, read 2026-10-16, Read
- Deferred, quality-relevant: "The verifier's sample can exceed 20, and Haiku may ignore the effort setting" — BR:65, read 2026-10-16, Read
- Deferred, quality-relevant: "The Firecrawl fallback after a 403 is a prompt rule only" and "No helper agent has the Mermaid Chart tool" — BR:66, read 2026-10-16, Read
- Deferred, quality-relevant: "the research skill does not say how to probe for connectors", "Spike and repo triage both describe writing the same registry row", "The tool-scan clone wording is vaguer than the other skills'" — BR:64, read 2026-10-16, Read
- Deferred, quality-relevant: "Several rules check that text is present rather than testing behavior" and the frontmatter parser test is not run in CI — BR:63, read 2026-10-16, Read
- Deferred, context-relevant: the one-line setup status at session start is not injected, "because a shell hook cannot see connectors" — BR:68, read 2026-10-16, Read
- Deferred, cosmetic: secret scan case-sensitivity, diagram edge cases (YAML frontmatter, code spans), SECURITY.md overstating the scan, "from the repo root" wording, Scorecard viewer rendered client-side — BR:63, 66, 68, read 2026-10-16, Read
- The report's own stated "What you decide next" is merge or run more self-tests; it lists no plan for the unrun live cases beyond "with the live cases" — BR:72-73, read 2026-10-16, Read

### Contradictions
- BR:64 says the spike-worker's isolated environment wraps only one command. The agent file's rule 2 does say to run creation, install, probe and cleanup in ONE Bash call or reuse the literal temp path — plugin/agents/spike-worker.md:42-45. The deferred item is therefore partly addressed in the prompt but still depends on the model following it. Not a true contradiction; a "what would settle it" test is a spike with a chained command.
- BR:34 and BR:68 describe the registry as single-writer. The synthesizer's normal output step also writes registry rows (plugin/agents/synthesizer.md:65-66), so there are at least three writers (see the next question).

### Inferences
- Priority among deferred items by effect on research quality: (1) verifier sample and model, (2) Firecrawl 403 fallback only as a prompt rule, (3) registry-row duplication, (4) connector probe not specified, (5) wording-sensitive graders. Everything under Docs and most under Checks is cosmetic. Rests on BR:63-68 and the agent files cited in the next question.
- The report counts the decision "researcher keeps Bash" as a cost of "one folder" style reversibility, but it is the only decision with a security consequence. That is a Phase 2 item, not a quality item for this round.

### Gaps
- The report cites a final reviewer that "found 2 real gaps" and fixes for four (BR:11) but does not name them. The git log has "Fix final-review issues: registry row writer, contradictions, hook matcher, clone location" (commit b90076f), which I did not open as a diff.
- No source here says how often a one-fact question gets misclassified as a multi-facet run, which is a likely lead-routing failure.

## Where do the prompts conflict or leave gaps when read together?

### Takeaway
Seven concrete conflicts or gaps. The worst for research quality: (1) the synthesizer drops any claim without a URL, so it would drop claims backed by clone files or DeepWiki-confirmed file paths that the researcher is told to cite; (2) routing.md recommends Parallel `full content` for verification while the researcher forbids it; (3) the verifier lacks the tools the researcher uses for 403 pages and cannot check clone-path citations; (4) the registry has three writers; (5) tool-scan and the researcher's call budget disagree; (6) the 25,000-character subagent rule has no actor; (7) the lead's worker cap and the effort table disagree. Confidence: high (each is quoted from the files).

### Cited findings
- **Clone citations vs URL-only drop rule.** The researcher is told to "Cite the file path in the clone and the repo URL" for DeepWiki claims — plugin/agents/researcher.md:67-68, read 2026-10-16, Read. The synthesizer excludes any claim "with no URL, or with only a search snippet" — plugin/agents/synthesizer.md:24-26, read 2026-10-16, Read. The Spike-mode exemption covers only claims about the spike run — plugin/agents/synthesizer.md:42-45, read 2026-10-16, Read. A claim cited only as `path in a clone` is not a URL, and the note schema also requires a URL on every Cited findings line — plugin/skills/research/note-schema.md:10-11, read 2026-10-16, Read. This brief's own rule (repo path and line citations) would be dropped by the synthesizer as written.
- **Parallel full content.** routing.md's fallback for "Verify and cite" is "Parallel fetch with full content, in a subagent" — plugin/skills/research/routing.md:13, read 2026-10-16, Read. The researcher says "never use Parallel `full_content`" — plugin/agents/researcher.md:46, read 2026-10-16, Read. The researcher is itself a subagent with `disallowedTools: Agent` (researcher.md:9), so "in a subagent" has no actor there either.
- **Verifier tool gap.** The researcher's 403/429 chain is Parallel fetch, Exa fetch, Firecrawl, then Playwright — plugin/agents/researcher.md:64-65. The verifier tools are Read, Edit, Grep, Glob, ToolSearch, WebFetch, Parallel fetch and Exa fetch, with no Bash, Firecrawl or Playwright — plugin/agents/verifier.md:6, read 2026-10-16, Read. A page the researcher opened through Firecrawl or Playwright will fail in the verifier as "page did not open" and be marked unverified (verifier.md:23-24). Claims cited to a clone file cannot be re-opened at all (temp dir, no Bash).
- **Verifier sample.** "Pick up to 20" but must include "every claim in the summary paragraph, every number, and every claim marked high confidence" — plugin/agents/verifier.md:17-18, read 2026-10-16, Read. The inclusion rule can exceed 20, which BR:65 notes. The verifier runs on `model: haiku` (verifier.md:4). The existing 533- and 543-line findings files (research/findings/methodology.md, packaging.md; `wc -l`, read 2026-10-16, Bash) would be sampled at a small fraction.
- **Three registry writers.** Tool-scan and repo-triage say the lead writes registry rows from `ROW:` lines — plugin/skills/tool-scan/SKILL.md:18-20 and plugin/skills/repo-triage/SKILL.md:24-26, read 2026-10-16, Read. The synthesizer's normal mode also adds rows to the registry — plugin/agents/synthesizer.md:65-66, read 2026-10-16, Read. In a spike, the synthesizer writes rows and the spike skill says "nobody else writes those rows" — plugin/skills/spike/SKILL.md:67-68, read 2026-10-16, Read, while spike step 2 runs `repo-triage`, which has the lead write a row for each path (repo-triage SKILL.md:46-47). Two writers for one candidate row, with no stated precedence. The research skill says "Never ... open a note" (research/SKILL.md:19-20) but the lead is the registry writer for tool-scan, with no step saying who dedupes against rows the synthesizer already wrote.
- **tool-scan budget vs researcher budget.** Tool-scan allows up to three candidate URLs per cluster, each needing triage, README read, two DeepWiki questions plus a clone confirmation and a Scorecard fetch — plugin/skills/tool-scan/SKILL.md:34-47, read 2026-10-16, Read. The researcher stops at "about 10 to 15 tool calls" (researcher.md:47-48) with `maxTurns: 40` (researcher.md:6). Three candidates by at least 5 calls each exceeds 15. Neither file says which limit wins.
- **Wording differences for the same rule.** Excluded claims go "under `## Open questions`" in the synthesizer's rule 1 (synthesizer.md:24-26) but "under Gaps" in its own EARS line (synthesizer.md:79-80) and in research/SKILL.md:210-211. findings-format.md has no Gaps section, only Open questions (findings-format.md:18, read 2026-10-16, Read). Return-size limits also differ: researcher 10 lines, synthesizer 12 lines, verifier 5 lines (researcher.md:87, synthesizer.md:68, verifier.md:42), but research/SKILL.md:200-202 states only the 10-line version.
- **Worker caps.** research/SKILL.md says "Never more than 8 workers per run" (line 17) and the table says "gap round included" (line 38). The "Landscape" row uses 5 workers (line 37). tool-scan says at most 8 clusters (tool-scan SKILL.md:13-14) and spike says at most three workers, but spike step 2 also launches a triage researcher per path before them (spike SKILL.md:55). Nothing counts the triage workers against 8. A gap round after 5 landscape workers has room for only 3, which the skill never states.
- **Steps with no actor.** The EARS line "When a tool's output is expected to exceed 25,000 characters, the call shall run in a subagent and return a summary of at most 2,000 characters" — plugin/skills/research/SKILL.md:208-209, read 2026-10-16, Read. The researcher cannot spawn subagents (researcher.md:9, 15), and the lead may not read pages, so no agent can satisfy it. The same holds for routing.md's "Playwright in a subagent" (routing.md:12, 16) and "Mermaid Chart MCP in a subagent" (routing.md:17), while system-map says "No plugin agent has this tool" (system-map SKILL.md:50-51, read 2026-10-16, Read).
- **Connector probing unspecified.** research/SKILL.md:77-80 says "Check which search tools exist in this session" but gives no method, and the dispatch template's `Tools:` line is a two-way choice (SKILL.md:120). The partial case (Parallel present, Exa missing) is not covered. BR:64 lists it, and research/open-questions.md:13 asks whether detection is even reliable.
- **Hook truncation vs INDEX size.** The hook injects only `head -n 30` of INDEX.md — plugin/hooks/session-start.sh:14, read 2026-10-16, Read. INDEX.md says "Keep it under 200 lines" and its header takes 9 lines — research/findings/INDEX.md:4, 1-9, read 2026-10-16, Read. After about 20 findings the newest lines stop being injected, which defeats the "re-inject after compact" mitigation in BR:35. The lead's own rule is to read INDEX.md first (research/SKILL.md:73) so the file read covers it, but only if the lead follows the step.
- **Lead steps numbering and per-step prompts.** Critical steps list 8 steps (research/SKILL.md:13-24) while Step details are numbered 1-6 and call "Plan" step 1 and "Report" step 6. A model told to follow "step 5" can mean gap-fill or Verify. Minor.
- **Model and effort.** The synthesizer is `model: inherit` with effort high, the lead says "Keep your own model and effort" (research/SKILL.md:181), so the merge quality depends on whatever model the user runs. Researchers are fixed on sonnet/medium. Haiku verifies (agents lines above).

### Contradictions
- plugin/skills/research/routing.md:13 ("Parallel fetch with full content, in a subagent") disagrees with plugin/agents/researcher.md:46 ("never use Parallel `full_content`"). Settle by deciding which file is canonical; the cheapest fix is to delete the routing.md fallback or make it "Parallel fetch with objective".
- plugin/skills/spike/SKILL.md:67-68 ("nobody else writes those rows") disagrees with plugin/skills/repo-triage/SKILL.md:46-47 (the lead writes the row for the same tool). Settle by naming one owner per verdict.
- plugin/agents/synthesizer.md:24-26 (excluded claims go to Open questions) disagrees with plugin/agents/synthesizer.md:79-80 and plugin/skills/research/SKILL.md:210-211 (they go to Gaps).

### Inferences
- Ranking by chance of biting a real run: the verifier tool gap and the clone-citation drop rule will fire on almost every repo-heavy run. The registry duplicate fires on every tool-scan or spike run that also yields a findings file. The tool-scan budget conflict fires whenever a cluster has three candidates. The 25,000-character rule is dead text. The hook's 30-line cap bites after about 20 findings. These are my conclusions from the cited line pairs, not observed failures.
- The self-test cannot catch any of these. Every fast case runs with mocks and single facets (see the first section), so a prompt conflict like the verifier tool gap is invisible to the 0.97.

### Gaps
- I did not test whether Claude Code applies agent `tools` allow-lists with the `mcp__plugin_research-agent_*` names the researcher lists (researcher.md:8). BR:66 says those names were "checked only by reading, not live".
- I did not read plugin/skills/setup/SKILL.md or interview/SKILL.md line by line. Setup's seven-tool probe could conflict with the research skill's two-tool probe.
- Whether `maxTurns: 40` and the 10-15 call guidance conflict in practice depends on how turns count (research/open-questions.md:14 lists this as unmeasured).

## Do research/open-questions.md and research/findings/INDEX.md show open items that block quality?

### Takeaway
Yes, in three ways. All five findings files are `unverified` because none has a `## Verification` section, so no claim in the repo's main evidence base has been spot-checked. Several open questions are about the plugin's own design assumptions (connector detection, `maxTurns`, whether structured returns help), and none can be answered offline. Two of the biggest files (methodology, packaging) are over 500 lines, which is hard on the verifier's 20-pair sample. Confidence: high.

### Cited findings
- All five lines in INDEX.md end with `unverified` — research/findings/INDEX.md:11-15, read 2026-10-16, Read
- `grep -c "## Verification"` returns 0 for architecture.md, context-management.md, methodology.md, packaging.md and tool-routing.md — research/findings/*.md, read 2026-10-16, Bash
- File lengths: architecture 153, context-management 145, methodology 533, packaging 543, tool-routing 296 lines; the tool registry is 77 lines — `wc -l`, read 2026-10-16, Bash
- INDEX.md defines `unverified` as "no Verification section yet" and the verifier "never writes it" — research/findings/INDEX.md:7-9, plugin/agents/verifier.md:38-40, read 2026-10-16, Read
- The cross-cutting open questions that touch plugin quality: connector detection is "an inferred pattern" (open-questions.md:13), whether `maxTurns` maps to tool calls (:14), whether structured return schemas improve merge quality (:15), real cost of the self-test (:16), rate limits for Parallel, Exa and DeepWiki (:17), no context-rot measurement for current models (:21), and no benchmark for depth-first integration research (:22) — research/open-questions.md:10-22, read 2026-10-16, Read
- "Does `/self-test` cost" is still listed as open even though a run happened; the build report records the cost ceiling as $5 (BR:46-47) but not the measured cost. Aggregate-result.json has a `costUsd` key — plugin/evals/results/2026-10-16T02-20-47-488Z/aggregate-result.json (keys), read 2026-10-16, Bash. I did not read its value.
- Git history shows the whole plugin was built in one day (19 commits, newest first: `981a205 Merge pull request #1` ... `06a6f4d Harden frontmatter parser`) — `git log --oneline`, run 2026-10-16, Bash
- The routing table cites `research/findings/tool-routing.md` as its evidence (routing.md:5), one of the five unverified files — plugin/skills/research/routing.md:5, read 2026-10-16, Read

### Contradictions
- None found. INDEX.md and the Verification greps agree.

### Inferences
- The prompts' routing rules (tool order, Firecrawl fallback, "lead holds little") rest on unverified findings, and open-questions.md:21 admits the context-rot rule rests on "Claude 4-era data". The most useful evidence-gathering step is to run the verifier on tool-routing.md and context-management.md first, because they back the routing and context-hygiene rules directly.
- The verifier has never run on real content, so its behaviour on 500-line files, on clone-path citations and on 403 pages is unobserved (see the previous question).
- Open-questions.md has no item for the prompt conflicts found here, and no item for "does the verifier work end to end". Both are candidates to add.

### Gaps
- I did not read the findings files' contents, only their structure, so I cannot say how many of their claims would fail verification.
- The `costUsd` value in aggregate-result.json was not read, so the "real cost of the fast suite" open question is not closed here.

## Ranked weaknesses (summary for the synthesizer)

| Rank | What fails | Files | Chance of biting a real run | Smallest fix |
| --- | --- | --- | --- | --- |
| 1 | Verifier cannot reopen what researchers opened via Firecrawl, Playwright or a clone, and its sample rule can exceed 20 on a Haiku model. All five findings are unverified and the verifier has never run on real content | plugin/agents/verifier.md:6, 17-18, 23-24; research/findings/INDEX.md:11-15 | High, on every repo-heavy run | Give the verifier Firecrawl and Bash (grep on a re-clone), cap the sample at a fixed 20 with a priority order, then run it on tool-routing.md and context-management.md |
| 2 | Synthesizer drops claims cited by clone path, the researcher is told to cite by clone path, the schema requires a URL | plugin/agents/synthesizer.md:24-26; researcher.md:67-68; note-schema.md:10-11 | High, on any DeepWiki or clone based facet | Allow `<repo URL> + <path:line>` as a valid citation in the three files |
| 3 | The self-test cannot see the pipeline tail (no verifier, INDEX, PLAN.md, gap round, cap, multi-facet or compaction grader). Four baselines pass some graders. Injection-resist fix unproven, one run per case | plugin/evals/**/graders; docs/self-test/2026-10-16-v0.1.md:23-38 | Certain, as a blind spot | Add one multi-facet mock case that checks Verification section, INDEX line, PLAN.md, and that the lead did not Read a note; re-run injection-resist; use runs: 3 |
| 4 | Registry rows have three writers (lead, synthesizer normal mode, synthesizer Spike mode) with no precedence | tool-scan SKILL.md:18-20; repo-triage SKILL.md:24-26; synthesizer.md:65-66; spike SKILL.md:67-68 | Medium-high on tool-scan/spike runs | Pick one writer (the lead, from ROW lines) and delete registry writes from the synthesizer, or make the synthesizer the only writer |
| 5 | Call budget conflict: tool-scan asks for 3 candidates by 5+ steps against a 10-15 call stop | tool-scan SKILL.md:34-47; researcher.md:47-48 | Medium-high on scans | Limit a tool-scan cluster to one candidate per worker, or say tool-scan's budget overrides |
| 6 | routing.md says Parallel full content and subagent fallbacks that the researcher forbids or cannot do. The 25,000 character EARS rule has no actor | routing.md:12-13, 16-17; researcher.md:46; research SKILL.md:208-209 | Medium (wasted context if followed) | Delete the contradicting routing entries; reword the 25,000 rule as "workers call with a pointed objective; the lead never opens such output" |
| 7 | Hook injects only the first 30 lines of INDEX.md, which will drop newer findings. No connector probe method; partial connector case missing | plugin/hooks/session-start.sh:14; research/SKILL.md:77-80 | Low now, medium after about 20 findings | Inject the last 30 lines, or the INDEX lines only; specify a ToolSearch probe for `mcp__Parallel_Search__*` and `mcp__Exa__*` separately |
| 8 | Cosmetic: step numbering mismatch in research SKILL.md, return-limit wording (10/12/5 lines), Open questions vs Gaps wording, secret scan case, SECURITY.md wording, "from the repo root" | research SKILL.md:13-24 vs 62-170; synthesizer.md:24-26 vs 79-80; BR:63, 68 | Low | Fix when touching the files for items 1 to 7 |

## Tools evaluated
None.
