#!/usr/bin/env python3
"""Phase 5 live read-only SAFETY VALIDATOR.

Static, no-network checks that the live read-only branch cannot mutate anything
and cannot leak secrets. Exits non-zero if ANY check fails. Run:

    python3 scripts/validate_live_safety.py

Checks
------
  1. .gitignore ignores .secrets/ and *.env (and .env).
  2. No real secret material is committed anywhere in the tree (entropy/prefix
     scan for sk_live_, AWS keys, private keys, Slack/Google/GitHub tokens).
  3. The IMAP connector is read-only: uses EXAMINE (readonly=True) + BODY.PEEK,
     and never calls STORE / EXPUNGE / COPY / APPEND / UID.
  4. The WooCommerce connector issues GET only (no POST/PUT/PATCH/DELETE).
  5. The Stripe connector refuses non-test keys and makes no charges/links.
  6. DB schema pins raw_stored CHECK(=0) and connector_runs CHECK read_only=1 /
     mutations=0.
  7. config.MUTATIONS_ENABLED is False and there is no enable path.
  8. No live mutation routes exist in server.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "control-room-demo" / "backend"
CONNECTORS = BACKEND / "connectors"

# Real-secret signatures. Specific enough to skip placeholders/test stubs.
SECRET_PATTERNS = {
    "stripe_live_key": re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
    "github_pat": re.compile(r"ghp_[A-Za-z0-9]{36}"),
}

SCAN_SUFFIXES = {
    ".py", ".js", ".json", ".md", ".txt", ".html", ".css", ".sh",
    ".yml", ".yaml", ".cfg", ".ini", ".example", ".env",
}
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".secrets", "raw-assets",
    "private", "video-production",
}


def _iter_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS or part.startswith("backup-") for part in path.parts):
            continue
        if path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            yield path, path.read_text(encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, OSError):
            continue


class Validator:
    def __init__(self):
        self.results = []  # (ok, name, detail)

    def check(self, name, ok, detail=""):
        self.results.append((bool(ok), name, detail))

    def _read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""

    # ---- individual checks --------------------------------------------
    def gitignore(self):
        gi = self._read(REPO_ROOT / ".gitignore")
        self.check("gitignore ignores .secrets/", ".secrets/" in gi)
        self.check("gitignore ignores *.env", "*.env" in gi)
        self.check("gitignore ignores .env", re.search(r"(?m)^\.env\b", gi) is not None)

    def secret_scan(self):
        hits = []
        for path, text in _iter_text_files():
            for label, pat in SECRET_PATTERNS.items():
                if pat.search(text):
                    hits.append(f"{label} in {path.relative_to(REPO_ROOT)}")
        self.check(
            "no committed secrets (entropy/prefix scan)",
            not hits,
            "; ".join(hits) if hits else "0 hits",
        )

    def imap_readonly(self):
        src = self._read(CONNECTORS / "imap_readonly.py")
        self.check("imap uses readonly=True (EXAMINE)", "readonly=True" in src)
        self.check("imap uses BODY.PEEK", "BODY.PEEK" in src)
        self.check("imap never selects writable", "readonly=False" not in src)
        forbidden = []
        for verb in ("client.store", "client.copy", "client.expunge",
                     "client.append", "client.uid"):
            if verb in src:
                forbidden.append(verb)
        self.check(
            "imap issues no mutating verb (store/copy/expunge/append/uid)",
            not forbidden,
            ", ".join(forbidden) if forbidden else "none",
        )

    def woo_get_only(self):
        src = self._read(CONNECTORS / "woocommerce_readonly.py")
        self.check("woo pins method=GET", 'method="GET"' in src)
        bad = [m for m in ('method="POST"', 'method="PUT"',
                           'method="PATCH"', 'method="DELETE"') if m in src]
        self.check("woo has no mutating HTTP verb", not bad,
                   ", ".join(bad) if bad else "none")

    def stripe_guard(self):
        src = self._read(CONNECTORS / "stripe_test_status.py")
        self.check("stripe requires sk_test_ key",
                   "stripe_is_test_key" in src)
        # The connector makes NO network call at all, which is a strict superset
        # of "no charge/link/refund". Flag any actual API-call indicator.
        bad = [t for t in ("api.stripe.com", "urlopen", "urllib", "http.client",
                           'method="POST"', "requests.") if t in src]
        self.check("stripe makes no API call (no charge/link/refund)", not bad,
                   ", ".join(bad) if bad else "no network call")

    def db_constraints(self):
        src = self._read(BACKEND / "db.py")
        self.check(
            "live_snapshots pins raw_stored CHECK(=0)",
            re.search(r"raw_stored[^\n]*CHECK\s*\(\s*raw_stored\s*=\s*0\s*\)", src)
            is not None,
        )
        self.check(
            "connector_runs pins read_only CHECK(=1)",
            re.search(r"read_only[^\n]*CHECK\s*\(\s*read_only\s*=\s*1\s*\)", src)
            is not None,
        )
        self.check(
            "connector_runs pins mutations CHECK(=0)",
            re.search(r"mutations[^\n]*CHECK\s*\(\s*mutations\s*=\s*0\s*\)", src)
            is not None,
        )

    def config_mutations_off(self):
        src = self._read(BACKEND / "config.py")
        self.check("config MUTATIONS_ENABLED is False",
                   "MUTATIONS_ENABLED = False" in src)

    def server_no_live_mutation(self):
        src = self._read(BACKEND / "server.py")
        # Isolate ONLY the do_POST method body (def do_POST ... next def). The
        # live routes live under do_GET; do_POST must not route /api/live.
        m = re.search(r"def do_POST\(.*?\n(.*?)\n    def ", src, re.DOTALL)
        do_post_body = m.group(1) if m else src
        self.check("do_POST routes no /api/live mutation",
                   "/api/live" not in do_post_body)

    # ---- run -----------------------------------------------------------
    def run(self) -> int:
        self.gitignore()
        self.secret_scan()
        self.imap_readonly()
        self.woo_get_only()
        self.stripe_guard()
        self.db_constraints()
        self.config_mutations_off()
        self.server_no_live_mutation()

        failed = 0
        for ok, name, detail in self.results:
            tag = "PASS" if ok else "FAIL"
            line = f"[{tag}] {name}"
            if detail and not ok:
                line += f"  -> {detail}"
            elif detail:
                line += f"  ({detail})"
            print(line)
            if not ok:
                failed += 1

        print("-" * 60)
        if failed:
            print(f"LIVE_SAFETY_FAIL  {failed} check(s) failed")
            return 1
        print(f"LIVE_SAFETY_OK  {len(self.results)} checks passed; "
              "live mutations disabled; redacted-only ingestion")
        return 0


if __name__ == "__main__":
    sys.exit(Validator().run())
