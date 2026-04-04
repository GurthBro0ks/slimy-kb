#!/usr/bin/env bash
set -euo pipefail

KB_WIKI="/home/slimy/kb/wiki"
VAULT_WIKI="/home/slimy/obsidian/slimyai-vault/Wiki"

mkdir -p "$VAULT_WIKI"

echo "[kb-obsidian-sync] Source: $KB_WIKI"
echo "[kb-obsidian-sync] Dest:   $VAULT_WIKI"

changed=0
deleted=0

if command -v rsync >/dev/null 2>&1; then
  echo "[kb-obsidian-sync] Mode: rsync"
  RSYNC_LOG=$(mktemp)
  rsync -rltv --no-perms --no-owner --no-group --delete --prune-empty-dirs \
    --include='*/' \
    --include='*.md' \
    --exclude='*' \
    --itemize-changes \
    "$KB_WIKI/" "$VAULT_WIKI/" | tee "$RSYNC_LOG"

  changed=$(grep -Ec '^[><ch\*].*\.md$|^\.d' "$RSYNC_LOG" || true)
  deleted=$(grep -Ec '^\*deleting\s+.*\.md$' "$RSYNC_LOG" || true)
  rm -f "$RSYNC_LOG"
else
  echo "[kb-obsidian-sync] Mode: cp fallback"

  while IFS= read -r -d '' src; do
    rel="${src#$KB_WIKI/}"
    dst="$VAULT_WIKI/$rel"
    mkdir -p "$(dirname "$dst")"
    if [[ ! -f "$dst" ]] || ! cmp -s "$src" "$dst"; then
      rm -f "$dst"
      cp "$src" "$dst"
      echo "[updated] $rel"
      changed=$((changed + 1))
    fi
  done < <(find "$KB_WIKI" -type f -name '*.md' -print0 | sort -z)

  while IFS= read -r -d '' dst; do
    rel="${dst#$VAULT_WIKI/}"
    src="$KB_WIKI/$rel"
    if [[ ! -f "$src" ]]; then
      rm -f "$dst"
      echo "[deleted] $rel"
      deleted=$((deleted + 1))
    fi
  done < <(find "$VAULT_WIKI" -type f -name '*.md' -print0 | sort -z)

  find "$VAULT_WIKI" -depth -type d -empty -delete
fi

# Browse-only mirror: make markdown read-only for the user.
find "$VAULT_WIKI" -type f -name '*.md' -exec chmod u-w {} +

total=$(find "$VAULT_WIKI" -type f -name '*.md' | wc -l | tr -d ' ')

echo "[kb-obsidian-sync] Complete: total=$total changed_or_touched=$changed deleted=$deleted"
echo "[kb-obsidian-sync] Note: Vault Wiki is a read-only mirror of canonical /home/slimy/kb/wiki"
