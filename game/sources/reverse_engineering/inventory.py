#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAIL_PROJECT_ROOT", Path.cwd())).resolve()

RAW_PATTERNS = [".apk", ".xapk", ".apks", ".aab", ".so", ".dex", ".odex", ".vdex", ".luac", ".pcap", ".pcapng", ".flow", ".har"]
SUSPECT_NAME_PATTERNS = [
    re.compile(r"rewrite", re.I),
    re.compile(r"fake", re.I),
    re.compile(r"final_solve", re.I),
    re.compile(r"solve_and_rewrite", re.I),
]
SAFE_EXTS = {".md", ".py", ".sh", ".json", ".txt", ".lua", ".yml", ".yaml", ".toml"}

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".harness"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(path: Path) -> str:
    rel = str(path.relative_to(ROOT))
    suffix = path.suffix.lower()
    if any(part in {"originals", "captures"} for part in path.parts):
        return "raw_evidence"
    if any(part == "quarantine" for part in path.parts):
        return "quarantined"
    if suffix in RAW_PATTERNS:
        return "raw_or_sensitive_artifact"
    if any(p.search(path.name) for p in SUSPECT_NAME_PATTERNS):
        return "suspect_mutating_script"
    if suffix in SAFE_EXTS:
        return "safe_project_file"
    if rel.startswith("scripts/"):
        return "safe_project_file"
    return "unknown_review_required"


def main() -> int:
    rows = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.is_symlink():
                continue
            rel = path.relative_to(ROOT).as_posix()
            try:
                size = path.stat().st_size
                digest = sha256(path) if size <= 50 * 1024 * 1024 else "SKIPPED_OVER_50MB"
            except OSError as exc:
                size = -1
                digest = f"ERROR:{exc}"
            rows.append({
                "path": rel,
                "size": size,
                "sha256": digest,
                "class": classify(path),
            })
    rows.sort(key=lambda r: r["path"])
    print(json.dumps({"root": str(ROOT), "files": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
