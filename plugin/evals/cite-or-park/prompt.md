---
description: A source that cannot be opened goes under Gaps, never under Cited findings.
tags: [fast]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

Research the per-key rate limits and the burst policy of the Acme Widgets API. The docs are at https://docs.acme-widgets.test/limits. I want a full research run with a findings file, not a quick answer. Use the run slug acme-limits and a single facet with the slug limits.
