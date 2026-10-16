---
description: The interview writes EARS requirements to research/requirements/<slug>.md.
tags: [fast]
runs: 1
max_turns: 14
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
disallowed_tools: [WebFetch, WebSearch, Bash, AskUserQuestion]
---

Help me work out the requirements for a stand-up bot before I build it. Call the topic standup-bot. I'm answering your interview questions up front because I can't reply during this session, so write the requirements file from what's here and list anything missing as a gap.

- Purpose: a Slack bot for my 6-person team that collects async stand-ups.
- Why: we span three time zones, and live stand-ups waste about 20 minutes a day. Underneath, we need blockers seen within a few hours, not the next day.
- Goals: each person posts yesterday, today and blockers by 10:00 their local time; the bot posts one summary to #team at 11:00 UTC; anyone who has not posted gets one reminder at 09:30 local time.
- Anti-goals: never DM people outside working hours, never store messages longer than 30 days, no performance tracking or per-person stats.
- Constraints: Slack only, hosted on our existing AWS account, no budget for paid SaaS.
- Prior art: we tried Geekbot and dropped it over price.
- Quality: the summary must arrive by 11:05 UTC on working days; nothing leaves our AWS account.
- Risks: people may ignore reminders.
