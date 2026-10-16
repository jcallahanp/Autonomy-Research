---
description: Pipeline tail. A two-facet run ends with a verified findings file, an INDEX line and PLAN.md Outputs filled in.
tags: [tail]
runs: 1
max_turns: 60
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

Research how the quuxdb embedded database keeps data safe: how its write-ahead log makes commits durable, and how backup and restore work. The docs are https://docs.quuxdb.test/wal and https://docs.quuxdb.test/backup. I want a full research run with a verified findings file, not a quick answer. Use the run slug quux-durability with two facets, slugs wal and backup.
