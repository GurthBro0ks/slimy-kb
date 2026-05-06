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
SCHEMA = ROOT / "game/data/schemas/gear.schema.json"
CANDIDATES = ROOT / "game/data/candidates/phase1c2_gear_entities_from_wiki/gear_entities_from_wiki.candidates.json"
STAT_ROWS = ROOT / "game/data/candidates/phase1c2_gear_entities_from_wiki/gear_stat_scaling_from_wiki.candidates.json"
SOURCE_FACTS = ROOT / "game/data/candidates/phase1c2_gear_entities_from_wiki/gear_source_facts_from_wiki.candidates.json"
OUTDIR = ROOT / "game/data/candidates/phase1c3_gear_schema_validation"

UTC_NOW = datetime.now(timezone.utc).isoformat()

ALLOWED_SLOT = {"weapon", "armor", "accessory"}
ALLOWED_RARITY = {"common", "uncommon", "rare", "epic", "legendary", "mythic"}

COLOR_TO_RARITY_CANDIDATE = {
    "green": "uncommon",
    "blue": "rare",
    "purple": "epic",
    "orange": "legendary",
    "red": "mythic",
    "white": "common",
}


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


def to_number(value: Any) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    text = re.sub(r"[^0-9.+-]", "", text)
    if not text or text in {"+", "-", ".", "+.", "-."}:
        return None
    try:
        n = float(text)
        return int(n) if n.is_integer() else n
    except Exception:
        return None


def infer_color_from_candidate(ent: dict[str, Any]) -> str | None:
    # Phase 1C.2 may have Color in cells_clean because gearrow template has Color as final argument.
    for key in ["color", "color_raw", "rarity_color"]:
        if ent.get(key):
            return str(ent[key]).strip().lower()

    raw = ent.get("raw_row") if isinstance(ent.get("raw_row"), dict) else {}
    cells = raw.get("cells_clean") or ent.get("cells_clean") or []
    if isinstance(cells, list):
        for cell in reversed(cells):
            s = str(cell).strip().lower()
            if s in COLOR_TO_RARITY_CANDIDATE:
                return s
    return None


def infer_slot_candidate(ent: dict[str, Any]) -> str | None:
    text_parts = [
        ent.get("source_section"),
        ent.get("source_subsection"),
        ent.get("origin_raw"),
        ent.get("effect_raw"),
    ]
    raw = ent.get("raw_row") if isinstance(ent.get("raw_row"), dict) else {}
    text_parts.extend(raw.get("cells_clean") or [])
    text = " ".join(str(x or "").lower() for x in text_parts)

    # Conservative guesses only.
    if "armor" in text or "helmet" in text or "suit" in text or "cape" in text or "shield" in text:
        return "armor"
    if "weapon" in text or "sword" in text or "wand" in text or "gun" in text or "staff" in text or "blade" in text:
        return "weapon"
    if "ring" in text or "amulet" in text or "charm" in text or "badge" in text or "accessory" in text:
        return "accessory"
    return None


def build_schema_candidate(ent: dict[str, Any]) -> dict[str, Any]:
    stats = ent.get("stats") if isinstance(ent.get("stats"), dict) else {}
    color = infer_color_from_candidate(ent)
    rarity = COLOR_TO_RARITY_CANDIDATE.get(color) if color else None
    slot = infer_slot_candidate(ent)

    return {
        "id": ent.get("id") or slugify(ent.get("name")),
        "name": ent.get("name"),
        "slot": slot,
        "rarity": rarity,
        "base_stats": {
            "hp": to_number(stats.get("hp")),
            "atk": to_number(stats.get("atk")),
            "def": to_number(stats.get("def")),
            "rush": to_number(stats.get("rush")),
        },
        "set_name": None,
        "set_bonus": None,
        "enhancement_cap": None,
        "source": ent.get("origin_raw"),
        "icon_ref": ent.get("icon_filename"),
        "notes": "Candidate generated from Gear.wiki aggregate table. Requires manual review before canonical promotion.",
        "tags": [
            "source:wiki_gg",
            "phase:1c3",
            "candidate_only",
        ],
        "_candidate_meta": {
            "source_entity_file": "game/data/candidates/phase1c2_gear_entities_from_wiki/gear_entities_from_wiki.candidates.json",
            "source_url": "https://supersnail.wiki.gg/wiki/Gear",
            "file_no": ent.get("file_no"),
            "color_candidate": color,
            "slot_inference": "heuristic" if slot else "missing",
            "rarity_inference": "color_map" if rarity else "missing",
            "source_confidence": ent.get("confidence"),
            "canonical_promotion": False,
            "spreadsheet_links": ent.get("spreadsheet_links", []),
            "effect_raw": ent.get("effect_raw"),
            "raw_cells": ent.get("cells_clean") or (ent.get("raw_row") or {}).get("cells_clean"),
        },
    }


def validate_candidate(obj: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    required = schema.get("required", [])
    for key in required:
        if key not in obj or obj.get(key) in [None, ""]:
            errors.append(f"missing_required:{key}")

    if not obj.get("id"):
        errors.append("missing:id")
    if not obj.get("name"):
        errors.append("missing:name")

    slot = obj.get("slot")
    if slot is None:
        errors.append("missing_or_uninferred:slot")
    elif slot not in ALLOWED_SLOT:
        errors.append(f"invalid_slot:{slot}")

    rarity = obj.get("rarity")
    if rarity is not None and rarity not in ALLOWED_RARITY:
        errors.append(f"invalid_rarity:{rarity}")

    base_stats = obj.get("base_stats")
    if not isinstance(base_stats, dict):
        errors.append("invalid_base_stats:not_object")
    else:
        for stat in ["hp", "atk", "def", "rush"]:
            value = base_stats.get(stat)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"invalid_base_stat:{stat}:not_number")

    if obj.get("tags") is not None and not isinstance(obj.get("tags"), list):
        errors.append("invalid_tags:not_array")

    return errors


def readiness_from_errors(errors: list[str], obj: dict[str, Any]) -> str:
    hard = [e for e in errors if e.startswith("missing_required") or e.startswith("missing:id") or e.startswith("missing:name")]
    if hard:
        return "blocked_missing_required"

    if any(e.startswith("missing_or_uninferred:slot") for e in errors):
        return "blocked_schema_gap_slot"

    if any(e.startswith("invalid_") for e in errors):
        return "blocked_invalid_shape"

    stats = obj.get("base_stats") or {}
    if not any(stats.get(k) is not None for k in ["hp", "atk", "def", "rush"]):
        return "blocked_no_stats"

    return "schema_shape_ready_needs_manual_review"


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    schema = load_json(SCHEMA)
    entities = load_json(CANDIDATES)
    stat_rows = load_json(STAT_ROWS)
    source_facts = load_json(SOURCE_FACTS)

    schema_ready = []
    validation_rows = []
    blocked = []
    ready = []
    error_counts = Counter()
    readiness_counts = Counter()
    slot_counts = Counter()
    rarity_counts = Counter()

    for ent in entities:
        obj = build_schema_candidate(ent)
        errors = validate_candidate(obj, schema)
        readiness = readiness_from_errors(errors, obj)

        row = {
            "id": obj.get("id"),
            "name": obj.get("name"),
            "readiness": readiness,
            "errors": errors,
            "slot_candidate": obj.get("slot"),
            "rarity_candidate": obj.get("rarity"),
            "base_stats": obj.get("base_stats"),
            "source_confidence": obj["_candidate_meta"].get("source_confidence"),
            "color_candidate": obj["_candidate_meta"].get("color_candidate"),
            "effect_raw": obj["_candidate_meta"].get("effect_raw"),
            "source": obj.get("source"),
            "canonical_promotion": False,
        }

        for err in errors:
            error_counts[err] += 1
        readiness_counts[readiness] += 1
        slot_counts[str(obj.get("slot"))] += 1
        rarity_counts[str(obj.get("rarity"))] += 1

        schema_ready.append(obj)
        validation_rows.append(row)

        if readiness == "schema_shape_ready_needs_manual_review":
            ready.append(obj)
        else:
            blocked.append(row)

    schema_gap_report = {
        "generated_at": UTC_NOW,
        "schema_file": str(SCHEMA),
        "candidate_input": str(CANDIDATES),
        "canonical_promotion": False,
        "candidate_count": len(entities),
        "schema_ready_needs_manual_review": len(ready),
        "blocked_count": len(blocked),
        "readiness_counts": dict(readiness_counts),
        "error_counts": dict(error_counts),
        "slot_counts": dict(slot_counts),
        "rarity_counts": dict(rarity_counts),
        "schema_observations": [
            "Current gear.schema.json appears to require slot, but Gear.wiki aggregate rows do not always expose a direct slot.",
            "Current rarity enum is semantic, while Gear.wiki uses color/tier values. A formal color-to-rarity mapping needs PM approval before canonical promotion.",
            "Gear.wiki provides HP, ATK, DEF, and RUSH cleanly for most candidates.",
            "Effects and origin fields are raw text and need downstream normalization.",
        ],
        "recommended_next_actions": [
            "Review whether gear.schema.json should add gear_color or tier_color as a first-class field.",
            "Review whether slot should be optional/nullable or inferred from separate source data.",
            "Manually inspect schema_shape_ready_needs_manual_review records before promotion.",
            "Keep blocked records as candidates until schema gap is resolved.",
        ],
    }

    promotion_packet_md = []
    promotion_packet_md.append("# Phase 1C.3 Manual Promotion Readiness Packet")
    promotion_packet_md.append("")
    promotion_packet_md.append(f"Generated UTC: {UTC_NOW}")
    promotion_packet_md.append("")
    promotion_packet_md.append("## Status")
    promotion_packet_md.append("")
    promotion_packet_md.append("No canonical promotion was performed.")
    promotion_packet_md.append("")
    promotion_packet_md.append("## Counts")
    promotion_packet_md.append("")
    promotion_packet_md.append(f"- Total candidates: {len(entities)}")
    promotion_packet_md.append(f"- Schema-shape ready but still needs manual review: {len(ready)}")
    promotion_packet_md.append(f"- Blocked: {len(blocked)}")
    promotion_packet_md.append("")
    promotion_packet_md.append("## Readiness Counts")
    promotion_packet_md.append("")
    for key, value in sorted(readiness_counts.items()):
        promotion_packet_md.append(f"- {key}: {value}")
    promotion_packet_md.append("")
    promotion_packet_md.append("## Top Schema Issues")
    promotion_packet_md.append("")
    for key, value in error_counts.most_common(30):
        promotion_packet_md.append(f"- {key}: {value}")
    promotion_packet_md.append("")
    promotion_packet_md.append("## Ready Candidate Preview")
    promotion_packet_md.append("")
    promotion_packet_md.append("| ID | Name | Slot | Rarity | HP | ATK | DEF | RUSH | Source |")
    promotion_packet_md.append("|---|---|---|---|---:|---:|---:|---:|---|")
    for obj in ready[:100]:
        stats = obj.get("base_stats") or {}
        promotion_packet_md.append(
            f"| {obj.get('id')} | {obj.get('name')} | {obj.get('slot')} | {obj.get('rarity')} | "
            f"{stats.get('hp')} | {stats.get('atk')} | {stats.get('def')} | {stats.get('rush')} | {str(obj.get('source') or '')[:80]} |"
        )
    promotion_packet_md.append("")
    promotion_packet_md.append("## Blocked Candidate Preview")
    promotion_packet_md.append("")
    promotion_packet_md.append("| ID | Name | Readiness | Errors |")
    promotion_packet_md.append("|---|---|---|---|")
    for row in blocked[:120]:
        promotion_packet_md.append(f"| {row.get('id')} | {row.get('name')} | {row.get('readiness')} | {'; '.join(row.get('errors') or [])} |")
    promotion_packet_md.append("")
    promotion_packet_md.append("## PM Decision Needed")
    promotion_packet_md.append("")
    promotion_packet_md.append("Before promotion, decide whether the canonical gear schema should be updated for actual Super Snail data.")
    promotion_packet_md.append("The biggest expected schema gap is slot inference and color/tier mapping.")
    promotion_packet_md.append("")

    write_json(OUTDIR / "gear_schema_ready_candidates.json", ready)
    write_json(OUTDIR / "gear_schema_adapted_all_candidates.json", schema_ready)
    write_json(OUTDIR / "gear_schema_validation_rows.json", validation_rows)
    write_json(OUTDIR / "gear_schema_blocked_candidates.json", blocked)
    write_json(OUTDIR / "gear_schema_gap_report.json", schema_gap_report)
    (OUTDIR / "manual_promotion_readiness_packet.md").write_text("\n".join(promotion_packet_md) + "\n", encoding="utf-8")

    with (OUTDIR / "gear_schema_validation_rows.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "id",
            "name",
            "readiness",
            "errors",
            "slot_candidate",
            "rarity_candidate",
            "hp",
            "atk",
            "def",
            "rush",
            "source_confidence",
            "color_candidate",
            "source",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in validation_rows:
            stats = row.get("base_stats") or {}
            writer.writerow({
                "id": row.get("id"),
                "name": row.get("name"),
                "readiness": row.get("readiness"),
                "errors": "; ".join(row.get("errors") or []),
                "slot_candidate": row.get("slot_candidate"),
                "rarity_candidate": row.get("rarity_candidate"),
                "hp": stats.get("hp"),
                "atk": stats.get("atk"),
                "def": stats.get("def"),
                "rush": stats.get("rush"),
                "source_confidence": row.get("source_confidence"),
                "color_candidate": row.get("color_candidate"),
                "source": row.get("source"),
            })

    manifest = {
        "generated_at": UTC_NOW,
        "phase": "1C.3",
        "canonical_promotion": False,
        "input_candidates": len(entities),
        "input_stat_rows": len(stat_rows),
        "input_source_facts": len(source_facts),
        "schema_ready_needs_manual_review": len(ready),
        "blocked_count": len(blocked),
        "readiness_counts": dict(readiness_counts),
        "error_counts": dict(error_counts),
        "outputs": [
            "gear_schema_ready_candidates.json",
            "gear_schema_adapted_all_candidates.json",
            "gear_schema_validation_rows.json",
            "gear_schema_validation_rows.csv",
            "gear_schema_blocked_candidates.json",
            "gear_schema_gap_report.json",
            "manual_promotion_readiness_packet.md",
            "manifest.json",
        ],
    }

    write_json(OUTDIR / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
