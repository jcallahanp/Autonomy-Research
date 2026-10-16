---
name: browser
description: How the engineer uses a web app that has no usable API - the ladder (API or MCP first, then a recorded Playwright flow, then exploratory Playwright MCP, then John), the challenge check after every navigation, read-after-write, and the stop-and-notify rule for logins, CAPTCHAs and bot challenges. Use before any browser_* tool call, before writing or running a flow under flows/, and whenever a page asks you to sign in or prove you are human.
---

# Browser

The browser is the last automated rung, not the first. It is headed, branded Google Chrome on the
droplet's virtual display (Xvfb `:99`), driven by the Playwright MCP server (`--browser chrome`),
with one persistent profile that John signed in to by hand. John can watch it, and take over, through
noVNC at `https://novnc.<domain>` behind Cloudflare Access.

## Rules that never bend

- **APIs first.** When an API or MCP route exists for an action, use it instead of the browser (F41).
- **No evasion.** Never use stealth plugins, `playwright-extra`, user-agent spoofing, fingerprint
  changes, proxy rotation, CAPTCHA solvers or solving services, or any trick that hides automation.
  Never edit the Playwright MCP launch flags; `playwright-mcp.sh` refuses `--headless`, `--isolated`
  and any profile, browser or proxy override.
- **Stop on any challenge.** A login page, CAPTCHA or bot check ends the task (see below). Do not
  retry, reload in a loop, open another tab or another browser, or try a different account.
- **Allowlisted hosts only.** Navigation goes only to hosts in `browser-allowlist.txt`; the PreToolUse
  hook denies the rest. Ask John (a T1 line) to add a host; never work around the hook.
- **Never sign in yourself.** Do not type passwords, one-time codes or recovery answers. Signing in is
  John's job, by hand, with `browser-login`.

## The ladder

Climb only when the rung below cannot do the job, and say in the task notes which rung you used and why.

1. **API or MCP.** The vendor API through the broker (`api-call`), or the vendor's MCP server. Check
   the project's `integrations` notes first.
2. **Recorded flow.** A Playwright script in the project at `flows/<app>/<task>.spec.ts`, reviewed and
   committed like any code. Run it when one exists for the action.
3. **Exploratory Playwright MCP.** The `browser_*` tools, step by step, for an action with no flow yet.
   When it works and will be repeated, record it as a flow (rung 2) in the same task.
4. **John.** If none of the above can do it safely, stop and add a T1 line describing what is needed.

## After every navigation: the challenge check

After every `browser_navigate`, every click that changes the page, and every flow step that loads a
page, take a `browser_snapshot` and run the challenge check on it:

```bash
# snapshot.json: {"url": "<Page URL>", "title": "<Page Title>", "text": "<the snapshot text>"}
python3 /opt/engineer/scripts/browser/challenge-check.py < snapshot.json
```

It prints `{"challenge": true|false, "kind": ..., "host": ...}` and exits 3 on a challenge, 0 when
clean, 2 on bad input. Kinds come from `templates/challenge-patterns.txt`: `google_blocked`,
`google_sorry`, `cloudflare`, `captcha`, `login_required`. Treat exit 2 as a challenge too: if you cannot
tell, stop. Also stop when you see any of these by eye even if the check is clean (a new pattern then
belongs in `challenge-patterns.txt`, added by John's review).

## When a challenge appears: stop and notify

When a login page, CAPTCHA or bot challenge appears, the engineer shall stop the task, record a
blocked note naming the host and kind, and add a T1 "re-login or clear the challenge on noVNC" line,
and shall not attempt to bypass it.

1. Stop browser work at once. Leave the tab as it is, so John sees the same page on noVNC.
2. Do not commit half-done browser writes as if they succeeded; note which steps ran.
3. End the session with these two lines in the final message (the supervisor turns them into the
   task's `blocked` note and the morning T1 item):

   ```
   BLOCKED: browser challenge kind=<kind> host=<host> url=<url>
   T1: Re-login or clear the challenge on <host> in noVNC (https://novnc.<domain>), then reply "N y" to retry.
   ```

John then opens noVNC, runs `browser-login <url>` if the profile needs a fresh sign-in (it opens Chrome
with no automation flags, and refuses while the Playwright browser holds the profile), clears the
challenge by hand, and answers the T1 line.

## Writes: always confirm with a separate read

Every write (create, edit, delete, send, save) is followed by a separate read that confirms it: reload
or navigate to the record, take a new snapshot, and check the exact value. A toast, a 200 response or a
closed dialog is not proof. If the read does not show the write, the action failed: say so, do not retry
blindly more than once, and never repeat a write that might already have happened without reading first
(no double sends, no duplicate records).

## Recorded flows

A flow lives at `flows/<app>/<task>.spec.ts` in the project, one action per file, and states its
precondition and postcondition at the top:

```ts
// Precondition: signed in to app.attio.com; the "Companies" object exists; record <name> does not exist.
// Postcondition: exactly one Companies record named <name>, with domain <domain>.
```

- The flow checks its precondition first and fails (does nothing) when it does not hold.
- After the write steps, it re-reads the record on a fresh page load and asserts the postcondition.
- It runs the challenge check after each page load and stops on a challenge, as above.
- It uses the same browser setup as the MCP server: branded Chrome (`channel: "chrome"`), headed, the
  persistent profile at `CHROME_PROFILE`, the egress proxy at `127.0.0.1:PROXY_PORT`. Never `headless`,
  never a fresh or default profile. Close the MCP browser first: only one Chrome may hold the profile.
- Selectors prefer roles and labels (`getByRole`, `getByLabel`) over CSS paths, so a vendor restyle
  breaks fewer flows.
- No credentials in a flow: it relies on the signed-in profile and stops at a login page.

## Writing it up

In the task notes, record for each browser action: the rung used and why the lower rungs could not do
it, the hosts visited, each write and the read that confirmed it, and any challenge with its kind.
