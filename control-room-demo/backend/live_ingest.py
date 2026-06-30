#!/usr/bin/env python3
"""Phase 5 live READ-ONLY ingestion CLI.

This is the ONLY entrypoint that talks to a live service, and it is read-only by
construction. It can:

  * ``--status``                          show secret-free config + DB posture
  * ``<connector> --dry-run``             fetch + redact + print; write NOTHING
  * ``<connector> --write --i-understand-read-only``
                                          fetch + redact + persist redacted
                                          snapshots to local SQLite

``--write`` writes ONLY to the local SQLite database (redacted snapshots). It
NEVER writes to the email / WooCommerce / Stripe service. There is no send,
mark-read, move, delete, order edit, refund, charge, or payment-link path here.

Connectors: ``email`` (IMAP, must-have), ``woocommerce`` (GET orders),
``stripe`` (test-mode status proof). Default limit 10, hard-capped at 10.

Examples
--------
    python3 control-room-demo/backend/live_ingest.py --status
    python3 control-room-demo/backend/live_ingest.py email --dry-run
    python3 control-room-demo/backend/live_ingest.py email --write --i-understand-read-only --limit 10
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

import config  # noqa: E402
import db  # noqa: E402
from connectors.base import DEFAULT_LIMIT, clamp_limit  # noqa: E402
from connectors.imap_readonly import IMAPReadOnlyConnector  # noqa: E402
from connectors.stripe_test_status import StripeTestStatusConnector  # noqa: E402
from connectors.woocommerce_readonly import WooCommerceReadOnlyConnector  # noqa: E402

CONNECTORS = {
    "email": IMAPReadOnlyConnector,
    "woocommerce": WooCommerceReadOnlyConnector,
    "stripe": StripeTestStatusConnector,
}


def _emit(payload: dict) -> None:
    """Print a JSON payload. Inputs here are already secret-free / redacted."""
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_status(cfg: config.LiveConfig, conn) -> int:
    payload = {
        "live_readonly_status": cfg.status(),
        "db": db.live_status(conn),
        "safety": {
            "mutations_enabled": False,
            "ingestion": "read-only; stores redacted snapshots (raw_stored=0)",
            "note": "No email send/mark/move/delete, no Woo edits/refunds, "
            "no Stripe charges/links/refunds, no Ads/shipping/cron/social.",
        },
    }
    _emit(payload)
    return 0


def cmd_run(cfg, conn, name, *, write, limit) -> int:
    builder = CONNECTORS[name]
    connector = builder(cfg)

    if not cfg.live_readonly_enabled:
        _emit({
            "connector": name,
            "ok": False,
            "rows_seen": 0,
            "rows_saved": 0,
            "note": "LIVE_READONLY_ENABLED is not true in "
            ".secrets/live-readonly.env; nothing fetched.",
        })
        return 3
    if not connector.is_ready():
        _emit({
            "connector": name,
            "ok": False,
            "rows_seen": 0,
            "rows_saved": 0,
            "note": f"{name} connector is not configured+enabled; nothing "
            "fetched. Run --status to see what is missing.",
            "status": connector.status(),
        })
        return 3

    result = connector.fetch(limit=limit)
    mode = "write-readonly" if write else "dry-run"

    rows_saved = 0
    run_id = None
    if write and result.ok:
        # Persist a run row + redacted snapshots. DB CHECK constraints reject any
        # non-read-only / raw row at the storage layer.
        run_id = db.start_connector_run(conn, name, mode)
        for snap in result.snapshots:
            db.add_live_snapshot(conn, run_id, snap)
            rows_saved += 1
        db.finish_connector_run(
            conn, run_id, rows_seen=result.rows_seen,
            rows_saved=rows_saved, ok=result.ok, note=result.note,
        )

    payload = {
        "connector": name,
        "mode": mode,
        "ok": result.ok,
        "rows_seen": result.rows_seen,
        "rows_saved": rows_saved,  # 0 for dry-run; persisted count for --write
        "snapshots_available": result.rows_saved,
        "read_only": True,
        "mutations": 0,
        "run_id": run_id,
        "note": result.note,
        # Snapshots are already redacted (raw_stored=0); safe to display.
        "sample_redacted_snapshots": [
            {k: s.get(k) for k in ("connector", "kind", "external_ref", "redacted")}
            for s in result.snapshots[:3]
        ],
    }
    if not write:
        payload["dry_run_note"] = (
            "DRY RUN: nothing written to the database or to any live service."
        )
    _emit(payload)
    return 0 if result.ok else 4


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="live_ingest",
        description="Phase 5 live READ-ONLY ingestion (redacted snapshots only).",
    )
    p.add_argument(
        "connector", nargs="?", choices=sorted(CONNECTORS),
        help="connector to run (omit with --status)",
    )
    p.add_argument("--status", action="store_true",
                   help="show secret-free config + DB posture; no network")
    p.add_argument("--dry-run", action="store_true",
                   help="fetch + redact + print; write NOTHING (default mode)")
    p.add_argument("--write", action="store_true",
                   help="persist redacted snapshots to LOCAL SQLite "
                        "(requires --i-understand-read-only)")
    p.add_argument("--i-understand-read-only", dest="ack", action="store_true",
                   help="required acknowledgement to pair with --write")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                   help=f"max rows (default {DEFAULT_LIMIT}, hard-capped at 10)")
    p.add_argument("--db", default=str(db.DEFAULT_DB_PATH), help="SQLite path")
    p.add_argument("--secrets", default=str(config.DEFAULT_SECRETS_PATH),
                   help="path to .secrets/live-readonly.env")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg = config.load_config(args.secrets)
    conn = db.connect(Path(args.db))
    try:
        db.init_schema(conn)
        if args.status or not args.connector:
            return cmd_status(cfg, conn)

        if args.write and not args.ack:
            print(
                "[live_ingest] --write requires --i-understand-read-only "
                "(it writes redacted snapshots to LOCAL SQLite only, never to "
                "any live service). Refusing.",
                file=sys.stderr,
            )
            return 2

        limit = clamp_limit(args.limit)
        return cmd_run(cfg, conn, args.connector, write=args.write, limit=limit)
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
