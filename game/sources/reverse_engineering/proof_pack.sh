#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/init.sh" >/dev/null
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROOF="$SNAIL_PROOF_DIR/proof_$STAMP"
mkdir -p "$PROOF"

{
  echo "# Proof Pack — $STAMP"
  echo ""
  echo "Root: $ROOT"
  echo "UTC:  $STAMP"
  echo ""
  echo "## Git"
  if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "- branch: $(git -C "$ROOT" branch --show-current 2>/dev/null || echo '?')"
    echo "- head: $(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'no commits yet')"
    echo "- remote: $(git -C "$ROOT" remote get-url origin 2>/dev/null || echo 'none')"
  else
    echo "- not a git repo"
  fi
} > "$PROOF/README.md"

PYTHONNOUSERSITE=1 python3 -S "$ROOT/scripts/inventory.py" > "$PROOF/inventory.json"

git -C "$ROOT" status --short > "$PROOF/git-status.txt" 2>/dev/null || true
git -C "$ROOT" diff --stat > "$PROOF/git-diff-stat.txt" 2>/dev/null || true

# Human-readable risky artifact list
PYTHONNOUSERSITE=1 python3 -S - "$PROOF/inventory.json" "$PROOF/risky-files.txt" <<'PY' >/dev/null
import json, sys
inp, outp = sys.argv[1], sys.argv[2]
data = json.load(open(inp))
risky = [f for f in data['files'] if f['class'] in ('raw_evidence','raw_or_sensitive_artifact','suspect_mutating_script','unknown_review_required')]
with open(outp, 'w') as f:
    for row in risky:
        f.write(f"{row['class']}\t{row['path']}\t{row['size']}\t{row['sha256']}\n")
PY

cat > "$PROOF/RESULT.txt" <<'EOF2'
PENDING_QA
EOF2

echo "$PROOF"
