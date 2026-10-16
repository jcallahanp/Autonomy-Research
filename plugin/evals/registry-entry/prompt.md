---
description: Evaluating a tool writes a research/tool-registry.md row with link, verified date, verdict and install surface.
tags: [fast]
runs: 1
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash]
---

Is widget-mcp (https://github.com/acme-labs/widget-mcp) worth adding to our toolkit? Evaluate it and log it in our tool registry.
