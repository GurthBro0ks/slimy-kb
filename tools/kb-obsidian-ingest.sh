#!/usr/bin/env bash
set -euo pipefail

KB_ROOT="/home/slimy/kb"
RAW_ARTICLES="$KB_ROOT/raw/articles"
RAW_RESEARCH="$KB_ROOT/raw/research"
RAW_ATTACH="$RAW_RESEARCH/attachments"
VAULT_ROOT="/home/slimy/obsidian/slimyai-vault"
STATE_DIR="$KB_ROOT/output/.state"
MANIFEST="$STATE_DIR/obsidian-ingest-manifest.tsv"

mkdir -p "$RAW_ARTICLES" "$RAW_RESEARCH" "$RAW_ATTACH" "$STATE_DIR"
[[ -f "$MANIFEST" ]] || : > "$MANIFEST"
chmod 664 "$MANIFEST" 2>/dev/null || true

file_hash() {
  local file="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$file" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    cksum "$file" | awk '{print $1 "-" $2}'
  fi
}

slugify() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
}

is_image_ext() {
  case "$1" in
    png|jpg|jpeg|gif|webp|svg|bmp|tif|tiff|heic|heif)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_doc_ext() {
  case "$1" in
    md|markdown|txt|rst|adoc)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

copy_if_changed() {
  local src="$1"
  local dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [[ ! -f "$dst" ]] || ! cmp -s "$src" "$dst"; then
    rm -f "$dst"
    cp "$src" "$dst"
  fi
}

declare -A old_hash=()
declare -A old_dest=()
declare -A new_hash=()
declare -A new_dest=()

while IFS=$'\t' read -r src hash dest; do
  [[ -n "$src" ]] || continue
  old_hash["$src"]="$hash"
  old_dest["$src"]="$dest"
done < "$MANIFEST"

processed=0
skipped=0
updated=0

scan_dirs=(
  "$VAULT_ROOT/Inbox/notes"
  "$VAULT_ROOT/Inbox/articles"
  "$VAULT_ROOT/Inbox/images"
  "$VAULT_ROOT/Projects"
)

echo "[kb-obsidian-ingest] Vault: $VAULT_ROOT"

for dir in "${scan_dirs[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "[skip] missing directory: $dir"
    continue
  fi

  while IFS= read -r -d '' src; do
    processed=$((processed + 1))
    rel="${src#$VAULT_ROOT/}"
    rel_no_ext="${rel%.*}"
    ext="${src##*.}"
    ext_lc="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
    stem_slug="$(slugify "$rel_no_ext")"
    source_hash="$(file_hash "$src")"

    if [[ "${old_hash[$src]:-}" == "$source_hash" ]] && [[ -n "${old_dest[$src]:-}" ]]; then
      # unchanged source; keep manifest mapping
      new_hash["$src"]="$source_hash"
      new_dest["$src"]="${old_dest[$src]}"
      skipped=$((skipped + 1))
      continue
    fi

    primary_dest_rel=""

    if is_image_ext "$ext_lc"; then
      attach_name="obsidian-${stem_slug}.${ext_lc}"
      wrapper_name="obsidian-${stem_slug}.md"
      attach_abs="$RAW_ATTACH/$attach_name"
      wrapper_abs="$RAW_RESEARCH/$wrapper_name"

      copy_if_changed "$src" "$attach_abs"

      cat > "$wrapper_abs" << WRAPEOF
# Obsidian Image Import: $(basename "$src")
> Category: research
> Source: obsidian-vault/$rel
> Imported: $(date -u +%Y-%m-%dT%H:%M:%SZ)
> Hash: $source_hash

Image attachment copied from the Obsidian vault.

![${stem_slug}](attachments/$attach_name)
WRAPEOF

      primary_dest_rel="${wrapper_abs#$KB_ROOT/}"
      echo "[ingested:image] $rel -> ${attach_abs#$KB_ROOT/} + ${wrapper_abs#$KB_ROOT/}"
      updated=$((updated + 1))
    elif is_doc_ext "$ext_lc"; then
      if [[ "$rel" == Inbox/articles/* ]]; then
        dest_abs="$RAW_ARTICLES/obsidian-${stem_slug}.md"
      elif [[ "$rel" == Inbox/notes/* ]]; then
        dest_abs="$RAW_RESEARCH/obsidian-${stem_slug}.md"
      else
        dest_abs="$RAW_RESEARCH/obsidian-${stem_slug}.md"
      fi

      copy_if_changed "$src" "$dest_abs"
      primary_dest_rel="${dest_abs#$KB_ROOT/}"
      echo "[ingested:doc] $rel -> $primary_dest_rel"
      updated=$((updated + 1))
    else
      # Unknown/binary content: copy as attachment and create provenance wrapper.
      attach_name="obsidian-${stem_slug}.${ext_lc}"
      wrapper_name="obsidian-${stem_slug}.md"
      attach_abs="$RAW_ATTACH/$attach_name"
      wrapper_abs="$RAW_RESEARCH/$wrapper_name"

      copy_if_changed "$src" "$attach_abs"

      cat > "$wrapper_abs" << WRAPEOF
# Obsidian File Import: $(basename "$src")
> Category: research
> Source: obsidian-vault/$rel
> Imported: $(date -u +%Y-%m-%dT%H:%M:%SZ)
> Hash: $source_hash

Non-markdown file copied from the Obsidian vault.

Attachment path:
- `attachments/$attach_name`
WRAPEOF

      primary_dest_rel="${wrapper_abs#$KB_ROOT/}"
      echo "[ingested:file] $rel -> ${attach_abs#$KB_ROOT/} + ${wrapper_abs#$KB_ROOT/}"
      updated=$((updated + 1))
    fi

    new_hash["$src"]="$source_hash"
    new_dest["$src"]="$primary_dest_rel"
  done < <(find "$dir" -type f -print0 | sort -z)
done

# Preserve manifest entries for files not touched this run.
for src in "${!old_hash[@]}"; do
  if [[ -z "${new_hash[$src]:-}" ]]; then
    new_hash["$src"]="${old_hash[$src]}"
    new_dest["$src"]="${old_dest[$src]}"
  fi
done

# Rewrite manifest atomically.
tmp_manifest="$(mktemp "$MANIFEST.tmp.XXXX")"
for src in "${!new_hash[@]}"; do
  printf '%s\t%s\t%s\n' "$src" "${new_hash[$src]}" "${new_dest[$src]}" >> "$tmp_manifest"
done
sort -o "$tmp_manifest" "$tmp_manifest"
mv "$tmp_manifest" "$MANIFEST"
chmod 664 "$MANIFEST" 2>/dev/null || true

echo "[kb-obsidian-ingest] Complete: processed=$processed updated=$updated skipped=$skipped"
echo "[kb-obsidian-ingest] Manifest: $MANIFEST"
