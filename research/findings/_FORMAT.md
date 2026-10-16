# Findings file format

Each findings file in this folder answers one research area for the researcher-agent design.
Use these sections, in this order:

1. `# <Area>` and a one-paragraph summary of the answer.
2. `## Questions and answers` — one `###` per question. Each answer states a confidence
   (high / medium / low) and the evidence it rests on.
3. `## Evidence` — one bullet per source: URL, date opened, the tool used to open it, and
   the specific claim it supports. Search snippets are not sources.
4. `## Implications for the researcher plugin` — concrete design consequences.
5. `## Tools evaluated` — a table with the same columns as `research/tool-registry.md`:
   `| Tool | Link | What it does | Where it runs | Verified | Verdict |`
6. `## Open questions` — things the evidence could not settle.
7. `## Verification` — written by the verifier after the synthesizer. It states the sample size
   (up to 20 statement-URL pairs), the count verified and unverified, and one line per
   unverified claim: the claim, its URL, and why it failed (page says otherwise, page did not
   open, claim not found).
