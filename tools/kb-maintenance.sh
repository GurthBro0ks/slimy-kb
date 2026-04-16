#!/usr/bin/env bash
# kb-maintenance.sh — Automated KB maintenance for NUC2
# Runs: pull, compile, lint, file-back, log, git commit, push, proof bundle
set -euo pipefail

KB_ROOT="/home/slimy/kb"
KB_TOOLS="$KB_ROOT/tools"
HOST=$(hostname -s)
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PROOF_DIR="/tmp/proof_kb_maintenance_$(date -u +%Y%m%dT%H%M%SZ)"
EXIT_CODE=0

mkdir -p "$PROOF_DIR"

log_step() {
    echo "[kb-maintenance] $(date +%H:%M:%S) — $1"
}

# ── STEP 1: Sync pull ──────────────────────────────────────────────────────────
log_step "Pulling latest KB..."
bash "$KB_TOOLS/kb-sync.sh" pull >> "$PROOF_DIR/step1-pull.log" 2>&1 || {
    echo "WARNING: pull failed, continuing with local state" >> "$PROOF_DIR/step1-pull.log"
}

# ── STEP 2: Compile if needed ────────────────────────────────────────────────
# Check for uncompiled raw files (don't spawn child compile — that needs auth)
log_step "Checking compile candidates..."
compile_candidates=$(bash "$KB_TOOLS/kb-compile-if-needed.sh" --dry-run --skip-child 2>&1 | grep -E "^  -" | awk '{print $2}' || true)
if [[ -n "$compile_candidates" ]]; then
    echo "Compile needed for:" >> "$PROOF_DIR/step2-compile.log"
    echo "$compile_candidates" >> "$PROOF_DIR/step2-compile.log"
    log_step "Compile needed for: $compile_candidates"
    echo "COMPILE_NEEDED=yes" >> "$PROOF_DIR/status.txt"
    COMPILE_NEEDED=yes
else
    echo "COMPILE_NEEDED=no" >> "$PROOF_DIR/status.txt"
    COMPILE_NEEDED=no
fi

# ── STEP 3: File-back status ──────────────────────────────────────────────────
# Compile candidates from Step 2 are the real file-back signal (uncompiled raw files).
# The wiki manager writes to output/ every 12h — checking output/ for recent files
# would always fire and tell operators to run a non-existent command. Removed.
if [[ "${COMPILE_NEEDED:-no}" == "yes" ]]; then
    log_step "File-back: compile candidates pending (see Step 2)"
else
    log_step "File-back: no uncompiled raw files"
fi

# ── STEP 4: Lint ─────────────────────────────────────────────────────────────
log_step "Running lint..."
set +e
bash "$KB_TOOLS/kb-lint.sh" >> "$PROOF_DIR/step4-lint.log" 2>&1
LINT_EXIT=$?
set -e
if [[ "$LINT_EXIT" -ne 0 ]]; then
    echo "WARNING: lint returned exit $LINT_EXIT" >> "$PROOF_DIR/step4-lint.log"
fi

# Copy lint outputs to proof dir
cp "$KB_ROOT/wiki/_orphans.md" "$PROOF_DIR/" 2>/dev/null || true
cp "$KB_ROOT/wiki/_weak-links.md" "$PROOF_DIR/" 2>/dev/null || true

# ── STEP 5: Append maintenance log entry ─────────────────────────────────────
log_step "Appending maintenance log entry..."
bash "$KB_TOOLS/kb-log-append.sh" maintenance "12h maintenance run" "auto-maintenance from kb-maintenance.sh $RUN_TS" >> "$PROOF_DIR/step5-log.log" 2>&1

# ── STEP 5b: Refresh git-backed metadata ──────────────────────────────────────
log_step "Refreshing page metadata..."
python3 "$KB_TOOLS/kb-apply-metadata.py" >> "$PROOF_DIR/step5b-metadata.log" 2>&1 || {
    echo "WARNING: metadata refresh failed" >> "$PROOF_DIR/step5b-metadata.log"
}

# ── STEP 6: Git add ──────────────────────────────────────────────────────────
log_step "Checking git status..."
cd "$KB_ROOT"
git add -A

# ── STEP 7: Git commit (only if actual changes) ─────────────────────────────
CHANGES=$(git --no-pager diff --cached --stat)
if [[ -n "$CHANGES" ]]; then
    log_step "Committing changes..."
    git --no-pager commit -m "kb: maintenance run $(date +%Y-%m-%d-%H%M) from $HOST" >> "$PROOF_DIR/step7-commit.log" 2>&1 || {
        echo "WARNING: commit failed" >> "$PROOF_DIR/step7-commit.log"
        EXIT_CODE=1
    }
else
    log_step "No changes to commit"
fi

# ── STEP 8: Push ──────────────────────────────────────────────────────────────
log_step "Pushing..."
bash "$KB_TOOLS/kb-sync.sh" push >> "$PROOF_DIR/step8-push.log" 2>&1 || {
    echo "WARNING: push failed" >> "$PROOF_DIR/step8-push.log"
    EXIT_CODE=1
}

# ── STEP 9: Vault mirror ─────────────────────────────────────────────────────
log_step "Syncing wiki to Obsidian vault..."
bash "$KB_TOOLS/kb-obsidian-sync.sh" >> "$PROOF_DIR/step9-vault-sync.log" 2>&1 || {
    echo "WARNING: vault sync failed" >> "$PROOF_DIR/step9-vault-sync.log"
}

# ── STEP 10: Proof bundle ────────────────────────────────────────────────────
{
    echo "# KB Maintenance Proof Bundle"
    echo ""
    echo "- **Run TS:** $RUN_TS"
    echo "- **Host:** $HOST"
    echo "- **Exit Code:** $EXIT_CODE"
    echo ""
    echo "## Steps Run"
    echo ""
    echo "1. pull — sync pull from origin"
    echo "2. compile — kb-compile-if-needed.sh (skip-child mode)"
    echo "3. file-back — compile candidate status (see Step 2 for details)"
    echo "4. lint — kb-lint.sh (with orphans + weak-links)"
    echo "5. log — appended maintenance entry to wiki/log.md"
    echo "5b. metadata — kb-apply-metadata.py (git-backed last-edited/version)"
    echo "6. commit — git commit if changes existed"
    echo "7. push — sync push to origin"
    echo "8. vault-mirror — kb-obsidian-sync.sh (wiki → vault)"
    echo ""
    echo "## Generated Files"
    echo ""
    echo "- _orphans.md: $([[ -f "$KB_ROOT/wiki/_orphans.md" ]] && echo "YES" || echo "NO")"
    echo "- _weak-links.md: $([[ -f "$KB_ROOT/wiki/_weak-links.md" ]] && echo "YES" || echo "NO")"
    echo "- wiki/log.md: $([[ -f "$KB_ROOT/wiki/log.md" ]] && echo "YES" || echo "NO")"
    echo ""
    echo "## Git Status"
    echo ""
    git status --short >> "$PROOF_DIR/git-status.txt" 2>&1
    cat "$PROOF_DIR/git-status.txt"
    echo ""
    echo "## Changes (if any)"
    echo ""
    cat "$PROOF_DIR/step7-commit.log" 2>/dev/null || echo "(no commit log)"
} > "$PROOF_DIR/PROOF.md"

log_step "Maintenance complete. Proof at $PROOF_DIR"
echo "EXIT_CODE=$EXIT_CODE"