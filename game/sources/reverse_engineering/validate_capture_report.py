#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


RISK_PATTERNS = [
    ("authorization_header", re.compile(r"\bauthorization\s*:\s*(bearer|basic|token)\s+[A-Za-z0-9._~+/=-]{8,}", re.I)),
    ("bearer_token", re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{20,}", re.I)),
    ("cookie_header", re.compile(r"\bcookie\s*:\s*[^<\n]{12,}", re.I)),
    ("set_cookie_header", re.compile(r"\bset-cookie\s*:\s*[^<\n]{12,}", re.I)),
    ("jwt_like_value", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}\b")),
    ("long_hex_secret", re.compile(r"\b(?:token|session|secret|auth|device|account)[-_ ]?(?:id|key|token|secret)?\s*[:=]\s*[A-Fa-f0-9]{24,}\b", re.I)),
    ("raw_request_marker", re.compile(r"^\s*(GET|POST|PUT|PATCH|DELETE)\s+/\S+\s+HTTP/\d(?:\.\d)?\s*$", re.I | re.M)),
    ("raw_json_secret_field", re.compile(r'"(?:token|access_token|refresh_token|session|cookie|authorization|device_id|account_id)"\s*:\s*"[^"<]{6,}"', re.I)),
]

ALLOWLIST_PATTERNS = [
    re.compile(r"`?<fill>`?"),
    re.compile(r"`?<sanitized>`?"),
    re.compile(r"`?<ignored/private path only>`?"),
    re.compile(r"`?<hash only>`?"),
    re.compile(r"no tokens?\.?$", re.I),
    re.compile(r"no cookies?\.?$", re.I),
    re.compile(r"no auth headers?\.?$", re.I),
    re.compile(r"no device ids?\.?$", re.I),
    re.compile(r"no account ids?\.?$", re.I),
]


def is_allowlisted(line: str) -> bool:
    stripped = line.strip()
    return any(pattern.search(stripped) for pattern in ALLOWLIST_PATTERNS)


def scan_text(text: str) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        if is_allowlisted(line):
            continue
        for name, pattern in RISK_PATTERNS:
            if pattern.search(line):
                findings.append((idx, name, line.strip()))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate sanitized Phase 3 capture reports before commit.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown/text report paths to validate")
    args = parser.parse_args()

    failed = False
    for path in args.paths:
        text = path.read_text(encoding="utf-8")
        findings = scan_text(text)
        if findings:
            failed = True
            print(f"FAIL {path}")
            for line_no, name, line in findings:
                print(f"  line {line_no}: {name}: {line[:160]}")
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
