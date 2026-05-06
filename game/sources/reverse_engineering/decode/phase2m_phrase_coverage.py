#!/usr/bin/env python3
"""Phase 2M phrase-template coverage pass.

Uses the standard phrase set from Phase 2L to measure how much of each small
handler's alphanumeric skeleton is covered by known phrase templates. It writes
redacted external views only; no full decoded source is committed.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from phase2h_punctuation_audit import ALNUM_MAPPING
from phase2l_standard_phrase_gap_audit import PHRASES


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


def phrase_skeleton(text: str) -> str:
    return "".join(ch for ch in text if ch.isascii() and ch.isalnum())


def find_all(haystack: str, needle: str) -> list[int]:
    starts = []
    pos = haystack.find(needle)
    while pos >= 0:
        starts.append(pos)
        pos = haystack.find(needle, pos + 1)
    return starts


def merged_coverage(spans: list[tuple[int, int]]) -> int:
    if not spans:
        return 0
    spans = sorted(spans)
    total = 0
    cur_start, cur_end = spans[0]
    for start, end in spans[1:]:
        if start <= cur_end:
            cur_end = max(cur_end, end)
        else:
            total += cur_end - cur_start
            cur_start, cur_end = start, end
    total += cur_end - cur_start
    return total


def redacted_view(skeleton_len: int, occurrences: list[dict[str, int | str]]) -> str:
    parts = []
    cursor = 0
    for occ in sorted(occurrences, key=lambda item: (int(item["start"]), -(int(item["end"]) - int(item["start"])))):
        start = int(occ["start"])
        end = int(occ["end"])
        if start < cursor:
            continue
        if start > cursor:
            parts.append(f"<gap:{start - cursor}>")
        parts.append(f"<{occ['phrase_id']}>")
        cursor = end
    if cursor < skeleton_len:
        parts.append(f"<gap:{skeleton_len - cursor}>")
    return " ".join(parts)


def run(input_proof: Path, output_root: Path) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    phrase_defs = [
        {"phrase_id": phrase_id, "skeleton": phrase_skeleton(plaintext)}
        for phrase_id, plaintext in PHRASES
    ]

    out_dir = output_root / f"proof_snail_phase2m_phrase_coverage_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    views_dir = out_dir / "redacted_views"
    views_dir.mkdir(parents=True, exist_ok=False)

    summary_rows = []
    sequence_rows = []
    for path in sorted(originals.glob("*.luac")):
        skeleton = decoded_alnum(body(path))
        occurrences = []
        spans = []
        for phrase in phrase_defs:
            phrase_len = len(phrase["skeleton"])
            for start in find_all(skeleton, phrase["skeleton"]):
                end = start + phrase_len
                occurrences.append({"file": path.name, "phrase_id": phrase["phrase_id"], "start": start, "end": end})
                spans.append((start, end))

        covered = merged_coverage(spans)
        coverage_pct = round((covered / len(skeleton) * 100.0), 2) if skeleton else 0.0
        summary_rows.append(
            {
                "file": path.name,
                "size": path.stat().st_size,
                "sha256": sha256(path),
                "skeleton_len": len(skeleton),
                "phrase_occurrences": len(occurrences),
                "covered_alnum": covered,
                "coverage_pct": coverage_pct,
            }
        )
        sequence_rows.extend(occurrences)
        (views_dir / f"{path.name}.view.txt").write_text(
            redacted_view(len(skeleton), occurrences) + "\n",
            encoding="utf-8",
        )

    summary_rows.sort(key=lambda row: (-float(row["coverage_pct"]), -int(row["phrase_occurrences"]), int(row["size"]), row["file"]))
    sequence_rows.sort(key=lambda row: (row["file"], int(row["start"]), row["phrase_id"]))

    def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    write_tsv(
        out_dir / "coverage_summary.tsv",
        summary_rows,
        ["file", "size", "sha256", "skeleton_len", "phrase_occurrences", "covered_alnum", "coverage_pct"],
    )
    write_tsv(out_dir / "phrase_sequence.tsv", sequence_rows, ["file", "phrase_id", "start", "end"])

    high_coverage = [row for row in summary_rows if float(row["coverage_pct"]) >= 50.0]
    manifest = {
        "phase": "2M",
        "input_proof": str(input_proof),
        "result": {
            "handlers_scanned": len(summary_rows),
            "phrase_sequence_rows": len(sequence_rows),
            "high_coverage_50pct": len(high_coverage),
            "max_coverage_pct": max((float(row["coverage_pct"]) for row in summary_rows), default=0.0),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2M Phrase Coverage Result",
                "",
                f"Input proof: `{input_proof}`",
                "",
                "## Result",
                "",
                f"- handlers scanned: {len(summary_rows)}",
                f"- phrase sequence rows: {len(sequence_rows)}",
                f"- handlers with >=50% phrase coverage: {len(high_coverage)}",
                f"- max coverage pct: {manifest['result']['max_coverage_pct']}",
                "- solved: false",
                "",
                "Redacted views contain only phrase IDs and gap lengths.",
                "They are external proof artifacts, not source reconstruction.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure standard phrase coverage over external small handlers.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.input_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
