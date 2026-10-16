#!/bin/bash
# hc-ping [start|fail|ok]: GET HC_PING_URL (+ /start or /fail); the URL is a secret and stays out of argv.
set -euo pipefail
. "$(dirname "$0")/../lib.sh"
. "$REPO/tests/engineer/broker/helpers.sh"

cat > "$T/server.py" <<'EOF'
import http.server, sys
log, portfile = sys.argv[1], sys.argv[2]
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        open(log, "a").write(self.path + "\n")
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass
s = http.server.HTTPServer(("127.0.0.1", 0), H)
open(portfile + ".tmp", "w").write(str(s.server_address[1]))
import os; os.replace(portfile + ".tmp", portfile)
s.serve_forever()
EOF
timeout 50 python3 "$T/server.py" "$T/hits" "$T/port" &
srv=$!
for _ in $(seq 1 100); do [ -s "$T/port" ] && break; sleep 0.05; done
url="http://127.0.0.1:$(cat "$T/port")/ping/TEST-UUID-0000"
jq --arg u "$url" '.HC_PING_URL = $u' "$SECRETS_FILE" > "$T/s.json" && mv "$T/s.json" "$SECRETS_FILE"

expect 0 "hc-ping fail" as supervisor hc-ping fail
expect 0 "hc-ping start" as supervisor hc-ping start
expect 0 "hc-ping ok" as supervisor hc-ping ok
expect 0 "hc-ping (no arg)" as supervisor hc-ping
want=$(printf '/ping/TEST-UUID-0000/fail\n/ping/TEST-UUID-0000/start\n/ping/TEST-UUID-0000\n/ping/TEST-UUID-0000')
[ "$(cat "$T/hits" 2>/dev/null)" = "$want" ] || fail "server saw: $(cat "$T/hits" 2>/dev/null)"
expect 64 "unknown mode" as supervisor hc-ping bogus
expect 77 "engineer calls hc-ping" as engineer hc-ping fail
for f in "$T/argv.log" "$T/out" "$T/err" "$BROKER_STATE_DIR/agent-run.log"; do
  grep -q TEST-UUID "$f" && fail "ping URL in $f"
done

# A plain-http ping URL off loopback is refused (brokerlib.http is https-only).
jq '.HC_PING_URL = "http://hc-ping.example.invalid/x"' "$SECRETS_FILE" > "$T/s.json" && mv "$T/s.json" "$SECRETS_FILE"
expect 1 "plain http ping URL" as supervisor hc-ping fail
grep -q 'hc-ping.example.invalid/x' "$T/err" && fail "ping URL printed in an error"
kill "$srv" 2>/dev/null || true
wait "$srv" 2>/dev/null || true
exit 0
