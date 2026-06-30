#!/usr/bin/env python3
"""IMAP READ-ONLY email connector (Phase 5 must-have).

Read-only guarantees, enforced in code:
  * The mailbox is opened with ``select(mailbox, readonly=True)`` -> IMAP issues
    ``EXAMINE``, not ``SELECT``. The session cannot mutate the mailbox.
  * Message bodies are fetched with ``BODY.PEEK[...]`` -> the ``\\Seen`` flag is
    NEVER set. We do not mark anything read.
  * This connector calls only ``select`` (readonly), ``search``, ``fetch`` (peek)
    and ``logout``. It NEVER calls ``store``, ``copy``, ``expunge``, ``append``,
    or ``uid('STORE'...)``. No send, no move, no delete.
  * Output is a redacted snapshot only (raw_stored = 0). Raw bodies/headers are
    never returned or persisted.

The IMAP client is injectable (``imap_factory``) so tests can drive a fake that
records every command and asserts no mutating verb was ever issued.
"""
from __future__ import annotations

import email
from datetime import datetime
from email.header import decode_header, make_header

import redaction
from connectors.base import Connector, ConnectorResult, DEFAULT_LIMIT, clamp_limit

# Header fields we peek. Message-Id is hashed (never stored raw) for dedupe.
HEADER_FIELDS = "SUBJECT FROM DATE MESSAGE-ID"
HEADER_ITEM = f"(BODY.PEEK[HEADER.FIELDS ({HEADER_FIELDS})])"
# First 2 KiB of the text part only, peeked (no \Seen).
TEXT_ITEM = "(BODY.PEEK[TEXT]<0.2048>)"


def _default_factory(host: str, port: int):
    import imaplib  # local import: only when an actual connection is made

    return imaplib.IMAP4_SSL(host, port)


def _literal_bytes(fetch_data) -> bytes:
    """Pull the literal payload out of an imaplib fetch response."""
    for part in fetch_data or []:
        if isinstance(part, tuple) and len(part) >= 2 and part[1] is not None:
            return part[1] if isinstance(part[1], (bytes, bytearray)) else b""
    return b""


def _decode_header_value(raw) -> str:
    if raw is None:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return str(raw)


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class IMAPReadOnlyConnector(Connector):
    name = "email"
    READ_ONLY = True

    def __init__(self, config, imap_factory=None):
        super().__init__(config)
        self._factory = imap_factory or _default_factory

    def is_ready(self) -> bool:
        return (
            self.config.live_readonly_enabled
            and self.config.email_configured
            and self.config.email_enabled
        )

    def status(self) -> dict:
        st = self.config.email_status().to_dict()
        st["ready"] = self.is_ready()
        st["live_readonly_enabled"] = self.config.live_readonly_enabled
        return st

    def fetch(self, limit: int = DEFAULT_LIMIT) -> ConnectorResult:
        limit = clamp_limit(limit)
        if not self.config.live_readonly_enabled:
            return ConnectorResult(
                self.name, ok=False,
                note="LIVE_READONLY_ENABLED is not true; refusing to connect.",
            )
        if not (self.config.email_configured and self.config.email_enabled):
            return ConnectorResult(
                self.name, ok=False,
                note="email connector not configured/enabled.",
            )

        creds = self.config.email_secrets()
        client = self._factory(creds["host"], creds["port"])
        snapshots: list = []
        rows_seen = 0
        try:
            client.login(creds["username"], creds["password"])
            # readonly=True -> EXAMINE. Anything but OK aborts before any fetch.
            typ, _ = client.select(creds["mailbox"], readonly=True)
            if typ != "OK":
                return ConnectorResult(
                    self.name, ok=False,
                    note=f"EXAMINE {creds['mailbox']!r} failed (typ={typ}).",
                )
            typ, data = client.search(None, "ALL")
            if typ != "OK":
                return ConnectorResult(
                    self.name, ok=False, note="IMAP search failed."
                )
            ids = (data[0].split() if data and data[0] else [])
            # Newest `limit`, newest-first.
            chosen = list(reversed(ids[-limit:]))
            for msg_id in chosen:
                snap = self._snapshot_for(client, msg_id)
                if snap is not None:
                    rows_seen += 1
                    snapshots.append(redaction.assert_no_raw(snap))
            return ConnectorResult(
                self.name,
                rows_seen=rows_seen,
                snapshots=snapshots,
                ok=True,
                note=(
                    f"EXAMINE {creds['mailbox']} (readonly) + BODY.PEEK; "
                    "no \\Seen set, no mutation."
                ),
            )
        finally:
            try:
                client.logout()
            except Exception:
                pass

    def _snapshot_for(self, client, msg_id):
        typ, hdr = client.fetch(msg_id, HEADER_ITEM)
        if typ != "OK":
            return None
        header_bytes = _literal_bytes(hdr)
        msg = email.message_from_bytes(header_bytes) if header_bytes else None

        typ, txt = client.fetch(msg_id, TEXT_ITEM)
        body_bytes = _literal_bytes(txt) if typ == "OK" else b""
        body_text = body_bytes.decode("utf-8", "replace") if body_bytes else ""

        subject = _decode_header_value(msg.get("Subject")) if msg else ""
        from_hdr = _decode_header_value(msg.get("From")) if msg else ""
        date_hdr = _decode_header_value(msg.get("Date")) if msg else ""
        message_id = msg.get("Message-Id") if msg else None
        seq = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)

        snap = {
            "connector": self.name,
            "kind": "email",
            "external_ref": redaction.stable_ref(message_id or f"seq:{seq}"),
            "captured_at": _now_iso(),
            "redacted": {
                "subject": redaction.preview(subject, 120),
                "from_domain": redaction.email_domain(from_hdr),
                "date": redaction.redact_text(date_hdr),
                "body_preview": redaction.preview(body_text, 160),
                "body_chars": len(body_text),
            },
            "raw_stored": 0,
        }
        return snap
