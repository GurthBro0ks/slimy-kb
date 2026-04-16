#!/usr/bin/env python3
"""
kb-apply-metadata.py — Apply git-backed "Last edited" and "Version" metadata to all wiki pages.

Computes per-page git revision count and latest commit SHA.
Inserts a visible, deterministic metadata block into each page.

Usage:
    python3 kb-apply-metadata.py [--dry-run] [--page <path>]
"""

import subprocess
import sys
import os
import re
import argparse
from pathlib import Path

KB_ROOT = Path("/home/slimy/kb")
KB_WIKI = KB_ROOT / "wiki"

MARKER_BEGIN = "<!-- KB METADATA"
MARKER_END = "KB METADATA -->"
BLOCK_RE = re.compile(
    r"<!-- KB METADATA\n.*?KB METADATA -->",
    re.DOTALL,
)


def git_last_edited(rel_path: str) -> str:
    try:
        ts = (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(KB_ROOT),
                    "log",
                    "-1",
                    "--format=%ad",
                    "--date=format:%Y-%m-%d %H:%M UTC",
                    "--",
                    rel_path,
                ],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        return ts or "unknown"
    except subprocess.CalledProcessError:
        return "unknown"


def git_version(rel_path: str) -> str:
    try:
        count = (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(KB_ROOT),
                    "rev-list",
                    "--count",
                    "HEAD",
                    "--",
                    rel_path,
                ],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        count = "0"
    try:
        sha = (
            subprocess.check_output(
                ["git", "-C", str(KB_ROOT), "log", "-1", "--format=%h", "--", rel_path],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        sha = "unknown"
    if count == "0":
        return "new"
    return f"r{count} / {sha}"


def build_metadata_block(rel_path: str) -> str:
    last_edited = git_last_edited(rel_path)
    version = git_version(rel_path)
    return f"{MARKER_BEGIN}\n> Last edited: {last_edited} (git)\n> Version: {version}\n{MARKER_END}"


def find_insert_point(lines: list[str]) -> int:
    """
    Find where to insert the metadata block.
    Strategy: after the last header blockquote line (> ...) that follows a # title,
    but before <!-- BEGIN MACHINE MANAGED --> or the first content line.
    Returns the line index (0-based) where the block should be inserted.
    """
    last_bq = -1
    saw_title = False
    machine_managed_line = -1
    first_content_after_header = -1

    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")

        if stripped.startswith("# ") and not saw_title:
            saw_title = True
            continue

        if not saw_title:
            continue

        if stripped.startswith("<!-- BEGIN MACHINE MANAGED"):
            machine_managed_line = i
            break

        if stripped.startswith("> "):
            last_bq = i
            continue

        if stripped == "":
            continue

        # First non-empty, non-blockquote, non-title line after header
        if first_content_after_header == -1 and last_bq >= 0:
            first_content_after_header = i
            break

    # Best: just before <!-- BEGIN MACHINE MANAGED -->
    if machine_managed_line >= 0:
        return machine_managed_line

    # After last blockquote line + a blank line
    if last_bq >= 0:
        insert = last_bq + 1
        # Skip blank lines right after blockquotes
        while insert < len(lines) and lines[insert].strip() == "":
            insert += 1
        return insert

    # Fallback: after first blank line after title
    if saw_title:
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == "":
                return i + 1

    # Last resort: line 1
    return 1


def apply_metadata(file_path: Path, dry_run: bool = False) -> tuple[bool, str]:
    """Apply metadata to a single page. Returns (changed, description)."""
    rel_path = str(file_path.relative_to(KB_ROOT))
    content = file_path.read_text()
    new_block = build_metadata_block(rel_path)

    existing_match = BLOCK_RE.search(content)
    if existing_match:
        if existing_match.group(0) == new_block:
            return False, "unchanged"
        if dry_run:
            return True, f"would update metadata in {rel_path}"
        new_content = (
            content[: existing_match.start()]
            + new_block
            + content[existing_match.end() :]
        )
        file_path.write_text(new_content)
        return True, f"updated metadata in {rel_path}"

    lines = content.split("\n")
    insert_idx = find_insert_point(lines)

    block_with_newline = "\n" + new_block + "\n"

    if dry_run:
        return True, f"would insert metadata at line {insert_idx + 1} in {rel_path}"

    new_lines = lines[:insert_idx] + [new_block, ""] + lines[insert_idx:]
    file_path.write_text("\n".join(new_lines))
    return True, f"inserted metadata at line {insert_idx + 1} in {rel_path}"


def main():
    parser = argparse.ArgumentParser(
        description="Apply git-backed metadata to wiki pages"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--page", default="")
    args = parser.parse_args()

    if args.page:
        p = Path(args.page)
        if not p.exists():
            print(f"File not found: {args.page}", file=sys.stderr)
            sys.exit(1)
        changed, desc = apply_metadata(p, args.dry_run)
        print(desc)
        sys.exit(0)

    md_files = sorted(KB_WIKI.rglob("*.md"))
    updated = 0
    skipped = 0

    for f in md_files:
        changed, desc = apply_metadata(f, args.dry_run)
        if changed:
            updated += 1
            if args.dry_run:
                print(f"  [dry-run] {desc}")
        else:
            skipped += 1

    print(
        f"kb-apply-metadata: total={len(md_files)} updated={updated} unchanged={skipped}"
    )


if __name__ == "__main__":
    main()
