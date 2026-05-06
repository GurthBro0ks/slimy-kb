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
GEAR_WIKI = ROOT / "game/sources/wiki_gg/Gear.wiki"
CALC_CANDIDATES = ROOT / "game/data/candidates/phase1c_gear_calculator/gear_items.candidates.json"
OUTDIR = ROOT / "game/data/candidates/phase1c1b_gear_page_table_cross_reference"

UTC_NOW = datetime.now(timezone.utc).isoformat()


def slugify(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


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


def tokens(value: Any) -> set[str]:
    stop = {"of", "the", "and", "a", "an", "s", "to", "in", "gear", "snail"}
    return {t for t in simple_text(value).split() if t and t not in stop}


def ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def token_score(a: str, b: str) -> float:
    ta = tokens(a)
    tb = tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def clean_wiki_cell(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^\|+", "", text).strip()
    text = re.sub(r"^!+", "", text).strip()
    text = re.sub(r"\[\[File:([^|\]]+)(?:\|[^]]*)?\]\]", r"\1", text, flags=re.I)
    text = re.sub(r"\[\[Image:([^|\]]+)(?:\|[^]]*)?\]\]", r"\1", text, flags=re.I)
    text = re.sub(r"\[\[([^|\]]+)\|([^]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^]]+)\]\]", r"\1", text)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^\u003e]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_links(value: str) -> list[str]:
    links: list[str] = []
    for m in re.finditer(r"\[\[([^|\]]+)\|([^]]+)\]\]", value):
        links.append(clean_wiki_cell(m.group(2)))
    for m in re.finditer(r"\[\[([^|\]]+)\]\]", value):
        target = m.group(1)
        if not target.lower().startswith(("file:", "image:", "category:")):
            links.append(clean_wiki_cell(target))
    seen = set()
    out = []
    for link in links:
        key = simple_text(link)
        if key and key not in seen:
            seen.add(key)
            out.append(link)
    return out


def extract_file_names(value: str) -> list[str]:
    files = []
    for m in re.finditer(r"\[\[(?:File|Image):([^|\]]+)", value, flags=re.I):
        files.append(m.group(1).strip())
    return files


def split_row_cells(row_text: str) -> list[str]:
    lines = []
    for raw in row_text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("|-") or line.startswith("{|") or line.startswith("|}"):
            continue
        if line.startswith("!") or line.startswith("|"):
            lines.append(line)

    cells: list[str] = []
    for line in lines:
        if line.startswith("!!"):
            parts = line[2:].split("!!")
        elif line.startswith("!"):
            parts = line[1:].split("!!")
        elif line.startswith("||"):
            parts = line[2:].split("||")
        elif line.startswith("|"):
            parts = line[1:].split("||")
        else:
            parts = [line]

        for part in parts:
            if part.strip():
                cells.append(part.strip())

    return cells


def parse_gear_tables(wikitext: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_section = "unknown"
    current_subsection = "unknown"
    in_table = False
    table_index = 0
    current_row: list[str] = []
    table_headers: list[str] = []

    def flush_row() -> None:
        nonlocal current_row, table_headers
        if not current_row:
            return

        row_text = "\n".join(current_row)
        cells_raw = split_row_cells(row_text)
        cells_clean = [clean_wiki_cell(c) for c in cells_raw]

        if not cells_clean:
            current_row = []
            return

        # Header rows
        if row_text.lstrip().startswith("!"):
            table_headers = [simple_text(c) for c in cells_clean]
            current_row = []
            return

        links = []
        files = []
        for cell in cells_raw:
            links.extend(extract_links(cell))
            files.extend(extract_file_names(cell))

        # Heuristic name extraction.
        # Prefer non-file wiki links, then cells after image/file-no, then any readable text cell.
        name = None
        if links:
            name = links[0]

        if not name:
            for c in cells_clean:
                c_simple = simple_text(c)
                if not c_simple:
                    continue
                if re.fullmatch(r"\d+", c_simple):
                    continue
                if c.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                    continue
                if c_simple in {"image", "file no", "name", "hp", "atk", "def", "rush", "effect", "origin"}:
                    continue
                name = c
                break

        # Capture likely stat cells.
        numeric_cells = []
        for c in cells_clean:
            n = re.sub(r"[^0-9.+%-]", "", c)
            if n and re.search(r"\d", n):
                numeric_cells.append(c)

        row = {
            "id": f"gear_wiki_row_{len(rows)+1:04d}",
            "source_file": "game/sources/wiki_gg/Gear.wiki",
            "section": current_section,
            "subsection": current_subsection,
            "table_index": table_index,
            "name_candidate": name,
            "name_slug": slugify(name),
            "wiki_links": links,
            "image_files": files,
            "cells_clean": cells_clean,
            "cells_raw": cells_raw,
            "numeric_cells": numeric_cells,
            "table_headers": table_headers,
            "created_at": UTC_NOW,
            "review_status": "wiki_table_row_candidate",
        }

        # Keep only meaningful rows. Gear rows usually have a name or image or multiple cells.
        if name or files or len(cells_clean) >= 4:
            rows.append(row)

        current_row = []

    for line in wikitext.splitlines():
        sec = re.match(r"^(=+)\s*(.*?)\s*\1\s*$", line)
        if sec:
            level = len(sec.group(1))
            title = clean_wiki_cell(sec.group(2))
            if level <= 2:
                current_section = title
                current_subsection = title
            else:
                current_subsection = title

        if line.startswith("{|"):
            in_table = True
            table_index += 1
            table_headers = []
            current_row = []
            continue

        if in_table and line.startswith("|}"):
            flush_row()
            in_table = False
            current_row = []
            continue

        if not in_table:
            continue

        if line.startswith("|-"):
            flush_row()
            current_row = [line]
        else:
            current_row.append(line)

    flush_row()
    return rows


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_calc_aliases(row: dict[str, Any]) -> list[str]:
    aliases = []
    for key in ["name", "id"]:
        if row.get(key):
            aliases.append(str(row[key]))

    raw = row.get("raw_record")
    if isinstance(raw, dict):
        for key, value in raw.items():
            k = simple_text(key)
            if k in {"name", "gear", "gear name", "item", "display name", "source key"} and value:
                aliases.append(str(value))

        # Also capture any string-looking fields that may contain actual gear labels.
        for value in raw.values():
            if isinstance(value, str):
                s = value.strip()
                if 2 <= len(s) <= 80 and not s.startswith("=") and not re.fullmatch(r"[0-9.,%+\-\s]+", s):
                    aliases.append(s)

    out = []
    seen = set()
    for a in aliases:
        key = simple_text(a)
        if key and key not in seen:
            seen.add(key)
            out.append(a)
    return out


def score_calc_to_wiki(calc: dict[str, Any], wiki_row: dict[str, Any]) -> dict[str, Any]:
    aliases = extract_calc_aliases(calc)
    wiki_name = wiki_row.get("name_candidate") or ""
    wiki_text = " ".join([str(wiki_name)] + [str(x) for x in wiki_row.get("wiki_links", [])] + [str(x) for x in wiki_row.get("cells_clean", [])])

    best_alias = None
    best_name_ratio = 0.0
    best_token = 0.0
    exact = False

    for alias in aliases:
        ar = simple_text(alias)
        wr = simple_text(wiki_name)
        full = simple_text(wiki_text)

        if ar and wr and ar == wr:
            exact = True

        best_name_ratio = max(best_name_ratio, ratio(ar, wr))
        best_token = max(best_token, token_score(ar, wr), token_score(ar, full))

        if best_alias is None or ratio(ar, wr) > ratio(simple_text(best_alias), wr):
            best_alias = alias

    score = 0.0
    reasons = []

    if exact:
        score += 1.0
        reasons.append("exact_row_name_match")

    if best_name_ratio >= 0.92:
        score += 0.85
        reasons.append("very_high_row_name_similarity")
    elif best_name_ratio >= 0.80:
        score += 0.65
        reasons.append("high_row_name_similarity")
    elif best_name_ratio >= 0.65:
        score += 0.35
        reasons.append("moderate_row_name_similarity")

    if best_token >= 0.9:
        score += 0.8
        reasons.append("very_high_token_overlap")
    elif best_token >= 0.6:
        score += 0.5
        reasons.append("high_token_overlap")
    elif best_token >= 0.4:
        score += 0.25
        reasons.append("moderate_token_overlap")

    score = min(score, 1.0)

    if score >= 0.95:
        match_class = "exact_or_near_exact"
    elif score >= 0.75:
        match_class = "strong_candidate"
    elif score >= 0.50:
        match_class = "possible_candidate"
    elif score >= 0.30:
        match_class = "weak_candidate"
    else:
        match_class = "unlikely"

    return {
        "wiki_row_id": wiki_row["id"],
        "wiki_name_candidate": wiki_row.get("name_candidate"),
        "wiki_section": wiki_row.get("section"),
        "wiki_subsection": wiki_row.get("subsection"),
        "wiki_image_files": wiki_row.get("image_files", []),
        "wiki_cells_clean": wiki_row.get("cells_clean", []),
        "best_alias": best_alias,
        "score": round(score, 4),
        "match_class": match_class,
        "name_similarity": round(best_name_ratio, 4),
        "token_overlap": round(best_token, 4),
        "reasons": reasons,
    }


def classify_calc_candidate(calc: dict[str, Any], best_score: float) -> str:
    name = simple_text(calc.get("name"))
    raw = calc.get("raw_record") if isinstance(calc.get("raw_record"), dict) else {}
    raw_text = simple_text(" ".join([str(calc.get("name", ""))] + [str(x) for x in raw.values()]))

    abstract_terms = {
        "attack", "armor", "realm", "form", "instrument", "hp", "atk", "def", "rush",
        "damage", "dmg", "crit", "poison", "fire", "water", "earth", "wind",
    }

    if best_score >= 0.75:
        return "probable_real_gear_entity"
    if name in abstract_terms:
        return "calculator_modifier_or_category_not_gear_entity"
    if any(term in raw_text for term in ["base", "per level", "computed", "formula", "equip"]):
        return "calculator_formula_row_needs_manual_mapping"
    return "unmatched_needs_manual_review"


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    wikitext = GEAR_WIKI.read_text(encoding="utf-8", errors="replace")
    calc_candidates = load_json(CALC_CANDIDATES)
    wiki_rows = parse_gear_tables(wikitext)

    matrix = []
    unmatched = []
    probable_matches = []

    for calc in calc_candidates:
        scored = [score_calc_to_wiki(calc, row) for row in wiki_rows]
        scored.sort(key=lambda x: (x["score"], x["name_similarity"], x["token_overlap"]), reverse=True)
        top = scored[:15]
        best = top[0] if top else None
        best_score = best["score"] if best else 0.0

        classification = classify_calc_candidate(calc, best_score)

        row = {
            "calculator_candidate_id": calc.get("id"),
            "calculator_candidate_name": calc.get("name"),
            "calculator_category_raw": calc.get("category_raw"),
            "calculator_slot_raw": calc.get("slot_raw"),
            "calculator_confidence": calc.get("confidence"),
            "best_score": best_score,
            "best_wiki_row_id": best.get("wiki_row_id") if best else None,
            "best_wiki_name": best.get("wiki_name_candidate") if best else None,
            "best_wiki_section": best.get("wiki_section") if best else None,
            "best_wiki_subsection": best.get("wiki_subsection") if best else None,
            "best_match_class": best.get("match_class") if best else None,
            "best_reasons": best.get("reasons") if best else [],
            "classification": classification,
            "top_matches": top,
            "review_status": "needs_manual_review",
            "created_at": UTC_NOW,
        }

        if best_score >= 0.50:
            probable_matches.append(row)
        else:
            unmatched.append(row)

        matrix.append(row)

    summary = {
        "generated_at": UTC_NOW,
        "phase": "1C.1B",
        "canonical_promotion": False,
        "gear_wiki_source": str(GEAR_WIKI),
        "calculator_candidate_count": len(calc_candidates),
        "gear_wiki_table_row_candidates": len(wiki_rows),
        "probable_match_count_score_0_50_plus": len(probable_matches),
        "unmatched_count": len(unmatched),
        "classification_counts": {},
        "outputs": [
            "gear_page_rows.candidates.json",
            "gear_calculator_to_gear_page_review_matrix.json",
            "gear_calculator_to_gear_page_review_matrix.csv",
            "unmatched_calculator_candidates.json",
            "manifest.json",
            "gear_page_table_review_summary.md",
        ],
    }

    for row in matrix:
        c = row["classification"]
        summary["classification_counts"][c] = summary["classification_counts"].get(c, 0) + 1

    (OUTDIR / "gear_page_rows.candidates.json").write_text(json.dumps(wiki_rows, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "gear_calculator_to_gear_page_review_matrix.json").write_text(json.dumps(matrix, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "unmatched_calculator_candidates.json").write_text(json.dumps(unmatched, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    with (OUTDIR / "gear_calculator_to_gear_page_review_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "calculator_candidate_id",
            "calculator_candidate_name",
            "calculator_category_raw",
            "calculator_slot_raw",
            "best_score",
            "best_wiki_name",
            "best_wiki_section",
            "best_wiki_subsection",
            "best_match_class",
            "classification",
            "best_reasons",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in matrix:
            writer.writerow({
                "calculator_candidate_id": row["calculator_candidate_id"],
                "calculator_candidate_name": row["calculator_candidate_name"],
                "calculator_category_raw": row["calculator_category_raw"],
                "calculator_slot_raw": row["calculator_slot_raw"],
                "best_score": row["best_score"],
                "best_wiki_name": row["best_wiki_name"],
                "best_wiki_section": row["best_wiki_section"],
                "best_wiki_subsection": row["best_wiki_subsection"],
                "best_match_class": row["best_match_class"],
                "classification": row["classification"],
                "best_reasons": "; ".join(row["best_reasons"]),
            })

    md = []
    md.append("# Phase 1C.1B Gear Page Table Review Summary")
    md.append("")
    md.append(f"Generated UTC: {UTC_NOW}")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- Calculator candidates: {summary['calculator_candidate_count']}")
    md.append(f"- Gear.wiki table row candidates parsed: {summary['gear_wiki_table_row_candidates']}")
    md.append(f"- Probable matches score >= 0.50: {summary['probable_match_count_score_0_50_plus']}")
    md.append(f"- Unmatched: {summary['unmatched_count']}")
    md.append("")
    md.append("## Classification Counts")
    md.append("")
    for key, value in sorted(summary["classification_counts"].items()):
        md.append(f"- {key}: {value}")
    md.append("")
    md.append("## Calculator Candidate Review Table")
    md.append("")
    md.append("| Calculator Candidate | Best Gear.wiki Row | Score | Classification |")
    md.append("|---|---|---:|---|")
    for row in matrix:
        md.append(f"| {row['calculator_candidate_name']} | {row['best_wiki_name'] or 'NONE'} | {row['best_score']} | {row['classification']} |")
    md.append("")
    md.append("## Gear.wiki Row Extraction Note")
    md.append("")
    md.append("The real Gear page is an aggregate table. Gear entities are mostly rows inside Gear.wiki, not separate page filenames.")
    md.append("")
    md.append("## Next Step")
    md.append("")
    md.append("Use Gear.wiki parsed rows as the better source for gear entity candidates.")
    md.append("Treat spreadsheet gear calculator rows as formulas/modifier candidates unless they directly match a Gear.wiki row.")
    md.append("Do not promote to canonical yet.")

    (OUTDIR / "gear_page_table_review_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
