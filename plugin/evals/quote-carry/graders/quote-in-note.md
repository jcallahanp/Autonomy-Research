---
# The worker's note carries the page's own wording for the compaction fact in a Quote: field.
type: regex
target: { source: file, path: research/runs/zorb-snapshots/notes/snapshots.md }
pattern: 'Quote:\s*["“][^"”\n]*folds the oldest two generations into one'
---
