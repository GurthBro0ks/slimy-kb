#!/usr/bin/env bash
# collect_nuc2_state.sh — Compact NUC2 host state digest
# Output: /home/slimy/kb/raw/research/YYYY-MM-DD-nuc2-state.md
set -euo pipefail

HOST=$(hostname -s)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
OUTPUT_DIR="/home/slimy/kb/raw/research"
mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="${OUTPUT_DIR}/${TIMESTAMP%%T*}-${HOST}-state.md"

{
  echo "# NUC2 State Digest"
  echo ""
  echo "**Timestamp:** $TIMESTAMP"
  echo "**Host:** $HOST"
  echo ""
  echo "## Systemd User Services"
  echo ""
  systemctl --user list-units --type=service --state=running --no-pager 2>/dev/null | grep -E '\.(service|timer)' | awk '{print "- " $0}' || echo "- (none)"
  echo ""
  echo "## Systemd User Timers"
  echo ""
  systemctl --user list-timers --all --no-pager 2>/dev/null | grep -E 'kb-maintenance|wiki-manager' || echo "- (no kb/wiki timers)"
  echo ""
  echo "## KB Maintenance Timer Status"
  echo ""
  local kb_maint=$(systemctl --user list-timers --all --no-pager 2>/dev/null | grep kb-maintenance || true)
  if [[ -n "$kb_maint" ]]; then
    echo "$kb_maint" | awk '{print "- " $0}'
  else
    echo "- kb-maintenance.timer: inactive"
  fi
  echo ""
  echo "## Active PM2 Processes"
  echo ""
  if command -v pm2 &>/dev/null; then
    pm2 list 2>/dev/null | grep -E 'online|errored|stopped' | head -20 | awk '{print "- " $0}' || echo "- (none)"
  else
    echo "- pm2: not available"
  fi
  echo ""
  echo "## Network Listening Ports (KB-relevant)"
  echo ""
  ss -tlnp 2>/dev/null | grep -E ':(3000|3838|3850|18790|18791|18792|18793|3307|5432|443|80)\s' | awk '{print "- " $0}' || echo "- (ss unavailable)"
  echo ""
  echo "## Disk Usage (KB-relevant paths)"
  echo ""
  for path in "/home/slimy/kb" "/home/slimy"; do
    if [[ -d "$path" ]]; then
      du -sh "$path" 2>/dev/null | awk -v p="$path" '{print "- " p ": " $1}'
    fi
  done
  echo ""
  echo "## Uptime"
  echo ""
  uptime | awk '{print "- " $0}'
  echo ""
  echo "## KB Git Status"
  echo ""
  cd /home/slimy/kb
  git -C /home/slimy/kb status --short 2>/dev/null | head -10 | awk '{print "- " $0}' || echo "- (not a git repo)"
  local git_ahead=$(git -C /home/slimy/kb log --oneline origin/main..HEAD 2>/dev/null | wc -l | tr -d ' ')
  local git_behind=$(git -C /home/slimy/kb log --oneline HEAD..origin/main 2>/dev/null | wc -l | tr -d ' ')
  echo "- ahead: $git_ahead"
  echo "- behind: $git_behind"
  echo ""
  echo "## KB Health Snapshot"
  echo ""
  if [[ -f /home/slimy/kb/wiki/_orphans.md ]]; then
    local orphan_count=$(grep -E "^\- \`" /home/slimy/kb/wiki/_orphans.md 2>/dev/null | wc -l | tr -d ' ')
    echo "- orphans (total): $orphan_count"
  fi
  if [[ -f /home/slimy/kb/wiki/_weak-links.md ]]; then
    local weak_count=$(grep -E "^\- \`" /home/slimy/kb/wiki/_weak-links.md 2>/dev/null | wc -l | tr -d ' ')
    echo "- weak-links (total): $weak_count"
  fi
  echo ""
  echo "## KB Raw Files (recent, 48h)"
  echo ""
  find /home/slimy/kb/raw -type f -name '*.md' -mtime -2 2>/dev/null | wc -l | awk '{print "- " $0 " raw/*.md files modified in last 48h"}'
  echo ""
  echo "## Vault Sync Status"
  echo ""
  if command -v pm2 &>/dev/null; then
    local vault_status=$(pm2 describe obsidian-headless-sync 2>/dev/null | grep -E 'status|uptime' | head -3 | awk '{print "- " $0}' || echo "- obsidian-headless-sync: not tracked")
    echo "$vault_status"
  fi
} > "$OUTPUT_FILE"

echo "NUC2 state digest: $OUTPUT_FILE"
