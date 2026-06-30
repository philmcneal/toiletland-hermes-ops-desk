#!/usr/bin/env python3
"""Config loader for the Phase 5 live read-only connectors.

Secrets live ONLY in ``.secrets/live-readonly.env`` (git-ignored). This module
parses that file into a :class:`LiveConfig`. It NEVER prints, logs, or returns
secret values: callers get presence booleans and non-secret hints (host, port,
masked username) via :meth:`LiveConfig.status`.

Safety gates surfaced here, never overridden anywhere downstream:
  * ``LIVE_READONLY_ENABLED`` must be true for any network fetch (dry-run/write).
  * Per-connector ``*_ENABLED`` flags gate each connector independently.
  * ``mutations_enabled`` is hard-wired False. There is no env var to turn it on.

This module performs NO network I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent.parent
DEFAULT_SECRETS_PATH = REPO_ROOT / ".secrets" / "live-readonly.env"

# Hard-wired, read-only by construction. No code path flips this True.
MUTATIONS_ENABLED = False

_TRUE = {"1", "true", "yes", "on", "enabled"}


def _is_true(value) -> bool:
    return str(value).strip().lower() in _TRUE


def _mask_username(value: str) -> str:
    """``alice@store.com`` -> ``a***@store.com``; never the full local part."""
    if not value:
        return ""
    if "@" in value:
        local, _, domain = value.partition("@")
        head = local[:1] if local else ""
        return f"{head}***@{domain}"
    return f"{value[:1]}***" if value else ""


def parse_env(text: str) -> dict:
    """Parse simple ``KEY=VALUE`` env text. Ignores blanks and ``#`` comments.
    Strips surrounding single/double quotes. Does not interpolate or exec.
    """
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            out[key] = value
    return out


@dataclass
class ConnectorStatus:
    name: str
    configured: bool
    enabled: bool
    read_only: bool = True
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "configured": self.configured,
            "enabled": self.enabled,
            "read_only": self.read_only,
            "mutations_enabled": False,
            "detail": self.detail,  # non-secret hints only
        }


class LiveConfig:
    """Holds parsed secrets in memory. Exposes presence/status, not values.

    Secret values are reachable only through the explicit ``*_secrets()``
    accessors used by the connectors themselves — never serialized or printed.
    """

    def __init__(self, values: dict | None = None, source: Path | None = None):
        self._v = dict(values or {})
        self.source = source

    # ---- master gate ---------------------------------------------------
    @property
    def live_readonly_enabled(self) -> bool:
        return _is_true(self._v.get("LIVE_READONLY_ENABLED", ""))

    @property
    def mutations_enabled(self) -> bool:  # always False, by construction
        return MUTATIONS_ENABLED

    # ---- email (IMAP read-only) ---------------------------------------
    @property
    def email_configured(self) -> bool:
        return all(
            self._v.get(k)
            for k in ("IMAP_HOST", "IMAP_USERNAME", "IMAP_PASSWORD")
        )

    @property
    def email_enabled(self) -> bool:
        return _is_true(self._v.get("IMAP_ENABLED", ""))

    def email_secrets(self) -> dict:
        return {
            "host": self._v.get("IMAP_HOST", ""),
            "port": int(self._v.get("IMAP_PORT", "993") or "993"),
            "username": self._v.get("IMAP_USERNAME", ""),
            "password": self._v.get("IMAP_PASSWORD", ""),
            "mailbox": self._v.get("IMAP_MAILBOX", "INBOX") or "INBOX",
        }

    def email_status(self) -> ConnectorStatus:
        host = self._v.get("IMAP_HOST", "")
        return ConnectorStatus(
            name="email",
            configured=self.email_configured,
            enabled=self.email_enabled,
            detail={
                "host": host or "[unset]",
                "port": self._v.get("IMAP_PORT", "993") if host else "[unset]",
                "username": _mask_username(self._v.get("IMAP_USERNAME", "")),
                "mailbox": self._v.get("IMAP_MAILBOX", "INBOX"),
                "method": "IMAP EXAMINE (readonly) + BODY.PEEK",
            },
        )

    # ---- WooCommerce (read-only GET) ----------------------------------
    @property
    def woo_configured(self) -> bool:
        return all(
            self._v.get(k)
            for k in ("WOO_BASE_URL", "WOO_CONSUMER_KEY", "WOO_CONSUMER_SECRET")
        )

    @property
    def woo_enabled(self) -> bool:
        return _is_true(self._v.get("WOO_ENABLED", ""))

    def woo_secrets(self) -> dict:
        return {
            "base_url": self._v.get("WOO_BASE_URL", "").rstrip("/"),
            "consumer_key": self._v.get("WOO_CONSUMER_KEY", ""),
            "consumer_secret": self._v.get("WOO_CONSUMER_SECRET", ""),
        }

    def woo_status(self) -> ConnectorStatus:
        base = self._v.get("WOO_BASE_URL", "")
        return ConnectorStatus(
            name="woocommerce",
            configured=self.woo_configured,
            enabled=self.woo_enabled,
            detail={
                "base_url": base or "[unset]",
                "method": "GET /wp-json/wc/v3/orders (read-only)",
            },
        )

    # ---- Stripe (test-mode status proof only) -------------------------
    @property
    def stripe_key(self) -> str:
        return self._v.get("STRIPE_TEST_SECRET_KEY", "")

    @property
    def stripe_configured(self) -> bool:
        return bool(self.stripe_key)

    @property
    def stripe_is_test_key(self) -> bool:
        return self.stripe_key.startswith("sk_test_")

    @property
    def stripe_enabled(self) -> bool:
        return _is_true(self._v.get("STRIPE_ENABLED", ""))

    def stripe_status(self) -> ConnectorStatus:
        return ConnectorStatus(
            name="stripe",
            configured=self.stripe_configured,
            enabled=self.stripe_enabled,
            detail={
                # Never the key itself: only whether it is a TEST key.
                "test_mode_key": self.stripe_is_test_key,
                "method": "test-mode status proof only (no charges/links/refunds)",
            },
        )

    # ---- aggregate -----------------------------------------------------
    def connector_statuses(self) -> dict:
        return {
            "email": self.email_status().to_dict(),
            "woocommerce": self.woo_status().to_dict(),
            "stripe": self.stripe_status().to_dict(),
        }

    def status(self) -> dict:
        """Secret-free status payload for CLI/API. Contains NO secret values."""
        connectors = self.connector_statuses()
        any_configured = any(c["configured"] for c in connectors.values())
        return {
            "live_readonly_enabled": self.live_readonly_enabled,
            "mutations_enabled": False,
            "secrets_file_present": self.source is not None,
            "any_connector_configured": any_configured,
            "connectors": connectors,
        }


def load_config(path: Path | str = DEFAULT_SECRETS_PATH) -> LiveConfig:
    """Load ``.secrets/live-readonly.env`` if present. Missing file -> empty
    config (status mode still works; fetch paths refuse). Never raises on a
    missing file.
    """
    p = Path(path)
    if not p.is_file():
        return LiveConfig({}, source=None)
    text = p.read_text(encoding="utf-8", errors="replace")
    return LiveConfig(parse_env(text), source=p)


if __name__ == "__main__":  # pragma: no cover - convenience
    import json

    cfg = load_config()
    # status() is secret-free by construction; safe to print.
    print(json.dumps(cfg.status(), indent=2))
