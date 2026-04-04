#!/usr/bin/env bash
set -euo pipefail

KB_ROOT="/home/slimy/kb"
RAW_ARTICLES="$KB_ROOT/raw/articles"
RAW_RESEARCH="$KB_ROOT/raw/research"
RAW_ATTACH="$RAW_RESEARCH/attachments"
VAULT_ROOT="/home/slimy/obsidian/slimyai-vault"
STATE_DIR="$KB_ROOT/output/.state"
MANIFEST="$STATE_DIR/obsidian-ingest-manifest.tsv"
RUN_TS_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
RUN_TS_FILE="$(date -u +%Y%m%d-%H%M%S)"
REPORT_PATH="$KB_ROOT/output/obsidian-ingest-report-$RUN_TS_FILE.md"

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

yaml_escape() {
  printf '%s' "$1" | sed -E 's/\\/\\\\/g; s/"/\\"/g'
}

append_changed_path() {
  local p="$1"
  changed_paths+=("$p")
}

append_warning() {
  local w="$1"
  warnings+=("$w")
}

write_doc_with_provenance() {
  local src="$1"
  local dst="$2"
  local rel="$3"
  local source_hash="$4"
  local doc_kind="$5"
  local folder="$6"

  local title stem esc_title esc_rel esc_folder esc_kind
  stem="$(basename "$src")"
  title="${stem%.*}"
  esc_title="$(yaml_escape "$title")"
  esc_rel="$(yaml_escape "$rel")"
  esc_folder="$(yaml_escape "$folder")"
  esc_kind="$(yaml_escape "$doc_kind")"

  local tmp out_end
  tmp="$(mktemp)"

  if [[ "$(head -n 1 "$src" 2>/dev/null || true)" == "---" ]]; then
    out_end="$(grep -n '^---[[:space:]]*$' "$src" | awk -F: 'NR==2 {print $1}')"
  else
    out_end=""
  fi

  if [[ -n "$out_end" ]]; then
    sed -n "1,$((out_end - 1))p" "$src" > "$tmp"
    cat >> "$tmp" <<EOF
kb_ingest_source: "obsidian-vault/$esc_rel"
kb_ingest_folder: "$esc_folder"
kb_ingest_relpath: "$esc_rel"
kb_ingest_timestamp: "$RUN_TS_UTC"
kb_ingest_hash: "$source_hash"
kb_ingest_type: "$esc_kind"
---
EOF
    sed -n "$((out_end + 1)),\$p" "$src" >> "$tmp"
  else
    cat > "$tmp" <<EOF
---
title: "$esc_title"
type: "$esc_kind"
source: "obsidian-vault/$esc_rel"
status: "captured"
created: "$RUN_TS_UTC"
kb_ingest_source: "obsidian-vault/$esc_rel"
kb_ingest_folder: "$esc_folder"
kb_ingest_relpath: "$esc_rel"
kb_ingest_timestamp: "$RUN_TS_UTC"
kb_ingest_hash: "$source_hash"
kb_ingest_type: "$esc_kind"
---

EOF
    cat "$src" >> "$tmp"
  fi

  mkdir -p "$(dirname "$dst")"
  if [[ ! -f "$dst" ]]; then
    mv "$tmp" "$dst"
    return 0
  fi
  if cmp -s "$tmp" "$dst"; then
    rm -f "$tmp"
    return 2
  fi
  mv "$tmp" "$dst"
  return 1
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
created=0
declare -a changed_paths=()
declare -a warnings=()

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
    append_warning "Missing directory: $dir"
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

    if [[ "${old_hash[$src]:-}" == "$source_hash" ]] \
      && [[ -n "${old_dest[$src]:-}" ]] \
      && [[ -f "$KB_ROOT/${old_dest[$src]}" ]]; then
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
      had_wrapper=0
      if [[ -f "$wrapper_abs" ]]; then
        had_wrapper=1
      fi

      if [[ ! -f "$attach_abs" ]]; then
        created=$((created + 1))
      elif ! cmp -s "$src" "$attach_abs"; then
        updated=$((updated + 1))
      fi
      copy_if_changed "$src" "$attach_abs"
      append_changed_path "${attach_abs#$KB_ROOT/}"

      cat > "$wrapper_abs" << WRAPEOF
# Obsidian Image Import: $(basename "$src")
> Category: research
> Source: obsidian-vault/$rel
> Folder: $(dirname "$rel")
> Relative Path: $rel
> Imported: $RUN_TS_UTC
> Hash: $source_hash

Image attachment copied from the Obsidian vault intake.

![${stem_slug}](attachments/$attach_name)
WRAPEOF

      if [[ "$had_wrapper" -eq 1 ]]; then
        updated=$((updated + 1))
      else
        created=$((created + 1))
      fi
      append_changed_path "${wrapper_abs#$KB_ROOT/}"
      primary_dest_rel="${wrapper_abs#$KB_ROOT/}"
      echo "[ingested:image] $rel -> ${attach_abs#$KB_ROOT/} + ${wrapper_abs#$KB_ROOT/}"
    elif is_doc_ext "$ext_lc"; then
      doc_kind="note"
      if [[ "$rel" == Inbox/articles/* ]]; then
        dest_abs="$RAW_ARTICLES/obsidian-${stem_slug}.md"
        doc_kind="article"
      elif [[ "$rel" == Inbox/notes/* ]]; then
        dest_abs="$RAW_RESEARCH/obsidian-${stem_slug}.md"
        doc_kind="note"
      elif [[ "$rel" == Projects/* ]]; then
        dest_abs="$RAW_RESEARCH/obsidian-${stem_slug}.md"
        doc_kind="project-note"
      else
        dest_abs="$RAW_RESEARCH/obsidian-${stem_slug}.md"
      fi

      folder="$(dirname "$rel")"
      had_dest=0
      if [[ -f "$dest_abs" ]]; then
        had_dest=1
      fi
      set +e
      write_doc_with_provenance "$src" "$dest_abs" "$rel" "$source_hash" "$doc_kind" "$folder"
      write_rc=$?
      set -e
      if [[ "$write_rc" -eq 0 ]]; then
        created=$((created + 1))
        append_changed_path "${dest_abs#$KB_ROOT/}"
      elif [[ "$write_rc" -eq 1 ]]; then
        if [[ "$had_dest" -eq 1 ]]; then
          updated=$((updated + 1))
        else
          created=$((created + 1))
        fi
        append_changed_path "${dest_abs#$KB_ROOT/}"
      else
        skipped=$((skipped + 1))
      fi

      primary_dest_rel="${dest_abs#$KB_ROOT/}"
      echo "[ingested:doc] $rel -> $primary_dest_rel"
    else
      # Unknown/binary content: copy as attachment and create provenance wrapper.
      attach_name="obsidian-${stem_slug}.${ext_lc}"
      wrapper_name="obsidian-${stem_slug}.md"
      attach_abs="$RAW_ATTACH/$attach_name"
      wrapper_abs="$RAW_RESEARCH/$wrapper_name"
      had_wrapper=0
      if [[ -f "$wrapper_abs" ]]; then
        had_wrapper=1
      fi

      if [[ ! -f "$attach_abs" ]]; then
        created=$((created + 1))
      elif ! cmp -s "$src" "$attach_abs"; then
        updated=$((updated + 1))
      fi
      copy_if_changed "$src" "$attach_abs"
      append_changed_path "${attach_abs#$KB_ROOT/}"

      cat > "$wrapper_abs" << WRAPEOF
# Obsidian File Import: $(basename "$src")
> Category: research
> Source: obsidian-vault/$rel
> Folder: $(dirname "$rel")
> Relative Path: $rel
> Imported: $RUN_TS_UTC
> Hash: $source_hash

Non-markdown file copied from the Obsidian vault.

Attachment path:
- `attachments/$attach_name`
WRAPEOF

      if [[ "$had_wrapper" -eq 1 ]]; then
        updated=$((updated + 1))
      else
        created=$((created + 1))
      fi
      append_changed_path "${wrapper_abs#$KB_ROOT/}"
      primary_dest_rel="${wrapper_abs#$KB_ROOT/}"
      echo "[ingested:file] $rel -> ${attach_abs#$KB_ROOT/} + ${wrapper_abs#$KB_ROOT/}"
      append_warning "Unknown extension '$ext_lc' imported as attachment wrapper for $rel"
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

{
  echo "# Obsidian Ingest Report"
  echo ""
  echo "- Timestamp (UTC): $RUN_TS_UTC"
  echo "- Vault Root: \`$VAULT_ROOT\`"
  echo "- Processed Count: $processed"
  echo "- Skipped Count: $skipped"
  echo "- Updated Count: $updated"
  echo "- Created Count: $created"
  echo ""
  echo "## Files Created/Updated"
  if [[ "${#changed_paths[@]}" -eq 0 ]]; then
    echo "- None"
  else
    printf '%s\n' "${changed_paths[@]}" | sort -u | sed 's/^/- /'
  fi
  echo ""
  echo "## Warnings"
  if [[ "${#warnings[@]}" -eq 0 ]]; then
    echo "- None"
  else
    printf '%s\n' "${warnings[@]}" | sed 's/^/- /'
  fi
} > "$REPORT_PATH"

echo "[kb-obsidian-ingest] Complete: processed=$processed updated=$updated skipped=$skipped created=$created"
echo "[kb-obsidian-ingest] Manifest: $MANIFEST"
echo "[kb-obsidian-ingest] Report: $REPORT_PATH"
