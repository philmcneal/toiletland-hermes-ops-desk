# Architecture

## Surfaces

- `control-room-demo/index.html` — single-page control room UI.
- `control-room-demo/app.js` — API-aware frontend with static fixture fallback.
- `control-room-demo/data/*.json` — redacted fixtures for queues, email, warranty, payments, agent pulse, and audit.
- `control-room-demo/backend/server.py` — local-only Python stdlib API/static server.
- `control-room-demo/backend/db.py` — SQLite schema, fixture seeding, decisions, audit rows, and live-readonly snapshot tables.
- `control-room-demo/backend/live_ingest.py` — explicit read-only ingest CLI for email/Woo/Stripe-test-status proof.
- `control-room-demo/backend/connectors/` — read-only connector adapters.

## Data flow

```text
fixtures / read-only connectors
          ↓
redaction + local SQLite snapshots
          ↓
control-room API
          ↓
owner approval UI
          ↓
append-only audit event, executed=false
```

The demo intentionally separates **signal ingestion** from **business mutation**. Live signals can enter read-only, but no external service is changed.
