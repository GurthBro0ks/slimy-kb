#!/usr/bin/env bash
# kb-idea-ingest.sh
# Ingest human-owned notes/photos metadata from vault Ideas folder into KB raw.
# Usage: kb-idea-ingest.sh [--dry-run]
set -euo pipefail

DRY_RUN="${1:-}"
HOST=$(hostname -s)
TODAY=$(date +%Y-%m-%d)
KB_ROOT="/home/slimy/kb"
VAULT_IDEAS="/home/slimy/obsidian/slimyai-vault/Ideas"
RAW_IDEAS="$KB_ROOT/raw/ideas"
RAW_PHOTOS="$KB_ROOT/raw/photos"

mkdir -p "$RAW_IDEAS" "$RAW_PHOTOS"

if [[ ! -d "$VAULT_IDEAS" ]]; then
    echo "[kb-idea-ingest] Vault Ideas folder not found at $VAULT_IDEAS — nothing to ingest"
    exit 0
fi

process_idea_file() {
    local src="$1"
    local rel_path="$2"
    local slug
    slug=$(basename "$src" .md | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed "s/[^a-z0-9-]//g")
    local out="$RAW_IDEAS/${TODAY}-${HOST}-idea-${slug}.md"

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "[DRY-RUN] Would ingest: $src -> $out"
        return
    fi

    local title
    title=$(grep -m1 '^# ' "$src" 2>/dev/null | sed 's/^# //' || echo "$slug")
    local body
    body=$(cat "$src" 2>/dev/null || true)

    cat > "$out" << EOF
---
name: ${TODAY}-idea-${slug}
description: ${title}
type: idea
---

# ${title}

> Source: vault://Ideas/${rel_path} | Ingested: ${TODAY} | Host: ${HOST}

${body}
EOF
    echo "[kb-idea-ingest] Ingested $src -> $out"
}

process_photo() {
    local src="$1"
    local rel_path="$2"
    local slug
    slug=$(basename "$src" | tr ' ' '-' | sed "s/[^a-zA-Z0-9._-]//g")
    local out="$RAW_PHOTOS/${TODAY}-${HOST}-photo-${slug}.md"

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "[DRY-RUN] Would create photo metadata: $src -> $out"
        return
    fi

    local filename
    filename=$(basename "$src")
    local size
    size=$(stat -c%s "$src" 2>/dev/null || stat -f%z "$src" 2>/dev/null || echo "unknown")
    local mdate
    mdate=$(stat -c%y "$src" 2>/dev/null | cut -d' ' -f1 || stat -f%Sm -t%Y-%m-%d "$src" 2>/dev/null || echo "$TODAY")

    cat > "$out" << EOF
---
name: ${TODAY}-photo-${slug}
description: Photo file placeholder for ${filename}
type: photo
---

# Photo: ${filename}

> File: \`${filename}\` | Size: ${size} bytes | Modified: ${mdate}
> Source: vault://Ideas/Photos/${rel_path}
> Host: ${HOST}

## Metadata
- **Filename:** ${filename}
- **Size:** ${size} bytes
- **Modified:** ${mdate}
- **Vault path:** Ideas/Photos/${rel_path}
EOF
    echo "[kb-idea-ingest] Created photo metadata $out"
}

echo "[kb-idea-ingest] Starting ingest from $VAULT_IDEAS..."

# Ingest idea markdown files
shopt -s nullglob
for idea_file in "$VAULT_IDEAS"/**/*.md; do
    [[ "$idea_file" == *".obsidian"* ]] && continue
    rel_path="${idea_file#$VAULT_IDEAS/}"
    process_idea_file "$idea_file" "$rel_path"
done

# Ingest photo metadata
for ext in jpg jpeg png gif webp svg; do
    for photo in "$VAULT_IDEAS"/**/*.$ext; do
        [[ "$photo" == *".obsidian"* ]] && continue
        rel_path="${photo#$VAULT_IDEAS/}"
        process_photo "$photo" "$rel_path"
    done
done

echo "[kb-idea-ingest] Done. Ideas written to $RAW_IDEAS; photo metadata written to $RAW_PHOTOS"
