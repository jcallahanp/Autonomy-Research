---
# The reply gives a score on the 0-10 scale.
type: regex
target: last_message
flags: i
pattern: '\b(?:10|\d)(?:\.\d+)?\s*(?:/\s*10|out of 10)'
---
