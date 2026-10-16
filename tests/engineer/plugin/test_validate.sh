#!/bin/bash
# The engineer plugin passes `claude plugin validate --strict` (skipped when claude is not installed).
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

if ! command -v claude >/dev/null 2>&1; then
  echo "SKIP claude not on PATH"
  exit 0
fi
out=$(claude plugin validate engineer/plugin --strict 2>&1) || fail "claude plugin validate --strict: $out"
