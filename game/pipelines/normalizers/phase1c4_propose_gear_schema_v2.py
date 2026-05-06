#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(".")
SCHEMA_V1 = ROOT / "game/data/schemas/gear.schema.json"
CANDIDATES = ROOT / "game/data/candidates/phase1c2_gear_entities_from_wiki/gear_entities_from_wiki.candidates.json"
PHASE1C3 = ROOT / "game/data/candidates/phase1c3_gear_schema_validation/gear_schema_validation_rows.json"
OUTDIR = ROOT / "game/data/candidates/phase1c4_gear_schema_v2_proposal"
SCHEMA_PROPOSAL = ROOT / "game/data/schemas/proposals/gear.schema.v2.proposal.json"

UTC_NOW = datetime.now(timezone.utc).isoformat()

TIER_COLORS = ["white", "gray", "green", "blue", "purple", "orange", "red"]
STAT_KEYS = ["hp", "atk", "def", "rush"]

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

def to_number(value: Any) -> int | float | None:
    if isinstance(value, bool) or value in [None, ""]:
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        text = str(value).replace(",", "").strip()
        n = float(text)
        return int(n) if n.is_integer() else n
    except Exception:
        return None

def load_color_map_from_wiki() -> dict[str, str]:
    """Parse Gear.wiki to extract color from raw {{gearrow}} template lines."""
    gear_wiki = ROOT / "game/sources/wiki_gg/Gear.wiki"
    text = gear_wiki.read_text(encoding="utf-8", errors="replace")
    color_map = {}
    
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{{gearrow|"):
            continue
        # Extract the template body
        match = re.match(r"\{\{gearrow\|(.+)\}\}", line)
        if not match:
            continue
        body = match.group(1)
        # Find the last pipe-separated argument that's a color
        # But we need to handle nested templates, so split carefully
        args = []
        current = []
        depth = 0
        for char in body:
            if char == '{':
                depth += 1
                current.append(char)
            elif char == '}':
                depth -= 1
                current.append(char)
            elif char == '|' and depth == 0:
                args.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            args.append(''.join(current).strip())
        
        if len(args) >= 2:
            name = args[0]
            # Some gearrows have 10 args with set name as last arg (e.g., Lotus Platform)
            # Try last arg first, then second-to-last
            for idx in [-1, -2]:
                if abs(idx) <= len(args):
                    arg = args[idx].lower().strip()
                    if arg in TIER_COLORS:
                        color_map[name] = arg
                        break
    
    return color_map

# Load color map once
COLOR_MAP = load_color_map_from_wiki()

def extract_color(ent: dict[str, Any]) -> str | None:
    # First try the color map from raw wiki parsing
    name = ent.get("name")
    if name and name in COLOR_MAP:
        return COLOR_MAP[name]
    
    # Fallback to checking cells
    raw_row = ent.get("raw_row") if isinstance(ent.get("raw_row"), dict) else {}
    cells = ent.get("cells_clean") or raw_row.get("cells_clean") or []
    for cell in reversed(cells):
        s = str(cell).strip().lower()
        if s in TIER_COLORS:
            return s
    return None

def adapt_to_v2(ent: dict[str, Any]) -> dict[str, Any]:
    stats = ent.get("stats") if isinstance(ent.get("stats"), dict) else {}
    base_stats = {k: to_number(stats.get(k)) for k in STAT_KEYS}

    return {
        "id": ent.get("id"),
        "name": ent.get("name"),
        "tier_color": extract_color(ent),
        "slot": ent.get("slot") or None,
        "base_stats": base_stats,
        "effect": ent.get("effect_raw"),
        "origin": ent.get("origin_raw"),
        "file_no": ent.get("file_no"),
        "icon_filename": ent.get("icon_filename"),
        "source": {
            "type": "wiki_gg",
            "url": "https://supersnail.wiki.gg/wiki/Gear",
            "file": ent.get("source_file"),
            "section": ent.get("source_section"),
            "subsection": ent.get("source_subsection"),
        },
        "spreadsheet_links": ent.get("spreadsheet_links", []),
        "notes": "Candidate generated from Gear.wiki gearrow template. Manual review required before canonical promotion.",
        "tags": ["source:wiki_gg", "candidate", "phase:1c4"],
        "canonical_promotion": False,
    }

def validate_v2(obj: dict[str, Any]) -> list[str]:
    errors = []

    for key in ["id", "name", "base_stats", "source"]:
        if obj.get(key) in [None, ""]:
            errors.append(f"missing_required:{key}")

    if obj.get("tier_color") not in TIER_COLORS:
        errors.append("missing_or_invalid:tier_color")

    stats = obj.get("base_stats")
    if not isinstance(stats, dict):
        errors.append("invalid:base_stats_not_object")
    else:
        for stat in STAT_KEYS:
            value = stats.get(stat)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"invalid_stat:{stat}")
        if not any(stats.get(k) is not None for k in STAT_KEYS):
            errors.append("missing:all_core_stats")

    src = obj.get("source")
    if not isinstance(src, dict) or not src.get("url"):
        errors.append("missing:source_url")

    return errors

def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    SCHEMA_PROPOSAL.parent.mkdir(parents=True, exist_ok=True)

    schema_v1 = load_json(SCHEMA_V1)
    candidates = load_json(CANDIDATES)
    phase1c3_rows = load_json(PHASE1C3)

    schema_v2 = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Gear Entity Schema v2 Proposal",
        "description": "Proposed Super Snail gear schema based on Gear.wiki aggregate gearrow templates. Slot is optional because Gear.wiki does not classify gear by weapon/armor/accessory.",
        "type": "object",
        "required": ["id", "name", "tier_color", "base_stats", "source"],
        "properties": {
            "id": {"type": "string", "description": "Unique slug for the gear item."},
            "name": {"type": "string", "description": "Display name from Gear.wiki."},
            "tier_color": {
                "type": "string",
                "enum": TIER_COLORS,
                "description": "Actual gear tier/color from the game/wiki."
            },
            "slot": {
                "type": ["string", "null"],
                "description": "Optional equip slot if confirmed from another source. Do not infer blindly.",
                "enum": ["weapon", "armor", "accessory", None]
            },
            "base_stats": {
                "type": "object",
                "required": ["hp", "atk", "def", "rush"],
                "properties": {
                    "hp": {"type": ["number", "null"]},
                    "atk": {"type": ["number", "null"]},
                    "def": {"type": ["number", "null"]},
                    "rush": {"type": ["number", "null"]}
                },
                "additionalProperties": False
            },
            "effect": {"type": ["string", "null"], "description": "Raw effect text from wiki."},
            "origin": {"type": ["string", "null"], "description": "Raw origin/acquisition text from wiki."},
            "file_no": {"type": ["number", "integer", "null"], "description": "File number from wiki table when present."},
            "icon_filename": {"type": ["string", "null"], "description": "Icon filename from wiki table when present."},
            "source": {
                "type": "object",
                "required": ["type", "url"],
                "properties": {
                    "type": {"type": "string"},
                    "url": {"type": "string"},
                    "file": {"type": ["string", "null"]},
                    "section": {"type": ["string", "null"]},
                    "subsection": {"type": ["string", "null"]}
                },
                "additionalProperties": True
            },
            "spreadsheet_links": {"type": "array", "items": {"type": "object"}},
            "notes": {"type": ["string", "null"]},
            "tags": {"type": "array", "items": {"type": "string"}},
            "canonical_promotion": {"type": "boolean"}
        },
        "additionalProperties": False,
        "x_pm_decisions_needed": [
            "Approve tier_color as first-class field.",
            "Approve slot as optional nullable field until another reliable source provides slot data.",
            "Approve raw effect/origin preservation before downstream normalization.",
            "Decide whether old rarity enum should be removed, retained as derived, or moved to a separate display mapping."
        ]
    }

    adapted = [adapt_to_v2(ent) for ent in candidates]

    validation_rows = []
    ready = []
    blocked = []
    error_counts = Counter()
    color_counts = Counter()

    for obj in adapted:
        errors = validate_v2(obj)
        color_counts[str(obj.get("tier_color"))] += 1
        for e in errors:
            error_counts[e] += 1

        row = {
            "id": obj.get("id"),
            "name": obj.get("name"),
            "tier_color": obj.get("tier_color"),
            "slot": obj.get("slot"),
            "errors": errors,
            "readiness": "v2_schema_ready_needs_manual_review" if not errors else "blocked_v2_validation",
            "canonical_promotion": False,
        }
        validation_rows.append(row)
        if errors:
            blocked.append(row)
        else:
            ready.append(obj)

    v1_readiness = Counter(row.get("readiness") for row in phase1c3_rows)

    decision_report = {
        "generated_at": UTC_NOW,
        "canonical_promotion": False,
        "candidate_count": len(candidates),
        "v1_result_summary": dict(v1_readiness),
        "v2_ready_needs_manual_review": len(ready),
        "v2_blocked": len(blocked),
        "v2_error_counts": dict(error_counts),
        "tier_color_counts": dict(color_counts),
        "recommended_pm_decision": {
            "slot": "make optional nullable; do not require weapon/armor/accessory for Gear.wiki-derived records",
            "tier_color": "add as required first-class field",
            "rarity": "do not force semantic rarity during import; derive later if needed",
            "effect_origin": "keep raw text now; normalize in later effect/origin pipelines",
            "canonical_promotion": "still locked until manual review packet is approved"
        },
        "schema_v1_required": schema_v1.get("required"),
        "schema_v2_required": schema_v2.get("required"),
    }

    write_json(SCHEMA_PROPOSAL, schema_v2)
    write_json(OUTDIR / "gear.schema.v2.proposal.copy.json", schema_v2)
    write_json(OUTDIR / "gear_v2_adapted_candidates.json", adapted)
    write_json(OUTDIR / "gear_v2_ready_candidates.json", ready)
    write_json(OUTDIR / "gear_v2_blocked_candidates.json", blocked)
    write_json(OUTDIR / "gear_v2_validation_rows.json", validation_rows)
    write_json(OUTDIR / "schema_v2_decision_report.json", decision_report)

    md = []
    md.append("# Phase 1C.4 Gear Schema v2 Proposal")
    md.append("")
    md.append(f"Generated UTC: {UTC_NOW}")
    md.append("")
    md.append("## PM Finding")
    md.append("")
    md.append("The current gear.schema.json is too strict for the actual Gear.wiki source shape.")
    md.append("Gear.wiki provides item identity, tier/color, HP, ATK, DEF, RUSH, effect, and origin.")
    md.append("It does not reliably provide weapon/armor/accessory slot classification.")
    md.append("")
    md.append("## Proposed Schema Decisions")
    md.append("")
    md.append("- Add `tier_color` as required first-class field.")
    md.append("- Make `slot` optional nullable.")
    md.append("- Preserve raw `effect` and `origin` as strings for later normalization.")
    md.append("- Preserve `source` object with wiki URL and local source file.")
    md.append("- Do not force semantic rarity during import.")
    md.append("")
    md.append("## Validation Results")
    md.append("")
    md.append(f"- Total candidates: {len(candidates)}")
    md.append(f"- v2 ready but needs manual review: {len(ready)}")
    md.append(f"- v2 blocked: {len(blocked)}")
    md.append("")
    md.append("## Tier Color Counts")
    md.append("")
    for color, count in sorted(color_counts.items()):
        md.append(f"- {color}: {count}")
    md.append("")
    md.append("## v2 Error Counts")
    md.append("")
    for err, count in error_counts.most_common():
        md.append(f"- {err}: {count}")
    md.append("")
    md.append("## Decision Needed")
    md.append("")
    md.append("Approve or reject gear.schema.v2.proposal.json before canonical import.")
    md.append("Recommended: approve v2 direction, then run Phase 1C.5 to prepare a no-write canonical import dry run.")
    md.append("")

    (OUTDIR / "schema_v2_proposal_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(decision_report, indent=2))

if __name__ == "__main__":
    main()
