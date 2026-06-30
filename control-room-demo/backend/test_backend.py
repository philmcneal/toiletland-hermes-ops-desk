#!/usr/bin/env python3
"""Tests for the Phase 1 local backend.

Run:
    python3 control-room-demo/backend/test_backend.py

Covers:
  * SQLite seeding from the real redacted fixtures is correct & idempotent.
  * Read APIs return the seeded collections.
  * approve/reject persist a DURABLE SQLite audit row and update status.
  * approve/reject make NO network/external call (sockets are blocked during
    the decision and it still succeeds, proving it is network-free).
  * Every decision is stamped executed=False / mode=fixture / connectors off.
  * Full HTTP surface (all GET routes + POST approve/reject) works on loopback.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
import db  # noqa: E402
import server  # noqa: E402

REAL_DATA_DIR = db.DEFAULT_DATA_DIR
EXPECTED = {  # fixture lengths that must round-trip through SQLite
    "queue_items": 4,
    "emails": 4,
    "warranty_cases": 4,
    "payment_requests": 3,
    "agent_pulse": 1,
    "audit_events": 9,
}


def _fresh_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return Path(path)


class TestSeedingAndReads(unittest.TestCase):
    def setUp(self):
        self.db_path = _fresh_db()
        self.conn = db.connect(self.db_path)
        db.seed_from_fixtures(self.conn, data_dir=REAL_DATA_DIR)

    def tearDown(self):
        self.conn.close()
        self.db_path.unlink(missing_ok=True)

    def test_counts_match_fixtures(self):
        self.assertEqual(db.counts(self.conn), EXPECTED)

    def test_collections_round_trip(self):
        self.assertEqual(
            [i["id"] for i in db.list_collection(self.conn, "queues")],
            ["earn-001", "operate-001", "spend-001", "warranty-001"],
        )
        self.assertEqual(len(db.list_collection(self.conn, "emails")), 4)
        self.assertEqual(len(db.list_collection(self.conn, "warranty-cases")), 4)
        self.assertEqual(len(db.list_collection(self.conn, "payment-requests")), 3)

    def test_agent_pulse_and_audit(self):
        pulse = db.get_agent_pulse(self.conn)
        self.assertFalse(pulse.get("live_connectors"))
        self.assertIn("summary", pulse)
        audit = db.list_audit(self.conn)
        self.assertEqual(len(audit), 9)
        self.assertTrue(all(row["executed"] == 0 for row in audit))

    def test_seeding_is_idempotent(self):
        again = db.connect(self.db_path)
        try:
            db.seed_from_fixtures(again, data_dir=REAL_DATA_DIR)
            self.assertEqual(db.counts(again), EXPECTED)
        finally:
            again.close()


class TestDecisionsAreDurableAndOffline(unittest.TestCase):
    def setUp(self):
        self.db_path = _fresh_db()
        self.conn = db.connect(self.db_path)
        db.seed_from_fixtures(self.conn, data_dir=REAL_DATA_DIR)

    def tearDown(self):
        self.conn.close()
        self.db_path.unlink(missing_ok=True)

    def test_approve_makes_no_network_call(self):
        before = db.counts(self.conn)["audit_events"]
        # Block ALL python sockets. A network-touching approval would explode;
        # a SQLite-only approval sails through.
        with mock.patch("socket.socket",
                        side_effect=AssertionError("network blocked")):
            result = db.apply_decision(
                self.conn, "earn-001", "approve", actor="unit-test"
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["item"]["status"], "approved-draft")
        self.assertFalse(result["adapter_result"]["executed"])
        self.assertEqual(result["adapter_result"]["mode"], "fixture")
        self.assertFalse(result["adapter_result"]["live_connectors"])
        self.assertEqual(result["audit"]["executed"], 0)
        self.assertEqual(
            db.counts(self.conn)["audit_events"], before + 1
        )

    def test_reject_persists_across_reconnect(self):
        db.apply_decision(self.conn, "pay-001", "reject", actor="unit-test")
        self.conn.commit()
        # Reopen a brand-new connection: durable on disk?
        reopened = db.connect(self.db_path)
        try:
            payments = {p["id"]: p for p in
                        db.list_collection(reopened, "payment-requests")}
            self.assertEqual(payments["pay-001"]["status"], "rejected-demo")
            last = db.list_audit(reopened)[-1]
            self.assertEqual(last["item_id"], "pay-001")
            self.assertEqual(last["outcome"], "rejected-demo")
            self.assertEqual(last["source"], "owner-approval")
            self.assertEqual(last["executed"], 0)
        finally:
            reopened.close()

    def test_unknown_item_raises(self):
        with self.assertRaises(KeyError):
            db.apply_decision(self.conn, "does-not-exist", "approve")

    def test_unknown_decision_raises(self):
        with self.assertRaises(ValueError):
            db.apply_decision(self.conn, "earn-001", "explode")

    def test_audit_is_append_only_on_repeated_decisions(self):
        start = db.counts(self.conn)["audit_events"]
        db.apply_decision(self.conn, "earn-001", "approve")
        db.apply_decision(self.conn, "earn-001", "reject")
        self.assertEqual(db.counts(self.conn)["audit_events"], start + 2)


class TestHttpSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = _fresh_db()
        cls.empty_secrets_path = Path(tempfile.mkdtemp()) / "missing-live-readonly.env"
        cls.httpd = server.make_server(
            host="127.0.0.1", port=0, db_path=cls.db_path,
            data_dir=REAL_DATA_DIR, verbose=False,
            secrets_path=cls.empty_secrets_path,
        )
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.db_path.unlink(missing_ok=True)
        cls.empty_secrets_path.parent.rmdir()

    def url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def get(self, path):
        with urllib.request.urlopen(self.url(path), timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def post(self, path, body=None):
        data = json.dumps(body or {}).encode("utf-8")
        req = urllib.request.Request(
            self.url(path), data=data, method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_health(self):
        status, body = self.get("/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["mode"], "fixture")
        self.assertFalse(body["live_connectors"])
        # Item counts are stable; audit only ever grows (append-only), and
        # other tests in this shared-server class may have added decision rows.
        c = body["counts"]
        for table in ("queue_items", "emails", "warranty_cases",
                      "payment_requests", "agent_pulse"):
            self.assertEqual(c[table], EXPECTED[table])
        self.assertGreaterEqual(c["audit_events"], EXPECTED["audit_events"])

    def test_get_collections(self):
        self.assertEqual(len(self.get("/api/queues")[1]), 4)
        self.assertEqual(len(self.get("/api/emails")[1]), 4)
        self.assertEqual(len(self.get("/api/warranty-cases")[1]), 4)
        self.assertEqual(len(self.get("/api/payment-requests")[1]), 3)
        self.assertIn("summary", self.get("/api/agent-pulse")[1])
        self.assertIsInstance(self.get("/api/audit")[1], list)

    def test_approve_then_audit_grows(self):
        before = len(self.get("/api/audit")[1])
        status, body = self.post("/api/approvals/operate-001/approve-draft")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(body["item"]["status"], "approved-draft")
        self.assertFalse(body["adapter_result"]["executed"])
        after = len(self.get("/api/audit")[1])
        self.assertEqual(after, before + 1)

    def test_reject_route(self):
        status, body = self.post("/api/approvals/warranty-case-001/reject")
        self.assertEqual(status, 200)
        self.assertEqual(body["item"]["status"], "rejected-demo")

    def test_live_routes_present_and_safe_when_empty(self):
        # With no live ingestion run, the live routes must still respond with
        # safe, empty shapes (the fixture demo keeps working).
        status, body = self.get("/api/live/status")
        self.assertEqual(status, 200)
        self.assertFalse(body["mutations_enabled"])
        self.assertIn("live_readonly", body)
        self.assertFalse(body["ingestion"]["live_readonly_ingestion"])
        self.assertEqual(body["ingestion"]["snapshot_count"], 0)
        self.assertFalse(body["live_readonly"]["any_connector_configured"])

        s2, snaps = self.get("/api/live/snapshots")
        self.assertEqual(s2, 200)
        self.assertEqual(snaps, [])

        s3, runs = self.get("/api/live/connector-runs")
        self.assertEqual(s3, 200)
        self.assertEqual(runs, [])

    def test_health_lists_live_routes(self):
        _status, body = self.get("/api/health")
        self.assertIn("/api/live/status", body["routes"])
        self.assertIn("/api/live/snapshots", body["routes"])
        self.assertIn("/api/live/connector-runs", body["routes"])

    def test_unknown_approval_404(self):
        try:
            self.post("/api/approvals/nope-999/approve-draft")
            self.fail("expected HTTPError 404")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)

    def test_static_index_and_app(self):
        with urllib.request.urlopen(self.url("/"), timeout=5) as resp:
            html = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("Autonomous Ops Desk", html)
        with urllib.request.urlopen(self.url("/app.js"), timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(
                resp.headers.get("Content-Type"),
                "text/javascript; charset=utf-8",
            )

    def test_static_path_traversal_blocked(self):
        try:
            with urllib.request.urlopen(
                self.url("/../../CLAUDE.md"), timeout=5
            ) as resp:
                # urllib normalizes most traversal; a 200 here must NOT be CLAUDE.md.
                body = resp.read().decode("utf-8", "ignore")
                self.assertNotIn("Non-negotiable safety", body)
        except urllib.error.HTTPError as exc:
            self.assertIn(exc.code, (400, 403, 404))


if __name__ == "__main__":
    unittest.main(verbosity=2)
