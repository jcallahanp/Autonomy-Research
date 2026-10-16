#!/bin/bash
# xvfb-session and novnc-session command lines (stubs only; nothing real starts), and the tunnel template.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"

R=$(mk_root "$T/a")
mkdir -p "$T/a/x11"
stub "$R" Xvfb "touch '$T/a/x11/X99'"
stub "$R" fluxbox "echo \"DISPLAY=\$DISPLAY\" > '$T/a/env'"
rc=0; X11_SOCKET_DIR="$T/a/x11" timeout 20 bash "$R/bin/xvfb-session" >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 0 ] || fail "xvfb-session exit $rc"
grep -qx 'Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp' "$T/a/argv.log" || fail "Xvfb argv: $(cat "$T/a/argv.log")"
grep -q '^fluxbox' "$T/a/argv.log" || fail "fluxbox not started"
grep -qx 'DISPLAY=:99' "$T/a/env" 2>/dev/null || fail "fluxbox DISPLAY not :99"

# Xvfb that never makes its socket: xvfb-session fails instead of starting fluxbox
R=$(mk_root "$T/b"); mkdir -p "$T/b/x11"
stub "$R" Xvfb "exit 1"; stub "$R" fluxbox
rc=0; X11_SOCKET_DIR="$T/b/x11" timeout 20 bash "$R/bin/xvfb-session" >/dev/null 2>&1 || rc=$?
[ "$rc" -ne 0 ] || fail "xvfb-session succeeded without a display"
! grep -q '^fluxbox' "$T/b/argv.log" || fail "fluxbox started without a display"

R=$(mk_root "$T/c")
stub "$R" x11vnc; stub "$R" websockify
rc=0; timeout 20 bash "$R/bin/novnc-session" >/dev/null 2>&1 || rc=$?
[ "$rc" -eq 0 ] || fail "novnc-session exit $rc"
for _ in $(seq 30); do grep -q '^x11vnc ' "$T/c/argv.log" 2>/dev/null && break; sleep 0.1; done
grep -qx 'x11vnc -display :99 -localhost -rfbport 5900 -forever -shared -nopw' "$T/c/argv.log" \
  || fail "x11vnc argv: $(cat "$T/c/argv.log")"
grep -qx 'websockify --web /usr/share/novnc 127.0.0.1:6080 127.0.0.1:5900' "$T/c/argv.log" \
  || fail "websockify argv: $(cat "$T/c/argv.log")"

# cloudflared template: only novnc.<domain> to the local noVNC port, everything else 404
tmpl=engineer/templates/cloudflared/config.yml.tmpl
grep -qx 'tunnel: {{TUNNEL_ID}}' "$tmpl" || fail "tmpl: tunnel line"
grep -qx 'credentials-file: /etc/cloudflared/{{TUNNEL_ID}}.json' "$tmpl" || fail "tmpl: credentials-file"
grep -qE '^ *- hostname: novnc\.\{\{DOMAIN\}\}$' "$tmpl" || fail "tmpl: hostname"
grep -qE '^ *service: http://127\.0\.0\.1:6080$' "$tmpl" || fail "tmpl: service"
[ "$(grep -E '^ *- ' "$tmpl" | tail -1 | tr -d ' ')" = "-service:http_status:404" ] || fail "tmpl: last rule not 404"
[ "$(grep -c 'hostname:' "$tmpl")" -eq 1 ] || fail "tmpl: more than one hostname"
