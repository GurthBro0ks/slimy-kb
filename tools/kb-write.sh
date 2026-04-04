#!/usr/bin/env bash
# Usage: kb-write.sh <relative-path> < content
# Example: echo "# My Note" | kb-write.sh raw/agent-learnings/2026-04-04-fix.md
# Pulls, writes the file, commits, pushes — atomic operation.
set -euo pipefail

KB_ROOT="/home/slimy/kb"
REL_PATH="${1:?Usage: kb-write.sh <relative-path>}"
HOST=$(hostname -s)

cd "$KB_ROOT"
bash tools/kb-sync.sh pull

mkdir -p "$(dirname "$REL_PATH")"
cat > "$REL_PATH"

git add "$REL_PATH"
git commit -m "kb: add $REL_PATH from $HOST"
bash tools/kb-sync.sh push
echo "[kb-write] Filed: $REL_PATH"
