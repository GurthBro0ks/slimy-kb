#!/usr/bin/env python3
"""Phase 2T conflict-aware overlay with promotable external templates."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

from phase2l_standard_phrase_gap_audit import PHRASES, decoded_alnum_positions, display_bytes, find_all, phrase_plain_alnum_offsets, phrase_skeleton
from phase2o_template_overlay_decoder import gap_statuses, load_context_index
from phase2s_promotable_template_trial import load_promotable_templates


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


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def template_defs(classifier_proof: Path) -> list[dict[str, object]]:
    defs: list[dict[str, object]] = [
        {
            "phrase_id": phrase_id,
            "source": "base",
            "plaintext": plaintext,
            "skeleton": phrase_skeleton(plaintext),
            "plain_offsets": phrase_plain_alnum_offsets(plaintext),
        }
        for phrase_id, plaintext in PHRASES
    ]
    for row in load_promotable_templates(classifier_proof):
        defs.append(
            {
                "phrase_id": row["phrase_id"],
                "source": "promotable_external",
                "plaintext": row["plaintext_sensitive"],
                "skeleton": row["skeleton"],
                "plain_offsets": phrase_plain_alnum_offsets(str(row["plaintext_sensitive"])),
            }
        )
    return defs


def select_with_overlap_rows(candidates: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    selected = []
    skipped = []
    occupied: set[int] = set()
    ordered = sorted(
        candidates,
        key=lambda row: (
            int(row["start"]),
            0 if row["source"] == "base" else 1,
            -(int(row["end"]) - int(row["start"])),
            str(row["phrase_id"]),
        ),
    )
    for row in ordered:
        span = set(range(int(row["start"]), int(row["end"])))
        overlap = occupied & span
        if overlap:
            skipped.append({**row, "overlap_alnum": len(overlap)})
            continue
        selected.append(row)
        occupied.update(span)
    return selected, skipped


def render(skeleton_len: int, selected: list[dict[str, object]]) -> str:
    parts = []
    cursor = 0
    for row in sorted(selected, key=lambda item: (int(item["start"]), int(item["end"]))):
        start = int(row["start"])
        end = int(row["end"])
        if start > cursor:
            parts.append(f"<unresolved_alnum:{start - cursor}>")
        parts.append(
            "<{phrase_id} source={source} known_gaps={known_gaps} unknown_gaps={unknown_gaps} conflict_gaps={conflict_gaps}>".format(
                **row
            )
        )
        cursor = end
    if cursor < skeleton_len:
        parts.append(f"<unresolved_alnum:{skeleton_len - cursor}>")
    return " ".join(parts)


def run(input_proof: Path, phrase_proof: Path, classifier_proof: Path, output_root: Path) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    context_index = load_context_index(phrase_proof)
    defs = template_defs(classifier_proof)
    out_dir = output_root / f"proof_snail_phase2t_conflict_overlay_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    views_dir = out_dir / "redacted_overlays"
    views_dir.mkdir(parents=True, exist_ok=False)

    input_rows = []
    selected_rows = []
    skipped_rows = []
    all_candidate_rows = []
    source_counts = Counter()
    known_gap_rows = 0
    unknown_gap_rows = 0
    conflict_gap_rows = 0

    for path in sorted(originals.glob("*.luac")):
        raw = body(path)
        skeleton, raw_offsets = decoded_alnum_positions(raw)
        input_rows.append({"file": path.name, "size": path.stat().st_size, "sha256": sha256_file(path), "skeleton_len": len(skeleton)})
        candidates = []
        for template in defs:
            phrase_len = len(str(template["skeleton"]))
            for start in find_all(skeleton, str(template["skeleton"])):
                end = start + phrase_len
                raw_phrase_offsets = raw_offsets[start:end]
                if template["source"] == "base":
                    statuses = gap_statuses(raw, raw_phrase_offsets, template, context_index)
                else:
                    statuses = []
                candidates.append(
                    {
                        "file": path.name,
                        "phrase_id": template["phrase_id"],
                        "source": template["source"],
                        "start": start,
                        "end": end,
                        "raw_start": raw_phrase_offsets[0],
                        "raw_end": raw_phrase_offsets[-1],
                        "known_gaps": statuses.count("known"),
                        "unknown_gaps": statuses.count("unknown"),
                        "conflict_gaps": statuses.count("conflict"),
                    }
                )
        selected, skipped = select_with_overlap_rows(candidates)
        selected_rows.extend(selected)
        skipped_rows.extend(skipped)
        all_candidate_rows.extend(candidates)
        for row in selected:
            source_counts[str(row["source"])] += 1
            known_gap_rows += int(row["known_gaps"])
            unknown_gap_rows += int(row["unknown_gaps"])
            conflict_gap_rows += int(row["conflict_gaps"])
        (views_dir / f"{path.name}.overlay.txt").write_text(render(len(skeleton), selected) + "\n", encoding="utf-8")

    write_tsv(out_dir / "input_inventory.tsv", input_rows, ["file", "size", "sha256", "skeleton_len"])
    write_tsv(
        out_dir / "candidate_occurrences.tsv",
        all_candidate_rows,
        ["file", "phrase_id", "source", "start", "end", "raw_start", "raw_end", "known_gaps", "unknown_gaps", "conflict_gaps"],
    )
    write_tsv(
        out_dir / "selected_occurrences.tsv",
        selected_rows,
        ["file", "phrase_id", "source", "start", "end", "raw_start", "raw_end", "known_gaps", "unknown_gaps", "conflict_gaps"],
    )
    write_tsv(
        out_dir / "skipped_overlaps.tsv",
        skipped_rows,
        ["file", "phrase_id", "source", "start", "end", "raw_start", "raw_end", "known_gaps", "unknown_gaps", "conflict_gaps", "overlap_alnum"],
    )

    manifest = {
        "phase": "2T",
        "input_proof": str(input_proof),
        "phrase_proof": str(phrase_proof),
        "classifier_proof": str(classifier_proof),
        "result": {
            "handlers_scanned": len(input_rows),
            "candidate_occurrences": len(all_candidate_rows),
            "selected_occurrences": len(selected_rows),
            "skipped_overlaps": len(skipped_rows),
            "selected_by_source": dict(sorted(source_counts.items())),
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
                "# Phase 2T Conflict Overlay Result",
                "",
                f"Input proof: `{input_proof}`",
                f"Phrase proof: `{phrase_proof}`",
                f"Classifier proof: `{classifier_proof}`",
                "",
                "## Result",
                "",
                f"- handlers scanned: {len(input_rows)}",
                f"- candidate occurrences: {len(all_candidate_rows)}",
                f"- selected occurrences: {len(selected_rows)}",
                f"- skipped overlaps: {len(skipped_rows)}",
                *[f"- selected {source}: {count}" for source, count in sorted(source_counts.items())],
                f"- known gap rows: {known_gap_rows}",
                f"- unknown gap rows: {unknown_gap_rows}",
                f"- conflict gap rows: {conflict_gap_rows}",
                "- solved: false",
                "",
                "Promotable template text is external-only.",
                "Redacted overlays keep base and promotable_external sources separately tagged.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Render conflict-aware overlays with promotable external templates.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--phrase-proof", required=True, type=Path)
    parser.add_argument("--classifier-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.input_proof, args.phrase_proof, args.classifier_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
