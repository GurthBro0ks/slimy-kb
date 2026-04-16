#!/usr/bin/env bash
# kb-apply-metadata.sh — Apply git-backed "Last edited" and "Version" metadata to all wiki pages.
# Usage: kb-apply-metadata.sh [--dry-run] [--page <path>]
# Computes per-page git revision count and latest commit SHA, inserts visible metadata lines.
set -euo pipefail

KB_ROOT="/home/slimy/kb"
KB_WIKI="$KB_ROOT/wiki"
DRY_RUN=false
SINGLE_PAGE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=true; shift ;;
        --page) SINGLE_PAGE="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

METADATA_MARKER_BEGIN="<!-- KB METADATA"
METADATA_MARKER_END="KB METADATA -->"

compute_page_metadata() {
    local file="$1"
    local rel="${file#$KB_ROOT/}"
    local last_edited version

    last_edited=$(git -C "$KB_ROOT" log -1 --format="%ad" --date=format:"%Y-%m-%d %H:%M UTC" -- "$rel" 2>/dev/null || echo "unknown")

    local rev_count
    rev_count=$(git -C "$KB_ROOT" rev-list --count HEAD -- "$rel" 2>/dev/null || echo "0")
    local short_sha
    short_sha=$(git -C "$KB_ROOT" log -1 --format="%h" -- "$rel" 2>/dev/null || echo "unknown")

    if [[ "$rev_count" == "0" ]]; then
        version="new"
    else
        version="r${rev_count} / ${short_sha}"
    fi

    echo "${last_edited}|${version}"
}

has_metadata_block() {
    grep -qF "$METADATA_MARKER_BEGIN" "$1" 2>/dev/null
}

apply_metadata_to_page() {
    local file="$1"
    local metadata
    metadata=$(compute_page_metadata "$file")
    local last_edited="${metadata%%|*}"
    local version="${metadata##*|}"

    local new_block
    new_block=$(printf '%s\n> Last edited: %s (git)\n> Version: %s\n%s' \
        "$METADATA_MARKER_BEGIN" "$last_edited" "$version" "$METADATA_MARKER_END")

    if has_metadata_block "$file"; then
        local existing_block
        existing_block=$(sed -n "/$METADATA_MARKER_BEGIN/,/$METADATA_MARKER_END/p" "$file")
        if [[ "$existing_block" == "$new_block" ]]; then
            return 1
        fi
        if $DRY_RUN; then
            echo "[dry-run] UPDATE $file"
            echo "  old: $(echo "$existing_block" | head -3)"
            echo "  new: $(echo "$new_block" | head -3)"
            return 0
        fi
        local tmp
        tmp=$(mktemp)
        sed "/$METADATA_MARKER_BEGIN/,/$METADATA_MARKER_END/c\\$(echo "$new_block" | sed 's/\//\\\//g')" "$file" > "$tmp" && mv "$tmp" "$file"
        return 0
    fi

    local insert_line=0
    local in_blockquote=false
    local last_bq_line=0
    local line_num=0

    while IFS= read -r line; do
        line_num=$((line_num + 1))
        if [[ "$line" =~ ^\>[[:space:]] ]]; then
            last_bq_line=$line_num
        elif [[ "$line" =~ ^\<!--[[:space:]]*BEGIN[[:space:]]MACHINE ]]; then
            break
        elif [[ -z "$line" ]]; then
            if [[ $last_bq_line -eq $((line_num - 1)) ]]; then
                continue
            fi
        else
            if [[ $last_bq_line -gt 0 ]] && [[ $insert_line -eq 0 ]]; then
                insert_line=$((last_bq_line + 1))
                break
            fi
        fi
    done < "$file"

    if [[ $insert_line -eq 0 ]]; then
        line_num=0
        while IFS= read -r line; do
            line_num=$((line_num + 1))
            if [[ "$line" =~ ^\<!--[[:space:]]*BEGIN[[:space:]]MACHINE ]]; then
                insert_line=$line_num
                break
            fi
        done < "$file"
    fi

    if [[ $insert_line -eq 0 ]]; then
        line_num=0
        while IFS= read -r line; do
            line_num=$((line_num + 1))
            if [[ -z "$line" ]] && [[ $line_num -gt 1 ]]; then
                insert_line=$line_num
                break
            fi
        done < "$file"
    fi

    if $DRY_RUN; then
        echo "[dry-run] INSERT at line $insert_line in $file"
        echo "  $new_block"
        return 0
    fi

    local tmp
    tmp=$(mktemp)
    {
        head -n $((insert_line - 1)) "$file"
        echo ""
        echo "$new_block"
        tail -n +"$insert_line" "$file"
    } > "$tmp" && mv "$tmp" "$file"
    return 0
}

if [[ -n "$SINGLE_PAGE" ]]; then
    if $DRY_RUN; then echo "Processing single page: $SINGLE_PAGE"; fi
    apply_metadata_to_page "$SINGLE_PAGE"
    echo "Done: $SINGLE_PAGE"
    exit 0
fi

updated=0
skipped=0
total=0

while IFS= read -r -d '' file; do
    total=$((total + 1))
    if apply_metadata_to_page "$file"; then
        updated=$((updated + 1))
    else
        skipped=$((skipped + 1))
    fi
done < <(find "$KB_WIKI" -name "*.md" -type f -print0 | sort -z)

echo "kb-apply-metadata: total=$total updated=$updated skipped=$skipped"
