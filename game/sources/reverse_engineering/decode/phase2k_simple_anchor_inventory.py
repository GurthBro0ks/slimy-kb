#!/usr/bin/env python3
"""Phase 2K simple handler anchor inventory.

Reads externally pulled small handler originals and emits sanitized structural
metadata for choosing future grammar anchors. It does not write decoded Lua.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from phase2h_punctuation_audit import ALNUM_MAPPING


TOKEN_HINTS = [
    "returnfunctionlpc",
    "RankM",
    "TopM",
    "EventMgr",
    "TaskM",
    "GroupM",
    "GroupWarM",
    "ArenaM",
    "MEuser",
    "ItemM",
    "BonusM",
    "Operationcmd",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def body(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:3] == b"\x14\x15\x16":
        return data[3:]
    return data


def decoded_alnum(raw: bytes) -> str:
    out = []
    for b in raw:
        ch = chr(b)
        if ch in ALNUM_MAPPING:
            out.append(ALNUM_MAPPING[ch])
        elif ch.isascii() and ch.isalnum():
            out.append(ch)
    return "".join(out)


def score_row(skeleton: str, size: int) -> int:
    score = 0
    if "returnfunctionlpc" in skeleton:
        score += 20
    if size <= 180:
        score += 10
    elif size <= 260:
        score += 6
    elif size <= 360:
        score += 3
    score += sum(5 for token in TOKEN_HINTS[1:] if token in skeleton)
    if len(skeleton) <= 120:
        score += 4
    return score


def run(input_proof: Path, output_root: Path, limit: int) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    out_dir = output_root / f"proof_snail_phase2k_simple_anchor_inventory_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    rows = []
    for path in sorted(originals.glob("*.luac")):
        raw = body(path)
        skeleton = decoded_alnum(raw)
        hits = [token for token in TOKEN_HINTS if token in skeleton]
        row = {
            "file": path.name,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "skeleton_len": len(skeleton),
            "has_return_function_lpc": "yes" if "returnfunctionlpc" in skeleton else "no",
            "token_hits": ",".join(hits),
            "anchor_score": score_row(skeleton, path.stat().st_size),
        }
        rows.append(row)

    rows.sort(key=lambda r: (-int(r["anchor_score"]), int(r["size"]), r["file"]))
    top_rows = rows[:limit]

    fields = ["file", "size", "sha256", "skeleton_len", "has_return_function_lpc", "token_hits", "anchor_score"]
    for name, data in [("simple_handler_inventory.tsv", rows), ("top_anchor_candidates.tsv", top_rows)]:
        with (out_dir / name).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(data)

    manifest = {
        "phase": "2K",
        "input_proof": str(input_proof),
        "result": {
            "handlers_scanned": len(rows),
            "top_limit": limit,
            "return_function_lpc_count": sum(1 for row in rows if row["has_return_function_lpc"] == "yes"),
            "scored_positive": sum(1 for row in rows if int(row["anchor_score"]) > 0),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2K Simple Anchor Inventory Result",
                "",
                f"Input proof: `{input_proof}`",
                "",
                "## Result",
                "",
                f"- handlers scanned: {len(rows)}",
                f"- return/function/lpc skeleton hits: {manifest['result']['return_function_lpc_count']}",
                f"- positive anchor scores: {manifest['result']['scored_positive']}",
                f"- top candidate limit: {limit}",
                "- solved: false",
                "",
                "This inventory is sanitized structural metadata only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory simple handler anchor candidates from external originals.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    parser.add_argument("--limit", default=80, type=int)
    args = parser.parse_args()
    print(run(args.input_proof, args.output_root, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
