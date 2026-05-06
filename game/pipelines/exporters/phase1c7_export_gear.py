#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(".")
SCHEMA = ROOT / "game/data/schemas/gear.schema.json"
CANON_DIR = ROOT / "game/data/canonical/gear"
INDEX_JSON = ROOT / "game/data/indexes/gear.index.json"
INDEX_CSV = ROOT / "game/data/indexes/gear.index.csv"
EXPORT_DIR = ROOT / "game/data/exports/gear"
REPORT = ROOT / "game/reports/audits/phase1c7-canonical-gear-qa-and-export-2026-05-06.md"

UTC_NOW = datetime.now(timezone.utc).isoformat()

TIER_ORDER = {
    "gray": 0,
    "white": 1,
    "green": 2,
    "blue": 3,
    "purple": 4,
    "orange": 5,
    "red": 6,
}

STAT_KEYS = ["hp", "atk", "def", "rush"]

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_record(path: Path, rec: dict[str, Any]) -> list[str]:
    errors = []

    for key in ["id", "name", "tier_color", "base_stats", "source"]:
        if rec.get(key) in [None, ""]:
            errors.append(f"{path.name}:missing_required:{key}")

    if rec.get("tier_color") not in TIER_ORDER:
        errors.append(f"{path.name}:invalid_tier_color:{rec.get('tier_color')}")

    if rec.get("slot") not in [None, "weapon", "armor", "accessory"]:
        errors.append(f"{path.name}:invalid_slot:{rec.get('slot')}")

    stats = rec.get("base_stats")
    if not isinstance(stats, dict):
        errors.append(f"{path.name}:invalid_base_stats:not_object")
    else:
        for stat in STAT_KEYS:
            if stat not in stats:
                errors.append(f"{path.name}:missing_stat_key:{stat}")
            elif stats[stat] is not None and not isinstance(stats[stat], (int, float)):
                errors.append(f"{path.name}:invalid_stat:{stat}")

    source = rec.get("source")
    if not isinstance(source, dict):
        errors.append(f"{path.name}:invalid_source:not_object")
    else:
        if not source.get("url"):
            errors.append(f"{path.name}:missing_source_url")
        if not source.get("type"):
            errors.append(f"{path.name}:missing_source_type")

    if rec.get("canonical_promotion") is not True:
        errors.append(f"{path.name}:canonical_promotion_not_true")

    return errors

def sort_key(rec: dict[str, Any]) -> tuple[int, str]:
    return (TIER_ORDER.get(rec.get("tier_color"), -1), str(rec.get("name") or ""))

def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    schema = load_json(SCHEMA)
    index = load_json(INDEX_JSON)

    files = sorted(CANON_DIR.glob("*.json"))
    if len(files) != 313:
        raise SystemExit(f"STOP: expected 313 canonical gear json files, got {len(files)}")

    records = []
    errors = []
    ids = []
    names = []

    for path in files:
        rec = load_json(path)
        records.append(rec)
        ids.append(rec.get("id"))
        names.append(rec.get("name"))
        errors.extend(validate_record(path, rec))

    duplicate_ids = {k: v for k, v in Counter(ids).items() if v > 1}
    duplicate_names = {k: v for k, v in Counter(names).items() if v > 1}

    if duplicate_ids:
        errors.append(f"duplicate_ids:{duplicate_ids}")

    if index.get("record_count") != 313:
        errors.append(f"index_record_count_mismatch:{index.get('record_count')}")

    index_ids = [row.get("id") for row in index.get("records", [])]
    missing_from_index = sorted(set(ids) - set(index_ids))
    extra_in_index = sorted(set(index_ids) - set(ids))

    if missing_from_index:
        errors.append(f"missing_from_index:{missing_from_index[:20]}")
    if extra_in_index:
        errors.append(f"extra_in_index:{extra_in_index[:20]}")

    if errors:
        write_json(EXPORT_DIR / "qa_errors.json", errors)
        raise SystemExit("STOP: canonical QA errors found. See qa_errors.json")

    sorted_records = sorted(records, key=sort_key)

    by_tier = defaultdict(list)
    for rec in sorted_records:
        by_tier[rec.get("tier_color")].append(rec)

    lightweight_cards = []
    search_index = []
    stats_summary = []

    for rec in sorted_records:
        stats = rec.get("base_stats") or {}
        lightweight_cards.append({
            "id": rec.get("id"),
            "name": rec.get("name"),
            "tier_color": rec.get("tier_color"),
            "slot": rec.get("slot"),
            "hp": stats.get("hp"),
            "atk": stats.get("atk"),
            "def": stats.get("def"),
            "rush": stats.get("rush"),
            "effect": rec.get("effect"),
            "origin": rec.get("origin"),
            "icon_filename": rec.get("icon_filename"),
        })

        search_index.append({
            "id": rec.get("id"),
            "name": rec.get("name"),
            "tier_color": rec.get("tier_color"),
            "keywords": sorted(set([
                str(rec.get("id") or ""),
                str(rec.get("name") or ""),
                str(rec.get("tier_color") or ""),
                str(rec.get("effect") or ""),
                str(rec.get("origin") or ""),
            ])),
        })

        stats_summary.append({
            "id": rec.get("id"),
            "name": rec.get("name"),
            "tier_color": rec.get("tier_color"),
            "total_hard_stats": sum((stats.get(k) or 0) for k in STAT_KEYS),
            "stats": stats,
        })

    tier_counts = {tier: len(rows) for tier, rows in sorted(by_tier.items(), key=lambda kv: TIER_ORDER.get(kv[0], -1))}

    export_all = {
        "generated_at": UTC_NOW,
        "schema": "game/data/schemas/gear.schema.json",
        "source": "game/data/canonical/gear",
        "record_count": len(sorted_records),
        "tier_counts": tier_counts,
        "records": sorted_records,
    }

    export_cards = {
        "generated_at": UTC_NOW,
        "record_count": len(lightweight_cards),
        "tier_counts": tier_counts,
        "cards": lightweight_cards,
    }

    export_search = {
        "generated_at": UTC_NOW,
        "record_count": len(search_index),
        "records": search_index,
    }

    export_stats = {
        "generated_at": UTC_NOW,
        "record_count": len(stats_summary),
        "records": sorted(stats_summary, key=lambda r: (TIER_ORDER.get(r["tier_color"], -1), -r["total_hard_stats"], r["name"])),
    }

    write_json(EXPORT_DIR / "gear.canonical.full.json", export_all)
    write_json(EXPORT_DIR / "gear.web.cards.json", export_cards)
    write_json(EXPORT_DIR / "gear.search.json", export_search)
    write_json(EXPORT_DIR / "gear.stats-summary.json", export_stats)
    write_json(EXPORT_DIR / "gear.by-tier.json", dict(by_tier))

    with (EXPORT_DIR / "gear.web.cards.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["id", "name", "tier_color", "slot", "hp", "atk", "def", "rush", "effect", "origin", "icon_filename"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in lightweight_cards:
            writer.writerow(row)

    export_files = sorted([p for p in EXPORT_DIR.glob("*") if p.is_file()])
    export_manifest = {
        "generated_at": UTC_NOW,
        "phase": "1C.7",
        "canonical_qa_pass": True,
        "canonical_record_count": len(records),
        "index_record_count": index.get("record_count"),
        "duplicate_ids": duplicate_ids,
        "duplicate_names": duplicate_names,
        "tier_counts": tier_counts,
        "schema_title": schema.get("title"),
        "schema_required": schema.get("required"),
        "exports": [
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in export_files
            if path.name != "manifest.json"
        ],
    }

    write_json(EXPORT_DIR / "manifest.json", export_manifest)

    report = []
    report.append("# Phase 1C.7 Canonical Gear QA and Export Audit")
    report.append("")
    report.append(f"Generated UTC: {UTC_NOW}")
    report.append("")
    report.append("## Result")
    report.append("")
    report.append("Canonical gear QA passed and website/bot export artifacts were generated.")
    report.append("")
    report.append("## Counts")
    report.append("")
    report.append(f"- Canonical gear records: {len(records)}")
    report.append(f"- Index records: {index.get('record_count')}")
    report.append(f"- Duplicate IDs: {len(duplicate_ids)}")
    report.append(f"- Duplicate names: {len(duplicate_names)}")
    report.append("")
    report.append("## Tier Counts")
    report.append("")
    for tier, count in tier_counts.items():
        report.append(f"- {tier}: {count}")
    report.append("")
    report.append("## Export Files")
    report.append("")
    for item in export_manifest["exports"]:
        report.append(f"- {item['path']} — {item['bytes']} bytes — sha256 {item['sha256']}")
    report.append("")
    report.append("## Next Step")
    report.append("")
    report.append("Phase 1D should import or map gear icon assets and create an asset manifest keyed by canonical gear ID.")
    report.append("After icon assets are stable, export files can be wired into slimy-monorepo website routes.")
    report.append("")

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(export_manifest, indent=2))

if __name__ == "__main__":
    main()
