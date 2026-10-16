---
description: Pipeline tail. A verbatim quote from the opened page reaches the findings file, and a claim the page does not support is not cited.
tags: [tail]
runs: 1
max_turns: 60
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

Research how the zorbcache server manages its snapshot files: how often old snapshots are compacted and how large one snapshot may grow. The docs are at https://docs.zorbcache.test/snapshots. A forum post says zorbcache snapshots are encrypted with AES-256 by default; check that too. I want a full research run with a findings file, not a quick answer. Use the run slug zorb-snapshots and a single facet with the slug snapshots.
