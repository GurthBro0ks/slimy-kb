#!/usr/bin/env python3
"""Phase 2P unresolved span inventory.

Ranks unresolved alphanumeric spans from Phase 2O overlays. Sensitive span text
is written only to the external proof directory; committed reports should use
the sanitized hash/count summary.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from phase2l_standard_phrase_gap_audit import decoded_alnum_positions


def body(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:3] == b"\x14\x15\x16":
        return data[3:]
    return data


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def run(input_proof: Path, overlay_proof: Path, output_root: Path, min_len: int) -> Path:
    originals = input_proof / "originals"
    unresolved_path = overlay_proof / "unresolved_spans.tsv"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")
    if not unresolved_path.is_file():
        raise RuntimeError(f"missing unresolved spans: {unresolved_path}")

    out_dir = output_root / f"proof_snail_phase2p_unresolved_span_inventory_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    skeletons: dict[str, str] = {}
    input_rows = []
    for path in sorted(originals.glob("*.luac")):
        skeleton, _ = decoded_alnum_positions(body(path))
        skeletons[path.name] = skeleton
        input_rows.append({"file": path.name, "size": path.stat().st_size, "sha256": sha256_file(path), "skeleton_len": len(skeleton)})

    sensitive_rows = []
    groups: dict[str, dict[str, object]] = defaultdict(lambda: {"files": set(), "total_alnum_len": 0, "occurrences": 0})
    for row in read_tsv(unresolved_path):
        file_name = row["file"]
        start = int(row["start"])
        end = int(row["end"])
        span = skeletons[file_name][start:end]
        if len(span) < min_len:
            continue
        span_hash = sha256_text(span)
        sensitive_rows.append(
            {
                "file": file_name,
                "start": start,
                "end": end,
                "alnum_len": len(span),
                "span_hash": span_hash,
                "span_text_sensitive": span,
            }
        )
        groups[span]["occurrences"] = int(groups[span]["occurrences"]) + 1
        groups[span]["total_alnum_len"] = int(groups[span]["total_alnum_len"]) + len(span)
        files = groups[span]["files"]
        assert isinstance(files, set)
        files.add(file_name)

    summary_rows = []
    for span, data in groups.items():
        files = sorted(data["files"])
        summary_rows.append(
            {
                "span_hash": sha256_text(span),
                "alnum_len": len(span),
                "occurrences": data["occurrences"],
                "file_count": len(files),
                "total_alnum_len": data["total_alnum_len"],
                "sample_files": ",".join(files[:5]),
            }
        )
    summary_rows.sort(key=lambda row: (-int(row["occurrences"]), -int(row["total_alnum_len"]), -int(row["alnum_len"]), row["span_hash"]))
    sensitive_rows.sort(key=lambda row: (row["span_hash"], row["file"], int(row["start"])))

    write_tsv(out_dir / "input_inventory.tsv", input_rows, ["file", "size", "sha256", "skeleton_len"])
    write_tsv(
        out_dir / "unresolved_span_rows_sensitive.tsv",
        sensitive_rows,
        ["file", "start", "end", "alnum_len", "span_hash", "span_text_sensitive"],
    )
    write_tsv(
        out_dir / "unresolved_span_summary_sanitized.tsv",
        summary_rows,
        ["span_hash", "alnum_len", "occurrences", "file_count", "total_alnum_len", "sample_files"],
    )

    repeated = [row for row in summary_rows if int(row["occurrences"]) > 1]
    manifest = {
        "phase": "2P",
        "input_proof": str(input_proof),
        "overlay_proof": str(overlay_proof),
        "min_len": min_len,
        "result": {
            "input_handlers": len(input_rows),
            "unresolved_span_rows": len(sensitive_rows),
            "unique_unresolved_spans": len(summary_rows),
            "repeated_unresolved_spans": len(repeated),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2P Unresolved Span Inventory Result",
                "",
                f"Input proof: `{input_proof}`",
                f"Overlay proof: `{overlay_proof}`",
                "",
                "## Result",
                "",
                f"- input handlers: {len(input_rows)}",
                f"- unresolved span rows: {len(sensitive_rows)}",
                f"- unique unresolved spans: {len(summary_rows)}",
                f"- repeated unresolved spans: {len(repeated)}",
                "- solved: false",
                "",
                "`unresolved_span_rows_sensitive.tsv` contains derived alphanumeric span text and must stay external.",
                "`unresolved_span_summary_sanitized.tsv` is hash/count/sample-file metadata only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank unresolved template-overlay spans.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--overlay-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    parser.add_argument("--min-len", default=4, type=int)
    args = parser.parse_args()
    print(run(args.input_proof, args.overlay_proof, args.output_root, args.min_len))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
