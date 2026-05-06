#!/usr/bin/env python3
"""Read-only Phase 2B cipher audit scaffold."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PROOF_DIR = Path("/tmp/proof_snail_protocol_reset_20260426T170226Z")
REQUIRED_ORIGINALS = (
    "list.luac",
    "msg_group_rank.luac",
    "msg_arena_top_query.luac",
)
UNMAPPED_ALNUMS = set("6HSbdr")
TARGET_KEYWORDS = ("group", "rank", "arena", "top", "score", "myrank", "group_war", "club")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_read_only(path: Path) -> bool:
    mode = stat.S_IMODE(path.stat().st_mode)
    return mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0


def printable_runs(data: bytes, min_len: int = 4) -> list[str]:
    runs: list[str] = []
    current: list[str] = []
    for byte in data:
        if byte in (9, 10, 13) or 32 <= byte <= 126:
            current.append(chr(byte))
        else:
            if len(current) >= min_len:
                runs.append("".join(current))
            current = []
    if len(current) >= min_len:
        runs.append("".join(current))
    return runs


def load_protocol_candidates(proof_dir: Path, original_strings: list[str]) -> list[str]:
    candidate = proof_dir / "out" / "protocol_messages_candidate.txt"
    if candidate.exists():
        return [line.strip() for line in candidate.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]

    quoted: list[str] = []
    for text in original_strings:
        quoted.extend(match.group(1) for match in re.finditer(r'"([^"]+)"', text))
        quoted.extend(match.group(1) for match in re.finditer(r"'([^']+)'", text))
    return quoted or original_strings


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def audit(proof_dir: Path, output_root: Path) -> Path:
    originals_dir = proof_dir / "originals"
    if not originals_dir.is_dir():
        raise FileNotFoundError(f"missing originals directory: {originals_dir}")

    original_paths = [originals_dir / name for name in REQUIRED_ORIGINALS]
    missing = [str(path) for path in original_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing required originals: " + ", ".join(missing))

    writable = [str(path) for path in original_paths if not is_read_only(path)]
    if writable:
        raise PermissionError("originals must be read-only: " + ", ".join(writable))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = output_root / f"proof_snail_phase2b_cipher_audit_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    hashes: list[str] = []
    all_strings: list[str] = []
    for path in original_paths:
        hashes.append(f"{sha256_file(path)}  {path}")
        all_strings.extend(printable_runs(path.read_bytes()))

    protocol_candidates = load_protocol_candidates(proof_dir, all_strings)
    unresolved_counts = Counter(char for text in protocol_candidates for char in text if char in UNMAPPED_ALNUMS)
    punctuation_counts = Counter(
        char
        for text in protocol_candidates
        for char in text
        if 32 <= ord(char) <= 126 and not char.isalnum() and char not in "@._"
    )

    target_samples = [
        text for text in protocol_candidates
        if any(keyword in text.lower() for keyword in TARGET_KEYWORDS)
    ][:80]

    write_lines(out_dir / "hashes.sha256", hashes)
    write_lines(out_dir / "observed_unmapped.txt", [f"{key}\t{unresolved_counts[key]}" for key in sorted(UNMAPPED_ALNUMS)])
    write_lines(out_dir / "punctuation_counts.txt", [f"{key}\t{count}" for key, count in punctuation_counts.most_common()])
    write_lines(out_dir / "string_samples.txt", protocol_candidates[:120])
    write_lines(out_dir / "rank_group_target_samples.txt", target_samples)

    result = [
        "# Phase 2B Cipher Audit Result",
        "",
        "Status: AUDIT_ONLY",
        "",
        f"Proof input: `{proof_dir}`",
        f"Originals audited: {len(original_paths)}",
        f"Protocol/string candidates reviewed: {len(protocol_candidates)}",
        "",
        "This audit does not solve, guess, or normalize cipher mappings.",
        "It only verifies read-only inputs and records current unresolved-character evidence.",
    ]
    write_lines(out_dir / "RESULT.md", result)
    return out_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a read-only Phase 2B cipher audit.")
    parser.add_argument("--proof-dir", type=Path, default=DEFAULT_PROOF_DIR, help="External proof directory containing originals/.")
    parser.add_argument("--output-root", type=Path, default=Path("/tmp"), help="Directory where the timestamped audit proof will be written.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        out_dir = audit(args.proof_dir, args.output_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
