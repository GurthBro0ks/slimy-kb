#!/usr/bin/env python3
"""Phase 2S promotable external template trial.

Uses only Phase 2R rows marked promotable=true. Candidate text remains
external-only; committed reports should use sanitized template metadata.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from phase2l_standard_phrase_gap_audit import PHRASES, phrase_skeleton
from phase2m_phrase_coverage import find_all, merged_coverage, redacted_view
from phase2q_external_template_trial import body, decoded_alnum


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_promotable_templates(classifier_proof: Path) -> list[dict[str, object]]:
    sensitive_path = classifier_proof / "candidate_classification_sensitive.tsv"
    if not sensitive_path.is_file():
        raise RuntimeError(f"missing sensitive candidate classification file: {sensitive_path}")

    candidates = []
    for row in read_tsv(sensitive_path):
        if row["promotable"] != "true":
            continue
        candidates.append(
            {
                "phrase_id": row["phrase_id"].replace("external_span_", "promotable_span_"),
                "span_hash": row["span_hash"],
                "plaintext_sensitive": row["plaintext_sensitive"],
                "skeleton": phrase_skeleton(row["plaintext_sensitive"]),
                "alnum_len": int(row["alnum_len"]),
                "occurrences": int(row["occurrences"]),
                "file_count": int(row["file_count"]),
                "category": row["category"],
            }
        )
    candidates.sort(key=lambda row: (str(row["category"]), -int(row["occurrences"]), row["span_hash"]))
    return candidates


def run(input_proof: Path, classifier_proof: Path, output_root: Path) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    candidates = load_promotable_templates(classifier_proof)
    phrase_defs = [{"phrase_id": phrase_id, "skeleton": phrase_skeleton(plaintext), "source": "base"} for phrase_id, plaintext in PHRASES]
    phrase_defs.extend({"phrase_id": row["phrase_id"], "skeleton": row["skeleton"], "source": "promotable_external"} for row in candidates)

    out_dir = output_root / f"proof_snail_phase2s_promotable_template_trial_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    views_dir = out_dir / "redacted_views"
    views_dir.mkdir(parents=True, exist_ok=False)

    summary_rows = []
    sequence_rows = []
    for path in sorted(originals.glob("*.luac")):
        skeleton = decoded_alnum(body(path))
        occurrences = []
        spans = []
        for phrase in phrase_defs:
            phrase_len = len(str(phrase["skeleton"]))
            if phrase_len == 0:
                continue
            for start in find_all(skeleton, str(phrase["skeleton"])):
                end = start + phrase_len
                occurrences.append(
                    {
                        "file": path.name,
                        "phrase_id": phrase["phrase_id"],
                        "source": phrase["source"],
                        "start": start,
                        "end": end,
                    }
                )
                spans.append((start, end))
        covered = merged_coverage(spans)
        coverage_pct = round((covered / len(skeleton) * 100.0), 2) if skeleton else 0.0
        promotable_hits = sum(1 for row in occurrences if row["source"] == "promotable_external")
        summary_rows.append(
            {
                "file": path.name,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
                "skeleton_len": len(skeleton),
                "phrase_occurrences": len(occurrences),
                "promotable_hits": promotable_hits,
                "covered_alnum": covered,
                "coverage_pct": coverage_pct,
            }
        )
        sequence_rows.extend(occurrences)
        (views_dir / f"{path.name}.view.txt").write_text(redacted_view(len(skeleton), occurrences) + "\n", encoding="utf-8")

    summary_rows.sort(key=lambda row: (-float(row["coverage_pct"]), -int(row["promotable_hits"]), -int(row["phrase_occurrences"]), row["file"]))
    sequence_rows.sort(key=lambda row: (row["file"], int(row["start"]), row["phrase_id"]))

    sensitive_template_rows = [
        {
            "phrase_id": row["phrase_id"],
            "span_hash": row["span_hash"],
            "alnum_len": row["alnum_len"],
            "occurrences": row["occurrences"],
            "file_count": row["file_count"],
            "category": row["category"],
            "plaintext_sensitive": row["plaintext_sensitive"],
        }
        for row in candidates
    ]
    sanitized_template_rows = [
        {
            "phrase_id": row["phrase_id"],
            "span_hash": row["span_hash"],
            "alnum_len": row["alnum_len"],
            "occurrences": row["occurrences"],
            "file_count": row["file_count"],
            "category": row["category"],
        }
        for row in candidates
    ]

    write_tsv(
        out_dir / "promotable_templates_sensitive.tsv",
        sensitive_template_rows,
        ["phrase_id", "span_hash", "alnum_len", "occurrences", "file_count", "category", "plaintext_sensitive"],
    )
    write_tsv(
        out_dir / "promotable_templates_sanitized.tsv",
        sanitized_template_rows,
        ["phrase_id", "span_hash", "alnum_len", "occurrences", "file_count", "category"],
    )
    write_tsv(
        out_dir / "coverage_summary.tsv",
        summary_rows,
        ["file", "size", "sha256", "skeleton_len", "phrase_occurrences", "promotable_hits", "covered_alnum", "coverage_pct"],
    )
    write_tsv(out_dir / "phrase_sequence.tsv", sequence_rows, ["file", "phrase_id", "source", "start", "end"])

    high_coverage = [row for row in summary_rows if float(row["coverage_pct"]) >= 50.0]
    manifest = {
        "phase": "2S",
        "input_proof": str(input_proof),
        "classifier_proof": str(classifier_proof),
        "result": {
            "promotable_templates": len(candidates),
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
                "# Phase 2S Promotable Template Trial Result",
                "",
                f"Input proof: `{input_proof}`",
                f"Classifier proof: `{classifier_proof}`",
                "",
                "## Result",
                "",
                f"- promotable templates: {len(candidates)}",
                f"- handlers scanned: {len(summary_rows)}",
                f"- phrase sequence rows: {len(sequence_rows)}",
                f"- handlers with >=50% phrase coverage: {len(high_coverage)}",
                f"- max coverage pct: {manifest['result']['max_coverage_pct']}",
                "- solved: false",
                "",
                "Promotable template text is external-only.",
                "Committed reporting should use the sanitized template TSV.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Trial only Phase 2R promotable external templates.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--classifier-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.input_proof, args.classifier_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
