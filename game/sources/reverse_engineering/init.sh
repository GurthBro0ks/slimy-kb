#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SNAIL_PROJECT_ROOT="$ROOT"
export SNAIL_HARNESS_DIR="$ROOT/.harness"
export SNAIL_PROOF_DIR="$ROOT/.harness/proofs"
export SNAIL_LOG_DIR="$ROOT/.harness/logs"

mkdir -p "$SNAIL_PROOF_DIR" "$SNAIL_LOG_DIR" "$ROOT/reports" "$ROOT/originals" "$ROOT/quarantine"

echo "=== Super Snail Extraction Lite Harness ==="
echo "Project root: $ROOT"
echo "Proof dir:    $SNAIL_PROOF_DIR"
echo "Logs dir:     $SNAIL_LOG_DIR"

echo ""
echo "[tools]"
for cmd in git python3 bash sha256sum find sed awk; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ✓ $cmd"
  else
    echo "  ✗ $cmd missing"
  fi
done

echo ""
echo "[git]"
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "  repo:   yes"
  echo "  branch: $(git -C "$ROOT" branch --show-current 2>/dev/null || echo '?')"
  echo "  remote: $(git -C "$ROOT" remote get-url origin 2>/dev/null || echo 'none')"
  echo "  dirty:  $(git -C "$ROOT" status --porcelain | wc -l | tr -d ' ') files"
else
  echo "  repo: no git repo here yet"
fi

echo ""
echo "[artifact counts]"
printf "  %-16s %s\n" "luac:" "$(find "$ROOT" -type f -name '*.luac' | wc -l | tr -d ' ')"
printf "  %-16s %s\n" "apk/xapk:" "$(find "$ROOT" -type f \( -name '*.apk' -o -name '*.xapk' \) | wc -l | tr -d ' ')"
printf "  %-16s %s\n" "captures:" "$(find "$ROOT" -type f \( -name '*.pcap' -o -name '*.pcapng' -o -name '*.flow' -o -name '*.har' \) | wc -l | tr -d ' ')"
printf "  %-16s %s\n" "python scripts:" "$(find "$ROOT" -maxdepth 3 -type f -name '*.py' | wc -l | tr -d ' ')"
printf "  %-16s %s\n" "markdown:" "$(find "$ROOT" -maxdepth 3 -type f -name '*.md' | wc -l | tr -d ' ')"

echo ""
echo "Use: ./snail-run help"
