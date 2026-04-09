#!/usr/bin/env bash
# wiki_manager_stage1.sh — Stage 1 wiki manager runner
# Pulls, digests, generates todo queue, logs, commits.
set -euo pipefail

KB_ROOT="/home/slimy/kb"
KB_TOOLS="$KB_ROOT/tools"
HOST=$(hostname -s)
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PROOF_DIR="/tmp/proof_wiki_manager_stage1_$(date -u +%Y%m%dT%H%M%SZ)"
EXIT_CODE=0

mkdir -p "$PROOF_DIR"

log_step() {
    echo "[wiki-manager-s1] $(date +%H:%M:%S) — $1"
}

# ── STEP 1: Sync pull ──────────────────────────────────────────────────────────
log_step "Pulling latest KB..."
bash "$KB_TOOLS/kb-sync.sh" pull >> "$PROOF_DIR/step1-pull.log" 2>&1 || {
    echo "WARNING: pull failed, continuing" >> "$PROOF_DIR/step1-pull.log"
}

# ── STEP 2: Run collectors ────────────────────────────────────────────────────
log_step "Running collectors..."
bash "$KB_TOOLS/collect_nuc2_state.sh" >> "$PROOF_DIR/step2-nuc2-state.log" 2>&1 || EXIT_CODE=1
bash "$KB_TOOLS/collect_repo_digests.py" >> "$PROOF_DIR/step2-repo-digests.log" 2>&1 || EXIT_CODE=1
bash "$KB_TOOLS/collect_kb_health.sh" >> "$PROOF_DIR/step2-kb-health.log" 2>&1 || EXIT_CODE=1

# ── STEP 3: Read wiki meta + recent digests ───────────────────────────────────
log_step "Reading wiki meta..."
INDEX_CONTENT=$(cat "$KB_ROOT/wiki/_index.md" 2>/dev/null || echo "")
CONCEPTS_CONTENT=$(cat "$KB_ROOT/wiki/_concepts.md" 2>/dev/null || echo "")
LOG_CONTENT=$(cat "$KB_ROOT/wiki/log.md" 2>/dev/null || echo "")
PAGE_TYPES_CONTENT=$(cat "$KB_ROOT/wiki/_page-types.md" 2>/dev/null || echo "")
ORPHANS_CONTENT=$(cat "$KB_ROOT/wiki/_orphans.md" 2>/dev/null || echo "")
WEAK_LINKS_CONTENT=$(cat "$KB_ROOT/wiki/_weak-links.md" 2>/dev/null || echo "")

# Recent digests from NUC2 (last 48h)
RECENT_NUC2_DIGESTS=$(find "$KB_ROOT/raw/research" -name "*nuc2*" -name "*.md" -mtime -2 2>/dev/null | sort)
NUC1_INBOX="$KB_ROOT/raw/inbox-nuc1"
NUC1_ITEM_COUNT=0
NUC1_INTAKE_CONTENT=""
if [[ -d "$NUC1_INBOX" ]]; then
    NUC1_ITEM_COUNT=$(find "$NUC1_INBOX" -type f 2>/dev/null | wc -l | tr -d ' ')
    NUC1_INTAKE_CONTENT=$(cat "$NUC1_INBOX"/*.{md,json} 2>/dev/null || true)
fi

# Recent KB output
RECENT_OUTPUT=$(find "$KB_ROOT/output" -name '*.md' ! -name 'lint-report*' -mtime -2 2>/dev/null | sort | head -5)

# ── STEP 4: Generate todo queue ─────────────────────────────────────────────
log_step "Generating todo queue..."
python3 "$KB_TOOLS/wiki_manager_stage1.py" \
    --orphans "$ORPHANS_CONTENT" \
    --weak-links "$WEAK_LINKS_CONTENT" \
    --nuc1-count "$NUC1_ITEM_COUNT" \
    --nuc1-content "$NUC1_INTAKE_CONTENT" \
    --backend "${KB_MANAGER_BACKEND:-stub}" \
    --model "${KB_MANAGER_MODEL:-qwen2.5:7b}" \
    >> "$PROOF_DIR/step4-todo.log" 2>&1 || {
        echo "WARNING: todo generation had issues" >> "$PROOF_DIR/step4-todo.log"
    }

TODO_JSON="$KB_ROOT/output/todo_queue.json"
TODO_MD="$KB_ROOT/output/todo_queue.md"

# ── STEP 5: Log entry ────────────────────────────────────────────────────────
log_step "Appending log entry..."
NOTE="stage1 run: todos=$([[ -f "$TODO_JSON" ]] && python3 -c "import json; print(len(json.load(open('$TODO_JSON'))['tasks']))" 2>/dev/null || echo 0)), nuc1_inbox_items=$NUC1_ITEM_COUNT"
bash "$KB_TOOLS/kb-log-append.sh" wiki_manager "stage1 todo queue generation" "$NOTE" >> "$PROOF_DIR/step5-log.log" 2>&1 || EXIT_CODE=1

# ── STEP 6: Git commit (only if kb changed) ──────────────────────────────────
log_step "Checking git status..."
cd "$KB_ROOT"
git add -A

CHANGES=$(git --no-pager diff --cached --stat)
if [[ -n "$CHANGES" ]]; then
    log_step "Committing..."
    git --no-pager commit -m "kb: wiki-manager stage1 $(date +%Y-%m-%d-%H%M) from $HOST" >> "$PROOF_DIR/step6-commit.log" 2>&1 || {
        echo "WARNING: commit failed" >> "$PROOF_DIR/step6-commit.log"
        EXIT_CODE=1
    }
    DID_COMMIT=yes
else
    log_step "No changes to commit"
    DID_COMMIT=no
fi

# ── STEP 7: Push ──────────────────────────────────────────────────────────────
log_step "Pushing..."
bash "$KB_TOOLS/kb-sync.sh" push >> "$PROOF_DIR/step7-push.log" 2>&1 || {
    echo "WARNING: push failed" >> "$PROOF_DIR/step7-push.log"
    EXIT_CODE=1
}

# ── STEP 8: Proof bundle ─────────────────────────────────────────────────────
{
    echo "# Wiki Manager Stage 1 Proof Bundle"
    echo ""
    echo "- **Run TS:** $RUN_TS"
    echo "- **Host:** $HOST"
    echo "- **Exit Code:** $EXIT_CODE"
    echo "- **Backend:** ${KB_MANAGER_BACKEND:-stub}"
    echo "- **Model:** ${KB_MANAGER_MODEL:-qwen2.5:7b}"
    echo ""
    echo "## NUC1 Intake"
    echo ""
    echo "- inbox-nuc1 present: $([[ -d "$NUC1_INBOX" ]] && echo YES || echo NO)"
    echo "- NUC1 item count: $NUC1_ITEM_COUNT"
    echo ""
    echo "## Todo Queue"
    echo ""
    echo "- todo_queue.json: $([[ -f "$TODO_JSON" ]] && echo "YES" || echo "NO (may be empty/stub)")"
    echo "- todo_queue.md: $([[ -f "$TODO_MD" ]] && echo "YES" || echo "NO")"
    if [[ -f "$TODO_JSON" ]]; then
        python3 -c "import json; d=json.load(open('$TODO_JSON')); print(f'- total tasks: {len(d[\"tasks\"])}')" 2>/dev/null || echo "- (could not parse)"
        python3 -c "import json; d=json.load(open('$TODO_JSON')); sev={}; kind={}; [sev.update({t['severity']:sev.get(t['severity'],0)+1}) for t in d['tasks']]; [kind.update({t['kind']:kind.get(t['kind'],0)+1}) for t in d['tasks']]; print(f'- by severity: {sev}'); print(f'- by kind: {kind}')" 2>/dev/null || echo "- (could not aggregate)"
    fi
    echo ""
    echo "## Git"
    echo ""
    echo "- did_commit: $DID_COMMIT"
    echo "- changes:"
    echo "$CHANGES" | head -20 | sed 's/^/  /'
    echo ""
    echo "## Files Changed"
    echo ""
    find "$KB_ROOT/raw/research" -name "*${HOST}*" -mtime -1 2>/dev/null | sed 's/^/  /'
    echo ""
    echo "## Proof Dir"
    echo ""
    ls "$PROOF_DIR/" | sed 's/^/  /'
} > "$PROOF_DIR/REPORT.md"

log_step "Stage 1 complete. Proof at $PROOF_DIR"
echo "EXIT_CODE=$EXIT_CODE"
echo "PROOF_DIR=$PROOF_DIR"
echo "TODO_JSON=${TODO_JSON:-none}"
echo "TODO_MD=${TODO_MD:-none}"
echo "BACKEND=${KB_MANAGER_BACKEND:-stub}"
