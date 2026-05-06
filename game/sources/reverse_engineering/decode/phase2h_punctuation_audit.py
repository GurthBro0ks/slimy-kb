#!/usr/bin/env python3
"""Read-only punctuation/conflict audit for Phase 2H.

This is intentionally conservative. It does not rewrite originals and does not
claim a solved punctuation table. It compares short, anchored encrypted spans
against expected Lua readability anchors and emits evidence rows plus conflicts.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ALNUM_MAPPING = {
    "a": "v",
    "c": "0",
    "e": "k",
    "f": "e",
    "g": "a",
    "i": "W",
    "j": "P",
    "k": "u",
    "l": "w",
    "m": "N",
    "n": "z",
    "p": "t",
    "q": "q",
    "s": "5",
    "t": "2",
    "u": "f",
    "v": "d",
    "x": "b",
    "y": "m",
    "z": "h",
    "w": "K",
    "b": "Q",
    "d": "T",
    "r": "H",
    "A": "r",
    "B": "x",
    "C": "I",
    "E": "C",
    "F": "o",
    "I": "R",
    "J": "3",
    "L": "j",
    "N": "D",
    "O": "A",
    "P": "E",
    "Q": "G",
    "R": "O",
    "T": "s",
    "V": "y",
    "W": "l",
    "Z": "U",
    "H": "Y",
    "S": "K",
    "0": "4",
    "1": "S",
    "2": "1",
    "3": "p",
    "4": "i",
    "5": "g",
    "7": "n",
    "8": "c",
    "9": "M",
    "6": "6",
}


ANCHORS = [
    {
        "id": "group_rank_return_prefix",
        "file": "game_cmd_misc__msg_group_rank.luac",
        "marker": "AfpkA7(uk78p4F7 W38|_(=*)Ig7e9_TfpIg7eC7uF#IOmS",
        "plaintext": "return function(lpc)\n    RankM.setRankInfo(RANK",
        "note": "Known handler body prefix before constant separator drift.",
    },
    {
        "id": "arena_top_event_prefix",
        "file": "game_cmd_misc__msg_arena_top_query.luac",
        "marker": "Paf7p95A;u4Af+faf7p:OIPmO",
        "plaintext": "EventMgr.fire_event(ARENA",
        "note": "Known event dispatch prefix.",
    },
    {
        "id": "top_rank_setmyrank_prefix",
        "file": "game_cmd_misc__msg_top_rank.luac",
        "marker": "dF39-Tfp9VIg7e:W38-4v)*W38 Ag7e",
        "plaintext": "TopM.setMyRank(lpc.id, lpc.rank",
        "note": "Known top-rank update prefix.",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_body(path: Path) -> str:
    data = path.read_bytes()
    if data[:3] == b"\x14\x15\x16":
        data = data[3:]
    return data.decode("latin-1")


def display_char(ch: str) -> str:
    if ch == " ":
        return "<space>"
    if ch == "\n":
        return "\\n"
    if ch == "\r":
        return "\\r"
    if ch == "\t":
        return "\\t"
    return ch


def audit_anchor(originals: Path, anchor: dict[str, str]) -> list[dict[str, str | int]]:
    path = originals / anchor["file"]
    body = read_body(path)
    marker = anchor["marker"]
    start = body.find(marker)
    if start < 0:
        raise RuntimeError(f"marker not found for {anchor['id']} in {path}")

    plaintext = anchor["plaintext"]
    encrypted_span = body[start : start + min(len(marker), len(plaintext))]
    rows: list[dict[str, str | int]] = []
    for idx, (enc, plain) in enumerate(zip(encrypted_span, plaintext)):
        kind = "punct_candidate"
        expected = ""
        if enc in ALNUM_MAPPING:
            expected = ALNUM_MAPPING[enc]
            kind = "alnum_match" if expected == plain else "alnum_conflict"
        elif enc == plain:
            kind = "literal_match"

        rows.append(
            {
                "anchor_id": anchor["id"],
                "file": anchor["file"],
                "offset": start + idx,
                "enc": display_char(enc),
                "enc_hex": f"0x{ord(enc):02x}",
                "plain": display_char(plain),
                "plain_hex": f"0x{ord(plain):02x}",
                "known_alnum_plain": expected,
                "kind": kind,
                "note": anchor["note"],
            }
        )
    return rows


def write_tsv(path: Path, rows: list[dict[str, str | int]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(proof_dir: Path, output_root: Path) -> Path:
    originals = proof_dir / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    out_dir = output_root / f"proof_snail_phase2h_punctuation_audit_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=False)

    all_rows: list[dict[str, str | int]] = []
    for anchor in ANCHORS:
        all_rows.extend(audit_anchor(originals, anchor))

    grouped: dict[str, set[str]] = defaultdict(set)
    evidence_counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in all_rows:
        if row["kind"] == "punct_candidate":
            enc = str(row["enc"])
            plain = str(row["plain"])
            grouped[enc].add(plain)
            evidence_counts[(enc, plain)] += 1

    candidates = []
    conflicts = []
    for enc in sorted(grouped):
        plains = sorted(grouped[enc])
        row = {
            "enc": enc,
            "plain_candidates": json.dumps(plains, ensure_ascii=True),
            "candidate_count": len(plains),
            "evidence_count": sum(evidence_counts[(enc, p)] for p in plains),
        }
        candidates.append(row)
        if len(plains) > 1:
            conflicts.append(row)

    alnum_conflicts = [row for row in all_rows if row["kind"] == "alnum_conflict"]

    write_tsv(
        out_dir / "anchor_evidence.tsv",
        all_rows,
        [
            "anchor_id",
            "file",
            "offset",
            "enc",
            "enc_hex",
            "plain",
            "plain_hex",
            "known_alnum_plain",
            "kind",
            "note",
        ],
    )
    write_tsv(out_dir / "punctuation_candidates.tsv", candidates, ["enc", "plain_candidates", "candidate_count", "evidence_count"])
    write_tsv(out_dir / "punctuation_conflicts.tsv", conflicts, ["enc", "plain_candidates", "candidate_count", "evidence_count"])
    write_tsv(
        out_dir / "alnum_conflicts.tsv",
        alnum_conflicts,
        [
            "anchor_id",
            "file",
            "offset",
            "enc",
            "enc_hex",
            "plain",
            "plain_hex",
            "known_alnum_plain",
            "kind",
            "note",
        ],
    )

    manifest = {
        "phase": "2H",
        "proof_dir": str(proof_dir),
        "anchors": ANCHORS,
        "inputs": {
            str(path.relative_to(proof_dir)): {
                "sha256": sha256(path),
                "size": path.stat().st_size,
                "mode": oct(path.stat().st_mode & 0o777),
            }
            for path in sorted(originals.glob("*.luac"))
        },
        "result": {
            "anchor_rows": len(all_rows),
            "punctuation_candidates": len(candidates),
            "punctuation_conflicts": len(conflicts),
            "alnum_conflicts": len(alnum_conflicts),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    summary = [
        "# Phase 2H Punctuation Audit Result",
        "",
        f"Input proof: `{proof_dir}`",
        "",
        "## Result",
        "",
        f"- anchor rows: {len(all_rows)}",
        f"- punctuation candidates: {len(candidates)}",
        f"- punctuation conflicts: {len(conflicts)}",
        f"- alphanumeric conflicts: {len(alnum_conflicts)}",
        "- solved: false",
        "",
        "Conflicts mean the current anchors/table do not support a single safe punctuation mapping.",
        "Treat this as a fail-closed audit, not as a decoder.",
    ]
    (out_dir / "RESULT.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 2H read-only punctuation conflict audit.")
    parser.add_argument("--proof-dir", required=True, type=Path, help="Phase 2G proof directory containing originals/")
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    out_dir = run(args.proof_dir, args.output_root)
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
