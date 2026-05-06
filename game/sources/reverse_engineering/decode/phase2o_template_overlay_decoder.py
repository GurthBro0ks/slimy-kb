#!/usr/bin/env python3
"""Phase 2O redacted template overlay decoder.

Uses the Phase 2L phrase-local gap ledger to render redacted handler overlays:
phrase IDs, known/unknown/conflicting local gap counts, unresolved span lengths,
and input hashes. It does not emit full decoded Lua source.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from phase2l_standard_phrase_gap_audit import (
    PHRASES,
    decoded_alnum_positions,
    display_bytes,
    find_all,
    phrase_plain_alnum_offsets,
    phrase_skeleton,
)


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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_context_index(phrase_proof: Path) -> dict[tuple[str, str, str, str], dict[str, str]]:
    summary = phrase_proof / "context_gap_summary.tsv"
    if not summary.is_file():
        raise RuntimeError(f"missing context summary: {summary}")
    return {
        (row["phrase_id"], row["left_plain"], row["right_plain"], row["raw_gap_display"]): row
        for row in read_tsv(summary)
    }


def select_non_overlapping(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    accepted: list[dict[str, object]] = []
    occupied: set[int] = set()
    for occ in sorted(occurrences, key=lambda row: (int(row["start"]), -(int(row["end"]) - int(row["start"])), str(row["phrase_id"]))):
        span = set(range(int(occ["start"]), int(occ["end"])))
        if occupied & span:
            continue
        accepted.append(occ)
        occupied.update(span)
    return sorted(accepted, key=lambda row: (int(row["start"]), int(row["end"]), str(row["phrase_id"])))


def gap_statuses(raw: bytes, raw_phrase_offsets: list[int], phrase: dict[str, object], context_index: dict[tuple[str, str, str, str], dict[str, str]]) -> list[str]:
    plaintext = str(phrase["plaintext"])
    plain_offsets = list(phrase["plain_offsets"])
    statuses = []
    for gap_idx in range(len(raw_phrase_offsets) - 1):
        raw_gap = raw[raw_phrase_offsets[gap_idx] + 1 : raw_phrase_offsets[gap_idx + 1]]
        plain_gap = plaintext[plain_offsets[gap_idx] + 1 : plain_offsets[gap_idx + 1]]
        if not raw_gap and not plain_gap:
            continue
        key = (
            str(phrase["phrase_id"]),
            plaintext[plain_offsets[gap_idx]],
            plaintext[plain_offsets[gap_idx + 1]],
            display_bytes(raw_gap),
        )
        row = context_index.get(key)
        if row is None:
            statuses.append("unknown")
        elif int(row["candidate_count"]) == 1:
            statuses.append("known")
        else:
            statuses.append("conflict")
    return statuses


def render_overlay(skeleton_len: int, occurrences: list[dict[str, object]]) -> str:
    parts = []
    cursor = 0
    for occ in occurrences:
        start = int(occ["start"])
        end = int(occ["end"])
        if start > cursor:
            parts.append(f"<unresolved_alnum:{start - cursor}>")
        parts.append(
            "<{phrase_id} known_gaps={known_gaps} unknown_gaps={unknown_gaps} conflict_gaps={conflict_gaps}>".format(
                **occ
            )
        )
        cursor = end
    if cursor < skeleton_len:
        parts.append(f"<unresolved_alnum:{skeleton_len - cursor}>")
    return " ".join(parts)


def run(input_proof: Path, phrase_proof: Path, output_root: Path) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    context_index = load_context_index(phrase_proof)
    phrase_defs = [
        {
            "phrase_id": phrase_id,
            "plaintext": plaintext,
            "skeleton": phrase_skeleton(plaintext),
            "plain_offsets": phrase_plain_alnum_offsets(plaintext),
        }
        for phrase_id, plaintext in PHRASES
    ]

    out_dir = output_root / f"proof_snail_phase2o_template_overlay_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    views_dir = out_dir / "redacted_overlays"
    views_dir.mkdir(parents=True, exist_ok=False)

    input_rows = []
    occurrence_rows = []
    unresolved_rows = []
    known_gap_rows = 0
    unknown_gap_rows = 0
    conflict_gap_rows = 0

    for path in sorted(originals.glob("*.luac")):
        raw = body(path)
        skeleton, raw_offsets = decoded_alnum_positions(raw)
        input_rows.append({"file": path.name, "size": path.stat().st_size, "sha256": sha256(path), "skeleton_len": len(skeleton)})

        found = []
        for phrase in phrase_defs:
            phrase_len = len(str(phrase["skeleton"]))
            for start in find_all(skeleton, str(phrase["skeleton"])):
                raw_phrase_offsets = raw_offsets[start : start + phrase_len]
                statuses = gap_statuses(raw, raw_phrase_offsets, phrase, context_index)
                found.append(
                    {
                        "file": path.name,
                        "phrase_id": phrase["phrase_id"],
                        "start": start,
                        "end": start + phrase_len,
                        "raw_start": raw_phrase_offsets[0],
                        "raw_end": raw_phrase_offsets[-1],
                        "known_gaps": statuses.count("known"),
                        "unknown_gaps": statuses.count("unknown"),
                        "conflict_gaps": statuses.count("conflict"),
                    }
                )

        selected = select_non_overlapping(found)
        cursor = 0
        for occ in selected:
            start = int(occ["start"])
            if start > cursor:
                unresolved_rows.append({"file": path.name, "start": cursor, "end": start, "alnum_len": start - cursor})
            cursor = int(occ["end"])
            known_gap_rows += int(occ["known_gaps"])
            unknown_gap_rows += int(occ["unknown_gaps"])
            conflict_gap_rows += int(occ["conflict_gaps"])
        if cursor < len(skeleton):
            unresolved_rows.append({"file": path.name, "start": cursor, "end": len(skeleton), "alnum_len": len(skeleton) - cursor})

        occurrence_rows.extend(selected)
        (views_dir / f"{path.name}.overlay.txt").write_text(render_overlay(len(skeleton), selected) + "\n", encoding="utf-8")

    write_tsv(out_dir / "input_inventory.tsv", input_rows, ["file", "size", "sha256", "skeleton_len"])
    write_tsv(
        out_dir / "overlay_occurrences.tsv",
        occurrence_rows,
        ["file", "phrase_id", "start", "end", "raw_start", "raw_end", "known_gaps", "unknown_gaps", "conflict_gaps"],
    )
    write_tsv(out_dir / "unresolved_spans.tsv", unresolved_rows, ["file", "start", "end", "alnum_len"])

    manifest = {
        "phase": "2O",
        "input_proof": str(input_proof),
        "phrase_proof": str(phrase_proof),
        "result": {
            "handlers_scanned": len(input_rows),
            "selected_phrase_occurrences": len(occurrence_rows),
            "unresolved_spans": len(unresolved_rows),
            "known_gap_rows": known_gap_rows,
            "unknown_gap_rows": unknown_gap_rows,
            "conflict_gap_rows": conflict_gap_rows,
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2O Template Overlay Result",
                "",
                f"Input proof: `{input_proof}`",
                f"Phrase proof: `{phrase_proof}`",
                "",
                "## Result",
                "",
                f"- handlers scanned: {len(input_rows)}",
                f"- selected phrase occurrences: {len(occurrence_rows)}",
                f"- unresolved spans: {len(unresolved_rows)}",
                f"- known gap rows: {known_gap_rows}",
                f"- unknown gap rows: {unknown_gap_rows}",
                f"- conflict gap rows: {conflict_gap_rows}",
                "- solved: false",
                "",
                "Redacted overlays contain only phrase IDs, local gap status counts, and unresolved alphanumeric lengths.",
                "They are not source reconstruction.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Render redacted template overlays from external handler originals.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--phrase-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.input_proof, args.phrase_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
