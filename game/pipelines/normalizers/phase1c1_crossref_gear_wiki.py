#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(".")
GEAR_FILE = ROOT / "game/data/candidates/phase1c_gear_calculator/gear_items.candidates.json"
WIKI_DIR = ROOT / "game/sources/wiki_gg"
OUTDIR = ROOT / "game/data/candidates/phase1c1_gear_wiki_cross_reference"

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
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokens(value: Any) -> set[str]:
    stop = {"of", "the", "and", "a", "an", "s", "to", "in"}
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def wiki_title_from_path(path: Path) -> str:
    return path.stem.replace("_", " ")


def safe_read(path: Path, limit: int = 400000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"READ_ERROR: {exc}"
    if len(data) > limit:
        return data[:limit]
    return data


@dataclass
class WikiPage:
    path: str
    filename: str
    title: str
    title_slug: str
    title_simple: str
    content_sample: str
    content_simple: str


def build_wiki_index() -> list[WikiPage]:
    pages: list[WikiPage] = []
    for path in sorted(WIKI_DIR.glob("*.wiki")):
        title = wiki_title_from_path(path)
        content = safe_read(path)
        pages.append(WikiPage(
            path=str(path),
            filename=path.name,
            title=title,
            title_slug=slugify(title),
            title_simple=simple_text(title),
            content_sample=content[:5000],
            content_simple=simple_text(content[:5000]),
        ))
    return pages


def extract_aliases(gear: dict[str, Any]) -> list[str]:
    aliases: list[str] = []
    name = gear.get("name")
    if name:
        aliases.append(str(name))

    raw = gear.get("raw_record")
    if isinstance(raw, dict):
        for key in ["name", "gear", "item", "gear_name", "display_name", "source_key"]:
            value = raw.get(key)
            if value:
                aliases.append(str(value))

        for key, value in raw.items():
            key_simple = simple_text(key)
            if key_simple in {"name", "gear", "item", "gear name", "display name"} and value:
                aliases.append(str(value))

    clean: list[str] = []
    seen = set()
    for item in aliases:
        norm = simple_text(item)
        if norm and norm not in seen:
            seen.add(norm)
            clean.append(item)
    return clean


def find_snippet(content: str, aliases: list[str]) -> str:
    lower = content.lower()
    for alias in aliases:
        a = str(alias).strip().lower()
        if not a:
            continue
        pos = lower.find(a)
        if pos >= 0:
            start = max(0, pos - 250)
            end = min(len(content), pos + len(a) + 350)
            return content[start:end].replace("\n", " ").strip()
    return content[:500].replace("\n", " ").strip()


def score_page(gear: dict[str, Any], page: WikiPage) -> dict[str, Any]:
    aliases = extract_aliases(gear)
    name = str(gear.get("name") or "")
    name_slug = slugify(name)
    name_simple = simple_text(name)

    best_alias = name
    best_exact_title = False
    best_title_ratio = 0.0
    best_token_score = 0.0
    best_content_hit = False

    for alias in aliases:
        alias_slug = slugify(alias)
        alias_simple = simple_text(alias)

        exact_title = alias_slug == page.title_slug
        title_r = ratio(alias_simple, page.title_simple)
        tok = token_score(alias_simple, page.title_simple)
        content_hit = bool(alias_simple and alias_simple in page.content_simple)

        if exact_title or title_r > best_title_ratio or tok > best_token_score or content_hit:
            best_alias = alias
            best_exact_title = best_exact_title or exact_title
            best_title_ratio = max(best_title_ratio, title_r)
            best_token_score = max(best_token_score, tok)
            best_content_hit = best_content_hit or content_hit

    score = 0.0
    reasons: list[str] = []

    if best_exact_title:
        score += 1.0
        reasons.append("exact_title_slug_match")

    if best_title_ratio >= 0.92:
        score += 0.85
        reasons.append("very_high_title_similarity")
    elif best_title_ratio >= 0.80:
        score += 0.65
        reasons.append("high_title_similarity")
    elif best_title_ratio >= 0.65:
        score += 0.35
        reasons.append("moderate_title_similarity")

    if best_token_score >= 0.9:
        score += 0.8
        reasons.append("very_high_token_overlap")
    elif best_token_score >= 0.6:
        score += 0.5
        reasons.append("high_token_overlap")
    elif best_token_score >= 0.4:
        score += 0.25
        reasons.append("moderate_token_overlap")

    if best_content_hit:
        score += 0.35
        reasons.append("candidate_name_found_in_content_sample")

    score = min(score, 1.0)

    if score >= 0.95:
        match_class = "exact_or_near_exact"
    elif score >= 0.75:
        match_class = "strong_candidate"
    elif score >= 0.5:
        match_class = "possible_candidate"
    elif score >= 0.3:
        match_class = "weak_candidate"
    else:
        match_class = "unlikely"

    return {
        "page_path": page.path,
        "page_title": page.title,
        "page_filename": page.filename,
        "best_alias": best_alias,
        "score": round(score, 4),
        "match_class": match_class,
        "title_similarity": round(best_title_ratio, 4),
        "token_overlap": round(best_token_score, 4),
        "content_hit": best_content_hit,
        "reasons": reasons,
    }


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    gear_items = load_json(GEAR_FILE)
    if not isinstance(gear_items, list):
        raise SystemExit("gear_items.candidates.json is not a list")

    wiki_pages = build_wiki_index()

    matrix: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    matched: list[dict[str, Any]] = []

    for gear in gear_items:
        gear_id = gear.get("id")
        gear_name = gear.get("name")
        aliases = extract_aliases(gear)

        scored = [score_page(gear, page) for page in wiki_pages]
        scored.sort(key=lambda x: (x["score"], x["title_similarity"], x["token_overlap"]), reverse=True)
        top = scored[:10]

        best = top[0] if top else None
        best_score = best["score"] if best else 0

        review_status = "needs_manual_review"
        if best_score >= 0.95:
            review_status = "wiki_match_high_confidence"
        elif best_score >= 0.75:
            review_status = "wiki_match_review_recommended"
        elif best_score >= 0.50:
            review_status = "wiki_match_possible"
        else:
            review_status = "no_good_wiki_match"

        row = {
            "gear_id": gear_id,
            "gear_name": gear_name,
            "aliases": aliases,
            "candidate_confidence": gear.get("confidence"),
            "category_raw": gear.get("category_raw"),
            "slot_raw": gear.get("slot_raw"),
            "best_wiki_page": best["page_path"] if best else None,
            "best_wiki_title": best["page_title"] if best else None,
            "best_score": best_score,
            "best_match_class": best["match_class"] if best else None,
            "best_reasons": best["reasons"] if best else [],
            "top_matches": top,
            "review_status": review_status,
            "source_file": "game/data/candidates/phase1c_gear_calculator/gear_items.candidates.json",
            "created_at": UTC_NOW,
        }

        if best and best_score >= 0.50:
            content = safe_read(Path(best["page_path"]))
            row["best_snippet"] = find_snippet(content, aliases)
            matched.append(row)
        else:
            row["best_snippet"] = None
            unmatched.append(row)

        matrix.append(row)

    summary = {
        "generated_at": UTC_NOW,
        "phase": "1C.1",
        "canonical_promotion": False,
        "gear_candidate_count": len(gear_items),
        "wiki_page_count": len(wiki_pages),
        "matched_count_score_0_50_plus": len(matched),
        "unmatched_count": len(unmatched),
        "high_confidence_count": sum(1 for row in matrix if row["best_score"] >= 0.95),
        "strong_or_better_count": sum(1 for row in matrix if row["best_score"] >= 0.75),
        "outputs": [
            "gear_wiki_review_matrix.json",
            "gear_wiki_review_matrix.csv",
            "unmatched_gear_candidates.json",
            "gear_wiki_review_summary.md",
        ],
    }

    (OUTDIR / "gear_wiki_review_matrix.json").write_text(json.dumps(matrix, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "unmatched_gear_candidates.json").write_text(json.dumps(unmatched, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (OUTDIR / "manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    with (OUTDIR / "gear_wiki_review_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "gear_id",
            "gear_name",
            "aliases",
            "candidate_confidence",
            "category_raw",
            "slot_raw",
            "best_wiki_page",
            "best_wiki_title",
            "best_score",
            "best_match_class",
            "best_reasons",
            "review_status",
        ])
        writer.writeheader()
        for row in matrix:
            writer.writerow({
                "gear_id": row["gear_id"],
                "gear_name": row["gear_name"],
                "aliases": "; ".join(row["aliases"]),
                "candidate_confidence": row["candidate_confidence"],
                "category_raw": row["category_raw"],
                "slot_raw": row["slot_raw"],
                "best_wiki_page": row["best_wiki_page"],
                "best_wiki_title": row["best_wiki_title"],
                "best_score": row["best_score"],
                "best_match_class": row["best_match_class"],
                "best_reasons": "; ".join(row["best_reasons"]),
                "review_status": row["review_status"],
            })

    md: list[str] = []
    md.append("# Phase 1C.1 Gear Wiki Review Summary")
    md.append("")
    md.append(f"Generated UTC: {UTC_NOW}")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- Gear candidates: {summary['gear_candidate_count']}")
    md.append(f"- Wiki pages indexed: {summary['wiki_page_count']}")
    md.append(f"- Matched at score >= 0.50: {summary['matched_count_score_0_50_plus']}")
    md.append(f"- Unmatched: {summary['unmatched_count']}")
    md.append(f"- High confidence score >= 0.95: {summary['high_confidence_count']}")
    md.append(f"- Strong or better score >= 0.75: {summary['strong_or_better_count']}")
    md.append("")
    md.append("## Review Matrix")
    md.append("")
    md.append("| Gear | Best Wiki Page | Score | Status |")
    md.append("|---|---|---:|---|")
    for row in matrix:
        md.append(f"| {row['gear_name']} | {row['best_wiki_title'] or 'NONE'} | {row['best_score']} | {row['review_status']} |")
    md.append("")
    md.append("## Unmatched Gear Candidates")
    md.append("")
    for row in unmatched:
        md.append(f"- {row['gear_name']} ({row['gear_id']}) — best: {row['best_wiki_title']} score {row['best_score']}")
    md.append("")
    md.append("## Next Step")
    md.append("")
    md.append("Use this matrix to decide which gear candidates are safe to promote later. Do not promote automatically.")
    md.append("Phase 1C.2 should build candidate source facts and aliases from high-confidence wiki matches only.")

    (OUTDIR / "gear_wiki_review_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
