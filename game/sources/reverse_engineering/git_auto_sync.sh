#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/init.sh" >/dev/null

if ! git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: $ROOT is not a git repo. Run: git init && git remote add origin <repo-url>"
  exit 1
fi

REMOTE="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
if [[ -z "$REMOTE" ]]; then
  echo "ERROR: no origin remote configured."
  exit 1
fi

# Run QA first; this creates a proof pack.
if ! "$ROOT/scripts/qa_gate.sh"; then
  echo "ERROR: QA failed. Refusing git autosync."
  exit 1
fi

# Allowlisted paths only. Do NOT use git add .
SAFE_PATHS=(
  "AGENTS.md"
  "PROJECT_INSTRUCTIONS.md"
  "QUALITY_CRITERIA.md"
  "feature_list.json"
  "claude-progress.md"
  "init.sh"
  "snail-run"
  ".gitignore"
  "scripts"
  "docs"
  "reports"
  "*.md"
  "*.py"
  "*.txt"
  "*.json"
)

for p in "${SAFE_PATHS[@]}"; do
  git -C "$ROOT" add "$p" 2>/dev/null || true
done

# Fail closed if forbidden files are staged.
STAGED_FORBIDDEN="$(git -C "$ROOT" diff --cached --name-status | awk '$1 !~ /^D/ {print $NF}' | grep -E '\.(luac|apk|xapk|apks|aab|so|pcap|pcapng|flow|har)$|(^|/)originals/|(^|/)quarantine/|(^|/)captures/|(^|/)\.env' || true)"
if [[ -n "$STAGED_FORBIDDEN" ]]; then
  echo "ERROR: forbidden files staged. Unstage them before pushing:"
  echo "$STAGED_FORBIDDEN"
  exit 1
fi

if git -C "$ROOT" diff --cached --quiet; then
  echo "No safe changes to commit."
  exit 0
fi

MSG="${1:-chore: update Super Snail extraction harness artifacts}"
git -C "$ROOT" commit -m "$MSG"
git -C "$ROOT" push origin "$(git -C "$ROOT" branch --show-current)"
echo "GitHub autosync complete."
