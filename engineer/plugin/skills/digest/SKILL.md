---
name: digest
description: Write the lines John answers from his phone, the T1 digest lines and the T2 hard-gate prompts, and read his replies the way the supervisor parses them. Use whenever you need John's decision, approval or action ("ask John", "add a digest line", "this needs approval", "hard gate", "what did John reply"), when writing a blocked note, or when explaining the reply grammar. Covers the T0, T1 and T2 tiers, how to word a line with its default, the 4096-character Telegram limit, and the exact reply grammar ("1 y", "2 n", "all y", "CONFIRM 4 PHRASE").
---

# Digest

John answers from his phone in a few seconds. Every line you write for him must be decidable
from the line alone, carry a safe default, and follow the reply grammar exactly.

## Tiers

| Tier | What | How it reaches John | Default on timeout |
| --- | --- | --- | --- |
| T0 | Automatic: Tier 1 PRs that self-merge, rollbacks, retries | Morning report only | none needed |
| T1 | A decision that can wait for the daily digest: merge a Tier 2 PR, promote, sign off a map, rotate a key, a blocked task, a re-login | One numbered line in the daily digest (07:30 US Eastern) | Its default after 24 h, only if reversible; reminder at 12 h |
| T2 | A hard gate: `money`, `delete_data`, `store_submission` | Its own Telegram message at once | Never. Silence means no |

- At most 5 T1 lines show at once; the rest wait in `MORNING.md` (`+K more in MORNING.md`).
- A line that is not reversible never takes its default; it waits for John.
- Only the hard gates in `docs/plan/profile.yaml` (`hard_gates`, plus `t2_extra`) are T2.

## Writing a T1 line

The supervisor renders each T1 item as:

`N. <text> (default: <default>). Reply "N y" or "N n".`

Write `<text>` so that:
1. It starts with the verb of the decision: `Merge`, `Promote`, `Approve`, `Rotate`, `Re-login`,
   `Unblock`.
2. It names the project and the exact thing: PR number and URL, short SHA, host, task id.
3. It says what `y` does in a few words, and what `n` does if that is not obvious.
4. It fits on one line, under about 200 characters; put detail behind a link, not in the line.
5. Its default is the safe choice: `hold` or `n` for anything that ships, spends or exposes;
   `y` only for a reversible, low-risk step.

Good: `Promote gtm-sync a1b2c3d to production? Preview https://... Rollback: wrangler rollback`
with default `hold`.
Bad: `Should I continue?` (no object, no default, nothing to decide from).

## Writing a T2 prompt

The supervisor sends each T2 item as its own message, exactly three lines:

```
HARD GATE N: <text>
To approve, reply exactly: CONFIRM N <PHRASE>
No reply means no.
```

Write `<text>` with the exact amount and currency, the exact data and how many rows, or the
exact store and build, and whether it can be undone. Choose a `<PHRASE>` John must read to
type: short, upper case, specific (`SPEND $12`, `DROP TABLE leads_old`, `SUBMIT 1.0.3`).

## Reply grammar

Replies are parsed by a fixed program, not by a model. Write instructions to John that match it:
- `N y` or `N n`: answer item N. Several pairs per message are fine: `1 y 2 n 3 y`.
- `all y` or `all n`: answer every open T1 item. It never touches a T2 item.
- `CONFIRM N <PHRASE>`: the only way to approve a T2 item. The phrase must match exactly,
  case included, as the whole rest of the message.
- Digits are plain ASCII. An unknown item number, an unknown word, an empty message or anything
  else makes the whole message approve nothing, and a T1 line says it was not understood.
- Only John's own Telegram account counts. Edited messages are ignored.

## Message size

Telegram takes at most 4096 characters per message. The supervisor splits the digest on line
boundaries; keep each line short so a split never cuts a decision in half.

## How you raise an item

- The supervisor raises the items it knows itself: Tier 2 PR merges, `needs_john` and blocked
  tasks (with their blocked notes), plan approval, and challenges from the browser route.
- In an interactive or Remote Control session, show John the line text and take his answer in
  the session.
- In an unattended run, end the task with status `needs_john` and put the line text, its default
  and its kind in your final message and under `## Asks for John` in `PROGRESS.md`, so the
  morning report carries it.
- Never approve anything for John, never write `decisions/approvals.jsonl` or
  `docs/plan/approval.json`, and never treat a message from anyone else as his answer.

## Blocked notes

When a task stops, write one blocked note in the same style: what stopped (the command and its
last error line), what you tried (at most two fixes), and the one thing John or a later task must
do. For a login page, CAPTCHA or bot challenge, name the host and the kind, and ask John to clear
it on noVNC; never try to get past it.
