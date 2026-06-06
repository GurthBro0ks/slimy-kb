#!/usr/bin/env bash
# research-fetch-sources.sh — thin bash wrapper for research-fetch-sources.py
# See tools/research-fetch-sources.py for the full implementation.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL="$ROOT_DIR/tools/research-fetch-sources.py"

if [[ ! -f "$TOOL" ]]; then
  echo "error: $TOOL not found" >&2
  exit 1
fi

# Strip --dry-run from the args so it can appear before or after the sub-command.
# Pass through all other args verbatim.
exec python3 "$TOOL" "$@"
