#!/usr/bin/env python3
"""SQLite persistence for the Toiletland x Hermes SMB Operator (Phase 1).

This module is fixture-only and read-mostly. It seeds a local SQLite database
from the existing redacted JSON fixtures in ``control-room-demo/data`` and
records owner approval/reject decisions as durable, append-only audit rows.

Hard safety invariant (Phase 0 + Phase 1):
    Nothing in this file opens a network socket, sends email, calls Stripe /
    WooCommerce / Google Ads, books shipping, mutates cron, posts to social, or
    submits a form. The only side effects are local SQLite writes. Approvals
    return an AdapterResult stamped ``executed=False, mode="fixture"``.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths & constants
# ----------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
DEMO_DIR = BACKEND_DIR.parent
DEFAULT_DATA_DIR = DEMO_DIR / "data"
DEFAULT_DB_PATH = BACKEND_DIR / "ops_desk.db"

# Phase 0/1 safety posture surfaced through every response.
MODE = "fixture"
LIVE_CONNECTORS = False

# The single, reused proof that an approval executed no external action.
def adapter_result() -> dict:
    """Stamp returned with every decision: nothing left the machine."""
    return {
        "mode": MODE,
        "executed": False,
        "live_connectors": LIVE_CONNECTORS,
        "external_id": None,
        "note": "Owner decision recorded to local SQLite audit only. "
        "No email/Stripe/WooCommerce/Ads/shipping/cron/social action fired.",
    }


# name used by the API  ->  (table, fixture filename, kind)
COLLECTIONS = {
    "queues": ("queue_items", "queue-items.json", "list"),
    "emails": ("emails", "email-command-center.json", "list"),
    "warranty-cases": ("warranty_cases", "warranty-cases.json", "list"),
    "payment-requests": ("payment_requests", "payment-requests.json", "list"),
    "agent-pulse": ("agent_pulse", "agent-ops-cron-fixture.json", "object"),
}

# Tables that hold an approvable item with a "status" field in its JSON blob.
ITEM_TABLES = ["queue_items", "emails", "warranty_cases", "payment_requests"]

# Default status applied by each decision (callers may override with `action`).
# "hold" = owner is keeping the item under review; it is still audited durably.
DECISION_STATUS = {
    "approve": "approved-draft",
    "reject": "rejected-demo",
    "hold": "needs-owner",
}
DECISION_VERB = {
    "approve": "approved (draft only)",
    "reject": "rejected",
    "hold": "kept under owner review",
}


# ----------------------------------------------------------------------------
# Connection & schema
# ----------------------------------------------------------------------------

def connect(db_path=DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table in ITEM_TABLES:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id        TEXT PRIMARY KEY,
                status    TEXT,
                position  INTEGER,
                data      TEXT NOT NULL
            )
            """
        )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_pulse (
            id   INTEGER PRIMARY KEY CHECK (id = 1),
            data TEXT NOT NULL
        )
        """
    )
    # Append-only audit log. seq is the durable ordering key.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            seq        INTEGER PRIMARY KEY AUTOINCREMENT,
            at         TEXT,
            actor      TEXT,
            item_id    TEXT,
            event      TEXT,
            outcome    TEXT,
            source     TEXT,
            mode       TEXT,
            executed   INTEGER NOT NULL DEFAULT 0,
            created_at TEXT
        )
        """
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"
    )
    # ---- Phase 5: live READ-ONLY ingestion (separate from fixtures) --------
    # connector_runs: one row per live_ingest run. The CHECK constraints make it
    # physically impossible to persist a non-read-only / mutating run.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS connector_runs (
            run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            connector   TEXT NOT NULL,
            mode        TEXT NOT NULL,
            started_at  TEXT,
            finished_at TEXT,
            rows_seen   INTEGER NOT NULL DEFAULT 0,
            rows_saved  INTEGER NOT NULL DEFAULT 0,
            ok          INTEGER NOT NULL DEFAULT 0,
            read_only   INTEGER NOT NULL DEFAULT 1 CHECK (read_only = 1),
            mutations   INTEGER NOT NULL DEFAULT 0 CHECK (mutations = 0),
            note        TEXT
        )
        """
    )
    # live_snapshots: redacted-only. raw_stored is CHECK (= 0) so the DB itself
    # rejects any attempt to persist raw content.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS live_snapshots (
            snap_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id        INTEGER,
            connector     TEXT NOT NULL,
            kind          TEXT,
            external_ref  TEXT,
            captured_at   TEXT,
            redacted_json TEXT NOT NULL,
            raw_stored    INTEGER NOT NULL DEFAULT 0 CHECK (raw_stored = 0),
            created_at    TEXT,
            FOREIGN KEY (run_id) REFERENCES connector_runs(run_id)
        )
        """
    )
    conn.commit()


# ----------------------------------------------------------------------------
# Seeding (idempotent)
# ----------------------------------------------------------------------------

def _load_fixture(data_dir: Path, filename: str):
    return json.loads((Path(data_dir) / filename).read_text(encoding="utf-8"))


def _table_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]


def seed_from_fixtures(conn, data_dir=DEFAULT_DATA_DIR, reseed=False) -> dict:
    """Populate SQLite from the redacted JSON fixtures.

    Idempotent: existing rows are left untouched (so durable owner decisions
    survive restarts) unless ``reseed=True`` clears tables first.
    """
    init_schema(conn)
    data_dir = Path(data_dir)
    cur = conn.cursor()
    seeded = {}

    if reseed:
        for table in ITEM_TABLES + ["agent_pulse", "audit_events"]:
            cur.execute(f"DELETE FROM {table}")
        cur.execute("DELETE FROM meta")

    # Item collections + agent pulse.
    for name, (table, filename, kind) in COLLECTIONS.items():
        if kind == "list":
            if _table_count(conn, table) > 0:
                seeded[table] = _table_count(conn, table)
                continue
            rows = _load_fixture(data_dir, filename)
            for pos, item in enumerate(rows):
                cur.execute(
                    f"INSERT INTO {table} (id, status, position, data) "
                    "VALUES (?, ?, ?, ?)",
                    (item.get("id"), item.get("status"), pos, json.dumps(item)),
                )
            seeded[table] = len(rows)
        else:  # single object (agent pulse)
            if _table_count(conn, "agent_pulse") > 0:
                seeded["agent_pulse"] = 1
                continue
            obj = _load_fixture(data_dir, filename)
            cur.execute(
                "INSERT INTO agent_pulse (id, data) VALUES (1, ?)",
                (json.dumps(obj),),
            )
            seeded["agent_pulse"] = 1

    # Audit log: seed the historical fixture rows once.
    if _table_count(conn, "audit_events") == 0:
        audit_rows = _load_fixture(data_dir, "audit-log.json")
        for row in audit_rows:
            cur.execute(
                "INSERT INTO audit_events "
                "(at, actor, item_id, event, outcome, source, mode, executed, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
                (
                    row.get("at"),
                    row.get("actor"),
                    row.get("item_id"),
                    row.get("event"),
                    row.get("outcome"),
                    "fixture-seed",
                    MODE,
                    _now_iso(),
                ),
            )
        seeded["audit_events"] = len(audit_rows)
    else:
        seeded["audit_events"] = _table_count(conn, "audit_events")

    conn.execute(
        "INSERT INTO meta (key, value) VALUES ('seeded_at', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (_now_iso(),),
    )
    conn.commit()
    return seeded


# ----------------------------------------------------------------------------
# Read queries
# ----------------------------------------------------------------------------

def list_collection(conn: sqlite3.Connection, name: str) -> list:
    table, _, _ = COLLECTIONS[name]
    rows = conn.execute(
        f"SELECT status, data FROM {table} ORDER BY position ASC"
    ).fetchall()
    out = []
    for row in rows:
        item = json.loads(row["data"])
        # The durable status column is the source of truth after a decision.
        if row["status"] is not None:
            item["status"] = row["status"]
        out.append(item)
    return out


def get_agent_pulse(conn: sqlite3.Connection) -> dict:
    row = conn.execute("SELECT data FROM agent_pulse WHERE id = 1").fetchone()
    return json.loads(row["data"]) if row else {}


def list_audit(conn: sqlite3.Connection) -> list:
    rows = conn.execute(
        "SELECT at, actor, item_id, event, outcome, source, mode, executed, "
        "seq, created_at FROM audit_events ORDER BY seq ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def counts(conn: sqlite3.Connection) -> dict:
    out = {}
    for table in ITEM_TABLES:
        out[table] = _table_count(conn, table)
    out["agent_pulse"] = _table_count(conn, "agent_pulse")
    out["audit_events"] = _table_count(conn, "audit_events")
    return out


# ----------------------------------------------------------------------------
# Phase 5: live READ-ONLY ingestion (connector_runs + live_snapshots)
# ----------------------------------------------------------------------------

def start_connector_run(conn, connector: str, mode: str) -> int:
    """Open a run row. read_only/mutations are pinned by table CHECK constraints."""
    init_schema(conn)
    cur = conn.execute(
        "INSERT INTO connector_runs "
        "(connector, mode, started_at, ok, read_only, mutations) "
        "VALUES (?, ?, ?, 0, 1, 0)",
        (connector, mode, _now_iso()),
    )
    conn.commit()
    return cur.lastrowid


def finish_connector_run(conn, run_id, *, rows_seen, rows_saved, ok, note) -> None:
    conn.execute(
        "UPDATE connector_runs SET finished_at=?, rows_seen=?, rows_saved=?, "
        "ok=?, note=? WHERE run_id=?",
        (_now_iso(), int(rows_seen), int(rows_saved), 1 if ok else 0,
         note, run_id),
    )
    conn.commit()


def add_live_snapshot(conn, run_id, snapshot: dict) -> int:
    """Persist ONE redacted snapshot. Re-asserts raw_stored==0 before writing;
    the table CHECK enforces it again at the storage layer.
    """
    if snapshot.get("raw_stored", None) != 0:
        raise ValueError("refusing snapshot with raw_stored != 0")
    redacted = snapshot.get("redacted", {})
    cur = conn.execute(
        "INSERT INTO live_snapshots "
        "(run_id, connector, kind, external_ref, captured_at, redacted_json, "
        " raw_stored, created_at) VALUES (?, ?, ?, ?, ?, ?, 0, ?)",
        (
            run_id,
            snapshot.get("connector"),
            snapshot.get("kind"),
            snapshot.get("external_ref"),
            snapshot.get("captured_at"),
            json.dumps(redacted),
            _now_iso(),
        ),
    )
    conn.commit()
    return cur.lastrowid


def list_connector_runs(conn, limit: int = 20) -> list:
    rows = conn.execute(
        "SELECT run_id, connector, mode, started_at, finished_at, rows_seen, "
        "rows_saved, ok, read_only, mutations, note FROM connector_runs "
        "ORDER BY run_id DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    return [dict(r) for r in rows]


def list_live_snapshots(conn, limit: int = 50, connector: str | None = None) -> list:
    if connector:
        rows = conn.execute(
            "SELECT snap_id, run_id, connector, kind, external_ref, captured_at, "
            "redacted_json, raw_stored FROM live_snapshots WHERE connector=? "
            "ORDER BY snap_id DESC LIMIT ?",
            (connector, int(limit)),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT snap_id, run_id, connector, kind, external_ref, captured_at, "
            "redacted_json, raw_stored FROM live_snapshots "
            "ORDER BY snap_id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        try:
            item["redacted"] = json.loads(item.pop("redacted_json") or "{}")
        except (json.JSONDecodeError, TypeError):
            item["redacted"] = {}
        out.append(item)
    return out


def live_counts(conn) -> dict:
    init_schema(conn)
    return {
        "connector_runs": _table_count(conn, "connector_runs"),
        "live_snapshots": _table_count(conn, "live_snapshots"),
    }


def live_status(conn) -> dict:
    """Aggregate live read-only posture for the API/frontend. Secret-free."""
    init_schema(conn)
    counts_ = live_counts(conn)
    by_connector = {}
    rows = conn.execute(
        "SELECT connector, COUNT(*) AS n FROM live_snapshots GROUP BY connector"
    ).fetchall()
    for r in rows:
        by_connector[r["connector"]] = r["n"]
    return {
        "snapshot_count": counts_["live_snapshots"],
        "run_count": counts_["connector_runs"],
        "snapshots_by_connector": by_connector,
        "live_readonly_ingestion": counts_["live_snapshots"] > 0,
        "mutations_enabled": False,
        "last_runs": list_connector_runs(conn, limit=5),
    }


# ----------------------------------------------------------------------------
# Decisions (the only write path triggered by the UI)
# ----------------------------------------------------------------------------

def find_item(conn: sqlite3.Connection, item_id: str):
    for table in ITEM_TABLES:
        row = conn.execute(
            f"SELECT id, status, data FROM {table} WHERE id = ?", (item_id,)
        ).fetchone()
        if row:
            return table, row
    return None, None


def record_audit(conn, *, at, actor, item_id, event, outcome,
                 source="owner-approval", executed=False) -> dict:
    cur = conn.execute(
        "INSERT INTO audit_events "
        "(at, actor, item_id, event, outcome, source, mode, executed, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (at, actor, item_id, event, outcome, source, MODE,
         1 if executed else 0, _now_iso()),
    )
    conn.commit()
    return conn.execute(
        "SELECT at, actor, item_id, event, outcome, source, mode, executed, "
        "seq, created_at FROM audit_events WHERE seq = ?",
        (cur.lastrowid,),
    ).fetchone()


def apply_decision(conn, item_id, decision, actor=None, action=None) -> dict:
    """Apply an owner approve/reject decision.

    Side effects, in full: update the item's status column and append one audit
    row, both in local SQLite. Returns the updated item, the new audit row, and
    an AdapterResult proving no external action executed.

    Raises ValueError for an unknown decision and KeyError for an unknown id.
    """
    if decision not in DECISION_STATUS:
        raise ValueError(f"unknown decision: {decision!r}")

    table, row = find_item(conn, item_id)
    if not row:
        raise KeyError(item_id)

    new_status = action or DECISION_STATUS[decision]
    item = json.loads(row["data"])
    item["status"] = new_status

    conn.execute(
        f"UPDATE {table} SET status = ?, data = ? WHERE id = ?",
        (new_status, json.dumps(item), item_id),
    )

    verb = DECISION_VERB[decision]
    event = (
        f"Owner {verb} via local backend; status set to {new_status}. "
        "No live connector, payment, email, shipping, vendor, ad, or cron "
        "action fired."
    )
    audit_row = record_audit(
        conn,
        at=_now_stamp(),
        actor=actor or "Owner (local backend)",
        item_id=item_id,
        event=event,
        outcome=new_status,
        source="owner-approval",
        executed=False,
    )
    conn.commit()

    return {
        "ok": True,
        "decision": decision,
        "item_id": item_id,
        "table": table,
        "item": item,
        "audit": dict(audit_row),
        "adapter_result": adapter_result(),
    }


# ----------------------------------------------------------------------------
# Time helpers (real time is fine; this is a live local backend, not the video)
# ----------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _now_stamp() -> str:
    # Mirror the human style used in the existing fixtures, e.g. "2026-06-29 23:55 PDT".
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


if __name__ == "__main__":  # pragma: no cover - convenience CLI
    c = connect()
    result = seed_from_fixtures(c)
    print("seeded:", json.dumps(result))
    print("counts:", json.dumps(counts(c)))
