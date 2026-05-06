#!/usr/bin/env python3
"""Phase 2R external candidate classifier.

Classifies Phase 2Q external candidate templates into promotion buckets while
keeping candidate text external. Committed reports should use only the sanitized
classification file.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import Counter
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def classify(text: str, occurrences: int, file_count: int) -> tuple[str, str, bool]:
    lower = text.lower()
    if text in {"orend", "endend", "localid", "cclogonlpc"} or lower.startswith("local"):
        return ("grammar_fragment", "small repeated Lua/control fragment", True)
    if "closecommunicating" in lower:
        return ("api_member_fragment", "repeated DormUtil/communicating utility fragment", True)
    if "pulluser" in lower or "setprop" in lower or "deleteprop" in lower:
        return ("api_member_fragment", "repeated manager/member call fragment", True)
    if text.isupper() or text.endswith("end") or occurrences <= 3 or file_count <= 3:
        return ("domain_or_event_constant", "domain/event-specific span; keep external until manager context proves reusable", False)
    return ("needs_review", "insufficient classification signal", False)


def run(template_proof: Path, output_root: Path) -> Path:
    sensitive_path = template_proof / "external_candidate_templates_sensitive.tsv"
    if not sensitive_path.is_file():
        raise RuntimeError(f"missing sensitive candidate template file: {sensitive_path}")

    out_dir = output_root / f"proof_snail_phase2r_candidate_classifier_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    sensitive_rows = []
    sanitized_rows = []
    for row in read_tsv(sensitive_path):
        occurrences = int(row["occurrences"])
        file_count = int(row["file_count"])
        category, reason, promotable = classify(row["plaintext_sensitive"], occurrences, file_count)
        sensitive_rows.append(
            {
                **row,
                "category": category,
                "promotable": str(promotable).lower(),
                "reason": reason,
            }
        )
        sanitized_rows.append(
            {
                "phrase_id": row["phrase_id"],
                "span_hash": row["span_hash"],
                "alnum_len": row["alnum_len"],
                "occurrences": row["occurrences"],
                "file_count": row["file_count"],
                "category": category,
                "promotable": str(promotable).lower(),
                "reason": reason,
            }
        )

    counts = Counter(row["category"] for row in sanitized_rows)
    promotable_count = sum(1 for row in sanitized_rows if row["promotable"] == "true")

    write_tsv(
        out_dir / "candidate_classification_sensitive.tsv",
        sensitive_rows,
        ["phrase_id", "span_hash", "alnum_len", "occurrences", "file_count", "plaintext_sensitive", "category", "promotable", "reason"],
    )
    write_tsv(
        out_dir / "candidate_classification_sanitized.tsv",
        sanitized_rows,
        ["phrase_id", "span_hash", "alnum_len", "occurrences", "file_count", "category", "promotable", "reason"],
    )

    manifest = {
        "phase": "2R",
        "template_proof": str(template_proof),
        "result": {
            "candidate_templates": len(sanitized_rows),
            "promotable_candidates": promotable_count,
            "category_counts": dict(sorted(counts.items())),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2R Candidate Classifier Result",
                "",
                f"Template proof: `{template_proof}`",
                "",
                "## Result",
                "",
                f"- candidate templates: {len(sanitized_rows)}",
                f"- promotable candidates: {promotable_count}",
                *[f"- {category}: {count}" for category, count in sorted(counts.items())],
                "- solved: false",
                "",
                "Candidate template text is external-only.",
                "Use `candidate_classification_sanitized.tsv` for committed reporting.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify external Phase 2Q candidate templates.")
    parser.add_argument("--template-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.template_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
