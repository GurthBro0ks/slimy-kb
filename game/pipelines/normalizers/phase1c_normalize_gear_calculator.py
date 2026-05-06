#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(".")
STAGING = ROOT / "game/data/staging/gear_calculator"
OUT = ROOT / "game/data/candidates/phase1c_gear_calculator"

GEAR_ITEMS = STAGING / "gear_items_extracted.json"
COST_TABLE = STAGING / "cost_level_table.json"
FORMULA_MAP = STAGING / "formula_map_original_unpatched.csv"
WORKBOOK_CELLS = STAGING / "workbook_nonempty_cells_original_unpatched.json"
FORMULA_FIXES = STAGING / "formula_fixes_2026-05-06.json"

UTC_NOW = datetime.now(timezone.utc).isoformat()

STAT_ALIASES = {
    "hp": "hp",
    "health": "hp",
    "atk": "atk",
    "attack": "atk",
    "def": "def",
    "defense": "def",
    "rush": "rush",
    "fame": "fame",
    "tech": "tech",
    "art": "art",
    "civ": "civ",
    "fth": "fth",
    "faith": "fth",
    "fire": "fire",
    "water": "water",
    "earth": "earth",
    "wind": "wind",
    "poison": "poison",
    "poisen": "poison",
}

KNOWN_NAME_FIXES = {
    "equipped": "equipped",
    "equiped": "equipped",
    "excaladbolg": "excaladbolg",
    "poisen": "poison",
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


def normalize_stat_name(value: Any) -> str | None:
    if value is None:
        return None
    key = slugify(value)
    key = KNOWN_NAME_FIXES.get(key, key)
    return STAT_ALIASES.get(key, key)


def to_number(value: Any) -> float | int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip().replace(",", "")
    if text == "":
        return None
    try:
        num = float(text)
        if num.is_integer():
            return int(num)
        return num
    except ValueError:
        return None


def walk_shapes(obj: Any, prefix: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        rows.append({"path": prefix or "$", "type": "dict", "keys": sorted(map(str, obj.keys()))[:50], "key_count": len(obj)})
        for k, v in list(obj.items())[:50]:
            rows.extend(walk_shapes(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        rows.append({"path": prefix or "$", "type": "list", "length": len(obj)})
        for i, v in enumerate(obj[:5]):
            rows.extend(walk_shapes(v, f"{prefix}[{i}]"))
    else:
        rows.append({"path": prefix or "$", "type": type(obj).__name__, "sample": obj})
    return rows


def flatten_records(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for key in ["items", "gear", "gear_items", "records", "rows", "data"]:
            value = obj.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        if all(isinstance(v, dict) for v in obj.values()):
            records = []
            for k, v in obj.items():
                row = dict(v)
                row.setdefault("source_key", k)
                records.append(row)
            return records
    return []


def find_first(row: dict[str, Any], candidates: list[str]) -> Any:
    lowered = {slugify(k): v for k, v in row.items()}
    for c in candidates:
        key = slugify(c)
        if key in lowered:
            return lowered[key]
    return None


def load_formula_map() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with FORMULA_MAP.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def formula_cell(row: dict[str, Any]) -> str:
    for key in ["cell", "Cell", "address", "Address", "coordinate", "Coordinate"]:
        if key in row and row[key]:
            return str(row[key])
    sheet = row.get("sheet") or row.get("Sheet") or ""
    addr = row.get("cell") or row.get("Cell") or ""
    return f"{sheet}!{addr}" if sheet and addr else ""


def formula_sheet(row: dict[str, Any]) -> str:
    for key in ["sheet", "Sheet", "worksheet", "Worksheet"]:
        if key in row and row[key]:
            return str(row[key])
    return ""


def formula_value(row: dict[str, Any]) -> str:
    for key in ["formula", "Formula", "value", "Value"]:
        if key in row and str(row[key]).startswith("="):
            return str(row[key])
    for _, value in row.items():
        if isinstance(value, str) and value.startswith("="):
            return value
    return ""


def build_fix_lookup(fix_manifest: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for fix in fix_manifest.get("fixes", []):
        sheet = str(fix.get("sheet") or "")
        if "cell" in fix:
            lookup[(sheet, str(fix["cell"]))] = fix
        for cell in fix.get("cells", []) or []:
            lookup[(sheet, str(cell))] = fix
        for cell in (fix.get("labels") or {}).keys():
            lookup[(sheet, str(cell))] = fix
    return lookup


def normalize_gear_items(raw_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    gear_candidates: list[dict[str, Any]] = []
    stat_scaling_candidates: list[dict[str, Any]] = []
    effect_scaling_candidates: list[dict[str, Any]] = []

    for idx, row in enumerate(raw_items, start=1):
        name = find_first(row, ["name", "gear", "item", "gear_name", "display_name"]) or row.get("source_key") or f"unknown_gear_{idx}"
        gear_id = slugify(name)

        category = find_first(row, ["category", "type", "section", "group"])
        slot = find_first(row, ["slot", "equipment_slot"])
        equipped = find_first(row, ["equipped", "equiped", "is_equipped"])

        base_stats: dict[str, Any] = {}
        per_level_stats: dict[str, Any] = {}
        raw_stat_fields: dict[str, Any] = {}

        # Check nested stats dict
        if isinstance(row.get("stats"), dict):
            for stat_key, stat_val in row["stats"].items():
                norm_key = normalize_stat_name(stat_key)
                if not norm_key:
                    continue
                # stat_val may be a dict with base/computed/per_effective_level
                if isinstance(stat_val, dict):
                    base_num = to_number(stat_val.get("base"))
                    if base_num is not None:
                        base_stats[norm_key] = base_num
                        raw_stat_fields[f"stats.{stat_key}.base"] = base_num
                    per_level = to_number(stat_val.get("per_effective_level"))
                    if per_level is not None:
                        per_level_stats[norm_key] = per_level
                        raw_stat_fields[f"stats.{stat_key}.per_effective_level"] = per_level
                else:
                    num = to_number(stat_val)
                    if num is not None:
                        base_stats[norm_key] = num
                        raw_stat_fields[f"stats.{stat_key}"] = stat_val

        for key, value in row.items():
            norm_key = normalize_stat_name(key)
            if norm_key in {"hp", "atk", "def", "rush", "fame", "tech", "art", "civ", "fth", "fire", "water", "earth", "wind", "poison"}:
                num = to_number(value)
                if num is not None:
                    base_stats[norm_key] = num
                    raw_stat_fields[key] = value

            key_slug = slugify(key)
            if key_slug.startswith("base_"):
                stat = normalize_stat_name(key_slug.replace("base_", ""))
                num = to_number(value)
                if stat and num is not None:
                    base_stats[stat] = num
                    raw_stat_fields[key] = value

            if key_slug.startswith("per_level_") or key_slug.endswith("_per_level"):
                stat = normalize_stat_name(key_slug.replace("per_level_", "").replace("_per_level", ""))
                num = to_number(value)
                if stat and num is not None:
                    per_level_stats[stat] = num
                    raw_stat_fields[key] = value

        gear_candidates.append({
            "id": gear_id,
            "name": str(name).strip(),
            "source_type": "spreadsheet_reverse_engineering",
            "source_file": "game/data/staging/gear_calculator/gear_items_extracted.json",
            "source_index": idx,
            "category_raw": category,
            "slot_raw": slot,
            "equipped_raw": equipped,
            "base_stats_candidate": base_stats,
            "per_level_stats_candidate": per_level_stats,
            "raw_record": row,
            "confidence": 0.65 if gear_id != "unknown" else 0.25,
            "review_status": "candidate_needs_review",
            "created_at": UTC_NOW,
        })

        for stat, value in base_stats.items():
            stat_scaling_candidates.append({
                "id": f"{gear_id}_{stat}_base",
                "gear_id": gear_id,
                "stat": stat,
                "scaling_type": "base",
                "value": value,
                "source_file": "game/data/staging/gear_calculator/gear_items_extracted.json",
                "source_index": idx,
                "confidence": 0.65,
                "review_status": "candidate_needs_review",
            })

        for stat, value in per_level_stats.items():
            stat_scaling_candidates.append({
                "id": f"{gear_id}_{stat}_per_level",
                "gear_id": gear_id,
                "stat": stat,
                "scaling_type": "per_level",
                "value": value,
                "source_file": "game/data/staging/gear_calculator/gear_items_extracted.json",
                "source_index": idx,
                "confidence": 0.65,
                "review_status": "candidate_needs_review",
            })

        # Handle nested effects list
        if isinstance(row.get("effects"), list):
            for eff_idx, effect in enumerate(row["effects"]):
                if not isinstance(effect, dict):
                    continue
                eff_name = effect.get("name") or effect.get("effect") or f"effect_{eff_idx+1}"
                eff_base = to_number(effect.get("base"))
                eff_per_level = to_number(effect.get("per_effective_level"))
                eff_computed = to_number(effect.get("computed"))
                eff_formula = effect.get("formula")
                effect_scaling_candidates.append({
                    "id": f"{gear_id}_effect_{eff_idx+1}",
                    "gear_id": gear_id,
                    "effect_name": str(eff_name),
                    "effect_base": eff_base,
                    "effect_per_level": eff_per_level,
                    "effect_computed": eff_computed,
                    "effect_formula": eff_formula,
                    "effect_text_raw": str(effect),
                    "source_file": "game/data/staging/gear_calculator/gear_items_extracted.json",
                    "source_index": idx,
                    "confidence": 0.55,
                    "review_status": "candidate_needs_review",
                })
        else:
            effect_text = find_first(row, ["effect", "bonus", "description", "special", "notes"])
            if effect_text:
                effect_scaling_candidates.append({
                    "id": f"{gear_id}_effect_1",
                    "gear_id": gear_id,
                    "effect_text_raw": str(effect_text),
                    "source_file": "game/data/staging/gear_calculator/gear_items_extracted.json",
                    "source_index": idx,
                    "confidence": 0.45,
                    "review_status": "candidate_needs_review",
                })

    return gear_candidates, stat_scaling_candidates, effect_scaling_candidates


def normalize_costs(cost_data: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    records: list[dict[str, Any]] = []
    if isinstance(cost_data, list):
        records = [x for x in cost_data if isinstance(x, dict)]
    elif isinstance(cost_data, dict):
        for key in ["costs", "levels", "rows", "data"]:
            if isinstance(cost_data.get(key), list):
                records = [x for x in cost_data[key] if isinstance(x, dict)]
                break
        if not records and all(isinstance(v, dict) for v in cost_data.values()):
            for k, v in cost_data.items():
                row = dict(v)
                row.setdefault("level", k)
                records.append(row)

    for idx, row in enumerate(records, start=1):
        level = find_first(row, ["level", "lvl", "enhancement_level"])
        for key, value in row.items():
            if slugify(key) in {"level", "lvl", "enhancement_level"}:
                continue
            num = to_number(value)
            if num is None:
                continue
            material = slugify(key)
            out.append({
                "id": f"level_{slugify(level)}_{material}",
                "level": to_number(level) if to_number(level) is not None else level,
                "material": material,
                "quantity": num,
                "source_file": "game/data/staging/gear_calculator/cost_level_table.json",
                "source_index": idx,
                "raw_record": row,
                "confidence": 0.7,
                "review_status": "candidate_needs_review",
            })
    return out


def normalize_formulas(formula_rows: list[dict[str, Any]], fixes: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    fix_lookup = build_fix_lookup(fixes)
    formulas: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    source_facts: list[dict[str, Any]] = []

    for idx, row in enumerate(formula_rows, start=1):
        sheet = formula_sheet(row)
        cell = ""
        for key in ["cell", "Cell", "address", "Address", "coordinate", "Coordinate"]:
            if key in row and row[key]:
                cell = str(row[key])
                break

        original_formula = formula_value(row)
        fix = fix_lookup.get((sheet, cell))
        effective_formula = fix.get("formula") if fix and "formula" in fix else original_formula

        formulas.append({
            "id": slugify(f"{sheet}_{cell}") or f"formula_{idx}",
            "sheet": sheet,
            "cell": cell,
            "original_formula": original_formula,
            "effective_formula": effective_formula,
            "patched": bool(fix),
            "patch_id": fix.get("id") if fix else None,
            "raw_record": row,
            "source_file": "game/data/staging/gear_calculator/formula_map_original_unpatched.csv",
            "source_index": idx,
            "confidence": 0.8 if original_formula else 0.25,
            "review_status": "candidate_needs_review",
        })

    for fix in fixes.get("fixes", []):
        issue_id = slugify(fix.get("id") or fix.get("reason") or "formula_fix")
        issues.append({
            "id": issue_id,
            "issue_type": "spreadsheet_formula_fix",
            "source_workbook": fixes.get("source_workbook"),
            "sheet": fix.get("sheet"),
            "cell": fix.get("cell"),
            "cells": fix.get("cells"),
            "formula": fix.get("formula"),
            "action": fix.get("action"),
            "reason": fix.get("reason"),
            "raw_fix": fix,
            "confidence": 0.9,
            "review_status": "accepted_as_staging_correction",
        })
        source_facts.append({
            "id": f"source_fact_{issue_id}",
            "claim": fix.get("reason") or f"Formula fix recorded for {issue_id}",
            "source_type": "spreadsheet",
            "source_file": "game/data/staging/gear_calculator/formula_fixes_2026-05-06.json",
            "confidence": 0.9,
            "related_entities": [],
            "notes": "Formula fix supplied during spreadsheet reverse-engineering review.",
        })

    return formulas, issues, source_facts


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    gear_data = load_json(GEAR_ITEMS)
    cost_data = load_json(COST_TABLE)
    workbook_cells = load_json(WORKBOOK_CELLS)
    fixes = load_json(FORMULA_FIXES)
    formula_rows = load_formula_map()

    raw_items = flatten_records(gear_data)

    gear_candidates, stat_scaling, effect_scaling = normalize_gear_items(raw_items)
    cost_candidates = normalize_costs(cost_data)
    formula_candidates, formula_issues, source_facts = normalize_formulas(formula_rows, fixes)

    shape_report = {
        "generated_at": UTC_NOW,
        "gear_items_shape": walk_shapes(gear_data)[:300],
        "cost_table_shape": walk_shapes(cost_data)[:300],
        "workbook_cells_shape": walk_shapes(workbook_cells)[:300],
        "formula_fixes_shape": walk_shapes(fixes)[:300],
        "raw_gear_record_count": len(raw_items),
        "formula_row_count": len(formula_rows),
        "notes": [
            "Candidate normalization is conservative.",
            "Raw records are preserved on each gear candidate.",
            "Canonical promotion is intentionally blocked until manual review.",
        ],
    }

    manifest = {
        "generated_at": UTC_NOW,
        "phase": "1C",
        "scope": "gear_calculator_candidate_normalization",
        "canonical_promotion": False,
        "outputs": {
            "gear_items": len(gear_candidates),
            "gear_stat_scaling": len(stat_scaling),
            "gear_effect_scaling": len(effect_scaling),
            "gear_cost_by_level": len(cost_candidates),
            "combat_formulas": len(formula_candidates),
            "known_formula_issues": len(formula_issues),
            "source_facts": len(source_facts),
        },
        "input_files": [
            str(GEAR_ITEMS),
            str(COST_TABLE),
            str(FORMULA_MAP),
            str(WORKBOOK_CELLS),
            str(FORMULA_FIXES),
        ],
    }

    write_json(OUT / "gear_items.candidates.json", gear_candidates)
    write_json(OUT / "gear_stat_scaling.candidates.json", stat_scaling)
    write_json(OUT / "gear_effect_scaling.candidates.json", effect_scaling)
    write_json(OUT / "gear_cost_by_level.candidates.json", cost_candidates)
    write_json(OUT / "combat_formulas.candidates.json", formula_candidates)
    write_json(OUT / "known_formula_issues.candidates.json", formula_issues)
    write_json(OUT / "source_facts.candidates.json", source_facts)
    write_json(OUT / "normalization_shape_report.json", shape_report)
    write_json(OUT / "manifest.json", manifest)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
