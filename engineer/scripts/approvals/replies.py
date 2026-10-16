"""Deterministic parser for John's Telegram replies (ruling 3, SP15, Review Focus 3).

Grammar, tokens split on whitespace:
  <n> y|n ...          answer T1 items; n is ASCII digits only
  all y | all n        every open T1 item the answered digest showed (never a T2, never "+K more")
  CONFIRM <n> <PHRASE> the one T2 item n; PHRASE must equal the item's phrase exactly
                       (case-sensitive; the whole rest of the message)
Any error approves nothing from the message.
"""
import re

_NUM = re.compile(r"[0-9]{1,9}")
_YN = {"y": "yes", "n": "no"}


def _fold(token: str) -> str:
    """Lower-case ASCII tokens only, so a lookalike letter never folds into y, n or all."""
    return token.lower() if token.isascii() else token


def _confirm(tokens: list, open_items: dict) -> dict:
    if len(tokens) < 3 or not _NUM.fullmatch(tokens[1]):
        return {"decisions": [], "errors": ["CONFIRM needs an item number and the phrase"]}
    n = int(tokens[1])
    item = open_items.get(n)
    if item is None:
        return {"decisions": [], "errors": [f"item {n} is not open"]}
    if item.get("tier") != "T2":
        return {"decisions": [], "errors": [f"item {n} is not a hard gate; reply \"{n} y\" or \"{n} n\""]}
    phrase = item.get("phrase")
    if not isinstance(phrase, str) or not phrase.split() or tokens[2:] != phrase.split():
        return {"decisions": [], "errors": [f"item {n}: the phrase does not match exactly"]}
    return {"decisions": [{"item": n, "answer": "yes"}], "errors": []}


def _pairs(tokens: list, open_items: dict, shown) -> dict:
    errors, answers = [], {}
    if len(tokens) % 2:
        errors.append(f"incomplete reply: {tokens[-1]!r} has no y or n")
        tokens = tokens[:-1]
    for target, word in zip(tokens[::2], tokens[1::2]):
        answer = _YN.get(_fold(word))
        if answer is None:
            errors.append(f"unknown answer {word!r}; use y or n")
            continue
        if _fold(target) == "all":
            nums = [n for n, it in sorted(open_items.items())
                    if it.get("tier") == "T1" and (shown is None or n in shown)]
            if not nums:
                errors.append("all: no open T1 items in the digest this reply answers")
        elif _NUM.fullmatch(target):
            n = int(target)
            item = open_items.get(n)
            if item is None:
                errors.append(f"item {n} is not open")
                continue
            if item.get("tier") != "T1":
                errors.append(f"item {n} is a hard gate; reply exactly: CONFIRM {n} <phrase>")
                continue
            nums = [n]
        else:
            errors.append(f"unknown token {target!r}")
            continue
        for n in nums:
            if n in answers:
                errors.append(f"item {n} answered more than once")
            answers[n] = answer
    if errors:
        return {"decisions": [], "errors": errors}
    return {"decisions": [{"item": n, "answer": a} for n, a in answers.items()], "errors": []}


def parse(text, open_items: dict, shown=None) -> dict:
    """{"decisions": [{"item": int, "answer": "yes"|"no"}], "errors": [str]}; errors mean no decisions.

    shown: the item numbers the digest being answered listed; `all` covers only those (None: every open T1).
    """
    if not isinstance(text, str) or not text.strip():
        return {"decisions": [], "errors": ["empty reply"]}
    tokens = text.split()
    if tokens[0] == "CONFIRM":
        return _confirm(tokens, open_items)
    return _pairs(tokens, open_items, shown)
