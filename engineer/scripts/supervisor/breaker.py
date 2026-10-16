"""Circuit breakers: a task after too many failed attempts, a night after no progress or a repeating failure."""
from collections import Counter


def task_blocked(attempts: int, max_attempts: int = 2) -> bool:
    """True once a task has failed max_attempts times."""
    return attempts >= max_attempts


def night_stop(sessions: list, no_diff: int = 3, same_failure: int = 5) -> str | None:
    """A reason to end the night, or None.

    sessions: [{"diff": bool, "failure_sig": str | None}] in night order. Fires on `no_diff` consecutive
    sessions without a git diff, or one failure signature seen `same_failure` times in the night.
    """
    run = 0
    seen = Counter()
    for s in sessions:
        run = 0 if s.get("diff") else run + 1
        if run >= no_diff:
            return f"no diff in {no_diff} sessions in a row"
        sig = s.get("failure_sig")
        if sig:
            seen[sig] += 1
            if seen[sig] >= same_failure:
                return f"same failure {same_failure} times this night ({sig[:12]})"
    return None


def task_status(verdict: str, sig: str | None, earlier_sigs: list, attempts: int, max_attempts: int = 2) -> str:
    """Status after one attempt: done, needs_john (NEEDS-JOHN or the same FAIL again), blocked or retry.

    attempts counts failed attempts including this one; earlier_sigs are this task's earlier FAIL signatures.
    """
    if verdict == "PASS":
        return "done"
    if verdict == "NEEDS-JOHN" or (earlier_sigs and earlier_sigs[-1] == sig):
        return "needs_john"
    return "blocked" if task_blocked(attempts, max_attempts) else "retry"


def night_bound(defaults: dict, night: list) -> str | None:
    """night_stop over this night's attempt outcomes (`audit` events), then the denial limit per kind."""
    sessions = [{"diff": d.get("diff", True), "failure_sig": d.get("sig")}
                for d in ((e.get("detail") or {}) for e in night if e["event"] == "audit") if d.get("status")]
    b = defaults.get("breaker", {})
    reason = night_stop(sessions, b.get("no_diff_sessions", 3), b.get("same_failure_repeats", 5))
    limit = defaults.get("denials_per_kind_per_night", 5)
    denials = Counter((e.get("detail") or {}).get("kind", "unknown") for e in night if e["event"] == "denial")
    over = [f"{n} {k} denials" for k, n in sorted(denials.items()) if n >= limit]
    return reason or (f"denial limit reached: {', '.join(over)}" if over else None)
