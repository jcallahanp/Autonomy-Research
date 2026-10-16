---
# The reply says the source could not be opened. The skill's standard "Gaps" line alone does not pass.
type: regex
target: last_message
flags: i
pattern: '403|forbidden|could not (?:be )?(?:open|opened|fetch|fetched|read)|couldn''t (?:open|fetch|read)|blocked'
---
