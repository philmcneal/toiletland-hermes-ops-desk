#!/usr/bin/env python3
"""Local backend for the Toiletland x Hermes SMB Operator (Phase 1).

Python-stdlib only: ``http.server`` + ``sqlite3``. No third-party deps, no
network egress. Serves the existing static control-room demo AND a small JSON
API backed by SQLite, so the frontend can run from backend data instead of
fetching the raw JSON fixtures directly.

Routes
------
GET  /api/health
GET  /api/queues
GET  /api/emails
GET  /api/warranty-cases
GET  /api/payment-requests
GET  /api/agent-pulse
GET  /api/audit
POST /api/approvals/<id>/approve-draft
POST /api/approvals/<id>/reject

Everything else is served as a static file from the control-room-demo folder.

Run
---
    python3 control-room-demo/backend/server.py            # 127.0.0.1:8770
    OPS_DESK_PORT=9000 python3 control-room-demo/backend/server.py

Safety: binds to 127.0.0.1 by default, keeps every live connector OFF, and the
approval routes only write durable SQLite audit rows. No live external action
is ever taken.
"""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402  (local module, after sys.path tweak)
import db  # noqa: E402  (local module, after sys.path tweak)

DEMO_DIR = Path(__file__).resolve().parent.parent

GET_COLLECTIONS = {
    "/api/queues": "queues",
    "/api/emails": "emails",
    "/api/warranty-cases": "warranty-cases",
    "/api/payment-requests": "payment-requests",
}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".map": "application/json",
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}


class OpsDeskHandler(BaseHTTPRequestHandler):
    # Configured by make_server().
    db_path = db.DEFAULT_DB_PATH
    data_dir = db.DEFAULT_DATA_DIR
    static_root = DEMO_DIR
    secrets_path = config.DEFAULT_SECRETS_PATH
    verbose = False

    server_version = "HermesOpsDesk/1.0"

    # ---- helpers -------------------------------------------------------
    def log_message(self, fmt, *args):  # noqa: D401
        if self.verbose:
            super().log_message(fmt, *args)

    def _conn(self):
        return db.connect(self.db_path)

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            parsed = json.loads(raw.decode("utf-8"))
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    # ---- verbs ---------------------------------------------------------
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._handle_health()
        if path == "/api/agent-pulse":
            conn = self._conn()
            try:
                return self._send_json(db.get_agent_pulse(conn))
            finally:
                conn.close()
        if path == "/api/audit":
            conn = self._conn()
            try:
                return self._send_json(db.list_audit(conn))
            finally:
                conn.close()
        if path == "/api/live/status":
            return self._handle_live_status()
        if path == "/api/live/snapshots":
            conn = self._conn()
            try:
                # redacted_json -> redacted dict; raw never stored, never sent.
                return self._send_json(db.list_live_snapshots(conn, limit=50))
            finally:
                conn.close()
        if path == "/api/live/connector-runs":
            conn = self._conn()
            try:
                return self._send_json(db.list_connector_runs(conn, limit=20))
            finally:
                conn.close()
        if path in GET_COLLECTIONS:
            conn = self._conn()
            try:
                return self._send_json(
                    db.list_collection(conn, GET_COLLECTIONS[path])
                )
            finally:
                conn.close()
        if path.startswith("/api/"):
            return self._send_json({"error": "not found", "path": path}, 404)
        return self._serve_static(path)

    def do_HEAD(self):
        # Reuse GET logic; _send_json/_serve_static skip the body for HEAD.
        self.do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        parts = [p for p in path.split("/") if p]
        # ["api", "approvals", "<id>", "approve-draft"|"reject"]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "approvals":
            item_id = unquote(parts[2])
            tail = parts[3]
            if tail == "approve-draft":
                return self._handle_decision(item_id, "approve")
            if tail == "reject":
                return self._handle_decision(item_id, "reject")
            if tail == "hold":
                return self._handle_decision(item_id, "hold")
        return self._send_json({"error": "not found", "path": path}, 404)

    # ---- handlers ------------------------------------------------------
    def _handle_health(self):
        conn = self._conn()
        try:
            payload = {
                "ok": True,
                "service": "hermes-smb-operator-backend",
                "mode": db.MODE,
                "demo_fixture_mode": True,
                "live_dry_run_mode": False,
                "live_connectors": db.LIVE_CONNECTORS,
                "db": str(self.db_path),
                "counts": db.counts(conn),
                "time": db._now_iso(),
                "routes": [
                    "/api/health", "/api/queues", "/api/emails",
                    "/api/warranty-cases", "/api/payment-requests",
                    "/api/agent-pulse", "/api/audit",
                    "/api/live/status", "/api/live/snapshots",
                    "/api/live/connector-runs",
                    "/api/approvals/{id}/approve-draft",
                    "/api/approvals/{id}/reject",
                    "/api/approvals/{id}/hold",
                ],
                "safety": [
                    "LIVE CONNECTORS OFF", "NO EMAIL SENT", "NO WOO UPDATE",
                    "NO LABEL BOOKED", "NO STRIPE CALL", "NO ADS CALL",
                    "NO CRON MUTATION", "NO POSTS", "OWNER APPROVAL REQUIRED",
                ],
            }
            return self._send_json(payload)
        finally:
            conn.close()

    def _handle_live_status(self):
        # Secret-free: config.status() exposes presence/hints only, never values.
        conn = self._conn()
        try:
            cfg = config.load_config(self.secrets_path)
            payload = {
                "live_readonly": cfg.status(),
                "ingestion": db.live_status(conn),
                "mutations_enabled": False,
                "note": "Live connectors are READ-ONLY. Snapshots are redacted "
                "(raw_stored=0). No external action is ever taken.",
            }
            return self._send_json(payload)
        finally:
            conn.close()

    def _handle_decision(self, item_id, decision):
        body = self._read_json_body()
        actor = body.get("actor")
        action = body.get("action")
        conn = self._conn()
        try:
            result = db.apply_decision(
                conn, item_id, decision, actor=actor, action=action
            )
            return self._send_json(result)
        except KeyError:
            return self._send_json(
                {"error": "item not found", "item_id": item_id}, 404
            )
        except ValueError as exc:
            return self._send_json({"error": str(exc)}, 400)
        finally:
            conn.close()

    # ---- static --------------------------------------------------------
    def _serve_static(self, path):
        rel = unquote(path).lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel = rel + "index.html"
        target = (self.static_root / rel).resolve()
        try:
            target.relative_to(self.static_root.resolve())
        except ValueError:
            return self._send_json({"error": "forbidden"}, 403)
        if not target.is_file():
            return self._send_json({"error": "not found", "path": path}, 404)

        ctype = CONTENT_TYPES.get(target.suffix.lower())
        if not ctype:
            ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)


LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")


def make_server(host="127.0.0.1", port=8770, db_path=db.DEFAULT_DB_PATH,
                data_dir=db.DEFAULT_DATA_DIR, verbose=False,
                secrets_path=config.DEFAULT_SECRETS_PATH):
    """Build (and seed) a server. Returns the ThreadingHTTPServer instance."""
    # Defense-in-depth: the Phase 1 backend is local-only by design. Enforce the
    # loopback invariant here too, so it holds for every caller (not just main()).
    if host not in LOOPBACK_HOSTS:
        raise ValueError(
            f"refusing non-loopback host {host!r}: the Phase 1 backend is "
            "local-only. Use 127.0.0.1 (a live phase needs explicit owner sign-off)."
        )
    conn = db.connect(db_path)
    try:
        db.seed_from_fixtures(conn, data_dir=data_dir)
    finally:
        conn.close()

    handler = type(
        "ConfiguredOpsDeskHandler",
        (OpsDeskHandler,),
        {
            "db_path": db_path,
            "data_dir": Path(data_dir),
            "static_root": DEMO_DIR,
            "secrets_path": secrets_path,
            "verbose": verbose,
        },
    )
    httpd = ThreadingHTTPServer((host, port), handler)
    return httpd


def main():
    host = os.environ.get("OPS_DESK_HOST", "127.0.0.1")
    port = int(os.environ.get("OPS_DESK_PORT", "8770"))
    db_path = os.environ.get("OPS_DESK_DB", str(db.DEFAULT_DB_PATH))
    data_dir = os.environ.get("OPS_DESK_DATA_DIR", str(db.DEFAULT_DATA_DIR))

    if host not in LOOPBACK_HOSTS:
        print(
            f"[ops-desk] refusing non-loopback host {host!r}; "
            "Phase 1 is local-only. Set OPS_DESK_HOST=127.0.0.1.",
            file=sys.stderr,
        )
        sys.exit(2)

    httpd = make_server(host=host, port=port, db_path=Path(db_path),
                        data_dir=Path(data_dir), verbose=True)
    print(f"[ops-desk] fixture-only backend on http://{host}:{port}")
    print(f"[ops-desk] db={db_path}  live_connectors=OFF  mode=fixture")
    print(f"[ops-desk] open http://{host}:{port}/ for the demo, "
          f"http://{host}:{port}/api/health for status")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[ops-desk] shutting down")
        httpd.shutdown()


if __name__ == "__main__":
    main()
