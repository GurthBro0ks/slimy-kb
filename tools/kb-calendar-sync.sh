#!/usr/bin/env bash
# kb-calendar-sync.sh
# Create or update today's daily note in the vault, populating with KB and system state.
# Usage: kb-calendar-sync.sh [--dry-run]
set -euo pipefail

DRY_RUN="${1:-}"
HOST=$(hostname -s)
TODAY=$(date +%Y-%m-%d)
KB_ROOT="/home/slimy/kb"
VAULT_DAILY="/home/slimy/obsidian/slimyai-vault/Daily"
OUT_FILE="$VAULT_DAILY/${TODAY}.md"

# Source webhook config if present (category: DAILY)
if [[ -f ~/.config/slimy/webhooks.env ]]; then
    source ~/.config/slimy/webhooks.env
fi
DISCORD_WEBHOOK="${DISCORD_WEBHOOK_DAILY:-}"

mkdir -p "$VAULT_DAILY"

# Gather state
conflict_count=$(find "$KB_ROOT" "$VAULT_DAILY" -type f -iname '*conflict*' 2>/dev/null | wc -l | tr -d ' ')

# Uncompiled count (raw files in last 7 days not in wiki sources — approximate)
uncompiled_count=$(find "$KB_ROOT/raw" -type f -name '*.md' -mtime -7 2>/dev/null | wc -l | tr -d ' ')

# Stale article count
stale_count=0
if [[ -f "$KB_ROOT/wiki/_stale.md" ]]; then
    count1=$(grep -c '^\[' "$KB_ROOT/wiki/_stale.md" 2>/dev/null || true)
    count2=$(grep -c '^- ' "$KB_ROOT/wiki/_stale.md" 2>/dev/null || true)
    stale_count=${count1:-0}
    [[ "$count2" -gt "$stale_count" ]] && stale_count=$count2
fi

# Compile candidates (raw files modified in last 7 days)
compile_candidates=$(find "$KB_ROOT/raw" -type f -name '*.md' -mtime -7 2>/dev/null | head -20 || true)

# Recent commits
recent_activity=""
for repo in /home/slimy/kb /opt/slimy/slimy-monorepo /home/slimy/mission-control; do
    if [[ -d "$repo" ]] && git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
        name=$(basename "$repo")
        last=$(git -C "$repo" log -1 --format="%h %s" 2>/dev/null || echo "—")
        recent_activity="${recent_activity}  - $name: $last\n"
    fi
done

# Check for failed services
failed_svcs=""
for svc in slimy-web-health slimy-report; do
    if systemctl --user is-failed "$svc" 2>/dev/null | grep -q failed; then
        failed_svcs="$failed_svcs $svc"
    fi
done

cat > "$OUT_FILE" << EOF
# Daily — $TODAY

> Host: $HOST | KB last sync: $(git -C "$KB_ROOT" log -1 --format=%ci 2>/dev/null | cut -d' ' -f1 || echo "unknown")

## Project Checklist
- [ ] Review compile candidates
- [ ] Check for conflict files
- [ ] Verify slimy-web.service status
- [ ] Verify mission-control.service status
- [ ] Run knowledge base sync

## Important Changes (Today)
${recent_activity:-  - No recent activity detected}

## Open Anomalies
${failed_svcs:+- FAILED services:${failed_svcs}}
- Uncompiled raw files: ${uncompiled_count}
- Conflict files: ${conflict_count}
- Stale articles: ${stale_count}

## Pending Maintenance
| Item | Count |
|---|---|
| Compile candidates | ${uncompiled_count} |
| Conflict files | ${conflict_count} |
| Stale wiki articles | ${stale_count} |
| Recent commits (7d) | see above |

## Recommended Actions
1. Run \`wiki compile-candidates\` to see uncompiled raw files
2. Run \`wiki conflicts\` to check for conflict files
3. Run \`wiki status\` for full KB state
4. Post daily to Discord if configured
EOF

echo "[kb-calendar-sync] Wrote daily note: $OUT_FILE"

# Optional Discord webhook
if [[ -n "$DISCORD_WEBHOOK" ]]; then
    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "[DRY-RUN] Would post Discord webhook"
    else
        local msg="Daily $TODAY on $HOST — compile: ${uncompiled_count}, conflicts: ${conflict_count}, stale: ${stale_count}"
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"content\": \"$msg\"}" >/dev/null 2>&1 && echo "[kb-calendar-sync] Posted Discord webhook" || echo "[kb-calendar-sync] Discord webhook post failed (non-critical)"
    fi
else
    echo "[kb-calendar-sync] DISCORD_WEBHOOK_DAILY not configured — skipping Discord post"
fi
