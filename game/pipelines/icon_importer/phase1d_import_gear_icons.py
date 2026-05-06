#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(".")
CANON_DIR = ROOT / "game/data/canonical/gear"
GEAR_CARDS = ROOT / "game/data/exports/gear/gear.web.cards.json"
ASSET_DIR = ROOT / "game/assets/icons/gear"
MANIFEST = ROOT / "game/assets/manifests/gear-icons.manifest.json"
EXPORT_WITH_ICONS = ROOT / "game/data/exports/gear/gear.web.cards.with-icons.json"
REPORT = ROOT / "game/reports/audits/phase1d-gear-icon-asset-manifest-2026-05-06.md"

API = "https://supersnail.wiki.gg/api.php"
USER_AGENT = "SlimyKB/1.0 gear icon importer"

UTC_NOW = datetime.now(timezone.utc).isoformat()

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_filename(value: str) -> str:
    text = str(value or "").strip()
    text = text.replace(" ", "_")
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    return text or "unknown.png"

def ext_from_mime_or_url(mime: str | None, url: str | None, fallback: str) -> str:
    if url:
        suffix = Path(urllib.parse.urlparse(url).path).suffix
        if suffix:
            return suffix
    if mime:
        ext = mimetypes.guess_extension(mime)
        if ext:
            return ext
    suffix = Path(fallback).suffix
    return suffix or ".png"

def api_query(params: dict[str, str]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{API}?{query}", headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_imageinfo(filename: str) -> dict[str, Any] | None:
    if not filename:
        return None

    title = filename
    if not title.lower().startswith("file:"):
        title = "File:" + title

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
            return {
                "title": title,
                "missing": True,
                "page": page,
            }
        infos = page.get("imageinfo") or []
        if infos:
            info = dict(infos[0])
            info["title"] = page.get("title", title)
            return info

    return None

def download_url(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()

def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_WITH_ICONS.parent.mkdir(parents=True, exist_ok=True)

    canon_files = sorted(CANON_DIR.glob("*.json"))
    if len(canon_files) != 313:
        raise SystemExit(f"STOP: expected 313 canonical gear records, got {len(canon_files)}")

    records = [load_json(p) for p in canon_files]
    cards_export = load_json(GEAR_CARDS)
    cards = cards_export.get("cards", [])

    # Derive icon filenames from gear names
    icon_names = sorted(set(f"{r['name']}.png" for r in records if r.get("name")))
    print(f"unique_icon_filenames={len(icon_names)}")

    manifest_records = []
    errors = []

    for idx, icon_name in enumerate(icon_names, start=1):
        print(f"[{idx}/{len(icon_names)}] {icon_name}")
        try:
            info = get_imageinfo(icon_name)
            if not info or info.get("missing"):
                errors.append({"icon_filename": icon_name, "error": "missing_imageinfo", "info": info})
                continue

            url = info.get("url")
            if not url:
                errors.append({"icon_filename": icon_name, "error": "missing_url", "info": info})
                continue

            data = download_url(url)
            digest = sha256_bytes(data)
            ext = ext_from_mime_or_url(info.get("mime"), url, icon_name)
            local_name = safe_filename(Path(icon_name).stem) + ext
            local_path = ASSET_DIR / local_name
            local_path.write_bytes(data)

            manifest_records.append({
                "id": safe_filename(Path(icon_name).stem).lower(),
                "category": "gear",
                "entity_refs": sorted([r["id"] for r in records if f"{r['name']}.png" == icon_name]),
                "icon_filename": icon_name,
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
                "attribution_note": "Downloaded via MediaWiki imageinfo URL for local KB/icon mapping.",
            })

            time.sleep(0.1)

        except Exception as exc:
            errors.append({"icon_filename": icon_name, "error": repr(exc)})

    by_icon = {row["icon_filename"]: row for row in manifest_records}

    card_rows = []
    for card in cards:
        card = dict(card)
        icon_filename = f"{card.get('name', '')}.png"
        icon = by_icon.get(icon_filename)
        if icon:
            card["icon_ref"] = icon["id"]
            card["icon_local_path"] = icon["local_path"]
            card["icon_hash_sha256"] = icon["hash_sha256"]
            card["icon_width"] = icon["width"]
            card["icon_height"] = icon["height"]
            card["icon_mime_type"] = icon["mime_type"]
        else:
            card["icon_ref"] = None
            card["icon_local_path"] = None
        card_rows.append(card)

    matched_cards = sum(1 for c in card_rows if c.get("icon_ref"))

    manifest = {
        "generated_at": UTC_NOW,
        "phase": "1D",
        "source": "MediaWiki imageinfo for gear names mapped to wiki file pages",
        "api": API,
        "canonical_gear_records": len(records),
        "unique_icon_filenames": len(icon_names),
        "downloaded_icons": len(manifest_records),
        "error_count": len(errors),
        "matched_web_cards": matched_cards,
        "unmatched_web_cards": len(card_rows) - matched_cards,
        "records": sorted(manifest_records, key=lambda r: r["id"]),
        "errors": errors,
    }

    write_json(MANIFEST, manifest)
    write_json(EXPORT_WITH_ICONS, {
        "generated_at": UTC_NOW,
        "record_count": len(card_rows),
        "matched_icon_count": matched_cards,
        "cards": card_rows,
    })

    tier_counts = Counter(c.get("tier_color") for c in card_rows)
    mime_counts = Counter(r.get("mime_type") for r in manifest_records)

    report = []
    report.append("# Phase 1D Gear Icon Asset Manifest Audit")
    report.append("")
    report.append(f"Generated UTC: {UTC_NOW}")
    report.append("")
    report.append("## Result")
    report.append("")
    report.append("Gear icon files were mapped from canonical gear names using the wiki.gg MediaWiki imageinfo API.")
    report.append("")
    report.append("## Counts")
    report.append("")
    report.append(f"- Canonical gear records: {len(records)}")
    report.append(f"- Unique icon filenames: {len(icon_names)}")
    report.append(f"- Downloaded icons: {len(manifest_records)}")
    report.append(f"- Errors: {len(errors)}")
    report.append(f"- Web cards with matched icons: {matched_cards}")
    report.append(f"- Web cards without matched icons: {len(card_rows) - matched_cards}")
    report.append("")
    report.append("## Tier Counts")
    report.append("")
    for key, value in sorted(tier_counts.items()):
        report.append(f"- {key}: {value}")
    report.append("")
    report.append("## MIME Counts")
    report.append("")
    for key, value in sorted(mime_counts.items()):
        report.append(f"- {key}: {value}")
    report.append("")
    report.append("## Errors")
    report.append("")
    if errors:
        for err in errors[:100]:
            report.append(f"- {err}")
    else:
        report.append("- None")
    report.append("")
    report.append("## Next Step")
    report.append("")
    report.append("If icon coverage is acceptable, Phase 1E can package gear exports for slimy-monorepo website integration.")
    report.append("If icon coverage is incomplete, add fallback lookup using category/file search before website integration.")
    report.append("")

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps({
        "canonical_gear_records": len(records),
        "unique_icon_filenames": len(icon_names),
        "downloaded_icons": len(manifest_records),
        "error_count": len(errors),
        "matched_web_cards": matched_cards,
        "unmatched_web_cards": len(card_rows) - matched_cards,
    }, indent=2))

    if len(icon_names) < 250:
        raise SystemExit("STOP: suspiciously low unique icon filename count.")
    if len(manifest_records) < 250:
        raise SystemExit("STOP: too few icons downloaded.")
    if matched_cards < 250:
        raise SystemExit("STOP: too few web cards matched to icons.")

if __name__ == "__main__":
    main()
