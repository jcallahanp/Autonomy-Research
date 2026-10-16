---
# The verbatim quote survives the merge: a Quote: field carries the page's own wording. The
# same words in prose with no Quote: do not pass, nor does a paraphrase. Curly quotes pass.
type: regex
target: { source: file, path: research/findings/zorb-snapshots.md }
pattern: 'Quote:\s*["“][^"”\n]*folds the oldest two generations into one'
---
