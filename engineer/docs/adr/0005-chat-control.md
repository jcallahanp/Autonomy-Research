# ADR 0005: Remote Control server mode plus Telegram for chat control

Status: accepted 2026-10-16

## Context
- John approves and steers from his phone (blueprint decisions.md, ruling 3).
- Remote Control server mode keeps a process on a headless host waiting for remote connections and sends push notifications (engineer-host E103, E106); it exits after about 10 minutes offline (engineer-host E104).
- Channels relays chat and approval prompts from Telegram to a running session; anyone on the sender allowlist can approve (engineer-host E97, E98, E100).
- NanoClaw runs on the Agent SDK, whose use on a Max token is policy-contested (engineer-host E88, E113, E120); OpenClaw has a long advisory history (blueprint decisions.md, area 14).

## Decision
- Remote Control in server mode is the phone cockpit, run by an `engineer-remote-control` unit with `Restart=always`.
- A Telegram channel session runs under an `engineer-channels` unit, with a sender allowlist of John's id only.
- The supervisor's own Telegram bot sends the daily digest and T2 prompts through the broker's `tg-send` and `tg-poll` jobs.
- No NanoClaw or OpenClaw in v1. A Slack bridge on an API key is a later option.

## Consequences
- Two bots by default until SP16 shows one can be shared (Open decision 4).
- SP87 checks Remote Control and the Telegram channel on one host at the same time; SP08 checks the relay under tmux.
- The reply parser never approves on unknown input (plan Review Focus 3).
