# Local Backend (Phase 1)

A small **Python-stdlib** backend that gives the control-room demo durable
persistence without changing the hackathon story or adding any live connector.

- Stack: `http.server` + `sqlite3` only. **No third-party dependencies.**
- Data: seeded from the existing redacted fixtures in `../data/*.json`.
- Persistence: owner approve/reject/hold decisions are written as **durable,
  append-only SQLite audit rows** (no more browser-only state).
- Safety: binds to `127.0.0.1`, keeps every live connector **OFF**, and never
  opens a network socket or calls Stripe / WooCommerce / Google Ads / email /
  shipping / cron / social. Decisions return `executed=false, mode=fixture`.

## Run

```bash
# From the project root
python3 control-room-demo/backend/server.py
# or
./control-room-demo/backend/run.sh
# or pick a port
OPS_DESK_PORT=9000 python3 control-room-demo/backend/server.py
```

Then open:

- `http://127.0.0.1:8770/` — the full demo, now reading from SQLite
- `http://127.0.0.1:8770/api/health` — status + counts + safety posture

The original static demo is untouched and still runs without the backend:

```bash
cd control-room-demo && python3 -m http.server 8765 --bind 127.0.0.1
```

When the page is served by plain `http.server`, `/api/*` is absent, the frontend
detects this and falls back to the static JSON fixtures and embedded data — the
hackathon demo behaves exactly as before.

## API

| Method | Route                                   | Purpose                                  |
| ------ | --------------------------------------- | ---------------------------------------- |
| GET    | `/api/health`                           | status, counts, safety rails             |
| GET    | `/api/queues`                           | triage queue items                       |
| GET    | `/api/emails`                           | Email Command Center items               |
| GET    | `/api/warranty-cases`                   | warranty cases                           |
| GET    | `/api/payment-requests`                 | Stripe-shaped payment drafts             |
| GET    | `/api/agent-pulse`                      | Agent Pulse fixture                      |
| GET    | `/api/audit`                            | durable audit log (append-only)          |
| POST   | `/api/approvals/{id}/approve-draft`     | record owner approval (draft only)       |
| POST   | `/api/approvals/{id}/reject`            | record owner rejection                   |
| POST   | `/api/approvals/{id}/hold`              | keep under owner review (still audited)   |

POST body is optional JSON: `{"actor": "...", "action": "approved-draft"}`.
Every decision updates the item's `status` and appends one audit row. The
response includes an `adapter_result` proving nothing executed:

```json
{ "mode": "fixture", "executed": false, "live_connectors": false, "external_id": null }
```

## Tests

```bash
python3 control-room-demo/backend/test_backend.py
```

The suite proves seeding is correct & idempotent, the full HTTP surface works,
and — critically — that an approval **succeeds with all sockets blocked**, i.e.
it makes no network/external call.

## Files

- `db.py` — schema, idempotent seeding, read queries, `apply_decision`.
- `server.py` — `http.server` API + static file serving (127.0.0.1 only).
- `test_backend.py` — `unittest` suite (no external calls).
- `ops_desk.db` — generated SQLite file (gitignored).

## Not in this phase

No live connectors, credentials, or network calls. Stripe/Ads/email/Woo/
shipping/cron remain fixture/dry-run only and owner-gated, per
`../../CLAUDE_CODE_LIVE_INTEGRATION_BACKLOG.md` (Phases 2+).
