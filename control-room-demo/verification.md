# Control Room Demo Verification

Verified: 2026-06-28 02:53 PDT after interrupted `/goal` sprint resumed.

## Scope verified

- Static local demo: `control-room-demo/index.html`
- Frontend logic: `control-room-demo/app.js`
- Styles: `control-room-demo/styles.css`
- Fixture data under `control-room-demo/data/`
- Email Command Center
- Agent Pulse
- Warranty Command Center
- Payment/parts approval rail
- Browser-local audit behavior

## Server

Restarted local static server cleanly after a stale Python HTTP server returned an empty curl response.

Current server:

- URL: `http://127.0.0.1:8765/`
- Session: `proc_4bc3d95c9b53`
- PID: `84517`
- Command: `python3 -m http.server 8765 --bind 127.0.0.1`

HTTP health check returned:

- `HTTP/1.0 200 OK`
- `Content-type: text/html`
- `Content-Length: 33342`

## Automated checks

Command run from `control-room-demo/`:

```bash
for f in data/*.json; do python3 -m json.tool "$f" >/dev/null; done
node --check app.js
```

Result:

- `json_files_ok=7`
- `node_check_ok=app.js`

Workspace text scan:

- `text_files_checked 55`
- `secret_or_pii_hits none`

## Browser smoke check

Browser loaded `http://127.0.0.1:8765/#Overview`.

Observed tabs:

- Overview
- Email 4
- Triage 4
- Warranty 4
- Payments 3
- Audit

Email Command Center check:

- Email tab opens
- 4 fake/redacted email cards render
- `Warranty follow-up needs service recovery` opens
- draft-only approval rail works locally
- disabled live email controls render
- approving draft only appends local audit row saying no email was sent or marked read

Agent Pulse check:

- Next Command Brief: `07:30 PT`
- Quiet watchdogs: `8`
- Owner approvals: `3`
- Stale theses: `5`
- Schedule cards: `4`
- Safety rails: `6`

Safety controls observed:

- 16 disabled live-action buttons after reset/interaction flow
- `Live actions OFF` visible
- `Proposal only — no cron changed` visible
- browser-local audit row appears after approval click

## Visual check

Browser visual inspection shows the current light dashboard is recordable:

- header and top safety pills are readable
- Email tab exists in the main nav
- Agent Pulse section is visible and clear on Overview
- KPI cards, risk mix, approval funnel, needs-attention cards, and safety rails are laid out cleanly
- no major layout breakage observed

## Safety boundary

Verified demo remains fixture-only and local-only.

No live systems touched:

- no email sent
- no email marked read/moved/deleted
- no WooCommerce update
- no shipping label booked
- no supplier/customer portal action
- no payment link created
- no card/customer charged
- no refund/replacement processed
- no parts/vendor purchase
- no cron mutation
- no Telegram target touched
- no trading/brokerage action
- no public X/Discord/Typeform post


## Network access verification — Tailscale/home LAN

Verified: 2026-06-28 PDT.

Created launchers:

- `serve-network.sh` — supports `MODE=tailscale`, `MODE=lan`, and `MODE=all`.
- `serve-tailscale.sh` — safe wrapper for tailnet-only mode.

Running listeners verified:

- `127.0.0.1:8765` — local-only server
- `<tailscale-ip>:8765` — Tailscale/tailnet server (real tailnet IP redacted)
- `<lan-ip>:8765` — home-LAN server (real LAN IP redacted)

HTTP checks returned `HTTP/1.0 200 OK` for:

- `http://<tailscale-ip>:8765/`
- `http://<lan-ip>:8765/`

Browser loaded the Tailscale URL and confirmed:

- title: `Toiletland × Hermes · Autonomous Ops Desk`
- tabs: Overview, Email 4, Triage 4, Warranty 4, Payments 3, Audit
- Email cards: 4
- Agent Pulse schedule cards: 4

Security posture:

- default remote mode binds to the Tailscale IP only
- home-LAN mode binds to the detected LAN IP only
- `0.0.0.0` is not used unless explicitly requested with `MODE=all`
