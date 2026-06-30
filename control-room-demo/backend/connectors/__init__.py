"""Phase 5 live READ-ONLY connectors.

Every connector in this package is read-only by construction:
  * no IMAP STORE / COPY / EXPUNGE / APPEND / DELETE
  * no HTTP POST / PUT / PATCH / DELETE
  * no Stripe charges / payment links / refunds
  * output is always a *redacted* snapshot (raw_stored = 0)

``scripts/validate_live_safety.py`` statically enforces these invariants.
"""
