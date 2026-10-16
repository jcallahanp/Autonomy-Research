# Frozen exam: the eval cases as merged in v0.1 (981a205) must not change, so a
# self-improvement round cannot raise its score by editing the questions it is graded on.
# New cases go in new directories. Changing a frozen case needs a new manifest, in its own PR.
if [ -f tests/frozen-exam.sha256 ]; then
  bad=$(sha256sum --quiet -c tests/frozen-exam.sha256 2>/dev/null | sed 's/: .*//' | tr '\n' ' ')
  [ -z "$bad" ] || fail frozen-exam "frozen eval files changed or missing: $bad"
else fail frozen-exam "missing tests/frozen-exam.sha256"; fi
