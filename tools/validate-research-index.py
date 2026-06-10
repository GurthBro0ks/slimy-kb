#!/usr/bin/env python3
"""
tools/validate-research-index.py
Phase 1 Research Farm validator.

Validates research/indexes/index.json against the contracts declared in
research/templates/. Uses only the Python standard library.

Checks:
  * Top-level fields present: schema_version, source, theme, items.
  * Each item has the minimum required fields and correct enum values.
  * topic_path is repo-relative, points under research/, points to an
    existing file, and the basename (without .md) matches the item slug.
  * pdf_path / report_path / critic_path / proof_path, when set, live
    under research/ and do not escape with '..'.
  * If an item has status == 'completed', the proof_path, report_path,
    and critic_path must be set and resolve to existing files.

Exit code:
  0  -> RESULT=PASS
  1  -> RESULT=FAIL
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
INDEX_PATH = os.path.join(REPO_ROOT, "research", "indexes", "index.json")
RESEARCH_DIR = os.path.join(REPO_ROOT, "research")

ALLOWED_STATUS = {"queued", "claimed", "running", "completed", "failed", "archived"}
ALLOWED_PRIORITY = {"low", "normal", "high", "urgent"}
ALLOWED_DEPTH = {"quick", "standard", "deep"}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,80}$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")
TOPIC_RE = re.compile(r"^research/topics/[a-z0-9][a-z0-9-]{1,80}\.md$")
PATH_RE = re.compile(r"^research/[A-Za-z0-9._/-]+$")


def _err(errors: List[str], msg: str) -> None:
    errors.append(msg)


def _is_under_research(rel_path: str) -> bool:
    """True if the repo-relative path lives under research/ and has no '..'."""
    if not rel_path or rel_path != rel_path.strip():
        return False
    if ".." in rel_path.split("/"):
        return False
    if not rel_path.startswith("research/"):
        return False
    return True


def _abs(rel_path: str) -> str:
    return os.path.normpath(os.path.join(REPO_ROOT, rel_path))


def _check_item(item: Any, idx: int, errors: List[str]) -> None:
    if not isinstance(item, dict):
        _err(errors, f"items[{idx}]: not a JSON object")
        return

    label = f"items[{idx}]"

    # Required fields.
    for field in ("slug", "title", "status", "priority", "depth", "topic_path", "tags"):
        if field not in item:
            _err(errors, f"{label}: missing required field '{field}'")

    slug = item.get("slug")
    if isinstance(slug, str):
        if not SLUG_RE.match(slug):
            _err(errors, f"{label}: slug '{slug}' does not match ^[a-z0-9][a-z0-9-]{{1,80}}$")
    elif "slug" in item:
        _err(errors, f"{label}: slug must be a string")

    title = item.get("title")
    if not isinstance(title, str) or not title.strip():
        _err(errors, f"{label}: title must be a non-empty string")

    status = item.get("status")
    if status not in ALLOWED_STATUS:
        _err(errors, f"{label}: status '{status}' not in {sorted(ALLOWED_STATUS)}")

    priority = item.get("priority")
    if priority not in ALLOWED_PRIORITY:
        _err(errors, f"{label}: priority '{priority}' not in {sorted(ALLOWED_PRIORITY)}")

    depth = item.get("depth")
    if depth not in ALLOWED_DEPTH:
        _err(errors, f"{label}: depth '{depth}' not in {sorted(ALLOWED_DEPTH)}")

    tags = item.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) and TAG_RE.match(t) for t in tags):
        _err(errors, f"{label}: tags must be an array of ^[a-z0-9][a-z0-9-]{{1,40}}$ strings")

    topic_path = item.get("topic_path")
    if isinstance(topic_path, str):
        if not TOPIC_RE.match(topic_path):
            _err(
                errors,
                f"{label}: topic_path '{topic_path}' must match ^research/topics/<slug>.md$",
            )
        else:
            topic_abs = _abs(topic_path)
            if not os.path.isfile(topic_abs):
                _err(errors, f"{label}: topic_path file does not exist on disk: {topic_path}")
            expected_slug = os.path.splitext(os.path.basename(topic_path))[0]
            if isinstance(slug, str) and slug != expected_slug:
                _err(
                    errors,
                    f"{label}: slug '{slug}' does not match topic_path basename '{expected_slug}'",
                )
    elif "topic_path" in item:
        _err(errors, f"{label}: topic_path must be a string")

    # Optional path fields must be null or live under research/.
    for path_field in ("pdf_path", "report_path", "critic_path", "proof_path"):
        if path_field not in item:
            continue
        val = item[path_field]
        if val is None:
            continue
        if not isinstance(val, str) or not PATH_RE.match(val):
            _err(
                errors,
                f"{label}: {path_field} '{val}' must be null or a repo-relative path under research/",
            )
            continue
        # proof_path should specifically be a directory under research/runs/.
        if path_field == "proof_path":
            if not val.startswith("research/runs/"):
                _err(
                    errors,
                    f"{label}: proof_path '{val}' must start with 'research/runs/'",
                )
            else:
                abs_path = _abs(val)
                if not os.path.isdir(abs_path):
                    _err(
                        errors,
                        f"{label}: proof_path directory does not exist on disk: {val}",
                    )

    # If the item claims to be completed, the burrow artifacts must exist.
    if status == "completed":
        for path_field, kind in (("proof_path", "directory"), ("report_path", "file"), ("critic_path", "file")):
            val = item.get(path_field)
            if not val:
                _err(errors, f"{label}: status=completed requires '{path_field}' to be set")
                continue
            if not _is_under_research(val):
                _err(errors, f"{label}: {path_field} '{val}' must be under research/")
                continue
            abs_path = _abs(val)
            if kind == "directory" and not os.path.isdir(abs_path):
                _err(errors, f"{label}: {path_field} directory missing: {val}")
            elif kind == "file" and not os.path.isfile(abs_path):
                _err(errors, f"{label}: {path_field} file missing: {val}")

    # Field types for the other optionals.
    if "confidence" in item and item["confidence"] is not None:
        c = item["confidence"]
        if not isinstance(c, (int, float)) or not (0.0 <= float(c) <= 1.0):
            _err(errors, f"{label}: confidence must be null or 0.0-1.0")
    for int_field in ("source_count", "citation_count"):
        if int_field in item:
            v = item[int_field]
            if not isinstance(v, int) or v < 0:
                _err(errors, f"{label}: {int_field} must be a non-negative integer")


def validate(index_path: str = INDEX_PATH) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []
    if not os.path.isfile(index_path):
        return False, [f"index file not found: {index_path}"], {}

    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"index file is not valid JSON: {e}"], {}

    if not isinstance(data, dict):
        return False, ["index root is not a JSON object"], {}

    for field in ("schema_version", "source", "theme", "items"):
        if field not in data:
            _err(errors, f"missing top-level field '{field}'")

    if data.get("source") != "slimy-kb":
        _err(errors, f"top-level source must be 'slimy-kb' (got {data.get('source')!r})")

    if data.get("theme") != "research_farm":
        _err(errors, f"top-level theme must be 'research_farm' (got {data.get('theme')!r})")

    if not isinstance(data.get("schema_version"), int) or data.get("schema_version", 0) < 1:
        _err(errors, "top-level schema_version must be a positive integer")

    items = data.get("items")
    if not isinstance(items, list):
        _err(errors, "top-level items must be a JSON array")
        items = []

    seen_slugs = set()
    for i, item in enumerate(items):
        _check_item(item, i, errors)
        if isinstance(item, dict) and isinstance(item.get("slug"), str):
            slug = item["slug"]
            if slug in seen_slugs:
                _err(errors, f"items[{i}]: duplicate slug '{slug}'")
            seen_slugs.add(slug)

    return (len(errors) == 0), errors, data


def main() -> int:
    args = sys.argv[1:]
    index_path = INDEX_PATH
    if args:
        if args[0] in ("-h", "--help"):
            print(__doc__)
            return 0
        index_path = os.path.abspath(args[0])

    ok, errors, data = validate(index_path)
    print(f"index path: {index_path}")
    print(f"items: {len(data.get('items', [])) if isinstance(data, dict) else 'n/a'}")
    if errors:
        print("errors:")
        for e in errors:
            print(f"  - {e}")
    print(f"RESULT={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
