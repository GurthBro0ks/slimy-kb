#!/usr/bin/env bash
# Usage: bash /home/slimy/kb/tools/kb-search.sh "search terms"
set -euo pipefail
QUERY="${1:?Usage: kb-search.sh \"search terms\"}"
KB_WIKI="/home/slimy/kb/wiki"
echo "=== KB Search: $QUERY ==="
echo ""
grep -ril "$QUERY" "$KB_WIKI" 2>/dev/null | while read -r file; do
    relpath="${file#$KB_WIKI/}"
    echo "--- $relpath ---"
    grep -in -C 2 "$QUERY" "$file" 2>/dev/null | head -20
    echo ""
done
COUNT=$(grep -ril "$QUERY" "$KB_WIKI" 2>/dev/null | wc -l)
echo "=== $COUNT files matched ==="
