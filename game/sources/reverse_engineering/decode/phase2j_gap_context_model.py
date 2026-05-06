#!/usr/bin/env python3
"""Phase 2J context model for raw gap transforms.

Consumes Phase 2I gap evidence and groups raw punctuation/control runs by
left/right alphanumeric context. This identifies locally stable transforms
without claiming global punctuation mappings.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(phase2i_proof: Path, output_root: Path) -> Path:
    evidence_path = phase2i_proof / "gap_evidence.tsv"
    if not evidence_path.is_file():
        raise RuntimeError(f"missing gap evidence: {evidence_path}")

    rows = read_tsv(evidence_path)
    out_dir = output_root / f"proof_snail_phase2j_gap_context_model_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    by_context: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    by_raw_gap: dict[str, Counter[str]] = defaultdict(Counter)
    by_plain_gap: dict[str, Counter[str]] = defaultdict(Counter)

    for row in rows:
        left = row["left_plain"]
        right = row["right_plain"]
        raw_gap = row["raw_gap_display"]
        plain_gap = row["plain_gap_display"]
        by_context[(left, right, raw_gap)][plain_gap] += 1
        by_raw_gap[raw_gap][plain_gap] += 1
        by_plain_gap[plain_gap][raw_gap] += 1

    context_rows = []
    conflict_free = []
    repeated_conflict_free = []
    conflicted = []
    for (left, right, raw_gap), candidates in sorted(by_context.items()):
        candidate_map = dict(sorted(candidates.items()))
        row = {
            "left_plain": left,
            "right_plain": right,
            "raw_gap_display": raw_gap,
            "plain_gap_candidates": json.dumps(candidate_map, ensure_ascii=True, sort_keys=True),
            "candidate_count": len(candidate_map),
            "evidence_count": sum(candidate_map.values()),
        }
        context_rows.append(row)
        if len(candidate_map) == 1:
            only = next(iter(candidate_map))
            enriched = {**row, "plain_gap": only}
            conflict_free.append(enriched)
            if row["evidence_count"] > 1:
                repeated_conflict_free.append(enriched)
        else:
            conflicted.append(row)

    raw_gap_rows = [
        {
            "raw_gap_display": raw_gap,
            "plain_gap_candidates": json.dumps(dict(sorted(counter.items())), ensure_ascii=True, sort_keys=True),
            "candidate_count": len(counter),
            "evidence_count": sum(counter.values()),
        }
        for raw_gap, counter in sorted(by_raw_gap.items())
    ]

    plain_gap_rows = [
        {
            "plain_gap_display": plain_gap,
            "raw_gap_candidates": json.dumps(dict(sorted(counter.items())), ensure_ascii=True, sort_keys=True),
            "candidate_count": len(counter),
            "evidence_count": sum(counter.values()),
        }
        for plain_gap, counter in sorted(by_plain_gap.items())
    ]

    write_tsv(
        out_dir / "context_gap_summary.tsv",
        context_rows,
        ["left_plain", "right_plain", "raw_gap_display", "plain_gap_candidates", "candidate_count", "evidence_count"],
    )
    write_tsv(
        out_dir / "context_gap_conflict_free.tsv",
        conflict_free,
        [
            "left_plain",
            "right_plain",
            "raw_gap_display",
            "plain_gap",
            "plain_gap_candidates",
            "candidate_count",
            "evidence_count",
        ],
    )
    write_tsv(
        out_dir / "context_gap_repeated_conflict_free.tsv",
        repeated_conflict_free,
        [
            "left_plain",
            "right_plain",
            "raw_gap_display",
            "plain_gap",
            "plain_gap_candidates",
            "candidate_count",
            "evidence_count",
        ],
    )
    write_tsv(
        out_dir / "context_gap_conflicts.tsv",
        conflicted,
        ["left_plain", "right_plain", "raw_gap_display", "plain_gap_candidates", "candidate_count", "evidence_count"],
    )
    write_tsv(out_dir / "raw_gap_summary.tsv", raw_gap_rows, ["raw_gap_display", "plain_gap_candidates", "candidate_count", "evidence_count"])
    write_tsv(out_dir / "plain_gap_summary.tsv", plain_gap_rows, ["plain_gap_display", "raw_gap_candidates", "candidate_count", "evidence_count"])

    manifest = {
        "phase": "2J",
        "input_phase2i_proof": str(phase2i_proof),
        "result": {
            "gap_rows": len(rows),
            "context_rows": len(context_rows),
            "context_conflict_free": len(conflict_free),
            "context_repeated_conflict_free": len(repeated_conflict_free),
            "context_conflicts": len(conflicted),
            "global_raw_gap_rows": len(raw_gap_rows),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2J Gap Context Model Result",
                "",
                f"Input proof: `{phase2i_proof}`",
                "",
                "## Result",
                "",
                f"- gap rows: {len(rows)}",
                f"- context rows: {len(context_rows)}",
                f"- context conflict-free rows: {len(conflict_free)}",
                f"- context repeated conflict-free rows: {len(repeated_conflict_free)}",
                f"- context conflict rows: {len(conflicted)}",
                f"- global raw gap rows: {len(raw_gap_rows)}",
                "- solved: false",
                "",
                "This proof identifies local transform candidates by context.",
                "It does not promote global punctuation mappings.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phase 2J context model from Phase 2I gap evidence.")
    parser.add_argument("--phase2i-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.phase2i_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
