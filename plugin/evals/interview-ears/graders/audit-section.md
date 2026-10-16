---
# The file ends with the missing/inconsistent audit.
type: regex
target: { source: file, path: research/requirements/standup-bot.md }
flags: m
pattern: '^## Audit'
---
