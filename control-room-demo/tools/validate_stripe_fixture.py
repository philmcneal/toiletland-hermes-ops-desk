#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'data' / 'payment-requests.json'
payments = json.loads(path.read_text())
count = 0
total_cents = 0
for item in payments:
    skill = item.get('stripe_skill') or {}
    if not skill:
        raise SystemExit(f"MISSING stripe_skill for {item.get('id')}")
    if skill.get('mode') != 'test_fixture_no_api_call':
        raise SystemExit(f"UNSAFE mode for {item['id']}: {skill.get('mode')}")
    if not str(skill.get('idempotency_key', '')).endswith('owner-approval-required'):
        raise SystemExit(f"MISSING owner approval idempotency key for {item['id']}")
    payload = skill.get('payload') or {}
    lines = payload.get('line_items') or []
    line_total = sum(int(line['unit_amount']) * int(line.get('quantity', 1)) for line in lines)
    if line_total != int(skill.get('amount_cents', -1)):
        raise SystemExit(f"AMOUNT MISMATCH {item['id']}: lines={line_total} skill={skill.get('amount_cents')}")
    guardrails = ' | '.join(item.get('guardrails') or [])
    if 'No' not in guardrails or 'live API disabled' not in guardrails:
        raise SystemExit(f"GUARDRAILS TOO WEAK for {item['id']}")
    count += 1
    total_cents += line_total
print(f"STRIPE_DRY_RUN_OK payloads={count} total_under_review=CAD {total_cents/100:.2f} live_api_calls=0")
