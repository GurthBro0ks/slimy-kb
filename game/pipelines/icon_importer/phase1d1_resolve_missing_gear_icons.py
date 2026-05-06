#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(".")
CANON_DIR = ROOT / "game/data/canonical/gear"
GEAR_CARDS = ROOT / "game/data/exports/gear/gear.web.cards.json"
CARDS_WITH_ICONS = ROOT / "game/data/exports/gear/gear.web.cards.with-icons.json"
ASSET_DIR = ROOT / "game/assets/icons/gear"
MANIFEST = ROOT / "game/assets/manifests/gear-icons.manifest.json"
RESOLUTION_MANIFEST = ROOT / "game/assets/manifests/gear-icons-missing-resolution.json"
REPORT = ROOT / "game/reports/audits/phase1d1-missing-gear-icon-resolution-2026-05-06.md"

API = "https://supersnail.wiki.gg/api.php"
USER_AGENT = "SlimyKB/1.0 missing gear icon resolver"
UTC_NOW = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

MANUAL_ALIASES = {
    "Persian Composite Bow": ["Parsian Composite Bow.png", "Persian Composite Bow.png"],
    "Mithraic Bow & Spear": ["Mithraic Bow and Spear.png", "Mithraic Bow & Spear.png", "Mithraic Bow Spear.png"],
    "Amulet of Will +1": ["Amulet of Will.png", "Amulet of Will 1.png", "Amulet of Will +1.png"],
    "Lotus Platform III": ["Lotus Platform.png", "Lotus Platform III.png"],
    "Lotus Platform VI": ["Lotus Platform.png", "Lotus Platform VI.png"],
    "Lotus Platform IX": ["Lotus Platform.png", "Lotus Platform IX.png"],
}

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_filename(value: str) -> str:
    text = str(value or "").strip().replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    return text or "unknown.png"

def simple(value: str) -> str:
    text = str(value or "").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, simple(a), simple(b)).ratio()

def api_query(params: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_imageinfo(filename: str) -> dict[str, Any] | None:
    title = filename if filename.lower().startswith("file:") else "File:" + filename
    data = api_query({
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": title,
        "iiprop": "url|size|sha1|mime|metadata",
    })
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        if "missing" in page:
            return None
        infos = page.get("imageinfo") or []
        if infos:
            info = dict(infos[0])
            info["title"] = page.get("title", title)
            return info
    return None

def allimages_prefix(prefix: str) -> list[str]:
    out = []
    data = api_query({
        "action": "query",
        "format": "json",
        "list": "allimages",
        "aiprefix": prefix,
        "ailimit": "50",
    })
    for item in data.get("query", {}).get("allimages", []):
        name = item.get("name")
        if name:
            out.append(name)
    return out

def search_pages(term: str) -> list[str]:
    out = []
    data = api_query({
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": term,
        "srlimit": "20",
    })
    for item in data.get("query", {}).get("search", []):
        title = item.get("title")
        if title and title.startswith("File:"):
            out.append(title.replace("File:", ""))
    return out

def gear_page_images() -> list[str]:
    out = []
    data = api_query({
        "action": "query",
        "format": "json",
        "titles": "Gear",
        "prop": "images",
        "imlimit": "max",
    })
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        for img in page.get("images", []) or []:
            title = img.get("title", "")
            if title.startswith("File:"):
                out.append(title.replace("File:", ""))
    return out

def download_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()

def ext_from_info(info: dict[str, Any], fallback: str) -> str:
    url = info.get("url")
    if url:
        suffix = Path(urllib.parse.urlparse(url).path).suffix
        if suffix:
            return suffix
    mime = info.get("mime")
    if mime:
        ext = mimetypes.guess_extension(mime)
        if ext:
            return ext
    return Path(fallback).suffix or ".png"

def resolve_one(card: dict[str, Any], gear_images: list[str]) -> dict[str, Any]:
    name = card.get("name") or ""
    current_filename = card.get("icon_filename") or ""

    candidates = []
    if current_filename:
        candidates.append(current_filename)

    candidates.extend(MANUAL_ALIASES.get(name, []))
    candidates.append(f"{name}.png")
    candidates.append(f"{name.replace('&', 'and')}.png")
    candidates.append(f"{name.replace('+', '').strip()}.png")

    # Prefix lookup from first word or full name chunk.
    first = name.split()[0] if name.split() else name
    for p in [name[:20], first]:
        try:
            candidates.extend(allimages_prefix(p))
            time.sleep(0.1)
        except Exception:
            pass

    try:
        candidates.extend(search_pages(name))
        time.sleep(0.1)
    except Exception:
        pass

    # Fuzzy search embedded Gear page images.
    scored_images = sorted(
        gear_images,
        key=lambda img: ratio(name, Path(img).stem),
        reverse=True,
    )
    candidates.extend(scored_images[:15])

    seen = set()
    clean_candidates = []
    for c in candidates:
        c = str(c or "").strip()
        if not c:
            continue
        key = c.lower()
        if key not in seen:
            seen.add(key)
            clean_candidates.append(c)

    attempts = []
    for cand in clean_candidates:
        info = get_imageinfo(cand)
        attempts.append({"candidate": cand, "found": bool(info)})
        if not info:
            continue

        # Require either manual alias, direct-ish similarity, or Gear page image similarity.
        sim = ratio(name, Path(cand).stem)
        if cand in MANUAL_ALIASES.get(name, []) or sim >= 0.58:
            return {
                "resolved": True,
                "name": name,
                "gear_id": card.get("id"),
                "original_icon_filename": current_filename,
                "resolved_icon_filename": cand,
                "imageinfo": info,
                "similarity": sim,
                "attempts": attempts,
            }

    return {
        "resolved": False,
        "name": name,
        "gear_id": card.get("id"),
        "original_icon_filename": current_filename,
        "attempts": attempts,
    }

def main() -> None:
    manifest = load_json(MANIFEST)
    cards_with = load_json(CARDS_WITH_ICONS)
    cards_base = load_json(GEAR_CARDS)

    cards = cards_with.get("cards", [])
    missing = [c for c in cards if not c.get("icon_ref")]

    print("missing_count_before", len(missing))
    for c in missing:
        print("MISSING", c.get("id"), c.get("name"), c.get("icon_filename"))

    gear_images = gear_page_images()
    print("gear_page_images", len(gear_images))

    resolutions = []
    newly_downloaded = []

    existing_by_icon = {r.get("icon_filename"): r for r in manifest.get("records", [])}
    existing_by_id = {r.get("id"): r for r in manifest.get("records", [])}

    for card in missing:
        res = resolve_one(card, gear_images)
        resolutions.append(res)
        if not res.get("resolved"):
            continue

        info = res["imageinfo"]
        url = info.get("url")
        if not url:
            res["resolved"] = False
            res["download_error"] = "missing_url"
            continue

        data = download_url(url)
        digest = sha256_bytes(data)
        local_base = safe_filename(Path(res["resolved_icon_filename"]).stem)
        ext = ext_from_info(info, res["resolved_icon_filename"])
        local_path = ASSET_DIR / f"{local_base}{ext}"
        local_path.write_bytes(data)

        icon_record = {
            "id": local_base.lower(),
            "category": "gear",
            "entity_refs": [res["gear_id"]],
            "icon_filename": res["resolved_icon_filename"],
            "source_title": info.get("title"),
            "original_url": url,
            "description_url": info.get("descriptionurl"),
            "local_path": str(local_path),
            "hash_sha256": digest,
            "wiki_sha1": info.get("sha1"),
            "width": info.get("width"),
            "height": info.get("height"),
            "size_bytes": len(data),
            "wiki_size_bytes": info.get("size"),
            "mime_type": info.get("mime"),
            "retrieved_at": UTC_NOW,
            "license_note": "Source: Super Snail wiki.gg. Preserve attribution and verify license before public redistribution.",
            "attribution_note": "Resolved during Phase 1D.1 missing icon fallback lookup.",
            "resolution_note": {
                "original_icon_filename": res.get("original_icon_filename"),
                "similarity": res.get("similarity"),
            }
        }

        manifest["records"].append(icon_record)
        newly_downloaded.append(icon_record)

    # Rebuild card icon refs from manifest records.
    by_icon = {}
    by_ref = {}
    for r in manifest.get("records", []):
        by_icon[r.get("icon_filename")] = r
        for ref in r.get("entity_refs", []) or []:
            by_ref[ref] = r

    updated_cards = []
    for card in cards:
        c = dict(card)
        icon = None
        if c.get("icon_filename") in by_icon:
            icon = by_icon[c.get("icon_filename")]
        if not icon and c.get("id") in by_ref:
            icon = by_ref[c.get("id")]
        if icon:
            c["icon_ref"] = icon.get("id")
            c["icon_local_path"] = icon.get("local_path")
            c["icon_hash_sha256"] = icon.get("hash_sha256")
            c["icon_width"] = icon.get("width")
            c["icon_height"] = icon.get("height")
            c["icon_mime_type"] = icon.get("mime_type")
        updated_cards.append(c)

    matched = sum(1 for c in updated_cards if c.get("icon_ref"))
    still_missing = [c for c in updated_cards if not c.get("icon_ref")]

    manifest["downloaded_icons"] = len(manifest.get("records", []))
    manifest["matched_web_cards"] = matched
    manifest["unmatched_web_cards"] = len(still_missing)
    manifest["error_count"] = len(manifest.get("errors", []))
    manifest["phase1d1_updated_at"] = UTC_NOW

    write_json(MANIFEST, manifest)
    write_json(CARDS_WITH_ICONS, {
        "generated_at": UTC_NOW,
        "record_count": len(updated_cards),
        "matched_icon_count": matched,
        "unmatched_icon_count": len(still_missing),
        "cards": updated_cards,
    })

    write_json(RESOLUTION_MANIFEST, {
        "generated_at": UTC_NOW,
        "phase": "1D.1",
        "missing_count_before": len(missing),
        "newly_downloaded": len(newly_downloaded),
        "matched_after": matched,
        "still_missing": len(still_missing),
        "resolutions": resolutions,
        "new_icon_records": newly_downloaded,
        "still_missing_cards": still_missing,
    })

    report = []
    report.append("# Phase 1D.1 Missing Gear Icon Resolution Audit")
    report.append("")
    report.append(f"Generated UTC: {UTC_NOW}")
    report.append("")
    report.append("## Results")
    report.append("")
    report.append(f"- Missing before: {len(missing)}")
    report.append(f"- Newly downloaded: {len(newly_downloaded)}")
    report.append(f"- Matched cards after: {matched}")
    report.append(f"- Still missing: {len(still_missing)}")
    report.append("")
    report.append("## Newly Resolved")
    report.append("")
    for r in newly_downloaded:
        report.append(f"- {r['entity_refs']} -> {r['icon_filename']} -> {r['local_path']}")
    report.append("")
    report.append("## Still Missing")
    report.append("")
    if still_missing:
        for c in still_missing:
            report.append(f"- {c.get('id')} — {c.get('name')} — {c.get('icon_filename')}")
    else:
        report.append("- None")
    report.append("")
    report.append("## Notes")
    report.append("")
    report.append("Resolution used manual aliases, MediaWiki imageinfo, allimages prefix search, wiki search, and Gear page embedded image fallback.")
    report.append("")

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps({
        "missing_before": len(missing),
        "newly_downloaded": len(newly_downloaded),
        "matched_after": matched,
        "still_missing": len(still_missing),
    }, indent=2))

    if matched < 305:
        raise SystemExit("STOP: icon match coverage still below 305 cards.")

if __name__ == "__main__":
    main()
