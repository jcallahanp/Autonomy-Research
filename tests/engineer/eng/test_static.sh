#!/bin/bash
# Static checks over engineer/: bash syntax and strict mode, Python compiles, file size, no secrets.
# Vendored Superpowers files (exact paths in engineer/plugin/superpowers.sha256) skip the code-style
# checks; the secret scan still covers them. Usage: test_static.sh [DIR]  (default engineer)
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
E=${1:-engineer}

declare -A vendored=()
if [ -f "$E/plugin/superpowers.sha256" ]; then
  while read -r _ p; do [ -n "${p:-}" ] && vendored["$E/plugin/$p"]=1; done < "$E/plugin/superpowers.sha256"
fi
own() { [ -z "${vendored[$1]:-}" ]; }

bash_files=(); py_files=()
while IFS= read -r -d '' f; do own "$f" && bash_files+=("$f"); done < <(find "$E" -type f -name '*.sh' -print0)
while IFS= read -r -d '' f; do own "$f" && py_files+=("$f"); done < <(find "$E" -type f -name '*.py' -print0)
while IFS= read -r -d '' f; do
  own "$f" || continue
  first=$(head -1 "$f")
  if [[ "$first" =~ ^\#!(/bin/bash|/usr/bin/env\ bash)$ ]]; then bash_files+=("$f")
  elif [[ "$first" =~ ^\#!(/usr/bin/python3|/usr/bin/env\ python3)( -I)?$ ]]; then py_files+=("$f"); fi
done < <(find "$E" -type f ! -name '*.*' -print0)

for f in "${bash_files[@]}"; do
  bash -n "$f" 2>/dev/null || fail "$f: bash -n"
  sed -n '2,3p' "$f" | grep -qx 'set -euo pipefail' || fail "$f: line 2 or 3 is not 'set -euo pipefail'"
done

for f in "${py_files[@]}"; do
  python3 - "$f" "$T/pyc" <<'EOF' 2>/dev/null || fail "$f: py_compile"
import py_compile, sys
py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)
EOF
done

code=("${bash_files[@]}" "${py_files[@]}")
while IFS= read -r -d '' f; do own "$f" && code+=("$f"); done < <(find "$E" -type f \( -name '*.js' -o -name '*.mjs' -o -name '*.ts' \) -print0)
for f in "${code[@]}"; do
  n=$(wc -l < "$f"); [ "$n" -le 200 ] || fail "$f: $n lines (limit 200)"
done

secret='(sk-ant-|ghp_[A-Za-z0-9]{20,}|github_pat_|xox[baprs]-|AKIA[0-9A-Z]{16}|[0-9]{8,10}:[A-Za-z0-9_-]{35}|BEGIN [A-Z ]*PRIVATE KEY)'
hits=$(grep -rlE "$secret" "$E" 2>/dev/null || true)
[ -z "$hits" ] || fail "secret-shaped text in: $(echo "$hits" | paste -sd ' ' -)"
