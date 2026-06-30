#!/usr/bin/env python3
"""Stripe TEST-MODE status connector (Phase 5 optional).

This connector proves a configured Stripe key is a TEST key and nothing more.

Hard limits:
  * Accepts only ``sk_test_`` keys. A live (``sk_live_``) key is REFUSED outright
    and never used.
  * Makes NO network call at all — not even a read GET. It inspects the key
    prefix locally and reports test-mode. No charges, no Payment Links, no
    Checkout Sessions, no refunds, no balance pulls.
  * The key value is never returned or logged; only the boolean ``test_mode``.

Output is a redacted status snapshot (raw_stored = 0).
"""
from __future__ import annotations

from datetime import datetime

import redaction
from connectors.base import Connector, ConnectorResult, DEFAULT_LIMIT


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class StripeTestStatusConnector(Connector):
    name = "stripe"
    READ_ONLY = True

    def is_ready(self) -> bool:
        return (
            self.config.live_readonly_enabled
            and self.config.stripe_configured
            and self.config.stripe_is_test_key
            and self.config.stripe_enabled
        )

    def status(self) -> dict:
        st = self.config.stripe_status().to_dict()
        st["ready"] = self.is_ready()
        st["live_readonly_enabled"] = self.config.live_readonly_enabled
        return st

    def fetch(self, limit: int = DEFAULT_LIMIT) -> ConnectorResult:
        if not self.config.stripe_configured:
            return ConnectorResult(
                self.name, ok=False, note="stripe key not configured."
            )
        if not self.config.stripe_is_test_key:
            # Never touch a non-test key. This is the whole point of the guard.
            return ConnectorResult(
                self.name, ok=False,
                note="configured Stripe key is NOT sk_test_; refusing to use it.",
            )
        if not self.config.stripe_enabled:
            return ConnectorResult(
                self.name, ok=False, note="stripe connector not enabled."
            )

        snap = {
            "connector": self.name,
            "kind": "stripe_status",
            "external_ref": redaction.stable_ref("stripe", "test-mode"),
            "captured_at": _now_iso(),
            "redacted": {
                "test_mode": True,
                "livemode": False,
                "proof": "sk_test_ key present; no API call made",
                "charges_enabled": False,
            },
            "raw_stored": 0,
        }
        return ConnectorResult(
            self.name,
            rows_seen=1,
            snapshots=[redaction.assert_no_raw(snap)],
            ok=True,
            note="test-mode status proof only; no network call, no mutation.",
        )
