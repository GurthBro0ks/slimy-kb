#!/usr/bin/env bash
# Usage: bash /home/slimy/kb/tools/kb-search.sh "search terms"
set -euo pipefail
QUERY="${1:?Usage: kb-search.sh \"search terms\"}"
KB_ROOT="/home/slimy/kb"
SEARCH_DIRS=("$KB_ROOT/wiki" "$KB_ROOT/raw")
echo "=== KB Search: $QUERY ==="
echo ""

FILES="$(grep -ril -- "$QUERY" "${SEARCH_DIRS[@]}" 2>/dev/null || true)"
if [ -n "$FILES" ]; then
    while read -r file; do
        [ -z "$file" ] && continue
        relpath="${file#$KB_ROOT/}"
        echo "--- $relpath ---"
        grep -in -C 2 -- "$QUERY" "$file" 2>/dev/null | head -20
        echo ""
    done <<< "$FILES"
fi

COUNT=$(printf "%s\n" "$FILES" | sed '/^$/d' | wc -l)
echo "=== $COUNT files matched ==="
