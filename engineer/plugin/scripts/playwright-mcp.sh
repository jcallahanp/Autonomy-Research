#!/bin/bash
set -euo pipefail
# Starts the Playwright MCP server for the engineer: headed branded Chrome (channel "chrome") on the Xvfb
# display, a persistent non-default profile, all traffic through the local egress proxy.
#
# Flags checked against the @playwright/mcp README at tag v0.0.83 on 2026-10-16
# (https://github.com/microsoft/playwright-mcp/blob/v0.0.83/README.md, "Configuration" options table):
#   --browser          "browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge."
#   --user-data-dir    "path to the user data directory. If not specified, a temporary directory will be created."
#   --proxy-server     "specify proxy server, for example "http://myproxy:3128" ..."
#   --headless         "run browser in headless mode, headed by default"  (so we pass nothing: headed)
#   --isolated         "keep the browser profile in memory, do not save it to disk."
# Chrome 136+ refuses automation on its default data directory (engineer-host E13), so that path is refused.
# No stealth plugin, user-agent change, proxy rotation or CAPTCHA solver is ever added here (John's decision 4).

root=$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)
export PATH="$root/bin:$PATH"
# shellcheck disable=SC1091
. "$root/etc/engineer.conf"

die() { echo "playwright-mcp: $2" >&2; exit "$1"; }

# Arguments may add options, never weaken the fixed ones (headed, persistent profile, proxy, branded Chrome).
for a in "$@"; do
  case "$a" in
    *--headless*|*--isolated*|*--user-data-dir*|*--browser*|*--executable-path*|*--proxy-server*|\
    *--proxy-bypass*|*--cdp-endpoint*|*--extension*|*--config*|*--storage-state*|*--device*|*--user-agent*)
      die 2 "refused argument: $a" ;;
  esac
done

profile=${CHROME_PROFILE:-}
while [ "${profile%/}" != "$profile" ]; do profile=${profile%/}; done
case "$profile" in
  "") die 2 "CHROME_PROFILE is empty" ;;
  */.config/google-chrome|.config/google-chrome) die 2 "CHROME_PROFILE is Chrome's default profile: $profile" ;;
esac

pin=$(awk -F'\t' '$1=="@playwright/mcp"{print $3}' "$root/templates/bootstrap-packages.txt")
case "$pin" in
  [0-9]*.[0-9]*.[0-9]*) ;;
  *) die 1 "no @playwright/mcp pin in templates/bootstrap-packages.txt" ;;
esac

export DISPLAY
exec npx --no-install "@playwright/mcp@$pin" --browser chrome --user-data-dir "$profile" \
  --proxy-server "http://127.0.0.1:$PROXY_PORT" "$@"
