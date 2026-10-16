---
paths:
  - "research/**"
---

# Research files

Template-side rule for anything under `research/`. The format lives in files, not here.

- Findings files follow `research/findings/_FORMAT.md`: section order, confidence, the Evidence
  bullet shape (URL, date opened, tool) and the Verification section.
- Every claim about a tool cites a page opened in the session. Search snippets are not sources.
  An unreachable source goes under Gaps, never into findings uncited.
- Every tool evaluated gets a row in `research/tool-registry.md`: name, link, what it does,
  verified date, verdict.
- Anything unanswered goes in `research/open-questions.md`, not into a guess.
- Requirements go in `research/requirements/<slug>.md` as EARS statements; spike results in
  `research/spikes/<slug>.md`, negative results kept.
- Do not paste a fetched page or a full findings file into the lead's context. Read it in a
  subagent and take back a short summary.
