# Phase 5 — Live READ-ONLY Connectors

This adds a **credible, read-only** path from real business systems (email,
WooCommerce, Stripe test mode) into the local backend. It is deliberately *not*
live autonomy: nothing is ever sent, changed, charged, moved, or deleted.

> **One-line posture:** live reads in, **redacted** snapshots stored, **zero**
> mutations out. If there are no live snapshots, the static fixture demo (and the
> recorded video) are completely unchanged.

## What it is / is not

| Capability | Status |
|---|---|
| Read email headers + a peeked body preview (IMAP) | ✅ read-only |
| Read recent WooCommerce orders (GET) | ✅ read-only |
| Prove a Stripe key is test-mode | ✅ status only, no API call |
| Send / mark-read / move / delete email | ❌ never |
| Edit orders, refund, fulfil, change status | ❌ never |
| Stripe charges / Payment Links / Checkout / refunds | ❌ never |
| Google Ads / shipping / cron / social actions | ❌ never |

## Safety design (defense in depth)

1. **Secrets isolation.** Credentials live only in `.secrets/live-readonly.env`
   (git-ignored via `.secrets/` and `*.env`). `config.py` never prints, logs, or
   serializes a secret value — only presence booleans and non-secret hints
   (host, masked username).
2. **Read-only IMAP.** The mailbox is opened with `select(mailbox,
   readonly=True)` → the server runs `EXAMINE`, not `SELECT`. Bodies are fetched
   with `BODY.PEEK[...]`, so the `\Seen` flag is never set. The connector calls
   only `select`/`search`/`fetch`/`logout` — never `STORE`/`COPY`/`EXPUNGE`/
   `APPEND`/`UID`.
3. **GET-only WooCommerce.** The HTTP method is hard-pinned to `GET`; HTTPS is
   required; customer PII is never copied into a snapshot.
4. **Stripe is inert.** Only `sk_test_` keys are accepted (a live key is
   refused); the connector makes **no network call at all**.
5. **Redaction boundary.** `redaction.py` scrubs emails, phones, cards, URLs,
   IPs, postal codes, and long identifiers. `assert_no_raw()` re-checks every
   snapshot before storage and rejects any stray PII or unexpected key.
6. **Storage invariants.** `live_snapshots.raw_stored` has a SQL
   `CHECK (raw_stored = 0)`; `connector_runs` has `CHECK (read_only = 1)` and
   `CHECK (mutations = 0)`. The database itself refuses to persist raw or
   mutating rows.
7. **Explicit acknowledgement.** Persisting requires both `--write` and
   `--i-understand-read-only`. `--write` writes only to **local SQLite**, never
   to any live service.

## Setup

```bash
mkdir -p .secrets
cp live-readonly.env.example .secrets/live-readonly.env
# edit .secrets/live-readonly.env with real, read-only credentials
# set LIVE_READONLY_ENABLED=true and the connector's *_ENABLED=true
```

## Usage

```bash
# Secret-free status (config presence + DB posture). No network.
python3 control-room-demo/backend/live_ingest.py --status

# Preview only — fetch, redact, print; writes NOTHING.
python3 control-room-demo/backend/live_ingest.py email --dry-run

# Persist redacted snapshots to LOCAL SQLite (requires the ack flag).
python3 control-room-demo/backend/live_ingest.py email \
    --write --i-understand-read-only --limit 10
```

Connectors: `email` (must-have), `woocommerce`, `stripe`. Default limit is 10
and is hard-capped at 10.

## API (served by the existing local backend)

- `GET /api/live/status` — secret-free config + ingestion posture
- `GET /api/live/snapshots` — redacted snapshots (raw never stored or sent)
- `GET /api/live/connector-runs` — one row per ingest run

The frontend shows a `LIVE · READ-ONLY` badge and a small redacted-email strip
**only when** snapshot rows exist; otherwise the fixture demo is unchanged.

## Verify

```bash
python3 control-room-demo/backend/test_redaction.py
python3 control-room-demo/backend/test_live_connectors.py
python3 control-room-demo/backend/test_backend.py
python3 scripts/validate_live_safety.py
```
