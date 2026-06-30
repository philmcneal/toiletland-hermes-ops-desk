# Safety model

## Public claims

- The public demo uses redacted fixtures and public-masked live-readonly proof footage.
- The live-readonly branch has ingested bounded real email and WooCommerce data as redacted snapshots.
- Raw live records are not stored.
- Live mutations are disabled.

## Guardrails

- IMAP connector opens the mailbox read-only and uses peek-style fetching.
- WooCommerce connector is GET-only.
- Stripe connector accepts test-mode status proof only and refuses live keys.
- SQLite constraints enforce `raw_stored = 0`, `read_only = 1`, and `mutations = 0` for live connector rows.
- Local backend is loopback-only.
- Owner approval events are audited locally and return `executed=false`.

## What is intentionally not implemented

- Email send/mark-read/move/delete.
- WooCommerce order edits/refunds/status changes.
- Live Stripe charges/refunds/payment links.
- Google Ads spend/publish changes.
- Shipping/vendor/social automation.

Future live mutations would require explicit owner approval, test-mode/draft-mode where available, and stronger operational review.
