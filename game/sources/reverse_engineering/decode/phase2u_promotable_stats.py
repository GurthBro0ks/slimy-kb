#!/usr/bin/env python3
"""Phase 2U sanitized promotable-template stats."""

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


def load_template_meta(classifier_proof: Path) -> dict[str, dict[str, str]]:
    sanitized = classifier_proof / "candidate_classification_sanitized.tsv"
    if not sanitized.is_file():
        raise RuntimeError(f"missing sanitized classifier file: {sanitized}")
    meta = {}
    for row in read_tsv(sanitized):
        promoted_id = row["phrase_id"].replace("external_span_", "promotable_span_")
        meta[promoted_id] = row
    return meta


def run(overlay_proof: Path, classifier_proof: Path, output_root: Path) -> Path:
    selected_path = overlay_proof / "selected_occurrences.tsv"
    skipped_path = overlay_proof / "skipped_overlaps.tsv"
    if not selected_path.is_file():
        raise RuntimeError(f"missing selected occurrences: {selected_path}")
    if not skipped_path.is_file():
        raise RuntimeError(f"missing skipped overlaps: {skipped_path}")

    meta = load_template_meta(classifier_proof)
    stats = defaultdict(lambda: {"selected": 0, "skipped": 0, "files": set(), "selected_alnum": 0, "skipped_overlap_alnum": 0})

    for row in read_tsv(selected_path):
        if row["source"] != "promotable_external":
            continue
        item = stats[row["phrase_id"]]
        item["selected"] += 1
        item["selected_alnum"] += int(row["end"]) - int(row["start"])
        item["files"].add(row["file"])

    for row in read_tsv(skipped_path):
        if row["source"] != "promotable_external":
            continue
        item = stats[row["phrase_id"]]
        item["skipped"] += 1
        item["skipped_overlap_alnum"] += int(row["overlap_alnum"])
        item["files"].add(row["file"])

    rows = []
    for phrase_id, item in stats.items():
        template = meta.get(phrase_id, {})
        selected = int(item["selected"])
        skipped = int(item["skipped"])
        rows.append(
            {
                "phrase_id": phrase_id,
                "span_hash": template.get("span_hash", ""),
                "category": template.get("category", ""),
                "alnum_len": template.get("alnum_len", ""),
                "source_occurrences": template.get("occurrences", ""),
                "source_file_count": template.get("file_count", ""),
                "selected_occurrences": selected,
                "skipped_overlaps": skipped,
                "selected_file_count": len(item["files"]),
                "selected_alnum": item["selected_alnum"],
                "skipped_overlap_alnum": item["skipped_overlap_alnum"],
                "promotion_priority": selected * int(template.get("alnum_len", "0")) - skipped * 10,
            }
        )
    rows.sort(key=lambda row: (-int(row["promotion_priority"]), -int(row["selected_occurrences"]), row["phrase_id"]))

    out_dir = output_root / f"proof_snail_phase2u_promotable_stats_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)
    write_tsv(
        out_dir / "promotable_stats_sanitized.tsv",
        rows,
        [
            "phrase_id",
            "span_hash",
            "category",
            "alnum_len",
            "source_occurrences",
            "source_file_count",
            "selected_occurrences",
            "skipped_overlaps",
            "selected_file_count",
            "selected_alnum",
            "skipped_overlap_alnum",
            "promotion_priority",
        ],
    )

    manifest = {
        "phase": "2U",
        "overlay_proof": str(overlay_proof),
        "classifier_proof": str(classifier_proof),
        "result": {
            "promotable_templates_seen": len(rows),
            "total_selected_promotable": sum(int(row["selected_occurrences"]) for row in rows),
            "total_skipped_promotable": sum(int(row["skipped_overlaps"]) for row in rows),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2U Promotable Stats Result",
                "",
                f"Overlay proof: `{overlay_proof}`",
                f"Classifier proof: `{classifier_proof}`",
                "",
                "## Result",
                "",
                f"- promotable templates seen: {manifest['result']['promotable_templates_seen']}",
                f"- total selected promotable: {manifest['result']['total_selected_promotable']}",
                f"- total skipped promotable: {manifest['result']['total_skipped_promotable']}",
                "- solved: false",
                "",
                "This proof is sanitized: hashes, counts, categories, and file counts only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize sanitized stats for selected promotable external templates.")
    parser.add_argument("--overlay-proof", required=True, type=Path)
    parser.add_argument("--classifier-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.overlay_proof, args.classifier_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
