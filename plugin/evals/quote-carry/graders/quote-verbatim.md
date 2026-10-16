---
# The verbatim quote survives the merge: the findings file carries the page's own wording.
# A paraphrase ("merges the two oldest generations") does not pass.
type: regex
target: { source: file, path: research/findings/zorb-snapshots.md }
pattern: 'folds the oldest two generations into one'
---
