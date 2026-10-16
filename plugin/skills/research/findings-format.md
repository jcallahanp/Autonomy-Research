# Findings file format

Each findings file in `research/findings/` answers one research area. The research skill's
synthesizer writes it from the worker notes (`note-schema.md`, beside this file) and the
verifier appends section 7. Use these sections, in this order:

1. `# <Area>` and a one-paragraph summary of the answer.
2. `## Questions and answers` — one `###` per question. Each answer states a confidence
   (high / medium / low) and the evidence it rests on. Where sources disagree, a
   **Contradictions** paragraph inside that answer gives both claims with their URLs and says
   which the evidence favours, or that it is unresolved.
3. `## Evidence` — one bullet per cited claim: the source (a URL, or a repo `path:line`), date
   opened, the tool used to open it, the claim, and its `Quote: "<verbatim>"` copied unchanged
   from the note. Search snippets are not sources.
4. `## Implications for the researcher plugin` — concrete design consequences. For a question
   about another project, name that project instead (`## Implications for <project>`).
5. `## Tools evaluated` — a table with the same columns as `research/tool-registry.md`:
   `| Tool | Link | What it does | Where it runs | Verified | Verdict |`
6. `## Open questions` — things the evidence could not settle.
7. `## Verification` — written by the verifier after the synthesizer. It states the sample size
   (at most 20 cited claims, chosen by risk), the count verified and unverified, and one line
   per unverified claim: the claim, its URL or `path:line`, and why it failed (page says
   otherwise, page did not open, claim not found, uncertain).
