#!/usr/bin/env python3
"""WooCommerce READ-ONLY orders connector (Phase 5 optional).

Read-only guarantees, enforced in code:
  * Issues ONLY HTTP ``GET`` to ``/wp-json/wc/v3/orders`` (method hard-coded).
    No POST / PUT / PATCH / DELETE -> no order edits, no refunds, no fulfilment,
    no status changes.
  * Requires HTTPS. Refuses a non-https base URL.
  * Output is a redacted order snapshot only (raw_stored = 0): status, currency,
    total, line-item count, created date. NO customer name / email / address /
    phone / billing or shipping details are read into the snapshot.

The HTTP fetcher is injectable (``fetcher``) so tests run without a network.
"""
from __future__ import annotations

import base64
import json
from datetime import datetime

import redaction
from connectors.base import Connector, ConnectorResult, DEFAULT_LIMIT, clamp_limit

ORDERS_PATH = "/wp-json/wc/v3/orders"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _urllib_get(url: str, headers: dict, timeout: int = 20) -> bytes:
    """Default fetcher: a single read-only HTTPS GET via stdlib urllib."""
    import urllib.request  # local import: only when a real call is made

    # method is pinned to GET; this connector has no other verb.
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


class WooCommerceReadOnlyConnector(Connector):
    name = "woocommerce"
    READ_ONLY = True

    def __init__(self, config, fetcher=None):
        super().__init__(config)
        self._fetch = fetcher or _urllib_get

    def is_ready(self) -> bool:
        return (
            self.config.live_readonly_enabled
            and self.config.woo_configured
            and self.config.woo_enabled
        )

    def status(self) -> dict:
        st = self.config.woo_status().to_dict()
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
        if not (self.config.woo_configured and self.config.woo_enabled):
            return ConnectorResult(
                self.name, ok=False,
                note="woocommerce connector not configured/enabled.",
            )

        creds = self.config.woo_secrets()
        base = creds["base_url"]
        if not base.lower().startswith("https://"):
            return ConnectorResult(
                self.name, ok=False,
                note="refusing non-https WooCommerce base URL.",
            )

        token = base64.b64encode(
            f"{creds['consumer_key']}:{creds['consumer_secret']}".encode()
        ).decode()
        url = f"{base}{ORDERS_PATH}?per_page={limit}&page=1&orderby=date&order=desc"
        headers = {
            "Authorization": f"Basic {token}",
            "Accept": "application/json",
            "User-Agent": "HermesOpsDesk-readonly/1.0",
        }
        try:
            raw = self._fetch(url, headers)
            orders = json.loads(raw.decode("utf-8", "replace"))
        except Exception as exc:  # network/parse errors are non-fatal
            return ConnectorResult(
                self.name, ok=False,
                note=f"GET orders failed: {type(exc).__name__}",
            )
        if not isinstance(orders, list):
            return ConnectorResult(
                self.name, ok=False, note="unexpected orders payload shape."
            )

        snapshots = []
        for order in orders[:limit]:
            snapshots.append(redaction.assert_no_raw(self._snapshot(order)))
        return ConnectorResult(
            self.name,
            rows_seen=len(orders[:limit]),
            snapshots=snapshots,
            ok=True,
            note="GET /wp-json/wc/v3/orders (read-only); no mutation.",
        )

    def _snapshot(self, order: dict) -> dict:
        oid = order.get("id")
        number = order.get("number")
        return {
            "connector": self.name,
            "kind": "order",
            "external_ref": redaction.stable_ref(f"order:{oid}", number),
            "captured_at": _now_iso(),
            "redacted": {
                # Merchant-side, non-PII operational fields only.
                "status": str(order.get("status", "")),
                "currency": str(order.get("currency", "")),
                "total": str(order.get("total", "")),
                "line_items_count": len(order.get("line_items") or []),
                "date_created": redaction.redact_text(order.get("date_created")),
            },
            "raw_stored": 0,
        }
