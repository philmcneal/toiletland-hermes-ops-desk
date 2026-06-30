#!/usr/bin/env python3
"""Tests for the Phase 5 redaction layer.

Run:
    python3 -m unittest control-room-demo.backend.test_redaction
    (or)  python3 control-room-demo/backend/test_redaction.py

The redaction layer is the safety boundary: if it leaks, raw PII could reach
SQLite. These tests assert it scrubs PII and that ``assert_no_raw`` rejects any
snapshot that could carry raw content.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
import redaction  # noqa: E402


class TestRedactText(unittest.TestCase):
    def test_scrubs_email(self):
        out = redaction.redact_text("ping alice.smith@gmail.com now")
        self.assertNotIn("alice.smith@gmail.com", out)
        self.assertIn("[email]", out)

    def test_scrubs_phone(self):
        out = redaction.redact_text("call +1 604-555-1234 today")
        self.assertNotIn("604-555-1234", out)
        self.assertIn("[phone]", out)

    def test_scrubs_card_and_long_numbers(self):
        out = redaction.redact_text("card 4242 4242 4242 4242 order 100045321")
        self.assertNotIn("4242 4242 4242 4242", out)
        self.assertNotIn("100045321", out)
        self.assertIn("[card]", out)
        self.assertIn("[num]", out)

    def test_scrubs_url_and_ip(self):
        out = redaction.redact_text("see https://evil.test/a?token=abc at 10.0.0.5")
        self.assertNotIn("https://evil.test", out)
        self.assertNotIn("10.0.0.5", out)
        self.assertIn("[url]", out)
        self.assertIn("[ip]", out)

    def test_scrubs_postal(self):
        out = redaction.redact_text("ship to V6B 1A1 please")
        self.assertNotIn("V6B 1A1", out)
        self.assertIn("[postal]", out)

    def test_empty_and_none(self):
        self.assertEqual(redaction.redact_text(""), "")
        self.assertEqual(redaction.redact_text(None), "")


class TestAddressHelpers(unittest.TestCase):
    def test_email_domain(self):
        self.assertEqual(
            redaction.email_domain("Bob <bob@store.example.com>"),
            "store.example.com",
        )
        self.assertEqual(redaction.email_domain("not-an-email"), "[redacted]")

    def test_redact_email_address_keeps_domain_only(self):
        out = redaction.redact_email_address("jane.doe@toiletland.ca")
        self.assertNotIn("jane.doe", out)
        self.assertIn("toiletland.ca", out)
        self.assertTrue(out.startswith("[user]@"))


class TestPreview(unittest.TestCase):
    def test_truncates(self):
        out = redaction.preview("x" * 500, limit=160)
        self.assertLessEqual(len(out), 160)

    def test_redacts_before_truncating(self):
        out = redaction.preview("email me secret@x.com " * 20, limit=160)
        self.assertNotIn("secret@x.com", out)


class TestStableRef(unittest.TestCase):
    def test_deterministic(self):
        a = redaction.stable_ref("<msg-1@x>")
        b = redaction.stable_ref("<msg-1@x>")
        self.assertEqual(a, b)

    def test_distinct_inputs_distinct_refs(self):
        self.assertNotEqual(
            redaction.stable_ref("<msg-1@x>"),
            redaction.stable_ref("<msg-2@x>"),
        )

    def test_non_reversible_hex16(self):
        ref = redaction.stable_ref("super-secret-message-id@host")
        self.assertEqual(len(ref), 16)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{16}", ref))
        self.assertNotIn("secret", ref)


class TestAssertNoRaw(unittest.TestCase):
    def _good(self):
        return {
            "connector": "email",
            "kind": "email",
            "external_ref": "abc123def456abcd",
            "captured_at": "2026-06-30T08:42:00-07:00",
            "redacted": {
                "subject": "[email] asked about warranty",
                "from_domain": "gmail.com",
                "body_preview": "customer wants [num] order status",
                "body_chars": 421,
            },
            "raw_stored": 0,
        }

    def test_clean_snapshot_passes(self):
        snap = self._good()
        self.assertIs(redaction.assert_no_raw(snap), snap)

    def test_rejects_raw_stored_one(self):
        snap = self._good()
        snap["raw_stored"] = 1
        with self.assertRaises(ValueError):
            redaction.assert_no_raw(snap)

    def test_rejects_missing_raw_stored(self):
        snap = self._good()
        del snap["raw_stored"]
        with self.assertRaises(ValueError):
            redaction.assert_no_raw(snap)

    def test_rejects_extra_top_level_key(self):
        snap = self._good()
        snap["raw_body"] = "the actual email text"
        with self.assertRaises(ValueError):
            redaction.assert_no_raw(snap)

    def test_rejects_leaked_email_in_redacted(self):
        snap = self._good()
        snap["redacted"]["subject"] = "ping real.person@gmail.com"
        with self.assertRaises(ValueError):
            redaction.assert_no_raw(snap)

    def test_rejects_leaked_ip_in_nested_value(self):
        snap = self._good()
        snap["redacted"]["meta"] = ["seen from 8.8.8.8"]
        with self.assertRaises(ValueError):
            redaction.assert_no_raw(snap)


if __name__ == "__main__":
    unittest.main(verbosity=2)
