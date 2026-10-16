# Verify Argon 4 and other candidate models

Brief: Establish, from primary sources, what "Gemini Argon 4" is and which non-Claude models are worth considering as helpers to a Claude Code engineer in October 2026.
Run: research/runs/engineer-models/PLAN.md

## What is "Gemini Argon 4"; limits, price, free tier, data terms, Gemini CLI

### Takeaway
Real, but the name is "Gemini 4 Argon" (`gemini-4-argon`), not "Argon 4". GA on the Gemini API 2026-10-13 (a restricted preview was announced 2026-09-30). 1,048,576-token unified input+output window; $2/$10 per 1M tokens until 2026-11-30, then $4/$20. NOT on the free tier (paid API only), so free-tier prompt-training does not apply to it; the paid tier does not train on prompts. Gemini CLI is not optimised for it; Google says use Antigravity. Confidence: high.

### Cited findings
- Name and model code are "Gemini 4 Argon" / `gemini-4-argon`; 1,048,576 unified context, max output 65,536 default, up to 1,048,576 with long decode — https://ai.google.dev/gemini-api/docs/models/gemini-4-argon, opened 2026-10-16, WebFetch — Quote: "65,536 (default synchronous) / up to 1,048,576 (with long decode)"
- Changelog lists GA on 2026-10-13 and the next-newest Gemini releases (Nano Banana 2.1 Oct 6; Gemini 3.8 Flash Sep 2) — https://ai.google.dev/gemini-api/docs/changelog, opened 2026-10-16, WebFetch — Quote: "Gemini 4 Argon (`gemini-4-argon`) generally available (GA)"
- Google blog confirms global availability on 2026-10-13 and the intro price with expiry — https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/, opened 2026-10-16, WebFetch — Quote: "After the introductory period expires on November 30, 2026,"
- Pricing page: not on Free tier; $2 in / $10 out through 2026-11-30, then $4 / $20; cached $0.10 then $0.20; single rate, no context tiers; paid tier data row "No" (not used to improve products) — https://ai.google.dev/gemini-api/docs/pricing, opened 2026-10-16, WebFetch — Quote: "is not available on the Free tier or on the Google AI Pro plan."
- Terms: unpaid services (free quota, AI Studio) use submitted content to improve products and allow human review; paid services do not — https://ai.google.dev/gemini-api/terms, opened 2026-10-16, WebFetch — Quote: "Google uses the content you submit to the Services and any generated responses to provide, improve, and develop"
- Terms, paid: "Google doesn't use your prompts" or responses to improve products; logs kept for limited time for abuse and legal reasons — same URL, WebFetch — Quote: "Google logs prompts and responses for a limited period of time"
- Rate limits: no RPM/TPM given for Argon on the docs page; spend tiers apply (Tier 1 needs billing; Tier 2 $100 cumulative + 3 days; rolling 10-minute spend caps $10/$50/$200) — https://ai.google.dev/gemini-api/docs/rate-limits, opened 2026-10-16, WebFetch — Quote: "the API returns a `429 RESOURCE_EXHAUSTED` error."
- Gemini CLI: unpaid/Google One users moved to Antigravity CLI on 2026-06-18, and CLI is not optimised for Argon — https://geminicli.com/, opened 2026-10-16, WebFetch — Quote: "Gemini CLI has not been optimized for Gemini 4 Argon."
- Free-tier Gemini models exist (cheaper tier): Gemini 3.8 Flash is free of charge on free tier, paid $0.75/$3.75 through 2026-12-31 — https://ai.google.dev/gemini-api/docs/pricing, opened 2026-10-16, WebFetch — Quote: "Free of charge." (Gemini 3.8 Flash row, per fetch summary; the Pro-class models show "Not available")
- Model-card/blog snippets (DeepMind model card published 2026-10-13, knowledge cutoff March 2026, MoE) appeared in Exa search highlights only; not opened — see Gaps.

### Contradictions
- John: "Argon 4" — Google: "Gemini 4 Argon". Name order differs only; same model, release date 2026-10-13 matches John. Blog dated 2026-09-30 says "rolling out to a set of trusted cyber defenders" first; public GA was 2026-10-13.

### Inferences
- (mine) For a Claude Code engineer, Argon is a paid-API second opinion/long-document reader, not a free helper. The free-tier path is Gemini 3.8 Flash and similar, but those prompts may train Google models and be read by humans, so unsuitable for client or health data (rests on terms + pricing findings).
- (mine) Argon's $2/$10 intro price equals Claude Sonnet 5.5 ($2/$10) and GPT-6.1 Sol ($2/$10); from December it is double.

### Gaps
- Exact RPM/TPM for Argon per tier: only in the AI Studio rate-limit console, not on the docs page opened.
- DeepMind model card and evals page not opened (search highlights only); benchmark claims not cited.
- Antigravity CLI: how it authenticates with an API key, price and whether it can run headless: not opened. The GitHub issue google-gemini/gemini-cli#27713 (seen in search only) reports AI Studio API-key login was removed; unverified.
- Vertex AI model page seen in search only; Vertex data terms not opened.

## Other candidate models (OpenAI, xAI, DeepSeek, Qwen, Kimi, Mistral, Meta, 1M+ window)

### Takeaway
Six other vendors have 1M-class or near-1M windows in October 2026. Cheapest bulk: DeepSeek V4.1 Flash ($0.15 in / $0.60 out off-peak, 1M). Coding second opinion from a different lab: OpenAI GPT-6.1 Sol ($2/$10, 1.05M) via Codex. Open weights with 1M: Meta Muse Spark Open (released 2026-10-15), Qwen3.8 open. Only Google offers a free tier for current models, and only for Flash-class; no vendor page I opened offers free API use that is safe for private data. Confidence: medium (prices are vendor pages; data terms mostly unopened).

### Cited findings
- OpenAI flagship family: GPT-6 Astra $10/$50, GPT-6.1 Sol $2/$10, GPT-6 Luna $0.10/$0.50, each 1.05M context; no Codex-specific model listed — https://developers.openai.com/api/docs/models, opened 2026-10-16, WebFetch — Quote: "Context window: "1.05M"" (all three; per fetch)
- OpenAI API data: not used to train by default; abuse logs kept up to 30 days — https://developers.openai.com/api/docs/guides/your-data, opened 2026-10-16, WebFetch — Quote: "data sent to the OpenAI API is not used to train or improve OpenAI models."
- xAI Grok 4.7: 500k context (not 1M), $2/$6; only Grok 4.3 and 4.20 (older) have 1M — https://docs.x.ai/developers/grok-4-7, opened 2026-10-16, WebFetch — Quote: "500,000 tokens" (context window row)
- DeepSeek: `deepseek-flash` (V4.1 Flash) and `deepseek-v4-pro`, both 1M context; flash $0.15 in (miss) / $0.60 out off-peak, double at peak (01:00-04:00 and 06:00-10:00 UTC Mon-Fri) — https://api-docs.deepseek.com/quick_start/pricing/, opened 2026-10-16, WebFetch — Quote: "Peak hours are 01:00 - 04:00 and 06:00 - 10:00 UTC, Monday through Friday, excluding Chinese public holidays."
- DeepSeek terms say nothing on whether DeepSeek trains on inputs; users may use outputs to train other models — https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html, opened 2026-10-16, WebFetch — Quote: "training other models (such as model distillation), etc."
- Qwen3.8 Max (Alibaba Model Studio international): $2/$6, up to 1M input, 1M free tokens valid 90 days; page updated 2026-10-15 — https://www.alibabacloud.com/help/en/model-studio/model-pricing, opened 2026-10-16, WebFetch — Quote: "Last Updated:Oct 15, 2026"
- Kimi K3: 1,048,576 context, $3.00 in / $0.30 cached / $15.00 out — https://platform.kimi.ai/docs/pricing/chat, opened 2026-10-16, WebFetch — Quote: "Context window: 1,048,576 tokens" (per fetch summary, with price rows $3.00/$0.30/$15.00)
- Mistral: Large 4 list $1.36 in / $4.18 out, on sale $0.68/$2.09; Medium 3.5 $1.5/$7.5; Small 4 $0.15/$0.60 — https://docs.mistral.ai/inference/pricing, opened 2026-10-16, WebFetch — Quote: "Original price: $1.36" "Sale price: $0.68" (Large 4 input, per fetch)
- Meta: Muse Spark Open weights released, 816B total / 42B active, 1M context, Muse Model License with limited commercial terms, hosted at Together, Fireworks, Groq, OpenRouter etc. — https://research.meta.ai/blog/muse-spark-open, opened 2026-10-16, WebFetch — Quote: "Today, we're releasing the weights for Muse Spark Open, the most capable US open-weight model to date."
- Meta Muse Spark Open license: "free for many developers" — same URL — Quote: "Muse Model License with limited commercial terms, which allow many developers to use the model for free."

### Contradictions
- OpenAI model page says context 1.05M for GPT-6.1 Sol; ChatGPT Work/Codex default is 500,000 (raised from 272k on 2026-10-11 per cryptobriefing.com, not opened). Different surfaces, not a conflict: API max 1.05M, product default 500k.
- Alibaba page says first-party Qwen3.8 Max $2/$6 (international); Mercatus (not opened) lists the same. No conflict found.

### Inferences
- (mine) Specialty map: DeepSeek Flash = cheap bulk/long-document sweeps (1M, cents per run) but data goes to a Chinese-hosted API, so public data only; GPT-6.1 Sol via `codex exec` = different-lab coding second opinion; Gemini 4 Argon = long multimodal (video/PDF) and 1M-output tasks; Muse Spark Open or Qwen3.8 open weights = self-hostable, but need large GPU memory (HF blog: ~266 GB KV cache at 1M, not opened) so impractical for John unless via a US host; Mistral Small 4 / Large 3 (Apache 2.0, per search only) = cheap EU option.
- (mine) Fair Claude comparison: Sonnet 5.5 at $2/$10 with 1M is the same price as Argon's intro rate and GPT-6.1 Sol, so a second model must earn its place on diversity (different errors), vision/video, or price, not on window size.

### Gaps
- Not opened (Codex defaults to gpt-6.1-sol, scriptable via codex exec, plan-included: search highlights from learn.chatgpt.com only): OpenAI Codex pricing page, xAI data-sharing/free-credit terms, Kimi and Qwen data terms, Mistral free-tier data terms, Meta license text, Hugging Face blog. Search highlights only.
- No independent leaderboard (Artificial Analysis, LMArena) was opened; no quality ranking claimed.
- Grok free tier: none found on pages opened.
- Whether OpenAI "Daybreak" or "GPT-Rosalind" models matter: not investigated.

## Claude 1M-token variants and price

### Takeaway
Claude already has 1M windows on most current models, at standard price with no long-context premium except Haiku 5.5 (premium above 100k prompt tokens). Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Fable 5.1 $10/$50. So a 1M window is not a reason to leave Claude. Confidence: high.

### Cited findings
- 1M-token models listed (Fable 5.1, Mythos 5.1, Opus 5.5, Opus 5, Opus 4.6-4.8, Sonnet 5.5, Sonnet 5, Sonnet 4.6, Haiku 5.5) with 128k max output; Haiku 5.5 charges more above 100k — https://platform.claude.com/docs/en/build-with-claude/context-windows, opened 2026-10-16, WebFetch — Quote: "except on Claude Haiku 5.5, where prompts over 100,000 tokens cost more."
- Claude Code: Opus 4.6 and Sonnet 4.6 need `[1m]` variant selection via `/model`; usage credits required on Pro — https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans, opened 2026-10-16, WebFetch — Quote: "usage credits must be enabled to access"
- Prices: Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Fable 5.1 $10/$50, Haiku 5.5 from $0.10/$0.50 — https://platform.claude.com/docs/en/models/opus-5-5/overview (Exa highlights; page not opened by me) — see Gaps.

### Contradictions
- None found.

### Inferences
- (mine) John's Claude Code runs on a Max subscription, so Claude's 1M use costs plan usage, not per-token; Argon, GPT API, DeepSeek are extra per-token spend.

### Gaps
- Pricing page and model overview not opened directly (search highlights only); Claude price figures are therefore uncited here. Verify at https://platform.claude.com/docs/en/about-claude/pricing before spending.
- Whether Max-plan Claude Code exposes `[1m]` for Opus 5.5/Sonnet 5.5 without extra credits: only the help article summary was read.

## Recommendation, alternatives, rejects, spikes (facet-level)
- Recommend: keep Claude (Sonnet 5.5 / Opus 5.5, 1M) as the engine and the only worker by default. Add ONE optional paid helper, GPT-6.1 Sol through `codex exec` as an independent second-opinion reviewer (different lab, $2/$10, no training by default, can use a ChatGPT plan). Add Gemini 4 Argon API only for video/PDF/very-long-output jobs and only on the paid key.
- Alternatives: DeepSeek Flash for public-data bulk sweeps; Gemini 3.8 Flash free tier for non-sensitive scraps; Qwen3.8 Max or Kimi K3 as other second opinions.
- Rejected: free-tier Gemini for client/health data (terms permit training and human review); Grok 4.7 (500k, no advantage); Llama 4 (line ended April 2026 per a third-party page, EU licence block); self-hosting Muse Spark Open or Qwen 2.4T (hardware).
- Spike before building: (1) Antigravity CLI headless with API key and Argon; (2) `codex exec -m gpt-6.1-sol` read-only review from a Claude Code hook, with cost cap; (3) blind A/B of Sonnet 5.5 vs Argon vs GPT-6.1 Sol on 5 of John's real tasks; (4) read Argon rate limits in AI Studio.

## Tools evaluated
| Tool | Link | What it does | Where it runs | Verified | Verdict |
| --- | --- | --- | --- | --- | --- |
| Gemini 4 Argon (`gemini-4-argon`) | https://ai.google.dev/gemini-api/docs/models/gemini-4-argon | Google flagship, 1,048,576 unified window, $2/$10 intro then $4/$20, paid tier only | Gemini API (paid) | 2026-10-16 | Optional paid helper for video/PDF/long output; not free |
| Gemini 3.8 Flash (free tier) | https://ai.google.dev/gemini-api/docs/pricing | Free-of-charge Flash model; free tier content may train and be human-read | Gemini API | 2026-10-16 | Non-sensitive scraps only |
| Gemini CLI / Antigravity CLI | https://geminicli.com/ | Gemini CLI replaced by Antigravity CLI for unpaid/Google One users 2026-06-18; not optimised for Argon | local CLI | 2026-10-16 | Skip Gemini CLI for Argon; spike Antigravity |
| OpenAI GPT-6.1 Sol / Codex | https://developers.openai.com/api/docs/models | 1.05M, $2/$10, default Codex model, scriptable `codex exec` | OpenAI API / ChatGPT plan | 2026-10-16 | Recommended second-opinion helper; spike |
| xAI Grok 4.7 | https://docs.x.ai/developers/grok-4-7 | 500k, $2/$6 | xAI API | 2026-10-16 | Skip |
| DeepSeek V4.1 Flash / V4 Pro | https://api-docs.deepseek.com/quick_start/pricing/ | 1M, $0.15/$0.60 off-peak | DeepSeek API | 2026-10-16 | Cheap bulk, public data only |
| Qwen3.8 Max | https://www.alibabacloud.com/help/en/model-studio/model-pricing | 1M, $2/$6, 1M free tokens for 90 days | Alibaba Model Studio | 2026-10-16 | Alternative second opinion |
| Kimi K3 | https://platform.kimi.ai/docs/pricing/chat | 1,048,576, $3/$15 | Moonshot API | 2026-10-16 | Alternative; not recommended |
| Mistral Large 4 / Small 4 | https://docs.mistral.ai/inference/pricing | Large 4 $1.36/$4.18 (sale $0.68/$2.09); Small 4 $0.15/$0.60 | Mistral API | 2026-10-16 | Cheap EU alternative; context not checked |
| Meta Muse Spark Open | https://research.meta.ai/blog/muse-spark-open | Open weights, 816B/42B active, 1M, limited-commercial licence | self-host or US hosts | 2026-10-16 | Skip unless self-hosting; hardware heavy |
| Claude 1M models (Opus 5.5, Sonnet 5.5) | https://platform.claude.com/docs/en/build-with-claude/context-windows | 1M window at standard price | Claude Code | 2026-10-16 | Baseline engine |
