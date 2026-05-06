#!/usr/bin/env python3
"""Phase 2W grammar-fragment audit.

Audits external grammar candidates from Phase 2R/2T and writes a sanitized risk
summary. Fragment text remains external-only.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def risk_tag(alnum_len: int, selected: int, skipped: int) -> tuple[str, str]:
    if skipped:
        return ("hold", "has skipped overlaps")
    if alnum_len <= 6:
        return ("hold", "short grammar fragment needs punctuation-aware context")
    if selected < 5:
        return ("hold", "low selected occurrence count")
    return ("trial_ok", "no skipped overlaps and enough repeated context")


def run(classifier_proof: Path, overlay_proof: Path, output_root: Path) -> Path:
    sensitive_path = classifier_proof / "candidate_classification_sensitive.tsv"
    selected_path = overlay_proof / "selected_occurrences.tsv"
    skipped_path = overlay_proof / "skipped_overlaps.tsv"
    for path in (sensitive_path, selected_path, skipped_path):
        if not path.is_file():
            raise RuntimeError(f"missing required input: {path}")

    grammar = {}
    for row in read_tsv(sensitive_path):
        if row["category"] != "grammar_fragment":
            continue
        phrase_id = row["phrase_id"].replace("external_span_", "promotable_span_")
        grammar[phrase_id] = row

    counts = defaultdict(lambda: {"selected": 0, "skipped": 0, "files": set(), "skipped_overlap_alnum": 0})
    for row in read_tsv(selected_path):
        if row["phrase_id"] not in grammar:
            continue
        counts[row["phrase_id"]]["selected"] += 1
        counts[row["phrase_id"]]["files"].add(row["file"])
    for row in read_tsv(skipped_path):
        if row["phrase_id"] not in grammar:
            continue
        counts[row["phrase_id"]]["skipped"] += 1
        counts[row["phrase_id"]]["files"].add(row["file"])
        counts[row["phrase_id"]]["skipped_overlap_alnum"] += int(row["overlap_alnum"])

    sensitive_rows = []
    sanitized_rows = []
    for phrase_id, meta in grammar.items():
        selected = int(counts[phrase_id]["selected"])
        skipped = int(counts[phrase_id]["skipped"])
        alnum_len = int(meta["alnum_len"])
        tag, reason = risk_tag(alnum_len, selected, skipped)
        base = {
            "phrase_id": phrase_id,
            "span_hash": meta["span_hash"],
            "alnum_len": alnum_len,
            "source_occurrences": meta["occurrences"],
            "source_file_count": meta["file_count"],
            "selected_occurrences": selected,
            "selected_file_count": len(counts[phrase_id]["files"]),
            "skipped_overlaps": skipped,
            "skipped_overlap_alnum": counts[phrase_id]["skipped_overlap_alnum"],
            "risk_tag": tag,
            "reason": reason,
        }
        sanitized_rows.append(base)
        sensitive_rows.append({**base, "plaintext_sensitive": meta["plaintext_sensitive"]})

    sanitized_rows.sort(key=lambda row: (row["risk_tag"], -int(row["selected_occurrences"]), row["phrase_id"]))
    sensitive_rows.sort(key=lambda row: (row["risk_tag"], -int(row["selected_occurrences"]), row["phrase_id"]))

    out_dir = output_root / f"proof_snail_phase2w_grammar_fragment_audit_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)
    write_tsv(
        out_dir / "grammar_fragment_audit_sanitized.tsv",
        sanitized_rows,
        [
            "phrase_id",
            "span_hash",
            "alnum_len",
            "source_occurrences",
            "source_file_count",
            "selected_occurrences",
            "selected_file_count",
            "skipped_overlaps",
            "skipped_overlap_alnum",
            "risk_tag",
            "reason",
        ],
    )
    write_tsv(
        out_dir / "grammar_fragment_audit_sensitive.tsv",
        sensitive_rows,
        [
            "phrase_id",
            "span_hash",
            "alnum_len",
            "source_occurrences",
            "source_file_count",
            "selected_occurrences",
            "selected_file_count",
            "skipped_overlaps",
            "skipped_overlap_alnum",
            "risk_tag",
            "reason",
            "plaintext_sensitive",
        ],
    )

    risk_counts = defaultdict(int)
    for row in sanitized_rows:
        risk_counts[row["risk_tag"]] += 1
    manifest = {
        "phase": "2W",
        "classifier_proof": str(classifier_proof),
        "overlay_proof": str(overlay_proof),
        "result": {
            "grammar_candidates": len(sanitized_rows),
            "risk_counts": dict(sorted(risk_counts.items())),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2W Grammar Fragment Audit Result",
                "",
                f"Classifier proof: `{classifier_proof}`",
                f"Overlay proof: `{overlay_proof}`",
                "",
                "## Result",
                "",
                f"- grammar candidates: {len(sanitized_rows)}",
                *[f"- {tag}: {count}" for tag, count in sorted(risk_counts.items())],
                "- solved: false",
                "",
                "Fragment text is external-only. Committed reports should use the sanitized audit.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit external grammar fragments for promotion risk.")
    parser.add_argument("--classifier-proof", required=True, type=Path)
    parser.add_argument("--overlay-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.classifier_proof, args.overlay_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
