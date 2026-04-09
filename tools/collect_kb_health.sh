#!/usr/bin/env bash
# collect_kb_health.sh — KB health snapshot
# Output: /home/slimy/kb/raw/research/YYYY-MM-DD-nuc2-kb-health.md
set -euo pipefail

HOST=$(hostname -s)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
OUTPUT_DIR="/home/slimy/kb/raw/research"
mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="${OUTPUT_DIR}/${TIMESTAMP%%T*}-${HOST}-kb-health.md"
KB_ROOT="/home/slimy/kb"
WIKI="$KB_ROOT/wiki"
RAW="$KB_ROOT/raw"
OUTPUT="$KB_ROOT/output"

{
  echo "# KB Health Snapshot"
  echo ""
  echo "**Timestamp:** $TIMESTAMP"
  echo "**Host:** $HOST"
  echo ""
  echo "## File Counts"
  echo ""
  echo "- wiki/*.md (articles): $(find "$WIKI" -maxdepth 1 -name '*.md' ! -name '_*' 2>/dev/null | wc -l | tr -d ' ')"
  echo "- wiki/_*.md (meta): $(find "$WIKI" -maxdepth 1 -name '_*.md' 2>/dev/null | wc -l | tr -d ' ')"
  echo "- raw/**/*.md: $(find "$RAW" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  echo "- output/*.md: $(find "$OUTPUT" -name '*.md' ! -name 'lint-report*' 2>/dev/null | wc -l | tr -d ' ')"
  echo ""
  echo "## Index Files"
  echo ""
  echo "- wiki/_index.md: $([[ -f "$WIKI/_index.md" ]] && echo "YES" || echo "NO")"
  echo "- wiki/_concepts.md: $([[ -f "$WIKI/_concepts.md" ]] && echo "YES" || echo "NO")"
  echo "- wiki/_page-types.md: $([[ -f "$WIKI/_page-types.md" ]] && echo "YES" || echo "NO")"
  echo "- wiki/_orphans.md: $([[ -f "$WIKI/_orphans.md" ]] && echo "YES" || echo "NO")"
  echo "- wiki/_weak-links.md: $([[ -f "$WIKI/_weak-links.md" ]] && echo "YES" || echo "NO")"
  echo "- wiki/log.md: $([[ -f "$WIKI/log.md" ]] && echo "YES" || echo "NO")"
  echo "- wiki/_nuc-intake.md: $([[ -f "$WIKI/_nuc-intake.md" ]] && echo "YES" || echo "NO")"
  echo ""
  echo "## Orphan & Weak-Link Counts"
  echo ""
  if [[ -f "$WIKI/_orphans.md" ]]; then
    echo "### Orphans (0 inbound links)"
    grep -E "^\- \`" "$WIKI/_orphans.md" 2>/dev/null | wc -l | awk '{print "- count: " $0}'
  fi
  if [[ -f "$WIKI/_weak-links.md" ]]; then
    echo "### Weak Links (<=1 inbound link)"
    grep -E "^\- \`" "$WIKI/_weak-links.md" 2>/dev/null | wc -l | awk '{print "- count: " $0}'
  fi
  echo ""
  echo "## Log Recent Entries (last 5)"
  echo ""
  if [[ -f "$WIKI/log.md" ]]; then
    grep "^## \[" "$WIKI/log.md" | tail -5 | sed 's/^## /- /'
  else
    echo "- no log found"
  fi
  echo ""
  echo "## Recent Output Files (48h)"
  echo ""
  find "$OUTPUT" -name '*.md' ! -name 'lint-report*' -mtime -2 2>/dev/null | sort | while read -r f; do
    echo "- ${f#$OUTPUT/} ($(date -r "$f" +%Y-%m-%d\ %H:%M))"
  done
  echo ""
  echo "## Compile Candidates"
  echo ""
  if [[ -f /tmp/wiki-last-compile-candidates-$USER.tsv ]]; then
    wc -l < /tmp/wiki-last-compile-candidates-$USER.tsv | awk '{print "- pending candidates: " $0}'
    cat /tmp/wiki-last-compile-candidates-$USER.tsv 2>/dev/null | head -5 | sed 's/^/  /'
  else
    echo "- no compile candidates file"
  fi
  echo ""
  echo "## NUC1 Inbox"
  echo ""
  inbox_nuc1="$KB_ROOT/raw/inbox-nuc1"
  if [[ -d "$inbox_nuc1" ]]; then
    count=$(find "$inbox_nuc1" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "- inbox-nuc1 files: $count"
    find "$inbox_nuc1" -type f -mtime -1 2>/dev/null | sed 's/^/  - /' | head -10
  else
    echo "- inbox-nuc1/: not present"
  fi
  echo ""
  echo "## Tools Present"
  echo ""
  for tool in kb-lint.sh kb-log-append.sh kb-sync.sh kb-maintenance.sh wiki; do
    if [[ -x "$KB_ROOT/tools/$tool" ]] || [[ -f "$KB_ROOT/tools/$tool" ]]; then
      echo "- $tool: YES"
    else
      echo "- $tool: NO"
    fi
  done
} > "$OUTPUT_FILE"

echo "KB health digest: $OUTPUT_FILE"
