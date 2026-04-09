#!/usr/bin/env bash
# kb-log-append.sh — Append an event entry to the KB wiki log
# Usage: bash kb-log-append.sh <event_type> <short_title> [notes]
# event_type: ingest | compile | query | lint | file-back | maintenance
set -euo pipefail

KB_ROOT="${KB_ROOT:-/home/slimy/kb}"
LOG_FILE="$KB_ROOT/wiki/log.md"
HOST=$(hostname -s)
ACTOR="kb-maintenance"

EVENT_TYPE="${1:-}"
SHORT_TITLE="${2:-}"
NOTES="${3:-}"

if [[ -z "$EVENT_TYPE" || -z "$SHORT_TITLE" ]]; then
    echo "Usage: kb-log-append.sh <event_type> <short_title> [notes]"
    echo "  event_type: ingest|compile|query|lint|file-back|maintenance"
    exit 1
fi

TIMESTAMP=$(date +%Y-%m-%d\ %H:%M)
RUN_TS_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)

cd "$KB_ROOT"

# Capture git state
if git rev-parse --git-dir >/dev/null 2>&1; then
    COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "uncommitted")
else
    COMMIT="no-git"
fi

# Detect affected paths by checking recent changes
AFFECTED_WIKI=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | grep '^wiki/' | grep -v '^wiki/log.md$' | grep -v '^wiki/_index.md$' | grep -v '^wiki/_concepts.md$' | grep -v '^wiki/_orphans.md$' | grep -v '^wiki/_weak-links.md$' | awk '{print "  - " $0}' || true)
AFFECTED_RAW=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | grep '^raw/' | awk '{print "  - " $0}' || true)

# Build the entry
ENTRY="## [$TIMESTAMP] $EVENT_TYPE | $SHORT_TITLE
- actor: $ACTOR
- host: $HOST
- affected_paths:
$AFFECTED_WIKI${AFFECTED_RAW:-  - (none)}
- summary: $SHORT_TITLE
- commit: $COMMIT
- notes: $NOTES

"

# Append to log
echo "$ENTRY" >> "$LOG_FILE"

echo "[kb-log-append] Entry appended to $LOG_FILE"
echo "  type=$EVENT_TYPE title=$SHORT_TITLE"