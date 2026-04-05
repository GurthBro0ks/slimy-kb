#!/usr/bin/env bash
# kb-compile-if-needed.sh
# Check whether new raw files exist that are not yet referenced; run compile if yes.
# Usage: kb-compile-if-needed.sh [--dry-run] [--force]
set -euo pipefail

DRY_RUN="${1:-}"
FORCE="${2:-}"
HOST=$(hostname -s)
TODAY=$(date +%Y-%m-%d)
KB_ROOT="/home/slimy/kb"

# Collect compile candidates (same logic as wiki CLI)
collect_compile_candidates() {
    local -A referenced=()
    local wiki_file ref
    local -a source_lines=()

    while IFS= read -r wiki_file; do
        [[ -f "$wiki_file" ]] || continue
        mapfile -t source_lines < <(grep -hE '^> Sources:' "$wiki_file" 2>/dev/null || true)
        for ref in "${source_lines[@]}"; do
            grep -oE 'raw/[A-Za-z0-9._/-]+\.md' <<< "$ref" 2>/dev/null
        done
    done < <(find "$KB_ROOT/wiki" -type f -name '*.md' ! -name '_*.md' 2>/dev/null)

    find "$KB_ROOT/raw" -type f -name '*.md' -printf '%P\n' 2>/dev/null | sort | while IFS= read -r raw_rel; do
        if [[ -z "${referenced[$raw_rel]:-}" ]]; then
            printf '%s\n' "$raw_rel"
        fi
    done
}

echo "[kb-compile-if-needed] Checking for uncompiled raw files..."

mapfile -t candidates < <(collect_compile_candidates)
count=${#candidates[@]}

echo "[kb-compile-if-needed] Found $count uncompiled raw file(s)"

if [[ "$count" -eq 0 ]]; then
    echo "[kb-compile-if-needed] No compile needed — all raw files are referenced. Exiting cleanly."
    echo "[kb-compile-if-needed] Summary: KB is up-to-date as of $TODAY $HOST"
    exit 0
fi

echo "[kb-compile-if-needed] Compile candidates:"
for c in "${candidates[@]}"; do
    echo "  - $c"
done

if [[ "$FORCE" != "--force" && "$DRY_RUN" == "--dry-run" ]]; then
    echo "[kb-compile-if-needed] DRY-RUN: would trigger compile for $count file(s)"
    exit 0
fi

if [[ "$FORCE" == "--force" ]]; then
    echo "[kb-compile-if-needed] FORCE flag set — triggering compile"
elif [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[kb-compile-if-needed] DRY-RUN: would trigger compile for $count file(s)"
    exit 0
fi

echo "[kb-compile-if-needed] Triggering KB compile prompt..."
bash "$KB_ROOT/tools/wiki" prompt-compile >/dev/null 2>&1
latest_prompt=$(ls -t "$KB_ROOT/output/prompts/compile-prompt-"*.md 2>/dev/null | head -1 || true)

if [[ -n "$latest_prompt" ]]; then
    echo "[kb-compile-if-needed] Compile prompt written to: $latest_prompt"
    echo "[kb-compile-if-needed] To run compile, execute the prompt or run: wiki prompt-compile"
else
    echo "[kb-compile-if-needed] WARNING: compile prompt file not found"
fi
