# ADR 0004: DigitalOcean droplet with branded Chrome

Status: accepted 2026-10-16

## Context
- The engineer needs one always-on Ubuntu host it controls, with a logged-in browser for Attio, Clay and n8n (blueprint decisions.md, areas 6 and 14).
- DigitalOcean Basic 4 vCPU / 8 GiB costs $48/month with its own public IPv4; snapshots cost $0.06/GB-month (engineer-host E64).
- Playwright can drive branded Google Chrome through `channel` (engineer-host E12); Chrome 136+ ignores remote debugging on the default profile (engineer-host E13).
- Google and Attio terms bar bypassing protective measures (engineer-host E17, E18); Google may refuse automated sign-in (engineer-host E3, E5).

## Decision
- Host: a DigitalOcean droplet in US East, Ubuntu 24.04 LTS, 4 vCPU / 8 GB.
- Browser: headed branded Chrome through Playwright `channel chrome` (Playwright MCP `--browser chrome`), with a persistent non-default profile on Xvfb.
- John signs in by hand once through noVNC behind Cloudflare Access; an SSH tunnel is the fallback (engineer-host E80).
- APIs first. On any bot challenge the engineer stops and notifies John (blueprint flow.md F41). No stealth, proxy rotation or CAPTCHA solvers.
- Fallbacks, only if the setup-day sign-in test fails: a Tailscale exit node at home for the browser's traffic (engineer-host E81), or the same setup on a home Mac mini ($899, engineer-host E74).

## Consequences
- `doctor.sh` checks the size; the browser route, challenge check and units are built in stage 1.
- Setup-day spikes SP85 (sign-in from the droplet IP), SP86 (logins survive a snapshot), SP88 (memory on 8 GB) and SP89 (DigitalOcean acceptable-use policy) can change this call.
- Snapshot the droplet after the hand sign-in; weekly backups stay off (Open decision 9).
