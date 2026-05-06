#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(".")
SCHEMA_V2 = ROOT / "game/data/schemas/proposals/gear.schema.v2.proposal.json"
V2_READY = ROOT / "game/data/candidates/phase1c4_gear_schema_v2_proposal/gear_v2_ready_candidates.json"
V2_ALL = ROOT / "game/data/candidates/phase1c4_gear_schema_v2_proposal/gear_v2_adapted_candidates.json"
SOURCE_FACTS = ROOT / "game/data/candidates/phase1c2_gear_entities_from_wiki/gear_source_facts_from_wiki.candidates.json"
OUTDIR = ROOT / "game/data/candidates/phase1c5_gear_canonical_dry_run"

UTC_NOW = datetime.now(timezone.utc).isoformat()
TIER_COLORS = ["gray", "white", "green", "blue", "purple", "orange", "red"]
STAT_KEYS = ["hp", "atk", "def", "rush"]

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

def slugify(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"

def validate_dry_record(obj: dict[str, Any]) -> list[str]:
    errors = []

    for key in ["id", "name", "tier_color", "base_stats", "source"]:
        if obj.get(key) in [None, ""]:
            errors.append(f"missing_required:{key}")

    if obj.get("tier_color") not in TIER_COLORS:
        errors.append(f"invalid_tier_color:{obj.get('tier_color')}")

    if obj.get("slot") not in [None, "weapon", "armor", "accessory"]:
        errors.append(f"invalid_slot:{obj.get('slot')}")

    stats = obj.get("base_stats")
    if not isinstance(stats, dict):
        errors.append("invalid_base_stats:not_object")
    else:
        for stat in STAT_KEYS:
            if stat not in stats:
                errors.append(f"missing_stat_key:{stat}")
            elif stats[stat] is not None and not isinstance(stats[stat], (int, float)):
                errors.append(f"invalid_stat_value:{stat}")

    src = obj.get("source")
    if not isinstance(src, dict):
        errors.append("invalid_source:not_object")
    else:
        if not src.get("type"):
            errors.append("missing_source:type")
        if not src.get("url"):
            errors.append("missing_source:url")

    if obj.get("canonical_promotion") is not False:
        errors.append("canonical_promotion_not_false_in_dry_run")

    return errors

def canonicalize_candidate(obj: dict[str, Any]) -> dict[str, Any]:
    cid = slugify(obj.get("id") or obj.get("name"))
    stats = obj.get("base_stats") if isinstance(obj.get("base_stats"), dict) else {}

    canonical = {
        "id": cid,
        "name": obj.get("name"),
        "tier_color": obj.get("tier_color"),
        "slot": obj.get("slot"),
        "base_stats": {
            "hp": stats.get("hp"),
            "atk": stats.get("atk"),
            "def": stats.get("def"),
            "rush": stats.get("rush"),
        },
        "effect": obj.get("effect"),
        "origin": obj.get("origin"),
        "file_no": obj.get("file_no"),
        "icon_filename": obj.get("icon_filename"),
        "source": obj.get("source"),
        "spreadsheet_links": obj.get("spreadsheet_links") or [],
        "notes": obj.get("notes"),
        "tags": sorted(set((obj.get("tags") or []) + ["dry_run:phase1c5"])),
        "canonical_promotion": False,
    }

    return canonical

def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    schema = load_json(SCHEMA_V2)
    ready = load_json(V2_READY)
    all_candidates = load_json(V2_ALL)
    source_facts = load_json(SOURCE_FACTS)

    dry_records = []
    validation_rows = []
    blocked = []
    error_counts = Counter()
    tier_counts = Counter()
    duplicate_ids = []
    seen_ids = {}

    for obj in ready:
        rec = canonicalize_candidate(obj)

        if rec["id"] in seen_ids:
            duplicate_ids.append(rec["id"])
        seen_ids[rec["id"]] = seen_ids.get(rec["id"], 0) + 1

        errors = validate_dry_record(rec)
        for e in errors:
            error_counts[e] += 1

        tier_counts[str(rec.get("tier_color"))] += 1

        row = {
            "id": rec.get("id"),
            "name": rec.get("name"),
            "tier_color": rec.get("tier_color"),
            "slot": rec.get("slot"),
            "hp": rec.get("base_stats", {}).get("hp"),
            "atk": rec.get("base_stats", {}).get("atk"),
            "def": rec.get("base_stats", {}).get("def"),
            "rush": rec.get("base_stats", {}).get("rush"),
            "effect_present": bool(rec.get("effect")),
            "origin_present": bool(rec.get("origin")),
            "source_url": (rec.get("source") or {}).get("url") if isinstance(rec.get("source"), dict) else None,
            "errors": errors,
            "dry_run_status": "dry_run_ready_needs_manual_review" if not errors else "dry_run_blocked",
        }

        validation_rows.append(row)

        if errors:
            blocked.append(row)
        else:
            dry_records.append(rec)

    duplicate_detail = {k: v for k, v in seen_ids.items() if v > 1}

    by_tier_dir = OUTDIR / "dry_run_by_tier"
    by_tier_dir.mkdir(exist_ok=True)

    for color in TIER_COLORS:
        records = [r for r in dry_records if r.get("tier_color") == color]
        write_json(by_tier_dir / f"{color}.gear.dry_run.json", records)

    # One-file-per-gear dry-run tree for later canonical promotion review.
    one_file_dir = OUTDIR / "dry_run_records"
    one_file_dir.mkdir(exist_ok=True)
    for rec in dry_records:
        write_json(one_file_dir / f"{rec['id']}.json", rec)

    manifest = {
        "generated_at": UTC_NOW,
        "phase": "1C.5",
        "canonical_promotion": False,
        "schema_proposal": str(SCHEMA_V2),
        "input_ready_candidates": len(ready),
        "input_all_candidates": len(all_candidates),
        "input_source_facts": len(source_facts),
        "dry_run_ready_records": len(dry_records),
        "dry_run_blocked_records": len(blocked),
        "duplicate_ids": duplicate_detail,
        "tier_counts": dict(tier_counts),
        "error_counts": dict(error_counts),
        "outputs": [
            "gear_canonical_dry_run_records.json",
            "gear_canonical_dry_run_validation_rows.json",
            "gear_canonical_dry_run_validation_rows.csv",
            "gear_canonical_dry_run_blocked.json",
            "dry_run_by_tier/",
            "dry_run_records/",
            "manual_promotion_packet.md",
            "manifest.json",
        ],
    }

    write_json(OUTDIR / "gear_canonical_dry_run_records.json", dry_records)
    write_json(OUTDIR / "gear_canonical_dry_run_validation_rows.json", validation_rows)
    write_json(OUTDIR / "gear_canonical_dry_run_blocked.json", blocked)
    write_json(OUTDIR / "manifest.json", manifest)

    with (OUTDIR / "gear_canonical_dry_run_validation_rows.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "id", "name", "tier_color", "slot", "hp", "atk", "def", "rush",
            "effect_present", "origin_present", "source_url", "errors", "dry_run_status"
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in validation_rows:
            writer.writerow({
                **{k: row.get(k) for k in fields if k != "errors"},
                "errors": "; ".join(row.get("errors") or []),
            })

    md = []
    md.append("# Phase 1C.5 Gear Canonical Import Dry Run Packet")
    md.append("")
    md.append(f"Generated UTC: {UTC_NOW}")
    md.append("")
    md.append("## Status")
    md.append("")
    md.append("No canonical files were written.")
    md.append("This packet shows what would be promoted if the v2 schema is accepted as active.")
    md.append("")
    md.append("## Counts")
    md.append("")
    md.append(f"- Input ready candidates: {len(ready)}")
    md.append(f"- Dry-run ready records: {len(dry_records)}")
    md.append(f"- Dry-run blocked records: {len(blocked)}")
    md.append(f"- Duplicate IDs: {len(duplicate_detail)}")
    md.append("")
    md.append("## Tier Counts")
    md.append("")
    for tier, count in sorted(tier_counts.items()):
        md.append(f"- {tier}: {count}")
    md.append("")
    md.append("## Error Counts")
    md.append("")
    if error_counts:
        for err, count in error_counts.most_common():
            md.append(f"- {err}: {count}")
    else:
        md.append("- None")
    md.append("")
    md.append("## Promotion Preview")
    md.append("")
    md.append("| ID | Name | Tier | HP | ATK | DEF | RUSH | Effect | Origin |")
    md.append("|---|---|---|---:|---:|---:|---:|---|---|")
    for rec in dry_records[:120]:
        stats = rec.get("base_stats") or {}
        effect = str(rec.get("effect") or "")[:80]
        origin = str(rec.get("origin") or "")[:80]
        md.append(
            f"| {rec.get('id')} | {rec.get('name')} | {rec.get('tier_color')} | "
            f"{stats.get('hp')} | {stats.get('atk')} | {stats.get('def')} | {stats.get('rush')} | {effect} | {origin} |"
        )
    md.append("")
    md.append("## PM Decision Needed")
    md.append("")
    md.append("If this packet is acceptable, the next phase can activate schema v2 and write canonical gear records.")
    md.append("Recommended next phase: Phase 1C.6 schema activation and canonical import with final stop gate.")
    md.append("")

    (OUTDIR / "manual_promotion_packet.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
