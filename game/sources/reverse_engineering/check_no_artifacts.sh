#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[check] scanning for blocked artifact types..."

blocked=0

patterns=(
  "*.apk"
  "*.xapk"
  "*.apks"
  "*.aab"
  "*.obb"
  "*.luac"
  "*.flow"
  "*.har"
  "*.pcap"
  "*.pcapng"
  "*.pem"
  "*.key"
  "*.p12"
  "*.pfx"
)

for pat in "${patterns[@]}"; do
  while IFS= read -r -d '' file; do
    echo "BLOCKED: $file"
    blocked=1
  done < <(find . -type f -name "$pat" -print0)
done

if grep -RIlE "(access_token|refresh_token|session|cookie|password|Authorization:|Bearer )" . \
  --exclude-dir=.git \
  --exclude='check_no_artifacts.sh' \
  --exclude='*.md' \
  --exclude='.gitignore' \
  2>/dev/null; then
  echo "WARNING: possible secret/session text found above."
  blocked=1
fi

if [ "$blocked" -ne 0 ]; then
  echo "FAIL: blocked artifacts or possible secrets found."
  exit 1
fi

echo "PASS: no blocked artifacts found."
