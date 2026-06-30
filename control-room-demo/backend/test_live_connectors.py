#!/usr/bin/env python3
"""Tests for the Phase 5 live READ-ONLY connectors and ingestion.

Run:
    python3 control-room-demo/backend/test_live_connectors.py

These tests use FAKE clients (no network). They assert the read-only invariants
that make this branch safe:
  * IMAP opens the mailbox read-only (EXAMINE) and fetches with BODY.PEEK only.
  * IMAP never issues STORE / COPY / EXPUNGE / APPEND / UID (the fake raises if
    it does), so nothing is marked read, moved, or deleted.
  * Connectors emit redacted snapshots; raw PII never survives into a snapshot.
  * WooCommerce issues a GET only and drops customer PII.
  * Stripe refuses a non-test key and makes no network call.
  * Persisted rows are raw_stored=0; the DB CHECK rejects any raw/mutating row.
  * Dry-run writes nothing; --write requires the acknowledgement flag.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

import config  # noqa: E402
import db  # noqa: E402
import live_ingest  # noqa: E402
from connectors.base import Connector, clamp_limit  # noqa: E402
from connectors.imap_readonly import IMAPReadOnlyConnector  # noqa: E402
from connectors.stripe_test_status import StripeTestStatusConnector  # noqa: E402
from connectors.woocommerce_readonly import WooCommerceReadOnlyConnector  # noqa: E402


def _fresh_db() -> Path:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return Path(path)


# ----------------------------------------------------------------------------
# Fakes
# ----------------------------------------------------------------------------
class FakeIMAP:
    """Records commands; raises on ANY mutating verb."""

    def __init__(self):
        self.commands = []
        self.selected_readonly = None

    def login(self, user, password):
        # Never record the password.
        self.commands.append(("login", user))
        return ("OK", [b"ok"])

    def select(self, mailbox, readonly=False):
        self.commands.append(("select", mailbox, readonly))
        self.selected_readonly = readonly
        return ("OK", [b"3"])

    def search(self, charset, *criteria):
        self.commands.append(("search", criteria))
        return ("OK", [b"1 2 3"])

    def fetch(self, msg_id, items):
        self.commands.append(("fetch", msg_id, items))
        if "HEADER.FIELDS" in items:
            raw = (
                b"Subject: Warranty issue for order 100045321\r\n"
                b"From: Jane Doe <jane.doe@gmail.com>\r\n"
                b"Date: Mon, 30 Jun 2026 08:42:11 -0700\r\n"
                b"Message-Id: <abc-" + bytes(str(msg_id), "ascii") + b"@mail>\r\n\r\n"
            )
            return ("OK", [(b"x (BODY[HEADER] {%d}" % len(raw), raw), b")"])
        raw = (
            b"Hi, my bidet seat broke. Call me at 604-555-1234 or "
            b"jane.doe@gmail.com. Order 100045321. Thanks."
        )
        return ("OK", [(b"x (BODY[TEXT] {%d}" % len(raw), raw), b")"])

    # Any of these would be a read-only violation.
    def store(self, *a, **k):
        raise AssertionError("STORE called: would set flags / mark read")

    def copy(self, *a, **k):
        raise AssertionError("COPY called: would move the message")

    def expunge(self, *a, **k):
        raise AssertionError("EXPUNGE called: would delete")

    def append(self, *a, **k):
        raise AssertionError("APPEND called: would write a message")

    def uid(self, *a, **k):
        raise AssertionError("UID command called: unaudited verb")

    def logout(self):
        self.commands.append(("logout",))
        return ("BYE", [b"bye"])


def _email_cfg():
    return config.LiveConfig(
        {
            "LIVE_READONLY_ENABLED": "true",
            "IMAP_HOST": "imap.example.com",
            "IMAP_PORT": "993",
            "IMAP_USERNAME": "ops@example.com",
            "IMAP_PASSWORD": "app-password-never-logged",
            "IMAP_MAILBOX": "INBOX",
            "IMAP_ENABLED": "true",
        },
        source=Path("/tmp/fake.env"),
    )


# ----------------------------------------------------------------------------
# IMAP read-only connector
# ----------------------------------------------------------------------------
class TestIMAPReadOnly(unittest.TestCase):
    def setUp(self):
        self.fake = FakeIMAP()
        self.cfg = _email_cfg()
        self.connector = IMAPReadOnlyConnector(
            self.cfg, imap_factory=lambda host, port: self.fake
        )

    def test_uses_examine_readonly(self):
        self.connector.fetch(limit=10)
        self.assertIs(self.fake.selected_readonly, True)
        select_cmds = [c for c in self.fake.commands if c[0] == "select"]
        self.assertTrue(select_cmds and select_cmds[0][2] is True)

    def test_uses_body_peek_only(self):
        self.connector.fetch(limit=10)
        fetches = [c for c in self.fake.commands if c[0] == "fetch"]
        self.assertTrue(fetches)
        for _, _msg_id, items in fetches:
            self.assertIn("BODY.PEEK", items)
            # A bare BODY[...] fetch would set \Seen; must not appear.
            self.assertNotIn("BODY[", items)

    def test_no_mutating_verbs_called(self):
        # FakeIMAP raises on store/copy/expunge/append/uid; a clean run proves
        # none were issued.
        result = self.connector.fetch(limit=10)
        self.assertTrue(result.ok)
        verbs = {c[0] for c in self.fake.commands}
        self.assertEqual(
            verbs & {"store", "copy", "expunge", "append", "uid"}, set()
        )
        self.assertIn("logout", verbs)

    def test_snapshots_are_redacted(self):
        result = self.connector.fetch(limit=10)
        self.assertEqual(result.rows_seen, 3)
        blob = json.dumps(result.snapshots)
        self.assertNotIn("jane.doe@gmail.com", blob)
        self.assertNotIn("604-555-1234", blob)
        self.assertNotIn("100045321", blob)
        self.assertNotIn("Jane Doe", blob)
        for snap in result.snapshots:
            self.assertEqual(snap["raw_stored"], 0)
            self.assertEqual(snap["redacted"]["from_domain"], "gmail.com")

    def test_refuses_when_master_gate_off(self):
        cfg = _email_cfg()
        cfg._v["LIVE_READONLY_ENABLED"] = "false"
        connector = IMAPReadOnlyConnector(
            cfg, imap_factory=lambda h, p: self.fake
        )
        result = connector.fetch(limit=10)
        self.assertFalse(result.ok)
        # The fake was never touched.
        self.assertEqual(self.fake.commands, [])


# ----------------------------------------------------------------------------
# WooCommerce read-only connector
# ----------------------------------------------------------------------------
class TestWooReadOnly(unittest.TestCase):
    def setUp(self):
        self.cfg = config.LiveConfig(
            {
                "LIVE_READONLY_ENABLED": "true",
                "WOO_BASE_URL": "https://store.example.com",
                "WOO_CONSUMER_KEY": "ck_x",
                "WOO_CONSUMER_SECRET": "cs_y",
                "WOO_ENABLED": "true",
            },
            source=Path("/tmp/fake.env"),
        )
        self.calls = []

        def fake_fetch(url, headers, timeout=20):
            self.calls.append((url, headers))
            return json.dumps([
                {
                    "id": 4521, "number": "4521", "status": "processing",
                    "currency": "CAD", "total": "289.00",
                    "date_created": "2026-06-29T10:11:00",
                    "line_items": [{"name": "Bidet"}, {"name": "Kit"}],
                    "billing": {
                        "email": "buyer@gmail.com", "phone": "604-555-9999",
                        "first_name": "Buyer", "address_1": "123 Main St",
                    },
                },
            ]).encode("utf-8")

        self.connector = WooCommerceReadOnlyConnector(self.cfg, fetcher=fake_fetch)

    def test_get_only_and_https(self):
        result = self.connector.fetch(limit=10)
        self.assertTrue(result.ok)
        url, _headers = self.calls[0]
        self.assertTrue(url.startswith("https://"))
        self.assertIn("/wp-json/wc/v3/orders", url)

    def test_drops_customer_pii(self):
        result = self.connector.fetch(limit=10)
        blob = json.dumps(result.snapshots)
        for leak in ("buyer@gmail.com", "604-555-9999", "Buyer", "123 Main St"):
            self.assertNotIn(leak, blob)
        snap = result.snapshots[0]
        self.assertEqual(snap["redacted"]["status"], "processing")
        self.assertEqual(snap["redacted"]["line_items_count"], 2)
        self.assertEqual(snap["raw_stored"], 0)

    def test_refuses_non_https(self):
        self.cfg._v["WOO_BASE_URL"] = "http://insecure.example.com"
        result = self.connector.fetch(limit=10)
        self.assertFalse(result.ok)
        self.assertIn("https", result.note)


# ----------------------------------------------------------------------------
# Stripe test-mode status connector
# ----------------------------------------------------------------------------
class TestStripeTestStatus(unittest.TestCase):
    def test_accepts_test_key_no_network(self):
        cfg = config.LiveConfig({
            "LIVE_READONLY_ENABLED": "true",
            "STRIPE_TEST_SECRET_KEY": "sk_test_abc123",
            "STRIPE_ENABLED": "true",
        })
        result = StripeTestStatusConnector(cfg).fetch()
        self.assertTrue(result.ok)
        self.assertEqual(result.rows_seen, 1)
        snap = result.snapshots[0]
        self.assertTrue(snap["redacted"]["test_mode"])
        self.assertFalse(snap["redacted"]["livemode"])
        # The key value must never appear in the snapshot.
        self.assertNotIn("sk_test_abc123", json.dumps(snap))

    def test_refuses_live_key(self):
        cfg = config.LiveConfig({
            "LIVE_READONLY_ENABLED": "true",
            "STRIPE_TEST_SECRET_KEY": "sk_live_DANGER",
            "STRIPE_ENABLED": "true",
        })
        result = StripeTestStatusConnector(cfg).fetch()
        self.assertFalse(result.ok)
        self.assertNotIn("sk_live_DANGER", json.dumps(result.summary()))


# ----------------------------------------------------------------------------
# Base interface + limits
# ----------------------------------------------------------------------------
class TestBaseInterface(unittest.TestCase):
    def test_refuses_non_read_only_subclass(self):
        class Bad(Connector):
            READ_ONLY = False

        with self.assertRaises(RuntimeError):
            Bad(_email_cfg())

    def test_clamp_limit(self):
        self.assertEqual(clamp_limit(999), 10)
        self.assertEqual(clamp_limit(0), 1)
        self.assertEqual(clamp_limit(5), 5)
        self.assertEqual(clamp_limit("nope"), 10)


# ----------------------------------------------------------------------------
# DB persistence + CHECK constraints + ingestion CLI paths
# ----------------------------------------------------------------------------
class TestPersistenceAndIngest(unittest.TestCase):
    def setUp(self):
        self.db_path = _fresh_db()
        self.conn = db.connect(self.db_path)
        db.init_schema(self.conn)
        self.fake = FakeIMAP()
        self._orig = live_ingest.CONNECTORS["email"]
        live_ingest.CONNECTORS["email"] = (
            lambda cfg: IMAPReadOnlyConnector(
                cfg, imap_factory=lambda h, p: self.fake
            )
        )

    def tearDown(self):
        live_ingest.CONNECTORS["email"] = self._orig
        self.conn.close()
        self.db_path.unlink(missing_ok=True)

    def test_write_persists_redacted_rows(self):
        rc = live_ingest.cmd_run(
            _email_cfg(), self.conn, "email", write=True, limit=10
        )
        self.assertEqual(rc, 0)
        snaps = db.list_live_snapshots(self.conn)
        self.assertEqual(len(snaps), 3)
        self.assertTrue(all(s["raw_stored"] == 0 for s in snaps))
        blob = json.dumps(snaps)
        self.assertNotIn("jane.doe@gmail.com", blob)
        self.assertNotIn("604-555-1234", blob)
        runs = db.list_connector_runs(self.conn)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["read_only"], 1)
        self.assertEqual(runs[0]["mutations"], 0)
        self.assertEqual(runs[0]["rows_saved"], 3)

    def test_dry_run_persists_nothing(self):
        rc = live_ingest.cmd_run(
            _email_cfg(), self.conn, "email", write=False, limit=10
        )
        self.assertEqual(rc, 0)
        self.assertEqual(db.live_counts(self.conn)["live_snapshots"], 0)
        self.assertEqual(db.live_counts(self.conn)["connector_runs"], 0)

    def test_db_rejects_raw_stored_one(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO live_snapshots "
                "(connector, redacted_json, raw_stored) VALUES (?, ?, 1)",
                ("email", "{}"),
            )

    def test_db_rejects_mutating_run(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO connector_runs "
                "(connector, mode, read_only, mutations) VALUES (?, ?, 0, 1)",
                ("email", "write-readonly"),
            )

    def test_add_live_snapshot_refuses_raw(self):
        run_id = db.start_connector_run(self.conn, "email", "write-readonly")
        with self.assertRaises(ValueError):
            db.add_live_snapshot(
                self.conn, run_id,
                {"connector": "email", "redacted": {}, "raw_stored": 1},
            )

    def test_status_command_runs_without_network(self):
        rc = live_ingest.cmd_status(_email_cfg(), self.conn)
        self.assertEqual(rc, 0)
        self.assertEqual(self.fake.commands, [])  # never connected


if __name__ == "__main__":
    unittest.main(verbosity=2)
