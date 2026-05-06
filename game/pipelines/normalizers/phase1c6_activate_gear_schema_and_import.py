#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(".")
SCHEMA_ACTIVE = ROOT / "game/data/schemas/gear.schema.json"
SCHEMA_V2 = ROOT / "game/data/schemas/proposals/gear.schema.v2.proposal.json"
SCHEMA_ARCHIVE = ROOT / "game/data/schemas/archive/gear.schema.v1.pre-1c6.json"

DRY_RECORDS = ROOT / "game/data/candidates/phase1c5_gear_canonical_dry_run/gear_canonical_dry_run_records.json"
DRY_MANIFEST = ROOT / "game/data/candidates/phase1c5_gear_canonical_dry_run/manifest.json"

CANON_DIR = ROOT / "game/data/canonical/gear"
INDEX_FILE = ROOT / "game/data/indexes/gear.index.json"
OUT_REPORT = ROOT / "game/reports/audits/phase1c6-gear-schema-activation-and-canonical-import-2026-05-06.md"

UTC_NOW = datetime.now(timezone.utc).isoformat()
TIER_COLORS = ["gray", "white", "green", "blue", "purple", "orange", "red"]
STAT_KEYS = ["hp", "atk", "def", "rush"]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def validate_record(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []

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
        if not any(stats.get(k) is not None for k in STAT_KEYS):
            errors.append("missing_all_stats")

    source = obj.get("source")
    if not isinstance(source, dict):
        errors.append("invalid_source:not_object")
    else:
        if not source.get("type"):
            errors.append("missing_source_type")
        if not source.get("url"):
            errors.append("missing_source_url")

    return errors


def main() -> None:
    CANON_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_ARCHIVE.parent.mkdir(parents=True, exist_ok=True)

    manifest = load_json(DRY_MANIFEST)
    records = load_json(DRY_RECORDS)
    schema_v2 = load_json(SCHEMA_V2)

    if manifest.get("dry_run_ready_records") != 313:
        raise SystemExit("STOP: dry_run_ready_records not 313")
    if manifest.get("dry_run_blocked_records") != 0:
        raise SystemExit("STOP: dry_run_blocked_records not 0")
    if manifest.get("duplicate_ids"):
        raise SystemExit("STOP: duplicate IDs present")
    if manifest.get("error_counts"):
        raise SystemExit("STOP: dry-run error counts present")
    if len(records) != 313:
        raise SystemExit(f"STOP: expected 313 records, got {len(records)}")

    ids = [r.get("id") for r in records]
    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        raise SystemExit(f"STOP: duplicate IDs in dry records: {duplicate_ids}")

    validation_errors = {}
    for rec in records:
        errs = validate_record(rec)
        if errs:
            validation_errors[rec.get("id")] = errs

    if validation_errors:
        raise SystemExit(f"STOP: validation errors: {validation_errors}")

    if not SCHEMA_ARCHIVE.exists():
        shutil.copy2(SCHEMA_ACTIVE, SCHEMA_ARCHIVE)

    write_json(SCHEMA_ACTIVE, schema_v2)

    for rec in records:
        rec = dict(rec)
        rec["canonical_promotion"] = True
        rec["canonical_promoted_at"] = UTC_NOW
        rec["canonical_source_phase"] = "phase1c6"
        write_json(CANON_DIR / f"{rec['id']}.json", rec)

    index_rows = []
    tier_counts = Counter()

    for rec in sorted(records, key=lambda x: x["id"]):
        stats = rec.get("base_stats") or {}
        tier_counts[str(rec.get("tier_color"))] += 1
        index_rows.append({
            "id": rec.get("id"),
            "entity_type": "gear",
            "name": rec.get("name"),
            "tier_color": rec.get("tier_color"),
            "slot": rec.get("slot"),
            "data_file": f"game/data/canonical/gear/{rec['id']}.json",
            "icon_filename": rec.get("icon_filename"),
            "search_keywords": sorted(set([
                str(rec.get("name") or ""),
                str(rec.get("tier_color") or ""),
                str(rec.get("origin") or ""),
            ])),
            "stats": {
                "hp": stats.get("hp"),
                "atk": stats.get("atk"),
                "def": stats.get("def"),
                "rush": stats.get("rush"),
            },
        })

    index = {
        "generated_at": UTC_NOW,
        "entity_type": "gear",
        "record_count": len(index_rows),
        "source": "phase1c6 canonical import from Gear.wiki dry run",
        "schema": "game/data/schemas/gear.schema.json",
        "records": index_rows,
    }

    write_json(INDEX_FILE, index)

    with (ROOT / "game/data/indexes/gear.index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["id", "name", "tier_color", "slot", "hp", "atk", "def", "rush", "data_file"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in index_rows:
            stats = row.get("stats") or {}
            writer.writerow({
                "id": row.get("id"),
                "name": row.get("name"),
                "tier_color": row.get("tier_color"),
                "slot": row.get("slot"),
                "hp": stats.get("hp"),
                "atk": stats.get("atk"),
                "def": stats.get("def"),
                "rush": stats.get("rush"),
                "data_file": row.get("data_file"),
            })

    report_lines = []
    report_lines.append("# Phase 1C.6 Gear Schema Activation and Canonical Import Audit")
    report_lines.append("")
    report_lines.append(f"Generated UTC: {UTC_NOW}")
    report_lines.append("")
    report_lines.append("## Result")
    report_lines.append("")
    report_lines.append("Gear schema v2 was activated and canonical gear records were imported from the approved dry-run packet.")
    report_lines.append("")
    report_lines.append("## Counts")
    report_lines.append("")
    report_lines.append(f"- Canonical gear records written: {len(records)}")
    report_lines.append(f"- Duplicate IDs: {len(duplicate_ids)}")
    report_lines.append(f"- Validation errors: {len(validation_errors)}")
    report_lines.append("")
    report_lines.append("## Tier Counts")
    report_lines.append("")
    for tier, count in sorted(tier_counts.items()):
        report_lines.append(f"- {tier}: {count}")
    report_lines.append("")
    report_lines.append("## Files")
    report_lines.append("")
    report_lines.append(f"- Active schema: {SCHEMA_ACTIVE}")
    report_lines.append(f"- Archived v1 schema: {SCHEMA_ARCHIVE}")
    report_lines.append(f"- Canonical gear dir: {CANON_DIR}")
    report_lines.append(f"- Gear index: {INDEX_FILE}")
    report_lines.append("")
    report_lines.append("## Safety")
    report_lines.append("")
    report_lines.append("No non-gear canonical domains were modified.")
    report_lines.append("The import came from Phase 1C.5 dry-run records only.")
    report_lines.append("")

    OUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "generated_at": UTC_NOW,
        "canonical_records_written": len(records),
        "duplicate_ids": duplicate_ids,
        "validation_error_count": len(validation_errors),
        "tier_counts": dict(tier_counts),
        "active_schema": str(SCHEMA_ACTIVE),
        "schema_archive": str(SCHEMA_ARCHIVE),
        "canonical_dir": str(CANON_DIR),
        "index_file": str(INDEX_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
