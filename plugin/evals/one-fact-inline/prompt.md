---
description: A one-fact question is answered inline, with at most two content calls and no workers.
tags: [fast]
runs: 1
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

What is the default port a Redis server listens on? Give me the source.
