"""replies.parse: the deterministic Telegram reply grammar (Review Focus 3: nothing odd approves)."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "engineer" / "scripts"))
from approvals import replies  # noqa: E402


def t1(n):
    return {"item": n, "tier": "T1", "kind": "merge", "text": f"item {n}", "default": "no"}


def t2(n, phrase):
    return {"item": n, "tier": "T2", "kind": "other", "text": f"gate {n}", "phrase": phrase}


class Replies(unittest.TestCase):
    def assertRejected(self, text, open_items):
        out = replies.parse(text, open_items)
        self.assertEqual(out["decisions"], [], text)
        self.assertTrue(out["errors"], text)

    def test_pairs(self):
        out = replies.parse("1 y 2 n", {1: t1(1), 2: t1(2)})
        self.assertEqual(out, {"decisions": [{"item": 1, "answer": "yes"}, {"item": 2, "answer": "no"}],
                               "errors": []})

    def test_reply_all_covers_only_shown(self):
        out = replies.parse("all y", {1: t1(1), 2: t1(2), 3: t1(3)}, shown={1, 3})
        self.assertEqual([d["item"] for d in out["decisions"]], [1, 3])
        out = replies.parse("all y", {1: t1(1)}, shown=set())
        self.assertEqual(out["decisions"], [])
        self.assertTrue(out["errors"])
        out = replies.parse("2 y", {1: t1(1), 2: t1(2)}, shown={1})
        self.assertEqual(out["decisions"], [{"item": 2, "answer": "yes"}])

    def test_reply_all_y_skips_t2(self):
        out = replies.parse("all y", {1: t1(1), 4: t2(4, "SPEND $12")})
        self.assertEqual(out["decisions"], [{"item": 1, "answer": "yes"}])
        self.assertEqual(out["errors"], [])

    def test_reply_all_y_with_only_t2_open_approves_nothing(self):
        self.assertRejected("all y", {4: t2(4, "SPEND $12")})

    def test_reply_t2_plain_y_is_error(self):
        self.assertRejected("4 y", {4: t2(4, "SPEND $12")})

    def test_reply_confirm_exact(self):
        out = replies.parse("CONFIRM 4 SPEND $12", {4: t2(4, "SPEND $12")})
        self.assertEqual(out, {"decisions": [{"item": 4, "answer": "yes"}], "errors": []})

    def test_reply_confirm_wrong_case(self):
        self.assertRejected("confirm 4 spend $12", {4: t2(4, "SPEND $12")})
        self.assertRejected("CONFIRM 4 spend $12", {4: t2(4, "SPEND $12")})
        self.assertRejected("Confirm 4 SPEND $12", {4: t2(4, "SPEND $12")})

    def test_reply_confirm_wrong_phrase(self):
        self.assertRejected("CONFIRM 4 SPEND $13", {4: t2(4, "SPEND $12")})
        self.assertRejected("CONFIRM 4 SPEND", {4: t2(4, "SPEND $12")})
        self.assertRejected("CONFIRM 4 SPEND $12 1 y", {1: t1(1), 4: t2(4, "SPEND $12")})

    def test_reply_confirm_lookalike_phrase(self):
        self.assertRejected("CONFIRM 4 SPEND $１2", {4: t2(4, "SPEND $12")})
        self.assertRejected("CONFIRM 4 SPЕND $12", {4: t2(4, "SPEND $12")})  # Cyrillic Е

    def test_reply_confirm_on_t1_is_error(self):
        self.assertRejected("CONFIRM 1 SPEND $12", {1: t1(1)})

    def test_reply_confirm_not_first_is_error(self):
        self.assertRejected("1 y CONFIRM 4 SPEND $12", {1: t1(1), 4: t2(4, "SPEND $12")})

    def test_reply_fullwidth_digit(self):
        self.assertRejected("１ y", {1: t1(1)})

    def test_reply_other_script_digits(self):
        self.assertRejected("١ y", {1: t1(1)})  # Arabic-Indic one
        self.assertRejected("CONFIRM ４ SPEND $12", {4: t2(4, "SPEND $12")})

    def test_reply_lookalike_letters(self):
        self.assertRejected("1 у", {1: t1(1)})  # Cyrillic u
        self.assertRejected("1​ y", {1: t1(1)})  # zero-width space

    def test_reply_unknown_item_approves_nothing(self):
        self.assertRejected("1 y 9 y", {1: t1(1)})

    def test_reply_empty(self):
        self.assertRejected("", {1: t1(1)})
        self.assertRejected("   \n", {1: t1(1)})
        self.assertRejected(None, {1: t1(1)})

    def test_reply_yes_please(self):
        self.assertRejected("1 yes please", {1: t1(1)})

    def test_reply_odd_tokens(self):
        self.assertRejected("1 y 2", {1: t1(1), 2: t1(2)})

    def test_reply_conflicting_answers(self):
        self.assertRejected("1 y 1 n", {1: t1(1)})
        self.assertRejected("all y 2 n", {1: t1(1), 2: t1(2)})

    def test_reply_all_n(self):
        out = replies.parse("all n", {1: t1(1), 2: t1(2)})
        self.assertEqual(out["decisions"], [{"item": 1, "answer": "no"}, {"item": 2, "answer": "no"}])

    def test_reply_capitalised_t1_tokens_ok(self):
        out = replies.parse("All Y", {1: t1(1)})
        self.assertEqual(out["decisions"], [{"item": 1, "answer": "yes"}])


if __name__ == "__main__":
    unittest.main()
