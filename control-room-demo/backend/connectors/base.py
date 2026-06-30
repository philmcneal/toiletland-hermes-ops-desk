#!/usr/bin/env python3
"""Connector interface for Phase 5 live read-only ingestion.

A connector exposes exactly two capabilities:

  * ``status()``  -> a secret-free dict describing config presence / readiness.
  * ``fetch(limit)`` -> a :class:`ConnectorResult` of REDACTED snapshots.

There is deliberately no ``send``/``update``/``delete``/``mark`` method. The
interface itself has no mutation surface; a connector that needed one would not
fit this base class. ``READ_ONLY`` is asserted at construction time.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Default and hard-capped fetch limits. The CLI clamps to MAX_LIMIT so a typo
# can never pull a large mailbox/order page.
DEFAULT_LIMIT = 10
MAX_LIMIT = 10


@dataclass
class ConnectorResult:
    """Outcome of a single read-only fetch. Snapshots are already redacted."""

    connector: str
    rows_seen: int = 0
    snapshots: list = field(default_factory=list)
    ok: bool = True
    read_only: bool = True
    mutations: int = 0  # always 0; present so callers can assert on it
    note: str = ""

    @property
    def rows_saved(self) -> int:
        # "saved" == snapshots that survived redaction and are persistable.
        return len(self.snapshots)

    def summary(self) -> dict:
        return {
            "connector": self.connector,
            "rows_seen": self.rows_seen,
            "rows_saved": self.rows_saved,
            "ok": self.ok,
            "read_only": self.read_only,
            "mutations": self.mutations,
            "note": self.note,
        }


class Connector:
    """Base class. Subclasses MUST stay read-only."""

    name = "base"
    READ_ONLY = True

    def __init__(self, config):
        if not self.READ_ONLY:
            # Defense-in-depth: refuse to even construct a non-read-only
            # connector under this base class.
            raise RuntimeError(
                f"{type(self).__name__} declared READ_ONLY=False; "
                "Phase 5 forbids mutating connectors."
            )
        self.config = config

    def is_ready(self) -> bool:
        """Configured AND enabled AND the master live gate is on."""
        return False

    def status(self) -> dict:  # pragma: no cover - overridden
        raise NotImplementedError

    def fetch(self, limit: int = DEFAULT_LIMIT) -> ConnectorResult:  # pragma: no cover
        raise NotImplementedError


def clamp_limit(limit) -> int:
    """Coerce a requested limit into ``1..MAX_LIMIT``."""
    try:
        n = int(limit)
    except (TypeError, ValueError):
        return DEFAULT_LIMIT
    if n < 1:
        return 1
    return min(n, MAX_LIMIT)
