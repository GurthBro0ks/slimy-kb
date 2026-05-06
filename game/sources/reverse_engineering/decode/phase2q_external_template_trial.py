#!/usr/bin/env python3
"""Phase 2Q external unresolved-span template trial.

Builds candidate templates from the sensitive Phase 2P unresolved-span ledger
inside /tmp, measures coverage impact, and writes only sanitized summaries for
committed reporting. Candidate template text is external-only.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

from phase2h_punctuation_audit import ALNUM_MAPPING
from phase2l_standard_phrase_gap_audit import PHRASES, phrase_skeleton
from phase2m_phrase_coverage import find_all, merged_coverage, redacted_view


def sha256_file(path: Path) -> str:
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_candidate_templates(span_proof: Path, min_occurrences: int, min_len: int) -> list[dict[str, object]]:
    sensitive_path = span_proof / "unresolved_span_rows_sensitive.tsv"
    summary_path = span_proof / "unresolved_span_summary_sanitized.tsv"
    if not sensitive_path.is_file():
        raise RuntimeError(f"missing sensitive span rows: {sensitive_path}")
    if not summary_path.is_file():
        raise RuntimeError(f"missing sanitized span summary: {summary_path}")

    text_by_hash = {}
    for row in read_tsv(sensitive_path):
        text_by_hash.setdefault(row["span_hash"], row["span_text_sensitive"])

    candidates = []
    for row in read_tsv(summary_path):
        occurrences = int(row["occurrences"])
        alnum_len = int(row["alnum_len"])
        if occurrences < min_occurrences or alnum_len < min_len:
            continue
        span_hash = row["span_hash"]
        text = text_by_hash[span_hash]
        candidates.append(
            {
                "phrase_id": f"external_span_{span_hash[:12]}",
                "span_hash": span_hash,
                "plaintext_sensitive": text,
                "skeleton": phrase_skeleton(text),
                "alnum_len": alnum_len,
                "occurrences": occurrences,
                "file_count": int(row["file_count"]),
            }
        )
    candidates.sort(key=lambda row: (-int(row["occurrences"]), -int(row["alnum_len"]), row["span_hash"]))
    return candidates


def run(input_proof: Path, span_proof: Path, output_root: Path, min_occurrences: int, min_len: int) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    candidates = load_candidate_templates(span_proof, min_occurrences, min_len)
    phrase_defs = [{"phrase_id": phrase_id, "skeleton": phrase_skeleton(plaintext), "source": "base"} for phrase_id, plaintext in PHRASES]
    phrase_defs.extend({"phrase_id": row["phrase_id"], "skeleton": row["skeleton"], "source": "external_candidate"} for row in candidates)

    out_dir = output_root / f"proof_snail_phase2q_external_template_trial_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
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
        external_hits = sum(1 for row in occurrences if row["source"] == "external_candidate")
        summary_rows.append(
            {
                "file": path.name,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
                "skeleton_len": len(skeleton),
                "phrase_occurrences": len(occurrences),
                "external_candidate_hits": external_hits,
                "covered_alnum": covered,
                "coverage_pct": coverage_pct,
            }
        )
        sequence_rows.extend(occurrences)
        (views_dir / f"{path.name}.view.txt").write_text(redacted_view(len(skeleton), occurrences) + "\n", encoding="utf-8")

    summary_rows.sort(key=lambda row: (-float(row["coverage_pct"]), -int(row["external_candidate_hits"]), -int(row["phrase_occurrences"]), row["file"]))
    sequence_rows.sort(key=lambda row: (row["file"], int(row["start"]), row["phrase_id"]))

    sensitive_template_rows = [
        {
            "phrase_id": row["phrase_id"],
            "span_hash": row["span_hash"],
            "alnum_len": row["alnum_len"],
            "occurrences": row["occurrences"],
            "file_count": row["file_count"],
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
        }
        for row in candidates
    ]

    write_tsv(
        out_dir / "external_candidate_templates_sensitive.tsv",
        sensitive_template_rows,
        ["phrase_id", "span_hash", "alnum_len", "occurrences", "file_count", "plaintext_sensitive"],
    )
    write_tsv(
        out_dir / "external_candidate_templates_sanitized.tsv",
        sanitized_template_rows,
        ["phrase_id", "span_hash", "alnum_len", "occurrences", "file_count"],
    )
    write_tsv(
        out_dir / "coverage_summary.tsv",
        summary_rows,
        ["file", "size", "sha256", "skeleton_len", "phrase_occurrences", "external_candidate_hits", "covered_alnum", "coverage_pct"],
    )
    write_tsv(out_dir / "phrase_sequence.tsv", sequence_rows, ["file", "phrase_id", "source", "start", "end"])

    high_coverage = [row for row in summary_rows if float(row["coverage_pct"]) >= 50.0]
    manifest = {
        "phase": "2Q",
        "input_proof": str(input_proof),
        "span_proof": str(span_proof),
        "min_occurrences": min_occurrences,
        "min_len": min_len,
        "result": {
            "candidate_templates": len(candidates),
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
                "# Phase 2Q External Template Trial Result",
                "",
                f"Input proof: `{input_proof}`",
                f"Span proof: `{span_proof}`",
                "",
                "## Result",
                "",
                f"- candidate templates: {len(candidates)}",
                f"- handlers scanned: {len(summary_rows)}",
                f"- phrase sequence rows: {len(sequence_rows)}",
                f"- handlers with >=50% phrase coverage: {len(high_coverage)}",
                f"- max coverage pct: {manifest['result']['max_coverage_pct']}",
                "- solved: false",
                "",
                "Candidate template text is external-only.",
                "Committed reporting should use the sanitized template TSV.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Trial external candidate templates from repeated unresolved spans.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--span-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    parser.add_argument("--min-occurrences", default=3, type=int)
    parser.add_argument("--min-len", default=5, type=int)
    args = parser.parse_args()
    print(run(args.input_proof, args.span_proof, args.output_root, args.min_occurrences, args.min_len))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
