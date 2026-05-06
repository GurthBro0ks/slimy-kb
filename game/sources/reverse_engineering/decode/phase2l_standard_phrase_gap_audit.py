#!/usr/bin/env python3
"""Phase 2L standard phrase gap audit.

Scans externally pulled small handlers for repeated alphanumeric skeleton phrases
with known Lua/API punctuation, then aggregates raw gap evidence inside those
phrases. This promotes no mappings; it only records repeated, conflict-free
phrase-local transform evidence.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from phase2h_punctuation_audit import ALNUM_MAPPING


PHRASES = [
    ("return_function_lpc", "return function(lpc)"),
    ("eventmgr_fire_event", "EventMgr.fire_event"),
    ("rankm_set_my_rank", "RankM.setMyRank"),
    ("rankm_set_rank_info", "RankM.setRankInfo"),
    ("rankm_get_id_my_task_type", "RankM.getIdMyTaskType"),
    ("topm_set_my_rank", "TopM.setMyRank"),
    ("topm_set_rank_info", "TopM.setRankInfo"),
    ("taskm_set_week_top", "TaskM.setWeekTop"),
    ("taskm_set_week_top_my_rank", "TaskM.setWeekTopMyRank"),
    ("arenam_set_top", "ArenaM.setTop"),
    ("itemm_refresh_item", "ItemM.refreshItem"),
    ("dormutil_close_communicating", "DormUtil.closeCommunicating"),
    ("close_communicating_dorm", "closeCommunicatingDorm"),
    ("me_user_query", "ME.user.query"),
    ("me_user_set_ex", "ME.user.setEx"),
    ("me_user_set_temp", "ME.user.setTemp"),
    ("operation_cmd", "Operation.cmd"),
    ("lpc_id", "lpc.id"),
    ("lpc_rank", "lpc.rank"),
    ("lpc_list", "lpc.list"),
    ("lpc_type", "lpc.type"),
    ("lpc_start", "lpc.start"),
    ("lpc_group", "lpc.group"),
    ("lpc_classid", "lpc.classid"),
    ("lpc_amount", "lpc.amount"),
]


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


def decoded_alnum_positions(raw: bytes) -> tuple[str, list[int]]:
    chars = []
    offsets = []
    for idx, b in enumerate(raw):
        ch = chr(b)
        if ch in ALNUM_MAPPING:
            chars.append(ALNUM_MAPPING[ch])
            offsets.append(idx)
        elif ch.isascii() and ch.isalnum():
            chars.append(ch)
            offsets.append(idx)
    return "".join(chars), offsets


def phrase_skeleton(text: str) -> str:
    return "".join(ch for ch in text if ch.isascii() and ch.isalnum())


def phrase_plain_alnum_offsets(text: str) -> list[int]:
    return [idx for idx, ch in enumerate(text) if ch.isascii() and ch.isalnum()]


def display_bytes(data: bytes) -> str:
    out = []
    for b in data:
        if b == 10:
            out.append("\\n")
        elif b == 13:
            out.append("\\r")
        elif b == 9:
            out.append("\\t")
        elif 32 <= b <= 126:
            ch = chr(b)
            out.append("<space>" if ch == " " else ch)
        else:
            out.append(f"\\x{b:02x}")
    return "".join(out)


def display_text(text: str) -> str:
    return display_bytes(text.encode("utf-8"))


def find_all(haystack: str, needle: str) -> list[int]:
    starts = []
    pos = haystack.find(needle)
    while pos >= 0:
        starts.append(pos)
        pos = haystack.find(needle, pos + 1)
    return starts


def run(input_proof: Path, output_root: Path) -> Path:
    originals = input_proof / "originals"
    if not originals.is_dir():
        raise RuntimeError(f"missing originals directory: {originals}")

    out_dir = output_root / f"proof_snail_phase2l_standard_phrase_gap_{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=False)

    occurrence_rows = []
    gap_rows = []
    input_rows = []

    phrase_defs = [
        {
            "phrase_id": phrase_id,
            "plaintext": plaintext,
            "skeleton": phrase_skeleton(plaintext),
            "plain_offsets": phrase_plain_alnum_offsets(plaintext),
        }
        for phrase_id, plaintext in PHRASES
    ]

    for path in sorted(originals.glob("*.luac")):
        raw = body(path)
        decoded, raw_offsets = decoded_alnum_positions(raw)
        input_rows.append({"file": path.name, "size": path.stat().st_size, "sha256": sha256(path)})
        for phrase in phrase_defs:
            starts = find_all(decoded, phrase["skeleton"])
            for occurrence_index, start in enumerate(starts):
                raw_phrase_offsets = raw_offsets[start : start + len(phrase["skeleton"])]
                occurrence_rows.append(
                    {
                        "file": path.name,
                        "phrase_id": phrase["phrase_id"],
                        "occurrence_index": occurrence_index,
                        "decoded_skeleton_start": start,
                        "raw_start": raw_phrase_offsets[0],
                        "raw_end": raw_phrase_offsets[-1],
                    }
                )
                plain_offsets = phrase["plain_offsets"]
                plaintext = phrase["plaintext"]
                for gap_idx in range(len(raw_phrase_offsets) - 1):
                    raw_gap = raw[raw_phrase_offsets[gap_idx] + 1 : raw_phrase_offsets[gap_idx + 1]]
                    plain_gap = plaintext[plain_offsets[gap_idx] + 1 : plain_offsets[gap_idx + 1]]
                    if not raw_gap and not plain_gap:
                        continue
                    gap_rows.append(
                        {
                            "file": path.name,
                            "phrase_id": phrase["phrase_id"],
                            "left_plain": plaintext[plain_offsets[gap_idx]],
                            "right_plain": plaintext[plain_offsets[gap_idx + 1]],
                            "raw_gap_display": display_bytes(raw_gap),
                            "plain_gap_display": display_text(plain_gap),
                            "raw_gap_hex": raw_gap.hex(),
                            "raw_gap_len": len(raw_gap),
                            "plain_gap_len": len(plain_gap),
                        }
                    )

    by_context: dict[tuple[str, str, str, str], Counter[str]] = defaultdict(Counter)
    by_phrase: Counter[str] = Counter()
    for row in occurrence_rows:
        by_phrase[row["phrase_id"]] += 1
    for row in gap_rows:
        key = (row["phrase_id"], row["left_plain"], row["right_plain"], row["raw_gap_display"])
        by_context[key][row["plain_gap_display"]] += 1

    context_rows = []
    repeated_conflict_free = []
    conflicts = []
    for (phrase_id, left, right, raw_gap), candidates in sorted(by_context.items()):
        candidate_map = dict(sorted(candidates.items()))
        row = {
            "phrase_id": phrase_id,
            "left_plain": left,
            "right_plain": right,
            "raw_gap_display": raw_gap,
            "plain_gap_candidates": json.dumps(candidate_map, ensure_ascii=True, sort_keys=True),
            "candidate_count": len(candidate_map),
            "evidence_count": sum(candidate_map.values()),
        }
        context_rows.append(row)
        if len(candidate_map) > 1:
            conflicts.append(row)
        elif sum(candidate_map.values()) > 1:
            repeated_conflict_free.append({**row, "plain_gap": next(iter(candidate_map))})

    phrase_rows = [
        {"phrase_id": phrase_id, "occurrences": count}
        for phrase_id, count in sorted(by_phrase.items(), key=lambda item: (-item[1], item[0]))
    ]

    def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    write_tsv(out_dir / "input_inventory.tsv", input_rows, ["file", "size", "sha256"])
    write_tsv(
        out_dir / "phrase_occurrences.tsv",
        occurrence_rows,
        ["file", "phrase_id", "occurrence_index", "decoded_skeleton_start", "raw_start", "raw_end"],
    )
    write_tsv(
        out_dir / "phrase_counts.tsv",
        phrase_rows,
        ["phrase_id", "occurrences"],
    )
    write_tsv(
        out_dir / "gap_evidence.tsv",
        gap_rows,
        [
            "file",
            "phrase_id",
            "left_plain",
            "right_plain",
            "raw_gap_display",
            "plain_gap_display",
            "raw_gap_hex",
            "raw_gap_len",
            "plain_gap_len",
        ],
    )
    write_tsv(
        out_dir / "context_gap_summary.tsv",
        context_rows,
        ["phrase_id", "left_plain", "right_plain", "raw_gap_display", "plain_gap_candidates", "candidate_count", "evidence_count"],
    )
    write_tsv(
        out_dir / "context_gap_repeated_conflict_free.tsv",
        repeated_conflict_free,
        [
            "phrase_id",
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
        conflicts,
        ["phrase_id", "left_plain", "right_plain", "raw_gap_display", "plain_gap_candidates", "candidate_count", "evidence_count"],
    )

    manifest = {
        "phase": "2L",
        "input_proof": str(input_proof),
        "phrases": [{"phrase_id": p, "plaintext": t, "skeleton": phrase_skeleton(t)} for p, t in PHRASES],
        "result": {
            "handlers_scanned": len(input_rows),
            "phrase_occurrences": len(occurrence_rows),
            "gap_rows": len(gap_rows),
            "context_rows": len(context_rows),
            "repeated_conflict_free": len(repeated_conflict_free),
            "context_conflicts": len(conflicts),
            "solved": False,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "RESULT.md").write_text(
        "\n".join(
            [
                "# Phase 2L Standard Phrase Gap Audit Result",
                "",
                f"Input proof: `{input_proof}`",
                "",
                "## Result",
                "",
                f"- handlers scanned: {len(input_rows)}",
                f"- phrase occurrences: {len(occurrence_rows)}",
                f"- gap rows: {len(gap_rows)}",
                f"- context rows: {len(context_rows)}",
                f"- repeated conflict-free contexts: {len(repeated_conflict_free)}",
                f"- context conflicts: {len(conflicts)}",
                "- solved: false",
                "",
                "This proof expands repeated phrase-local transform evidence.",
                "It does not decode or commit full handler source.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit repeated standard phrase gaps from external small handler originals.")
    parser.add_argument("--input-proof", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("/tmp"), type=Path)
    args = parser.parse_args()
    print(run(args.input_proof, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
