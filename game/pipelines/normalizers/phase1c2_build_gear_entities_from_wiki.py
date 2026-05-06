#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(".")
LOCAL_GEAR_WIKI = ROOT / "game/sources/wiki_gg/Gear.wiki"
LIVE_GEAR_WIKI = ROOT / "game/sources/wiki_gg/Gear.live-api-2026-05-06.wiki"
GEAR_PAGE_ROWS = ROOT / "game/data/candidates/phase1c1b_gear_page_table_cross_reference/gear_page_rows.candidates.json"
CALC_MATRIX = ROOT / "game/data/candidates/phase1c1b_gear_page_table_cross_reference/gear_calculator_to_gear_page_review_matrix.json"
OUTDIR = ROOT / "game/data/candidates/phase1c2_gear_entities_from_wiki"

UTC_NOW = datetime.now(timezone.utc).isoformat()

STAT_KEYS = ["hp", "atk", "def", "rush"]

def slugify(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"

def simple_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"\[\[file:[^\]]+\]\]", " ", text, flags=re.I)
    text = re.sub(r"\{\{[^}]+\}\}", " ", text)
    text = re.sub(r"\[\[([^|\]]+)\|([^]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^]]+)\]\]", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def clean_wiki_cell(value: str) -> str:
    text = str(value or "").strip()
    text = re.sub(r"^\|+", "", text).strip()
    text = re.sub(r"^!+", "", text).strip()
    text = re.sub(r"\[\[File:([^|\]]+)(?:\|[^]]*)?\]\]", r"\1", text, flags=re.I)
    text = re.sub(r"\[\[Image:([^|\]]+)(?:\|[^]]*)?\]\]", r"\1", text, flags=re.I)
    text = re.sub(r"\[\[([^|\]]+)\|([^]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^]]+)\]\]", r"\1", text)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def to_number(value: Any) -> int | float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    text = re.sub(r"[^0-9.+-]", "", text)
    if not text or text in {"+", "-", ".", "+.", "-."}:
        return None
    try:
        num = float(text)
        if num.is_integer():
            return int(num)
        return num
    except Exception:
        return None

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def extract_links(value: str) -> list[str]:
    links = []
    for m in re.finditer(r"\[\[([^|\]]+)\|([^]]+)\]\]", value):
        target = m.group(1)
        label = m.group(2)
        if not target.lower().startswith(("file:", "image:", "category:")):
            links.append(clean_wiki_cell(label))
    for m in re.finditer(r"\[\[([^|\]]+)\]\]", value):
        target = m.group(1)
        if not target.lower().startswith(("file:", "image:", "category:")):
            links.append(clean_wiki_cell(target))
    out = []
    seen = set()
    for item in links:
        key = simple_text(item)
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out

def split_gearrow_args(template_body: str) -> list[str]:
    """Split gearrow template arguments by |, respecting nested templates."""
    args = []
    current = []
    depth = 0
    for char in template_body:
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
    return args

def parse_gearrows(wikitext: str) -> list[dict[str, Any]]:
    rows = []
    current_section = "unknown"
    current_subsection = "unknown"
    
    for line in wikitext.splitlines():
        line = line.strip()
        
        # Track sections
        sec = re.match(r"^(=+)\s*(.*?)\s*\1\s*$", line)
        if sec:
            level = len(sec.group(1))
            title = clean_wiki_cell(sec.group(2))
            if level <= 2:
                current_section = title
                current_subsection = title
            else:
                current_subsection = title
            continue
        
        # Parse tabber sections (e.g., |-|White=, |-|Green=)
        tabber = re.match(r"^\|-\|([^=]+)=?\s*$", line)
        if tabber:
            current_subsection = tabber.group(1).strip()
            continue
        
        # Look for gearrow templates
        for match in re.finditer(r"\{\{gearrow\|([^}]+)\}\}", line):
            template_body = match.group(1)
            args = split_gearrow_args(template_body)
            
            if len(args) < 9:
                # Some gearrows might have fewer args; pad with empty strings
                args = args + [''] * (9 - len(args))
            
            name = args[0].strip()
            file_no = to_number(args[1])
            hp = to_number(args[2])
            atk = to_number(args[3])
            def_ = to_number(args[4])
            rush = to_number(args[5])
            effect = args[6].strip() if len(args) > 6 else None
            origin = args[7].strip() if len(args) > 7 else None
            color = args[8].strip() if len(args) > 8 else None
            
            if not name:
                continue
            
            # Extract links from effect and origin
            all_links = []
            if effect:
                all_links.extend(extract_links(effect))
            if origin:
                all_links.extend(extract_links(origin))
            
            row = {
                "source_file": "game/sources/wiki_gg/Gear.wiki",
                "section": current_section,
                "subsection": current_subsection,
                "name": name,
                "name_slug": slugify(name),
                "file_no": file_no,
                "stats": {
                    "hp": hp,
                    "atk": atk,
                    "def": def_,
                    "rush": rush,
                },
                "effect_raw": effect if effect else None,
                "origin_raw": origin if origin else None,
                "rarity_color": color if color else None,
                "wiki_links": all_links,
                "raw_args": args,
            }
            rows.append(row)
    
    return rows

def infer_entity_from_row(row: dict[str, Any]) -> dict[str, Any]:
    name = row.get("name")
    stats = row.get("stats", {})
    
    entity = {
        "id": slugify(name),
        "name": name,
        "source_type": "wiki_gg_gear_table",
        "source_file": row["source_file"],
        "source_section": row.get("section"),
        "source_subsection": row.get("subsection"),
        "file_no": row.get("file_no"),
        "icon_filename": None,
        "stats": stats,
        "effect_raw": row.get("effect_raw"),
        "origin_raw": row.get("origin_raw"),
        "rarity_color": row.get("rarity_color"),
        "wiki_links": row.get("wiki_links", []),
        "cells_clean": row.get("raw_args", []),
        "raw_row": row,
        "confidence": 0.85 if name and any(v is not None for v in stats.values()) else 0.5,
        "review_status": "candidate_needs_review",
        "canonical_promotion": False,
        "created_at": UTC_NOW,
    }
    
    return entity

def dedupe_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {}
    for ent in entities:
        eid = ent["id"]
        if eid not in by_id:
            by_id[eid] = ent
        else:
            old = by_id[eid]
            old_count = sum(1 for v in old.get("stats", {}).values() if v is not None)
            new_count = sum(1 for v in ent.get("stats", {}).values() if v is not None)
            if new_count > old_count:
                ent["duplicate_candidates"] = old.get("duplicate_candidates", []) + [old]
                by_id[eid] = ent
            else:
                old.setdefault("duplicate_candidates", []).append(ent)
                by_id[eid] = old
    return list(by_id.values())

def link_spreadsheet_matches(entities: list[dict[str, Any]], matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for ent in entities:
        ent["spreadsheet_links"] = []
    
    for m in matrix:
        score = m.get("best_score") or 0
        best_name = m.get("best_wiki_name")
        if score < 0.75 or not best_name:
            continue
        best_slug = slugify(best_name)
        for ent in entities:
            if ent["id"] == best_slug or slugify(ent.get("name")) == best_slug:
                ent["spreadsheet_links"].append({
                    "calculator_candidate_id": m.get("calculator_candidate_id"),
                    "calculator_candidate_name": m.get("calculator_candidate_name"),
                    "score": score,
                    "classification": m.get("classification"),
                    "source_matrix": "game/data/candidates/phase1c1b_gear_page_table_cross_reference/gear_calculator_to_gear_page_review_matrix.json",
                })
    
    return entities

def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    
    local_text = LOCAL_GEAR_WIKI.read_text(encoding="utf-8", errors="replace")
    live_text = LIVE_GEAR_WIKI.read_text(encoding="utf-8", errors="replace") if LIVE_GEAR_WIKI.exists() else ""
    
    source_text = live_text if live_text and len(live_text) >= len(local_text) * 0.8 else local_text
    source_label = "live_api" if source_text == live_text and live_text else "local_file"
    
    parsed_rows = parse_gearrows(source_text)
    raw_entities = [infer_entity_from_row(row) for row in parsed_rows]
    raw_entities = [e for e in raw_entities if e.get("name") and e["id"] != "unknown"]
    
    entities = dedupe_entities(raw_entities)
    
    calc_matrix = load_json(CALC_MATRIX)
    entities = link_spreadsheet_matches(entities, calc_matrix)
    
    low_conf = [e for e in entities if e.get("confidence", 0) < 0.7]
    with_stats = [e for e in entities if any(v is not None for v in e.get("stats", {}).values())]
    
    stat_scaling = []
    for ent in entities:
        for stat, value in ent.get("stats", {}).items():
            if value is None:
                continue
            stat_scaling.append({
                "id": f"{ent['id']}_{stat}_wiki_base",
                "gear_id": ent["id"],
                "gear_name": ent["name"],
                "stat": stat,
                "value": value,
                "scaling_type": "wiki_table_base",
                "source_file": ent["source_file"],
                "source_section": ent.get("source_section"),
                "confidence": ent.get("confidence"),
                "review_status": "candidate_needs_review",
            })
    
    source_facts = []
    for ent in entities:
        source_facts.append({
            "id": f"source_fact_wiki_gear_{ent['id']}",
            "claim": f"Gear table lists {ent['name']} with stats {ent.get('stats')} and effect {ent.get('effect_raw')}",
            "source_type": "wiki",
            "source_file": ent["source_file"],
            "source_url": "https://supersnail.wiki.gg/wiki/Gear",
            "confidence": ent.get("confidence"),
            "related_entities": [ent["id"]],
            "notes": "Candidate source fact from Gear.wiki aggregate table. Requires manual review before canonical promotion.",
        })
    
    manifest = {
        "generated_at": UTC_NOW,
        "phase": "1C.2",
        "canonical_promotion": False,
        "source_text": source_label,
        "local_gear_wiki_lines": len(local_text.splitlines()),
        "live_gear_wiki_lines": len(live_text.splitlines()) if live_text else None,
        "parsed_gearrow_templates": len(parsed_rows),
        "raw_entity_candidates": len(raw_entities),
        "deduped_entity_candidates": len(entities),
        "entities_with_any_stat": len(with_stats),
        "low_confidence_entities": len(low_conf),
        "stat_scaling_rows": len(stat_scaling),
        "source_facts": len(source_facts),
        "outputs": [
            "gear_entities_from_wiki.candidates.json",
            "gear_stat_scaling_from_wiki.candidates.json",
            "gear_source_facts_from_wiki.candidates.json",
            "low_confidence_gear_entities.json",
            "gear_entities_from_wiki.csv",
            "manifest.json",
        ],
    }
    
    (OUTDIR / "gear_entities_from_wiki.candidates.json").write_text(json.dumps(entities, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "gear_stat_scaling_from_wiki.candidates.json").write_text(json.dumps(stat_scaling, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "gear_source_facts_from_wiki.candidates.json").write_text(json.dumps(source_facts, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "low_confidence_gear_entities.json").write_text(json.dumps(low_conf, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    
    with (OUTDIR / "gear_entities_from_wiki.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["id", "name", "file_no", "rarity_color", "hp", "atk", "def", "rush", "effect_raw", "origin_raw", "confidence", "spreadsheet_link_count"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for ent in entities:
            stats = ent.get("stats", {})
            writer.writerow({
                "id": ent.get("id"),
                "name": ent.get("name"),
                "file_no": ent.get("file_no"),
                "rarity_color": ent.get("rarity_color"),
                "hp": stats.get("hp"),
                "atk": stats.get("atk"),
                "def": stats.get("def"),
                "rush": stats.get("rush"),
                "effect_raw": ent.get("effect_raw"),
                "origin_raw": ent.get("origin_raw"),
                "confidence": ent.get("confidence"),
                "spreadsheet_link_count": len(ent.get("spreadsheet_links", [])),
            })
    
    summary = []
    summary.append("# Phase 1C.2 Gear Entities From Wiki Summary")
    summary.append("")
    summary.append(f"Generated UTC: {UTC_NOW}")
    summary.append("")
    summary.append("## Summary")
    summary.append("")
    summary.append(f"- Source text: {source_label}")
    summary.append(f"- Parsed gearrow templates: {len(parsed_rows)}")
    summary.append(f"- Raw entity candidates: {len(raw_entities)}")
    summary.append(f"- Deduped entity candidates: {len(entities)}")
    summary.append(f"- Entities with any stat: {len(with_stats)}")
    summary.append(f"- Low-confidence entities: {len(low_conf)}")
    summary.append(f"- Stat scaling rows: {len(stat_scaling)}")
    summary.append(f"- Source facts: {len(source_facts)}")
    summary.append("")
    summary.append("## Entity Preview")
    summary.append("")
    summary.append("| Name | HP | ATK | DEF | RUSH | Effect | Origin | Confidence |")
    summary.append("|---|---:|---:|---:|---:|---|---|---:|")
    for ent in entities[:80]:
        stats = ent.get("stats", {})
        summary.append(f"| {ent.get('name')} | {stats.get('hp')} | {stats.get('atk')} | {stats.get('def')} | {stats.get('rush')} | {str(ent.get('effect_raw') or '')[:80]} | {str(ent.get('origin_raw') or '')[:80]} | {ent.get('confidence')} |")
    summary.append("")
    summary.append("## PM Decision")
    summary.append("")
    summary.append("These are candidate gear entities only. They are not canonical.")
    summary.append("Phase 1C.3 should validate candidate shape against gear.schema.json and produce a promotion readiness report.")
    (OUTDIR / "gear_entities_from_wiki_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
