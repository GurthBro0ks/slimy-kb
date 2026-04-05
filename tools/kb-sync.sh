#!/usr/bin/env bash
# Usage:
#   kb-sync.sh pull    — pull latest before reading/working
#   kb-sync.sh push    — push after writing
#   kb-sync.sh sync    — pull then push (default)
set -euo pipefail

# Disable interactive pager — child compile runs non-interactively
export GIT_PAGER=cat
export PAGER=cat

KB_ROOT="/home/slimy/kb"
cd "$KB_ROOT"

ACTION="${1:-sync}"
HOST=$(hostname -s)

case "$ACTION" in
    pull)
        echo "[kb-sync] Pulling latest..."
        git --no-pager pull --rebase --autostash origin main 2>&1 || {
            echo "[kb-sync] WARNING: pull failed, working with local state"
        }
        ;;
    push)
        echo "[kb-sync] Pushing changes..."
        git --no-pager add -A
        CHANGES=$(git --no-pager diff --cached --stat)
        if [ -n "$CHANGES" ]; then
            git --no-pager commit -m "kb: auto-sync from $HOST $(date +%Y-%m-%d-%H%M)" 2>/dev/null || true
        fi
        git --no-pager push origin main 2>&1 || {
            echo "[kb-sync] WARNING: push failed, changes are committed locally"
            echo "[kb-sync] Run 'cd /home/slimy/kb && git --no-pager push' to retry"
        }
        ;;
    sync)
        "$0" pull
        "$0" push
        ;;
    *)
        echo "Usage: kb-sync.sh [pull|push|sync]"
        exit 1
        ;;
esac
