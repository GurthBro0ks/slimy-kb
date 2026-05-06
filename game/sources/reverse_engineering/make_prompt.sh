#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-build}"
shift || true
TASK="${*:-Run a health check and recommend next steps.}"

cat <<PROMPT
cat ./AGENTS.md
cat ./claude-progress.md
source ./init.sh

# MODE: $MODE
# TASK
$TASK

# OPERATING RULES
- Work inside this project folder only unless explicitly instructed otherwise.
- Preserve raw evidence. Do not overwrite .luac, APK/XAPK, .so, PCAP, HAR, mitmproxy, or originals files.
- Treat any script that rewrites originals as suspect until quarantined.
- Use proof packs for every claim.
- Do not use Discord/webhooks.
- Do not run git add .

# REQUIRED OUTPUTS
- Clear summary of files inspected and changed.
- Commands run and results.
- Proof directory path.
- Remaining unknowns.

When done:
1. Update ./claude-progress.md with commands run, files changed, proof directory, and remaining unknowns.
2. Update ./feature_list.json if relevant.
3. Run ./scripts/qa_gate.sh and save the proof path.
4. Run ./scripts/git_auto_sync.sh only after QA passes.
5. Do not commit originals, captures, APK/XAPK, .so, .luac, secrets, or account/session data.
PROMPT
