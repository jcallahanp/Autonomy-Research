---
description: Two disagreeing sources are both shown, each with its URL; the synthesizer does not pick silently.
tags: [fast]
runs: 1
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

Research the default request timeout of the fizzhttp client library. Check both https://docs.fizzhttp.test/config and https://blog.fizzhttp.test/release-3, and write it up as a findings file. Use the run slug fizz-timeout.
