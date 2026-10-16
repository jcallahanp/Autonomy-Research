# Multi-model (Area 10) - digest
Source: research/findings/engineer-models.md; verification: 17 of 20 verified, 3 unverified (findings "Verification", 2026-10-16)

## Decision
- Version 1 has no multi-model routing layer. Claude Code on John's Max login, with no gateway, is the only engine and the only writer (Q8). Anthropic "doesn't support routing Claude Code to non-Claude models through any gateway" (E57). A gateway credential replaces the Max login (E58), and gateway sessions lose HIPAA eligibility (E60, E82).
- A 1M window by itself earns no model a slot. Opus 5.5 and Sonnet 5.5 already have 1M windows at standard price (E20). Reliability falls near 1M: Opus 4.6 scores 93.0% at 256K and 76.0% at 1M on MRCR v2, on Anthropic's harness (E25, E26). The mean decay from 128K to 1M is 24.3% across 26 models (E29, E30). Successful agent runs stay under 20k-30k tokens (E33).
- Working ceiling: about 128K-256K for correctness-critical work. Above it, use Explore subagents and targeted reads (Q3 table; worker inference, spike S1).
- Review comes from a fresh-context Claude reviewer subagent with test output attached, after each feature. Every finding becomes a test or a recorded decline (Q8). The basis is that the diversity gain "is mostly the gain of an independent second look, which a fresh same-model session provides" (E41), and that a lightweight cross-model reviewer scores no higher than same-model review (E48).
- One cross-family reviewer is prepared but off by default: the official `openai/codex-plugin-cc` (E68), read-only (E67), output to a dated file, `public` and `internal` code only. It is switched on only if spike S3 shows added findings (Q8).
- Health data stays Claude-only. Unpaid Gemini terms allow human review of input (E76, E77), and gateway or third-party routes leave the BAA scope (E82). Whether OpenAI or Google offer a BAA for health was not researched (Q7).
- "Gemini Argon 4" is real: Google's "Gemini 4 Argon" (`gemini-4-argon`), GA on 2026-10-13 (E2, E3), with a 1,048,576-token unified window (E1). It costs $2 in / $10 out per 1M tokens through 2026-11-30, then $4 / $20, and is not on the free tier (E3, E4). It is not in v1; it waits for a paid-key spike on video, PDF and very-long-output jobs (Q8). The E1 "long decode" output figure is unverified.

## Alternatives and rejected
- Gemini 4 Argon on a paid key through an own wrapper (Agent SDK tool or script): alternative, for video, PDF or very-long-output jobs (Q8; E63).
- PAL MCP `clink`: alternative/reference; stale since 2025-12-15 (E65).
- DeepSeek V4.1 Flash: alternative for bulk sweeps of public data; its terms are silent on training on inputs (E14; Tools evaluated).
- Qwen3.8 Max or Kimi K3 as second opinions: alternatives; their data terms were not opened (Q8; Open questions 8).
- claude-code-router: alternative only for a separate API-key-billed experiment (E64).
- Claude Code through LiteLLM, OpenRouter or any gateway to non-Claude models: rejected. Unsupported, drops the Max login, leaves HIPAA (E57, E58, E60, E61). The LiteLLM PyPI compromise is search-text only.
- Free-tier Gemini, including 3.8 Flash, for client or health data: rejected (E76, E77).
- Gemini CLI with a free Google login: rejected; consumer serving ended 2026-06-18 (E69).
- OAuth-token reuse through third-party tools: rejected; Google forbids it (E71) and so does Anthropic (E62).
- Grok 4.7: rejected; 500k window, no edge (Tools evaluated).
- Self-hosting Muse Spark Open: rejected; 816B parameters (Tools evaluated).
- Whole repos routed into a 1M window: rejected (E33; Q3 table).
- A lightweight cross-model reviewer: rejected (E48).
- An ensemble "council" as default: rejected; no cost-justified evidence beyond two-reviewer coverage (E50, E51).
- Aider-style architect/editor split: rejected (E52).

## Stack
| Tool | What it does here | Where it runs | Cost | Evidence |
| --- | --- | --- | --- | --- |
| Claude Code (Max login, no gateway) | Only engine and only writer | Engineer VM | Max plan; Claude per-token prices not verified (Open questions 5) | E57, E58, E20 |
| Fresh-context Claude reviewer subagent (no write tools) | Review after each feature, with test output | Claude Code | Tokens | E41, E48 |
| Explore subagents and targeted reads | Replace whole-repo or 1M loads above about 128K-256K | Claude Code | Tokens | E33; Q3 table |
| `openai/codex-plugin-cc` / `codex exec` (off by default) | Optional read-only cross-family review to a dated file | Local plugin | OpenAI API key per call; GPT-6.1 Sol $2/$10 per 1M (Tools evaluated); ChatGPT-plan data terms not opened | E67, E68, E80 |
| Data-class wrapper + `model-routing.json` (built only if a second model is enabled) | Default-deny gate by class `public / internal / customer / health` | Agent SDK tool or script | Free | E63; Q7 (worker inference) |

## Setup steps
| Step | Automated or John | How it is verified |
| --- | --- | --- |
| 1. Confirm no gateway: no gateway credential or apiKeyHelper, Max login in use | Automated check | E58: the login stays in use when no gateway credential is set |
| 2. Add the reviewer subagent with no write tools | Automated | Spike S3 control arm |
| 3. Add a PreToolUse hook denying direct `gemini`, `codex`, `agy` or `curl` calls to model hosts | Automated | Spike S7 |
| Optional, only after S3 passes: | | |
| 4. Create an OpenAI API key (paid; not a job-wide env var) | John (paid-service key; findings name no automated path) | Spike S8: only the wrapper process sees it |
| 5. Label data paths with a class and write `model-routing.json` (`health: [anthropic]`) | Automated; John approves any non-Anthropic endpoint for health | Spike S6: unlabelled and `health` paths refused |
| 6. Install `codex-plugin-cc`, read-only | Automated | Spike S2 on 5 real diffs |
| 7. For Argon only: paid Gemini key; read the rate limits in the AI Studio console | John (console and billing) | Spike S9 before any spend |

## Repo composition
- Agents: the fresh-context reviewer, no write tools. This overlaps with engineer-protocol's `auditor` (Q8).
- Hooks: PreToolUse deny on direct vendor CLIs and model-host `curl` (Q7.3).
- Files: `model-routing.json`; data-class labels per directory or file; `reviews/` holding dated second-model outputs with the model id and a prompt hash; a "second opinion unavailable: <status>" line in the PR or plan on fallback (Q6, Q7).
- Scripts: one wrapper as the only route to another model, returning `{status: ok|empty|timeout|auth|quota}`, with at most one retry. Empty stdout counts as failure (Q6; worker inference).
- Plugins: `openai/codex-plugin-cc`, prepared and disabled (Q8).
- Superpowers, Beads and Ralph: not addressed in this findings file.

## Spikes
| Spike | Probe (what to run) | Pass criterion |
| --- | --- | --- |
| S1 | Explore subagent vs 1M whole-repo context on 20 real "how does X work" questions from John's repos | Correctness and token cost compared; confirms the 128K-256K ceiling |
| S2 | `codex-plugin-cc` review vs Claude's own review on 5 real diffs | Not stated beyond the comparison |
| S3 | Seeded bugs in 20-30 of John's PRs: fresh Claude reviewer vs Claude plus Codex (and Gemini), with a same-model fresh control | Codex adds findings beyond a second fresh Claude review; switches the reviewer on |
| S4 | Blind A/B of Sonnet 5.5 vs Gemini 4 Argon vs GPT-6.1 Sol on 5 real tasks, including a video or PDF job | Not stated |
| S5 | `agy` headless with an API key and Argon, including empty output at quota exhaustion; paid-key Gemini CLI headless | Not stated (behaviour recorded) |
| S6 | Data-class wrapper given an unlabelled path and a `health` path | Both refused and logged |
| S7 | PreToolUse hook against direct vendor CLI and model-host calls from Bash | Calls denied |
| S8 | Hook-launched subprocess environment | Only the intended environment; no stray keys |
| S9 | Read Argon's rate limits in the AI Studio console and the Claude pricing page | Done before any spend |
| S10 | Three recorded UI regressions: screenshot-review recall vs a Playwright assertion | Not stated; screenshot review is triage only (E53-E55) |

## Requirements served
- R10: data-class labels with a default-deny wrapper. Health is Claude-only, and GTM/customer PII goes to Claude or a paid API only (Q6 table, Q7).
- R17 (with engineer-protocol): a fresh-context reviewer after each feature (Q8).
- Q1: routing changes only after S1 and S3 are re-run on new model releases (Implications 9).
- Q5: agent reads are kept below about 128K-256K through Explore subagents (Implications 2).
- Q6: paid options carry prices (Argon $2/$10 then $4/$20; GPT-6.1 Sol $2/$10), and none is adopted without a spike showing gain (E4; Tools evaluated).
- Q7: one engine, no gateway, so the Max login and its terms stay intact (E58, E62).

## GTM scenario
- Scan as-is: Explore subagents and targeted reads over the Attio-Project repo, not a 1M whole-repo load. S1 runs on John's repos (Q3, S1).
- Fix Attio tables and views, set up Clay workflows, finish tooling: gap. This area adds no mechanism.
- Clean data: GTM/customer PII is the `customer` class. It may go only to Claude or a paid-tier API, never a free tier (Q6 table, Q7).

## Tensions
- R10 says John's current projects default to permissive. This area makes health Claude-only and default-deny until John decides per vendor (Q7).
- Engineer-protocol replaces the plain fresh reviewer with a script-first auditor. This area still recommends "a fresh-context Claude reviewer subagent ... after each feature" without the script layer. Protocol also scopes any cross-family look to Tier 2 changes (spike 4), while this area scopes it to `public`/`internal` code (S3).
- Worker recommendations conflicted: one optional paid helper, versus Claude-only, versus adding Codex plus a Gemini wrapper. The findings chose Claude-only for v1 (Q8 Contradictions).
- `codex-plugin-cc` runs on a ChatGPT subscription "(incl. Free)", but the no-training statement covers only the OpenAI API (Open questions 18).
- No Anthropic page says whether a Max session may spawn `codex` or `agy` with their own credentials. The findings treat it as allowed by inference (Open questions 19).
- Unverified claims: Argon's long-decode output figure (E1), the paid Gemini log-retention sentence (E6), and Greptile's per-model split (E45). The decision does not rest on them, but E6 matters if Argon is used.
- Second-opinion evidence is single-system, self-published or vendor-run (E41 and E50 self-published; E44 vendor) (Q4).
- No MRCR or ATLAS scores exist for Opus 5.5, GPT-6 or Gemini 4. Claude Code's own 1M behaviour is unmeasured (Open questions 11).

## Open for John
- Whether any non-Anthropic endpoint may ever see health data (Q7; Open questions 17).
- Whether to pay for an OpenAI API key for the off-by-default reviewer if S3 passes (Q8).
- Whether to fund the Argon spike on a paid Gemini key (Q8, S4, S9).
