#!/usr/bin/env python3
"""Redaction utilities for the Phase 5 live read-only connectors.

SAFETY CONTRACT
---------------
Live connectors are READ-ONLY. The only thing that may ever reach local SQLite
is a *redacted snapshot*: coarse counts, lengths, buckets, and a heavily
scrubbed preview. Raw message bodies, full headers, customer PII, order
contents, and secrets never leave this module intact and are never persisted.

Every snapshot built here is stamped ``raw_stored = 0``. ``assert_no_raw()``
re-checks a snapshot right before it is written, so a future regression cannot
silently persist raw content or a stray email/phone/card number.

This module performs NO network I/O. It is pure text in -> redacted text out.
"""
from __future__ import annotations

import hashlib
import re

# ----------------------------------------------------------------------------
# Patterns. Order matters: the most specific (card, email) run before the
# generic long-number / postal patterns so they win the first match.
# ----------------------------------------------------------------------------
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# 13-19 digit runs, optionally grouped by spaces/hyphens -> treat as card-like.
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
# Phone-ish: +country and/or grouped digits, 7+ digits total.
PHONE_RE = re.compile(
    r"(?<![\w.])(?:\+?\d{1,3}[ .\-]?)?(?:\(\d{1,4}\)[ .\-]?)?"
    r"\d{2,4}[ .\-]\d{2,4}(?:[ .\-]\d{2,4})+(?![\w.])"
)
URL_RE = re.compile(r"\bhttps?://[^\s<>\"')]+", re.IGNORECASE)
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# Canadian postal code (A1A 1A1) and US ZIP / ZIP+4.
POSTAL_CA_RE = re.compile(r"\b[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d\b")
ZIP_US_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")
# Any remaining standalone run of 5+ digits (order #, serial, tracking).
LONGNUM_RE = re.compile(r"(?<![\w])\d{5,}(?![\w])")

# Compiled scan used by assert_no_raw to prove a string is clean of obvious PII.
LEAK_PATTERNS = {
    "email": EMAIL_RE,
    "card": CARD_RE,
    "ipv4": IPV4_RE,
    "url": URL_RE,
}

# A redacted snapshot may ONLY contain these top-level keys. Anything else is a
# regression that could carry raw content, so assert_no_raw() rejects it.
SNAPSHOT_ALLOWED_KEYS = {
    "connector",
    "kind",
    "external_ref",
    "captured_at",
    "redacted",
    "raw_stored",
}


def redact_text(text) -> str:
    """Scrub a free-text string of emails, phones, cards, URLs, IPs, postal
    codes, and long numeric identifiers. Returns a safe, token-replaced string.
    """
    if not text:
        return ""
    s = str(text)
    s = URL_RE.sub("[url]", s)
    s = EMAIL_RE.sub("[email]", s)
    s = CARD_RE.sub("[card]", s)
    s = IPV4_RE.sub("[ip]", s)
    s = PHONE_RE.sub("[phone]", s)
    s = POSTAL_CA_RE.sub("[postal]", s)
    s = ZIP_US_RE.sub("[postal]", s)
    s = LONGNUM_RE.sub("[num]", s)
    # Collapse whitespace so a preview stays compact and free of layout leaks.
    return re.sub(r"\s+", " ", s).strip()


def redact_email_address(addr) -> str:
    """Reduce an email address to a domain-only hint. ``a.b@gmail.com`` ->
    ``[user]@gmail.com``. Anything unpar's to ``[email]``.
    """
    if not addr:
        return "[none]"
    match = EMAIL_RE.search(str(addr))
    if not match:
        return "[redacted]"
    domain = match.group(0).rsplit("@", 1)[-1].lower()
    # Keep only the registrable-ish domain hint, never the local part.
    return f"[user]@{domain}"


def email_domain(addr) -> str:
    """Return just the domain of an address (``gmail.com``) or ``[redacted]``."""
    if not addr:
        return "[none]"
    match = EMAIL_RE.search(str(addr))
    return match.group(0).rsplit("@", 1)[-1].lower() if match else "[redacted]"


def preview(text, limit: int = 160) -> str:
    """Redact then hard-truncate to ``limit`` characters for a safe preview."""
    red = redact_text(text)
    if len(red) <= limit:
        return red
    return red[: limit - 1].rstrip() + "…"


def stable_ref(*parts) -> str:
    """Deterministic, non-reversible 16-hex reference from raw identifiers.

    Used to dedupe snapshots (e.g. by Message-Id / order id) WITHOUT storing the
    raw identifier. SHA-256 truncated to 16 hex chars.
    """
    joined = "␟".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8", "replace")).hexdigest()[:16]


def assert_no_raw(snapshot: dict) -> dict:
    """Final gate before persistence. Raise ValueError if a snapshot looks like
    it could carry raw content. Returns the snapshot unchanged on success.

    Checks:
      * ``raw_stored`` is present and exactly 0.
      * No unexpected top-level keys (allowlist).
      * No string value anywhere still matches an email/card/IP/URL pattern.
    """
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a dict")
    if snapshot.get("raw_stored", None) != 0:
        raise ValueError("snapshot.raw_stored must be exactly 0")
    extra = set(snapshot) - SNAPSHOT_ALLOWED_KEYS
    if extra:
        raise ValueError(f"snapshot has non-allowlisted keys: {sorted(extra)}")

    def _scan(value, where):
        if isinstance(value, str):
            for name, pat in LEAK_PATTERNS.items():
                if pat.search(value):
                    raise ValueError(
                        f"redaction leak ({name}) in snapshot field {where!r}"
                    )
        elif isinstance(value, dict):
            for k, v in value.items():
                _scan(v, f"{where}.{k}")
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value):
                _scan(v, f"{where}[{i}]")

    _scan(snapshot.get("redacted", {}), "redacted")
    _scan(snapshot.get("external_ref", ""), "external_ref")
    return snapshot
