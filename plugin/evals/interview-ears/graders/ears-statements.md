---
# At least three EARS event-driven statements ("When ..., ... shall ...").
type: regex
target: { source: file, path: research/requirements/standup-bot.md }
pattern: '(?:\bWhen\b[^\n]*\bshall\b[\s\S]*){3}'
---
