#!/bin/bash
# Static checks over engineer/: bash syntax and strict mode, Python compiles, file size, no secrets.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

bash_files=()
while IFS= read -r -d '' f; do bash_files+=("$f"); done < <(find engineer -type f -name '*.sh' -print0)
if [ -d engineer/bin ]; then
  while IFS= read -r -d '' f; do
    case "$(basename "$f")" in *.*) continue ;; esac
    head -1 "$f" | grep -Eq '^#!(/bin/bash|/usr/bin/env bash)' && bash_files+=("$f")
  done < <(find engineer/bin -type f -print0)
fi
for f in "${bash_files[@]}"; do
  bash -n "$f" 2>/dev/null || fail "$f: bash -n"
  sed -n '2,3p' "$f" | grep -qx 'set -euo pipefail' || fail "$f: line 2 or 3 is not 'set -euo pipefail'"
done

while IFS= read -r -d '' f; do
  PYTHONPYCACHEPREFIX="$T/pyc" python3 -m py_compile "$f" 2>/dev/null || fail "$f: py_compile"
done < <(find engineer -type f -name '*.py' -print0)

code=("${bash_files[@]}")
while IFS= read -r -d '' f; do code+=("$f"); done < <(find engineer -type f \( -name '*.py' -o -name '*.js' -o -name '*.mjs' -o -name '*.ts' \) -print0)
for f in "${code[@]}"; do
  n=$(wc -l < "$f"); [ "$n" -le 200 ] || fail "$f: $n lines (limit 200)"
done

secret='(sk-ant-|ghp_[A-Za-z0-9]{20,}|github_pat_|xox[baprs]-|AKIA[0-9A-Z]{16}|[0-9]{8,10}:[A-Za-z0-9_-]{35}|BEGIN [A-Z ]*PRIVATE KEY)'
hits=$(grep -rlE "$secret" engineer 2>/dev/null || true)
[ -z "$hits" ] || fail "secret-shaped text in: $(echo "$hits" | paste -sd ' ' -)"
