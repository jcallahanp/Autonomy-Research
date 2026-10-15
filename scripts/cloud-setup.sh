#!/bin/bash
# Installs the Claude Code plugins this repo relies on.
# Cloud sessions don't install plugins listed in .claude/settings.json,
# so this runs as a SessionStart hook (and can be pasted into a cloud
# environment's setup script). It does nothing on a local machine.

if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  exit 0
fi

if claude plugin list 2>/dev/null | grep -q "superpowers@superpowers-marketplace"; then
  exit 0
fi

claude plugin marketplace add obra/superpowers-marketplace >/dev/null 2>&1
claude plugin install superpowers@superpowers-marketplace >/dev/null 2>&1
exit 0
