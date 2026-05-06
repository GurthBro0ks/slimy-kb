#!/usr/bin/env python3
"""Phase 2I raw-byte skeleton transform audit.

Aligns known handler readability anchors by proven alphanumeric skeleton only,
then records the raw encrypted byte runs between matched alphanumeric bytes.
This avoids forcing punctuation into a fake one-byte substitution table.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from phase2h_punctuation_audit import ALNUM_MAPPING


ANCHORS = [
    {
        "id": "group_rank_body",
        "file": "game_cmd_misc__msg_group_rank.luac",
        "plaintext": "return function(lpc)\n    RankM.setRankInfo(RANKID_GROUP, nil, lpc.list)\nend",
    },
    {
        "id": "arena_top_body",
        "file": "game_cmd_misc__msg_arena_top_query.luac",
        "plaintext": "return function(lpc)\n    EventMgr.fire_event(ARENATOP_QUERY, lpc)\nend",
    },
    {
        "id": "top_rank_body",
        "file": "game_cmd_misc__msg_top_rank.luac",
        "plaintext": "return function(lpc)\n    TopM.setMyRank(lpc.id, lpc.rank)\nend",
    },
    {
        "id": "week_task_rank_call",
        "file": "game_cmd_misc__msg_week_task_rank.luac",
        "plaintext": "return function(lpc)\nlocal rankId\nRankM.getIdMyTaskType(lpc.type)\nif rankId then\nRankM.setRankInfo(rankId, lpc.start, lpc.list)\nreturn\nend\nTaskM.setWeekTop(lpc.type, lpc.start, lpc.list)\nend",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def body_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:3] == b"\x14\x15\x16":
        return data[3:]
    return data


def plain_skeleton(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum())


def decoded_alnum_positions(raw: bytes) -> tuple[str, list[int]]:
    chars: list[str] = []
    offsets: list[int] = []
    for idx, b in enumerate(raw):
        ch = chr(b)
        if ch in ALNUM_MAPPING:
            chars.append(ALNUM_MAPPING[ch])
            offsets.append(idx)
        elif ch.isascii() and ch.isalnum():
            chars.append(ch)
            offsets.append(idx)
    return "".join(chars), offsets


def plain_alnum_positions(text: str) -> list[int]:
    return [idx for idx, ch in enumerate(text) if ch.isalnum()]


def display_bytes(data: bytes) -> str:
    out = []
    for b in data:
        if b == 10:
            out.append("\\n")
        elif b == 13:
            out.append("\\r")
        elif b == 9:
            out.append("\\t")
        elif 32 <= b <= 126:
            ch = chr(b)
            out.append("<space>" if ch == " " else ch)
        else:
            out.append(f"\\x{b:02x}")
    return "".join(out)


def display_text(text: str) -> str:
    return display_bytes(text.encode("utf-8"))


def audit_anchor(originals: Path, anchor: dict[str, str]) -> dict[str, object]:
    path = originals / anchor["file"]
    raw = body_bytes(path)
    decoded, raw_alnum_offsets = decoded_alnum_positions(raw)
    skeleton = plain_skeleton(anchor["plaintext"])
    start = decoded.find(skeleton)
    if start < 0:
        return {
            "anchor_id": anchor["id"],
            "file": anchor["file"],
            "skeleton_len": len(skeleton),
            "decoded_skeleton_start": -1,
            "raw_start": -1,
            "raw_end": -1,
            "status": "missing",
            "gap_rows": [],
        }

    plain_offsets = plain_alnum_positions(anchor["plaintext"])
    raw_offsets = raw_alnum_offsets[start : start + len(skeleton)]
    if len(raw_offsets) != len(plain_offsets):
        raise RuntimeError(f"offset length mismatch for {anchor['id']}")

    gap_rows = []
    for gap_idx in range(len(raw_offsets) - 1):
        raw_gap = raw[raw_offsets[gap_idx] + 1 : raw_offsets[gap_idx + 1]]
        plain_gap = anchor["plaintext"][plain_offsets[gap_idx] + 1 : plain_offsets[gap_idx + 1]]
        if not raw_gap and not plain_gap:
            continue
        gap_rows.append(
            {
                "anchor_id": anchor["id"],
                "file": anchor["file"],
                "left_plain": anchor["plaintext"][plain_offsets[gap_idx]],
                "right_plain": anchor["plaintext"][plain_offsets[gap_idx + 1]],
                "raw_start": raw_offsets[gap_idx] + 1,
                "raw_end_exclusive": raw_offsets[gap_idx + 1],
                "raw_gap_hex": raw_gap.hex(),
                "raw_gap_display": display_bytes(raw_gap),
                "plain_gap_display": display_text(plain_gap),
                "raw_gap_len": len(raw_gap),
                "plain_gap_len": len(plain_gap),
            }
        )

    return {
        "anchor_id": anchor["id"],
        "file": anchor["file"],
        "skeleton_len": len(skeleton),
        "decoded_skeleton_start": start,
        "raw_start": raw_offsets[0],
        "raw_end": raw_offsets[-1],
        "status": "found",
        "gap_rows": gap_rows,
    }


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(proof_dir: Path, output_root: Path) -> Path:
    originals = proof_dir / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    out_dir = output_root / f"proof_snail_phase2i_skeleton_transform_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    anchor_rows = []
    gap_rows = []
    for anchor in ANCHORS:
        result = audit_anchor(originals, anchor)
        anchor_rows.append({key: value for key, value in result.items() if key != "gap_rows"})
        gap_rows.extend(result["gap_rows"])

    repeated = {}
    for row in gap_rows:
        raw_gap = str(row["raw_gap_display"])
        plain_gap = str(row["plain_gap_display"])
        repeated.setdefault(raw_gap, set()).add(plain_gap)

    conflict_rows = [
        {
            "raw_gap_display": raw_gap,
            "plain_gap_candidates": json.dumps(sorted(candidates), ensure_ascii=True),
            "candidate_count": len(candidates),
        }
        for raw_gap, candidates in sorted(repeated.items())
        if len(candidates) > 1
    ]

    write_tsv(
        out_dir / "anchor_matches.tsv",
        anchor_rows,
        ["anchor_id", "file", "skeleton_len", "decoded_skeleton_start", "raw_start", "raw_end", "status"],
    )
    write_tsv(
        out_dir / "gap_evidence.tsv",
        gap_rows,
        [
            "anchor_id",
            "file",
            "left_plain",
            "right_plain",
            "raw_start",
            "raw_end_exclusive",
            "raw_gap_hex",
            "raw_gap_display",
            "plain_gap_display",
            "raw_gap_len",
            "plain_gap_len",
        ],
    )
    write_tsv(out_dir / "raw_gap_conflicts.tsv", conflict_rows, ["raw_gap_display", "plain_gap_candidates", "candidate_count"])

    manifest = {
        "phase": "2I",
        "input_proof": str(proof_dir),
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
            "anchors_found": len(anchor_rows),
            "anchors_missing": sum(1 for row in anchor_rows if row.get("status") == "missing"),
            "gap_rows": len(gap_rows),
            "raw_gap_conflicts": len(conflict_rows),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2I Skeleton Transform Audit Result",
                "",
                f"Input proof: `{proof_dir}`",
                "",
                "## Result",
                "",
                f"- anchors checked: {len(anchor_rows)}",
                f"- anchors missing: {sum(1 for row in anchor_rows if row.get('status') == 'missing')}",
                f"- gap rows: {len(gap_rows)}",
                f"- raw gap conflicts: {len(conflict_rows)}",
                "- solved: false",
                "",
                "This audit aligns by alphanumeric skeleton and records raw punctuation/control gaps.",
                "It is evidence for the transform layer, not a source decoder.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 2I raw-byte skeleton transform audit.")
    parser.add_argument("--proof-dir", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.proof_dir, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
