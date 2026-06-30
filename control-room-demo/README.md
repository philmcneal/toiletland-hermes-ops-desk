# Control Room Demo

Local demo for **Toiletland × Hermes — Autonomous Ops Desk**.

This UI demonstrates a safety-first SMB operating desk: queue triage, email command center, warranty work, payment/parts approval rail, growth drafts, and audit trail.

## Run static fixture mode

```bash
cd control-room-demo
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/>.

Static mode uses redacted JSON fixtures and browser-local state only.

## Run with local backend + SQLite audit trail

From the repository root:

```bash
python3 control-room-demo/backend/server.py
```

Open:

- <http://127.0.0.1:8770/> — demo UI
- <http://127.0.0.1:8770/api/health> — status/counts/safety posture

The frontend auto-detects the backend. When `/api/*` is present, it reads from SQLite; otherwise it falls back to static fixtures.

## What is in the demo

- **Overview:** KPI strip, risk mix, approval funnel, needs-attention queue, and safety boundaries.
- **Email Command Center:** redacted inbox triage, suggested Hermes skill, draft-only reply, owner gate, proof chips, disabled live controls.
- **Triage lane:** Earn / Operate / Spend / Warranty cards with source snippets, reasoning, proposed action, proof chips, and approval rail.
- **Warranty lane:** case queue, symptom → repair path, parts/refurb gate, supplier/RMA gate, bench-verification reminders, owner approval rail.
- **Payments lane:** Stripe-friendly payment/parts approval rail plus Google Ads dry-run growth loop. No live payment or ads API.
- **Agent Pulse:** sanitized scheduled-ops fixture with watchdog/briefing/safety cards. No live cron mutation.
- **Audit:** durable audit log when served by the backend.

## Safety boundaries

Allowed in demo:

- classify redacted/fixture messages
- route to the right operational lane
- draft owner-facing/customer-facing copy
- show owner approval gates
- append local audit rows

Disabled / not performed:

- no SMTP send
- no IMAP mark-read/move/delete
- no WooCommerce update
- no shipping label
- no refund/replacement
- no payment link or charge
- no Google Ads publish/spend change

For read-only live ingestion details, see the repository root `README_LIVE_READONLY.md`.
