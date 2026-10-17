# Setup day

The one sitting that turns the stage-1 code into a working engineer on a rented server. Read it on your
phone; type the commands on your Mac (Terminal). Each step says what you do, what you should see, and what
to do if it fails. Technical checks for the builder session are in
[setup-day-appendix.md](setup-day-appendix.md); you can skip that file.

## What you will have at the end
1. A private server (a "droplet") in New York running the engineer around the clock.
2. Overnight work (22:00-07:00 US Eastern) on the projects you list, as pull requests you can read.
3. A morning digest in Telegram at 07:30, where you approve or hold items by replying.
4. Remote Control and a Telegram chat to talk to the engineer during the day.
5. A Chrome on the server, signed in by you, that you can watch from your phone.

## Accounts and costs
| Service | What it is for | Cost | Source |
| --- | --- | --- | --- |
| DigitalOcean droplet, Basic 4 vCPU / 8 GB, New York, Ubuntu 24.04 | The server | $48/month; snapshots $0.06/GB per month | [engineer-host](../../research/findings/engineer-host.md) E64 |
| Weekly droplet backups | Off; snapshots instead (Open decision 9) | about $9.60/month if turned on (20% of $48) | [engineer-host](../../research/findings/engineer-host.md) E64 |
| Claude Max | The engineer's brain; nights use its limits | you already have it | - |
| GitHub Pro (yours) + a second account for the bot | Code, reviews, auto-merge | Pro already bought; bot account: check the price on the day | stage-1 plan |
| Cloudflare account, Tunnel and Access, plus a domain | A private web address for the server's screen | check the price on the day (not in the repo's sources) | - |
| Telegram, two bots from @BotFather | Digest, approvals, daytime chat | check the price on the day (not in the repo's sources) | - |
| healthchecks.io Hobbyist (20 checks); UptimeRobot Free (50 monitors) | Alerts to your phone if the engineer stops | free tiers | [engineer-deploy](../../research/findings/engineer-deploy.md) E129, E131 |
| Attio, Clay, n8n | The first project's tools | your current plans | - |
| Only if the sign-in test fails: Tailscale Personal | Send just the browser's traffic out through your home | free | [engineer-host](../../research/findings/engineer-host.md) E81 |
| Only if the sign-in test fails: a Mac mini M6 at home | The same setup at home | $899 one-off | [engineer-host](../../research/findings/engineer-host.md) E74 |

Any price not in this table: check the price on the day.

## Before the day
1. Merge the stage-1 pull request on GitHub.
2. Appendix part A (two download checksums, two package-signing keys, GitHub's SSH fingerprints) was done
   on 2026-10-17 in one small pull request; merge it if it is still open. Without it, step 4 below stops
   with "not pinned". **The builder** means a Claude Code session on this repo at claude.ai/code (a cloud session).
   Every change to this repo, before and during the day, is made there and reaches the server as a
   pull request you merge; the builder on the server only tests and tells you what to change.
3. Decide the open decisions (stage-1 plan, "Open decisions"), or keep the defaults: engine stays in this
   repo; only Attio, Clay, n8n and Google join this sitting; a domain you already have on Cloudflare; two
   Telegram bots; night 22:00-07:00 with the digest at 07:30; snapshots, no backups.
4. **Make `engineer-scratch` from the project skeleton** (the first night and the auto-merge test run there,
   and they need its files, checks included). On your Mac, in Terminal (install `gh` first with
   `brew install gh` if you do not have it):
   ```
   gh auth login --scopes workflow
   gh repo clone jcallahanp/Autonomy-Research
   python3 Autonomy-Research/engineer/bin/new-project engineer-scratch --name engineer-scratch --owner jcallahanp
   cd engineer-scratch && git init -b main && git add -A && git commit -m "Start from the engineer skeleton"
   gh repo create engineer-scratch --private --source . --push
   ```
   `gh auth login` asks a few questions: pick GitHub.com, HTTPS, and sign in with the browser. The
   `workflow` scope is what lets you push the checks file. If git asks who you are, run the two
   `git config` lines it prints, then the commit line again. Stuck: ask the builder to walk you through it.
5. Have ready: your phone with Telegram, your password manager, a second email address for the bot's
   GitHub account, your n8n address, and about an hour and a half.
6. If your Mac has no SSH key yet: in Terminal run `ssh-keygen -t ed25519` and press Enter at each question.

## The one sitting
Lines in grey boxes are typed on the server unless the step says otherwise. Never paste a secret value
into a chat with Claude; the `seed` command asks for it with the typing hidden.

**Bring the server up**
1. **Create the droplet.** You do: in DigitalOcean create a droplet: region New York, image Ubuntu 24.04
   (LTS), Basic, 4 vCPU / 8 GB ($48/month), authentication by SSH key (paste the contents of `~/.ssh/id_ed25519.pub`
   from your Mac), backups off, name `engineer`. You see: the droplet's IP address. If it fails: pick
   another New York data centre.
2. **Log in.** You do, on your Mac: `ssh root@<IP>` and answer `yes` once. You see: `root@engineer:~#`.
   If it fails: check the key you pasted is the `.pub` file.
3. **Give the server read-only access to this repo** (a "deploy key"). You do:
   ```
   ssh-keygen -t ed25519 -N "" -f /root/.ssh/autonomy-research
   cat /root/.ssh/autonomy-research.pub
   ```
   On GitHub, in Autonomy-Research's settings under Deploy keys, add that line; leave write access off. Then:
   ```
   GIT_SSH_COMMAND="ssh -i /root/.ssh/autonomy-research" git clone git@github.com:jcallahanp/Autonomy-Research.git /srv/autonomy-research
   git -C /srv/autonomy-research config core.sshCommand "ssh -i /root/.ssh/autonomy-research"
   ```
   The first time, ssh asks whether to trust github.com and shows a fingerprint. Type `yes` only if it is
   one of GitHub's published ones: `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU` (ED25519),
   `SHA256:p2QAMXNIC1TJYWeIOttrVc98/R1BUFWu3/LiyKgUfQM` (ECDSA) or
   `SHA256:uNiVztksCsDhcc0u9e8BujQXVUpKZIDTMczCvj3tD2s` (RSA), read 2026-10-17 from
   docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints.
   You see: "Cloning into...", then done. If it fails with "Permission denied": the deploy key is missing or
   on the wrong repo.
4. **Install everything that needs the administrator ("root").** You do:
   `sudo bash /srv/autonomy-research/engineer/scripts/setup-root.sh --install`. You see, after some minutes:
   `setup-root: install done`. If it fails: send the last 20 lines to the builder; it is safe to run again.
   This is its first real run, so a hiccup here is expected and fixable.
5. **Check the secret store's key.** Step 4 made it once with `age-keygen` (it is never replaced). You do:
   `cat /home/secretbroker/.config/sops/age/recipient.txt`. You see: one line starting `age1`. That key
   file is the one thing that unlocks every secret; it never leaves the server (the snapshot in step 21
   keeps a copy). Never run `age-keygen` yourself: a new key would lock the old secrets away.
6. **Install the engineer's own tools.** You do: `sudo -iu engineer`, then
   `bash /opt/engineer/scripts/bootstrap.sh`. You see: `bootstrap: done`. Then type `exit` and
   `sudo -iu engineer` again: the fresh login puts the new tools (`claude` among them) on the path. If it
   fails only at the Telegram plugin, carry on and run it again after step 7 (it is safe to repeat).
7. **Sign the engineer in to Claude.** You do, as engineer: `tmux new -s builder`, then
   `claude auth login` and sign in with your Max account (it shows a link; open it on your phone or Mac and
   paste the code back). Never use `claude setup-token`. Then `bash /opt/engineer/scripts/doctor.sh`. You
   see: only `OK` lines. If a line says `FAIL`: send it to the builder.
8. **Start the builder on the server.** You do: `claude`, then tell it: "You are the builder. Do
   setup-day appendix part B." It tests on its own for a while (tmux keeps it running if you disconnect:
   `Ctrl-b d`). Carry on below in a second Terminal window logged in as root.

**Accounts and secrets** (each secret: `sudo -u secretbroker /opt/engineer/bin/seed NAME`, type the value)
9. **Alerts.** Sign up for healthchecks.io (Hobbyist), make one check called `engineer-supervisor` with the
   period the builder gives you, and add your phone as the notification. Seed `HC_PING_URL` (the check's
   ping address). Sign up for UptimeRobot Free and seed `UPTIMEROBOT_API_KEY`.
10. **The bot's GitHub account and token.** In a private browser window, create a GitHub account with the
    second email; turn on two-factor sign-in. From your own account, invite it with write access to
    Autonomy-Research and `engineer-scratch`; accept as the bot. **As the bot** (the token is the bot's,
    never yours), open github.com/settings/tokens, choose "Generate new token (classic)", tick only the
    `repo` box, set an expiry date. Why classic: GitHub's page "Managing your personal access tokens"
    (read 2026-10-16) lists, among fine-grained tokens' gaps, contributing "to repositories where the user is
    an outside or repository collaborator", which is what the bot is on your repos. Seed it as `GH_BOT_PAT`.
11. **Branch protection** (from your own account) on Autonomy-Research and `engineer-scratch`: the builder
    prints a checklist (required checks, Code Owners review, "Dismiss stale pull request approvals when new
    commits are pushed", "Require approval of the most recent reviewable push", no bypass, no force
    pushes, auto-merge allowed). Tick each item; the builder then
    checks that the bot cannot push to main and that auto-merge works (test SP18). A repo on a personal
    account cannot limit who pushes to a branch, so the `engineer-records` rule is the builder's fallback.
12. **Telegram.** In Telegram, open @BotFather, send `/newbot` twice: a "supervisor" bot and a "chat" bot.
    Send `/start` to each. Seed the supervisor bot's token as `TG_SUPERVISOR_TOKEN`. Then find your own
    Telegram number-id (the token is read with typing hidden, so it stays off the screen):
    ```
    read -rs T && printf 'url = "https://api.telegram.org/bot%s/getUpdates"\n' "$T" | curl -sK - | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"][-1]["message"]["from"]["id"])'; unset T
    ```
    Seed that number twice, as `TG_JOHN_USER_ID` and as `TG_JOHN_CHAT_ID`. Keep the chat bot's token for step 23.
13. **Cloudflare tunnel** (a private road from the internet to the server's screen). You do, as root; the
    first three print a link to open or the tunnel ID (a long code); put yours in for `<ID>` and `<domain>`:
    ```
    cloudflared tunnel login
    cloudflared tunnel create engineer
    cloudflared tunnel route dns engineer novnc.<domain>
    install -d -m 0755 /etc/cloudflared && install -m 0600 /root/.cloudflared/<ID>.json /etc/cloudflared/
    sed -e 's/{{TUNNEL_ID}}/<ID>/g' -e 's/{{DOMAIN}}/<domain>/g' /opt/engineer/templates/cloudflared/config.yml.tmpl > /etc/cloudflared/config.yml
    cloudflared --config /etc/cloudflared/config.yml service install && systemctl start cloudflared
    ```
    You see: `systemctl status cloudflared` says active. If it fails: send the output to the builder.
14. **Cloudflare Access** (the lock on that road). In Cloudflare's Zero Trust dashboard add a self-hosted
    application for `novnc.<your domain>` whose only rule allows your one email. You see, on your phone at
    `https://novnc.<your domain>`: Cloudflare asks for your email, sends a code, then shows noVNC (a
    remote screen). If it fails: test SP71 below.
15. **Let the server reach your n8n.** You do, as root, with your n8n host name (for example
    `yourname.app.n8n.cloud`): `sudo bash /srv/autonomy-research/engineer/scripts/setup-root.sh --allow <n8n host>`.
    Tell the builder the host too: it adds it to `engineer/templates/browser-allowlist.txt` in its next
    pull request (through claude.ai/code), so the engineer's browser may open it after step 22.
16. **Sign the browser in by hand.** On your Mac open `https://novnc.<your domain>` and press Connect. As
    root run `sudo -iu engineer /opt/engineer/bin/browser-login https://accounts.google.com`. Chrome appears on the
    remote screen: sign in to Google, then open new tabs and sign in to Attio, Clay and n8n. If any site
    shows a puzzle, "unusual activity" or a phone check: stop and note it (test SP85).
17. **Tool keys.** Seed `ATTIO_API_KEY` (an Attio access token; needs a workspace admin), `N8N_API_KEY`
    (with an expiry date) and `N8N_BASE_URL` (your n8n address). The Clay command-line tool is not part of
    stage 1, so there is no Clay sign-in today; the browser sign-in of step 16 is enough.
18. **List the projects.** You do: `nano /etc/engineer/projects.txt` and add one line:
    `engineer-scratch jcallahanp/engineer-scratch main self_merge=on scratch=yes owner_login=jcallahanp`.
    Save (`Ctrl-o`, Enter, `Ctrl-x`). The builder then gives you the commands that make the first copies
    (appendix part C); paste them as root.
19. **Check every secret.** You do:
    `sudo -u supervisor /opt/engineer/scripts/checks/verify-all.sh --out /var/lib/engineer/setup-verify.md`
    then `cat /var/lib/engineer/setup-verify.md`. You see: every row `pass` or `manual`, and "setup test"
    on your phone. Rows marked `manual`: check by hand (the Clay row is n/a today). If one fails, it names
    the first bad secret: seed it again.
20. **Privacy.** In Claude's privacy settings choose 30 days or 5 years (Open decision 7).
21. **Snapshot.** Take a snapshot of the droplet in DigitalOcean ($0.06/GB per month). The builder runs the
    snapshot test (SP86).
22. **Lock** (only after test SP18 passed). Merge the builder's pull requests, then
    `git -C /srv/autonomy-research pull` and run step 4 again. Then:
    `sudo bash /srv/autonomy-research/engineer/scripts/setup-root.sh --lock`. You see: `setup-root: lock
    done`. From now on the engineer cannot change its own guards.
23. **Daytime chat.** You do: `sudo systemctl enable --now engineer-remote-control engineer-channels`. The
    builder walks you through giving the chat bot its token and pairing your phone. You see: the session
    in the Claude app, and the chat bot answering.
24. **First night.** Nothing to do: at 22:00 it starts on `engineer-scratch`. At 07:30 the digest arrives.

**After the day.** Add your first real project to `/etc/engineer/projects.txt` (`scratch=no`). When a plan
pull request arrives, move the test drafts from `docs/plan/contracts/acceptance/` into `tests/acceptance/`
yourself; the engineer is not allowed to write there. Approving a plan signs five files: `brief.md`,
`requirements.md`, `integrations.yaml`, `profile.yaml` and `tasks.json` (all in `docs/plan/`); a change to
any of them needs your approval again. A task counts as done only after its pull request has merged.

## Setup-day tests
The builder runs these and tells you each result. "You" marks the ones that need you.
| Test | What it checks | Pass looks like | If it fails |
| --- | --- | --- | --- |
| SP01 | Anthropic's Agent SDK billing and legal pages re-read | Quotes recorded in ADR 0001 | Tell you; nothing runs unattended until you decide |
| SP02 | `/login` keeps Remote Control, connectors, Chrome; no `setup-token` | All three work | Builder fixes; never switch to a token |
| SP04, SP05 | Unattended mode and turn/budget limits end cleanly | Known exit codes | Builder adjusts run defaults by PR |
| SP06, SP10, SP17 | Guards block under `-p`; admin settings honoured; plan-approval check blocks an edit | Blocked | Stay unlocked; fix by PR |
| SP07 | Real usage-limit message replaces the made-up one | Recorded after the first real limit | Nights may stop at a limit until done |
| SP08, SP87 | A night survives a stall; Remote Control and Telegram chat at once | Night ends in a known state | Builder fixes by PR |
| SP09, SP13, SP26 | Sandbox, bypass attempts and the web allowlist | Bypasses denied; `claude -p` still works | `--unlock`, fix by PR, `--install`, `--lock` |
| SP11, SP12 | The engineer cannot read secrets; a test secret never leaks | Nothing found | Do not lock; builder fixes |
| SP16 | One or two Telegram bots | Decision recorded | Keep two |
| SP18 (you) | Bot cannot push to main; auto-merge works with zero approvals | Refused, then merged | **Do not lock** until it passes |
| SP22, SP64, SP83 | Chrome and Playwright start on the virtual screen; guards see browser actions; the engineer plugin loads | Screenshot taken; action logged | Builder fixes by PR |
| SP71 (you) | noVNC through Cloudflare Access from your phone | Email code, then the screen | Fallback, from your Mac: `ssh -L 6080:127.0.0.1:6080 root@<IP>`, then open `http://localhost:6080` |
| SP72 (you) | healthchecks.io alert reaches your phone | Alert received | Check the phone notification setting |
| SP85 (you) | Google and Attio sign-in from the server's address | Signed in, no challenge | Fallback 1: Tailscale exit node at home for the browser only; fallback 2: Mac mini at home |
| SP86 | Sign-ins survive a snapshot restore | Still signed in | Sign in again after a restore; note it |
| SP88 | Memory with Attio, Clay and n8n tabs open | Under 8 GB | Resize the droplet (check the price on the day) |
| SP89 (you) | DigitalOcean's acceptable-use policy read | Nothing forbids it | Talk to the builder about the Mac mini |
| Pins, units | Every `TO-PIN` filled; admin files accepted; services start | `doctor.sh` all OK | Builder fixes by PR |

## If something goes wrong
- **Stop everything tonight:** `sudo touch /var/lib/engineer/STOP`. Every action the engineer tries is
  refused, the night ends and no new task starts (the digest waits too). `sudo rm /var/lib/engineer/STOP`
  resumes from the next night window (22:00-07:00).
- **Take the guards off for maintenance:** `sudo bash /srv/autonomy-research/engineer/scripts/setup-root.sh --unlock`
  (stops the night loop). Afterwards run `--install` and `--lock` again.
- **Where the morning report is:** the Telegram digest at 07:30, and `docs/runs/<date>-MORNING.md` on the
  `engineer-records` branch of each project on GitHub.
- **A step failed half-way:** steps 4, 6, 15, 19 and 22 are safe to repeat.
- **A site blocks the browser:** the engineer stops and tells you; it never tries to get round a check.

## Words used here
- **Droplet:** DigitalOcean's name for a rented server.
- **SSH key:** a pair of files that lets your Mac log in without a password; the `.pub` half is safe to share.
- **Deploy key:** an SSH key that opens one repo only, here read-only.
- **PR (pull request):** a proposed change you read and merge on GitHub.
- **Branch protection:** GitHub rules that stop anyone, the bot included, changing main without checks.
- **CODEOWNERS:** a file naming who must review changes to which files (you).
- **systemd unit:** a service the server starts by itself and restarts if it stops.
- **noVNC:** a web page that shows the server's screen and lets you click on it.
- **Snapshot:** a saved copy of the whole droplet you can restore later.
- **Seed:** put one secret into the encrypted store, typed by you, never shown.
