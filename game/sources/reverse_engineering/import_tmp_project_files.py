#!/usr/bin/env python3
"""
Import and organize Super Snail project files from /tmp into the workspace.
COPY ONLY. Do not move or delete anything from /tmp.
Focused scan — only known project files and the proof_snail directories.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/home/mint/projects/slimy_snail").resolve()
TMP = Path("/tmp").resolve()

# Exact known filenames to import
EXACT_FILES = [
    "substitution_table.txt",
    "substitution_table_v2.txt",
    "PROTOCOL_SPEC.md",
    "PROTOCOL_SPEC_v2.md",
    "decode_handlers.py",
    "decrypt_all.py",
    "test_decode.lua",
    "all_protocol_messages.txt",
    "all_protocol_messages_v2.txt",
    "list_clean_decoded.lua",
    "list_clean_decoded_v2.lua",
    "final_solve.py",
    "solve_and_rewrite.py",
    "analyze_punct.py",
    "manual_align.py",
    "test_list.py",
    "plan.py",
    "list.luac",
    "msg_group_rank.luac",
    "msg_arena_top_query.luac",
    "cipher_solve_log.txt",
    "align_dp.py",
    "align_manual.py",
    "analyze.py",
    "check_I.py",
    "check_chars.py",
    "check_rare.py",
    "check_t.py",
    "decode.py",
    "decrypt.py",
    "dump_clean.py",
    "exact_align.py",
    "find_unmapped.py",
    "full_decode.py",
    "generate_specs.py",
    "solve_cipher.py",
    "list_fully_decoded.lua",
    "msg_arena_top_query.lua",
    "msg_group_rank.lua",
    "protocol_messages.txt",
    "clean_a.txt",
    "clean_g.txt",
]

# Directories under /tmp that are project-related
PROJECT_DIRS = [
    "proof_snail_protocol_reset_*",
    "proof_snail*",
    "snail-api-recon*",
]

SKIP_DIRS = {".harness", ".git", "node_modules", "__pycache__", ".venv", "venv"}

RAW_EXTENSIONS = {".luac", ".apk", ".xapk", ".apks", ".aab", ".so", ".dex", ".odex", ".vdex", ".pcap", ".pcapng", ".flow", ".har"}

SUSPECT_NAME_PATTERNS = [
    re.compile(r"rewrite", re.I),
    re.compile(r"fake", re.I),
    re.compile(r"final_solve", re.I),
    re.compile(r"solve_and_rewrite", re.I),
]

LUAC_WRITE_PATTERNS = [
    re.compile(r"open\s*\(\s*[^)]*\.luac[^)]*['\"]w", re.I),
    re.compile(r">\s*.*\.luac", re.I),
    re.compile(r"write_bytes", re.I),
    re.compile(r"\.write\s*\(", re.I),
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def classify(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()

    if suffix in RAW_EXTENSIONS:
        return "raw_evidence"

    if name.startswith("substitution_table") and suffix == ".txt":
        return "substitution_tables"

    if name.startswith("protocol_spec") and suffix == ".md":
        return "protocol_docs"
    if name == "cipher_solve_log.txt":
        return "protocol_docs"

    if name.startswith("list_clean_decoded") and suffix == ".lua":
        return "decoded_outputs"
    if name.startswith("all_protocol_messages") and suffix == ".txt":
        return "decoded_outputs"
    if name == "protocol_messages.txt":
        return "decoded_outputs"

    if name in {"final_response.md", "claude_chat.md", "kimi_response.md"} or name.endswith("_response.md"):
        return "agent_reports"

    if suffix in {".py", ".sh", ".lua"}:
        if any(p.search(name) for p in SUSPECT_NAME_PATTERNS):
            return "suspect_scripts"
        # Content scan for .luac writes
        if path.stat().st_size < 5 * 1024 * 1024:
            try:
                content = path.read_text(errors="replace")
                for pat in LUAC_WRITE_PATTERNS:
                    if pat.search(content):
                        return "suspect_scripts"
            except Exception:
                pass
        return "safe_scripts"

    return "unknown_review_required"

def dest_dir_for_class(cls: str, stamp: str) -> Path:
    mapping = {
        "raw_evidence": ROOT / "originals" / "tmp-imports" / stamp,
        "suspect_scripts": ROOT / "quarantine" / "tmp-imports" / stamp / "suspect-scripts",
        "decoded_outputs": ROOT / "data" / "protocol" / "decoded",
        "substitution_tables": ROOT / "data" / "protocol" / "substitution-tables",
        "protocol_docs": ROOT / "docs" / "protocol",
        "agent_reports": ROOT / "reports" / "agent-chats",
        "safe_scripts": ROOT / "scripts" / "imported-tools",
        "unknown_review_required": ROOT / "quarantine" / "tmp-imports" / stamp / "unknown-review",
    }
    return mapping.get(cls, ROOT / "quarantine" / "tmp-imports" / stamp / "unknown-review")

def find_files() -> list[Path]:
    found = set()

    # Exact known files
    for fname in EXACT_FILES:
        src = TMP / fname
        if src.is_file() and not src.is_symlink():
            found.add(src.resolve())

    # Project directories (walk them)
    for pat in PROJECT_DIRS:
        for d in TMP.glob(pat):
            if not d.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(d):
                dirnames[:] = [dd for dd in dirnames if dd not in SKIP_DIRS and not dd.startswith(".")]
                for name in filenames:
                    path = Path(dirpath) / name
                    if path.is_file() and not path.is_symlink():
                        found.add(path.resolve())

    return sorted(found)

def copy_file(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        short_hash = sha256_file(src)[:8]
        stem = dst.stem
        suffix = dst.suffix
        new_name = f"{stem}__sha256_{short_hash}{suffix}"
        dst = dst.parent / new_name
        if dst.exists():
            new_name = f"{stem}__sha256_{short_hash}_{os.urandom(2).hex()}{suffix}"
            dst = dst.parent / new_name
    shutil.copy2(src, dst)
    return dst

def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"=== Super Snail /tmp Import ===")
    print(f"Timestamp: {stamp}")
    print(f"Root: {ROOT}")
    print(f"Scanning: {TMP}")

    files = find_files()
    print(f"Found {len(files)} candidate files")

    evidence_dir = ROOT / "evidence" / "tmp-imports" / stamp
    evidence_dir.mkdir(parents=True, exist_ok=True)

    manifest_tsv = evidence_dir / "MANIFEST.tsv"
    manifest_md = evidence_dir / "MANIFEST.md"
    source_tree = evidence_dir / "source-tree.txt"
    skipped_file = evidence_dir / "skipped.txt"

    rows = []
    skipped = []
    counts: dict[str, int] = {}

    for src in files:
        rel = str(src.relative_to(TMP)) if src.is_relative_to(TMP) else str(src)
        cls = classify(src)
        dst_dir = dest_dir_for_class(cls, stamp)
        dst = dst_dir / src.name

        try:
            actual_dst = copy_file(src, dst)
            size = actual_dst.stat().st_size
            digest = sha256_file(actual_dst)
            rows.append({
                "class": cls,
                "source_path": str(src),
                "dest_path": str(actual_dst.relative_to(ROOT)),
                "size_bytes": size,
                "sha256": digest,
                "action": "copied",
            })
            counts[cls] = counts.get(cls, 0) + 1
        except Exception as exc:
            skipped.append(f"{rel}\t{exc}")
            print(f"SKIP {rel}: {exc}")

    # Write TSV manifest
    with manifest_tsv.open("w", encoding="utf-8") as f:
        f.write("class\tsource_path\tdest_path\tsize_bytes\tsha256\taction\n")
        for r in rows:
            f.write(f"{r['class']}\t{r['source_path']}\t{r['dest_path']}\t{r['size_bytes']}\t{r['sha256']}\t{r['action']}\n")

    # Write MD manifest
    with manifest_md.open("w", encoding="utf-8") as f:
        f.write(f"# /tmp Import Manifest — {stamp}\n\n")
        f.write(f"- **Timestamp:** {stamp}\n")
        f.write(f"- **Source:** {TMP}\n")
        f.write(f"- **Files imported:** {len(rows)}\n")
        f.write(f"- **Skipped:** {len(skipped)}\n\n")
        f.write("## Counts by class\n\n")
        for cls, cnt in sorted(counts.items()):
            f.write(f"- {cls}: {cnt}\n")
        f.write("\n## Files\n\n")
        f.write("| class | dest | size | sha256 |\n")
        f.write("|-------|------|------|--------|\n")
        for r in rows:
            f.write(f"| {r['class']} | `{r['dest_path']}` | {r['size_bytes']} | `{r['sha256'][:16]}...` |\n")

    # Source tree hints
    with source_tree.open("w", encoding="utf-8") as f:
        f.write("# Source tree hints from /tmp\n\n")
        f.write("```\n")
        for d in sorted(set(p.parent for p in files)):
            f.write(f"{d}\n")
        f.write("```\n")

    # Skipped
    with skipped_file.open("w", encoding="utf-8") as f:
        f.write("# Skipped files\n\n")
        for line in skipped:
            f.write(f"{line}\n")

    # Make raw evidence read-only
    originals_dir = ROOT / "originals" / "tmp-imports" / stamp
    if originals_dir.exists():
        for f in originals_dir.rglob("*"):
            if f.is_file():
                f.chmod(0o444)
        print(f"Made {originals_dir} files read-only")

    # Report
    report = ROOT / "reports" / f"tmp-import-{stamp}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as f:
        f.write(f"# /tmp Import Report — {stamp}\n\n")
        f.write(f"- **Files imported:** {len(rows)}\n")
        f.write(f"- **Skipped:** {len(skipped)}\n")
        f.write(f"- **Evidence dir:** `evidence/tmp-imports/{stamp}/`\n")
        f.write(f"- **Originals dir:** `originals/tmp-imports/{stamp}/`\n")
        f.write(f"- **Quarantine dir:** `quarantine/tmp-imports/{stamp}/`\n\n")
        f.write("## Counts by class\n\n")
        for cls, cnt in sorted(counts.items()):
            f.write(f"- {cls}: {cnt}\n")
        f.write("\n## Next steps\n\n")
        f.write("1. Review quarantined scripts for `.luac` writes.\n")
        f.write("2. Verify safe scripts before moving to `scripts/`.\n")
        f.write("3. Run `./snail-run qa` before GitHub sync.\n")

    print(f"\nImport complete.")
    print(f"Evidence dir: {evidence_dir}")
    print(f"Report: {report}")
    print(f"Files imported: {len(rows)}")
    print(f"Skipped: {len(skipped)}")
    for cls, cnt in sorted(counts.items()):
        print(f"  {cls}: {cnt}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
