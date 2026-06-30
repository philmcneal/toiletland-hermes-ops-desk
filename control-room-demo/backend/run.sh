#!/usr/bin/env bash
# Start the Phase 1 local backend (Python stdlib http.server + SQLite).
# Fixture-only. Binds to 127.0.0.1. No live connectors, no network egress.
#
#   ./control-room-demo/backend/run.sh
#   OPS_DESK_PORT=9000 ./control-room-demo/backend/run.sh
#
# Then open http://127.0.0.1:${OPS_DESK_PORT:-8770}/ for the demo
# and        http://127.0.0.1:${OPS_DESK_PORT:-8770}/api/health for status.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export OPS_DESK_HOST="${OPS_DESK_HOST:-127.0.0.1}"
export OPS_DESK_PORT="${OPS_DESK_PORT:-8770}"
exec python3 "$HERE/server.py"
