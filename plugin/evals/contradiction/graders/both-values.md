---
# The findings file states both values, 30 and 60 seconds.
type: regex
target: { source: file, path: research/findings/fizz-timeout.md }
flags: i
pattern: '^(?=[\s\S]*\b30 ?(?:s|sec|secs|seconds)\b)(?=[\s\S]*\b60 ?(?:s|sec|secs|seconds)\b)'
---
