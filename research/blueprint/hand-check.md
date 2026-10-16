# Hand check of the engineer findings

Date: 2026-10-16. Checker: fresh hand checker (did not write any of the findings).

## Method

- Population: the 14 files `research/findings/engineer-*.md`.
- Sample: 20 cited claims across 10 files (models, deploy, security, human-loop, runtime, feasibility, briefing, browser, protocol, existing-systems). Weighted to claims the blueprint `research/blueprint/decisions.md` relies on: prices, limits, product behaviour, a security incident, a benchmark.
- Overlap rule: I read the `## Verification` sections of the ten files I drew from. Two first picks were already listed there as unverified (protocol E117, existing-systems S15), so I dropped them and took fresh claims (protocol E109, existing-systems S16).
- Re-opened every source myself with WebFetch (the only fetch tool that worked this run; Exa and Parallel were not needed; Firecrawl is not connected). Where a quote lived in a saved fetch file, I read that saved file at the matching line. No repo `path:line` citations were in the sample.
- Pages were treated as data. No fetched page carried instructions that I acted on.
- One URL in my first attempt was mistyped (GHSA advisory under `github.com/trivy/`), returned 404, and was retried at the correct `aquasecurity` path.
- Verdicts: fully supported (quote and claim match the page), partly supported (page backs the claim with a caveat, or a sub-detail I could not confirm), wrong (page contradicts), unreachable (could not open).

## Results

| # | File | Evidence ID | Claim in brief | URL | Verdict | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | engineer-models.md | E4 | Gemini 4 Argon $2/$10 per 1M through 2026-11-30, then $4/$20; not on Free tier | https://ai.google.dev/gemini-api/docs/pricing | Fully supported | Page: "$2.00 through November 30, 2026", "$4.00 starting December 1, 2026"; "not available on the Free tier or on the Google AI Pro plan." |
| 2 | engineer-models.md | E25 | Opus 4.6 MRCR v2 8-needle 93.0% at 256K, 76.0% at 1M | https://klu.ai/benchmarks/mrcr-v2 | Fully supported | Table row "93.0% at 256K; 76.0% at 1M". Secondary aggregator reporting Anthropic's runs; not re-run. |
| 3 | engineer-models.md | E58 | Gateway credential replaces the Max login and is billed per token; setting only ANTHROPIC_BASE_URL keeps the subscription | https://code.claude.com/docs/en/llm-gateway | Fully supported | "Setting only that variable, without a gateway credential, doesn't replace the subscription." |
| 4 | engineer-models.md | E20 | Haiku 5.5 is a 1M-context model; prompts over 100k tokens cost more on Haiku 5.5 | https://platform.claude.com/docs/en/build-with-claude/context-windows | Fully supported | "except on Claude Haiku 5.5, where prompts over 100,000 tokens cost more." |
| 5 | engineer-deploy.md | E1 | Workers Free: 100,000 requests/day, 10 ms CPU, 100 Workers per account | https://developers.cloudflare.com/workers/platform/limits/ | Partly supported | Daily limit quote and 10 ms CPU (plan table) verified. "100 Workers per account" was not on the page as I read it. |
| 6 | engineer-deploy.md | E52 | Public-repo scheduled workflows auto-disable after 60 days without activity; schedule can be delayed under load | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows | Fully supported | Both quotes match. |
| 7 | engineer-deploy.md | E23 | Neon Free: 100 CU-hours per project per month, 1 GB per project, compute suspends after 5 min idle | https://neon.com/docs/introduction/plans | Fully supported | Plan table: "100 CU-hours/project", "1 GB/project", "After 5 min". |
| 8 | engineer-security.md | E28 | GitHub Code Security $30 and Secret Protection $19 per active committer per month from 1 April 2025, now also on Team | https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/ | Partly supported | Both prices and the April 1, 2025 date verified. The "now also for Team plan" extension is not on the page as I read it. |
| 9 | engineer-security.md | E41 | Trivy compromise: malicious v0.69.4, 76 of 77 trivy-action tags force-pushed, 7 setup-trivy tags replaced, 2026-03-19; safe versions listed | https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23 | Partly supported | Summary confirms malicious v0.69.4, "76 of 77 version tags" and the 19 March 2026 date. Safe versions are in the table (Trivy 0.69.2, 0.69.3; trivy-action 0.35.0; setup-trivy 0.2.6). The finding's quoted sentence "Known safe versions include..." is not verbatim, and the "7 setup-trivy tags" count was not checked. |
| 10 | engineer-security.md | E26 | CodeQL CLI is free only on open-source codebases (and research) unless under a paid GitHub Advanced Security license | https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md | Partly supported | The GHSA license clause quote is verified and the open-source limit is stated. The "(and research)" parenthetical is not on the page as I read it. |
| 11 | engineer-human-loop.md | E42 | Subscription OAuth is for ordinary native use; developers building on the Agent SDK should use API key auth through Claude Console; no routing via Max credentials for others | https://code.claude.com/docs/en/legal-and-compliance | Fully supported | Quote matches verbatim; page also bars routing requests through Free, Pro or Max credentials on users' behalf. |
| 12 | engineer-human-loop.md | E109 | Remote Control keeps permission prompts and AskUserQuestion open until answered; other forwarded dialogs expire after five minutes | https://code.claude.com/docs/en/remote-control | Fully supported | Bullet "Forwarded dialogs expire" says both; the five-minute default and the no-action default are on the page. |
| 13 | engineer-human-loop.md | E115 | Channels in -p mode disable interactive tools (multiple-choice questions, plan approval) so the session never stalls | https://code.claude.com/docs/en/channels | Fully supported | Quote matches verbatim. |
| 14 | engineer-runtime.md | S15 | An API key in the environment overrides the subscription in -p (cost trap) | https://code.claude.com/docs/en/authentication | Fully supported | "In non-interactive mode (-p), the key is always used when present." The word "silently" is the finding's gloss; interactive mode does ask once. |
| 15 | engineer-runtime.md | C59 | Pro and Max have a five-hour session limit and a weekly limit, shared across Claude and Claude Code | https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan | Fully supported | Both quotes match. |
| 16 | engineer-feasibility.md | C42 | E2B free tier: $100 one-time credits, up to 1 hour per sandbox, up to 20 concurrent, $150 monthly plan fee | https://e2b.dev/pricing | Partly supported | Credits, 1-hour session and 20 concurrency verified on the free tier. The "$150 monthly plan fee" line was not confirmed in my fetch. |
| 17 | engineer-briefing.md | E53 | An API-key, gateway-token or cloud-credential session cannot publish artifacts; artifacts are off by default in -p runs | https://code.claude.com/docs/en/artifacts | Fully supported | Quote "Sessions using an API key, gateway token, or cloud-provider credential cannot publish." and the -p exclusion both on the page. |
| 18 | engineer-browser.md | T34 | DOM harnesses beat screenshot-only; Qwen3.8-27B 0.737-0.763 via DOM vs 0.480 via screenshots; declared-done vs verified gap up to 41 points | https://arxiv.org/html/2609.35026 | Partly supported | Both Qwen figures verified. The 41-point gap is the harness completion rate minus EMS (gpt-5.6-luna with openmanus, 1.00 vs 0.59), not a per-task declared-done count. The DOM-vs-screenshot comparison is one model, one run per pair. |
| 19 | engineer-protocol.md | E109 | Interrupted tool calls are not re-run on resume; Claude is told to check whether the call took effect | https://code.claude.com/docs/en/sessions | Fully supported | "doesn't finish or run again when you resume"; Claude "is told to check whether it took effect before running it again". |
| 20 | engineer-existing-systems.md | S16 | Clay Tables (Enterprise): query existing Clay table data from known tables | https://developers.clay.com/index.md (cited as http://developers.clay.com/) | Fully supported | Row: "Tables (Enterprise) | Query existing Clay table data from known tables". The finding cites the same page's .md sibling. |

## Totals

- Sampled: 20 cited claims, 10 files.
- Fully supported: 14.
- Partly supported: 6 (rows 5, 8, 9, 10, 16, 18).
- Wrong: 0.
- Unreachable: 0.

## Bar

Bar: zero wrong and at least 17 of 20 fully supported.
- Zero wrong: met.
- At least 17 fully supported: NOT met (14 of 20).

Result: the bar is not met. Every partly supported row is a sub-detail the page does not state, or a wording that overreaches the page, not a contradiction. Those six findings should be reworded or re-cited before the blueprint relies on them.

## Observations outside the sample

- protocol E117 (auto-continue in -p) is already listed in that file's Verification as overreaching. I re-read the page: it says the menu row is unavailable for -p runs, and that `/config autoContinueAtUsageLimit=false` works with -p. It does not say that auto-continue runs in -p. Not counted here.

## Follow-up (2026-10-16)
The bar was not met: 14 of 20 fully supported, against 17 required (zero wrong, which is met). The six partly supported claims share one pattern: the synthesizer added a detail beyond what the quoted page says (a count, a plan tier, a fee, a scope). All six were corrected in the findings files and, where repeated, in the blueprint, each marked "(corrected after hand check, 2026-10-16)". Correcting the sampled claims does not show the rest of the population is clean; the pattern is the input for a round 2 of research-agent self-improvement, which needs John's go.
