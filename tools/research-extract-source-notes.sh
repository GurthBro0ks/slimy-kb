#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL="$ROOT_DIR/tools/research-extract-source-notes.py"

if [[ ! -f "$TOOL" ]]; then
  echo "error: $TOOL not found" >&2
  exit 1
fi

exec python3 "$TOOL" "$@"
