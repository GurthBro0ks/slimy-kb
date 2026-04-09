#!/usr/bin/env bash
# wiki_manager_stage1.sh — Stage 1.86 wiki manager runner
# Pulls, digests, generates todo queue, logs, commits.
set -uo pipefail

KB_ROOT="/home/slimy/kb"
KB_TOOLS="$KB_ROOT/tools"
HOST=$(hostname -s)
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PROOF_DIR="/tmp/proof_wiki_manager_stage1_$(date -u +%Y%m%dT%H%M%SZ)"
EXIT_CODE=0

mkdir -p "$PROOF_DIR"

log_step() {
    echo "[wiki-manager-s1.86] $(date +%H:%M:%S) — $1"
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

# ── STEP 3: Read wiki meta + NUC1 inbox ────────────────────────────────────────
log_step "Reading wiki meta..."
INDEX_CONTENT=$(cat "$KB_ROOT/wiki/_index.md" 2>/dev/null || echo "")
CONCEPTS_CONTENT=$(cat "$KB_ROOT/wiki/_concepts.md" 2>/dev/null || echo "")
LOG_CONTENT=$(cat "$KB_ROOT/wiki/log.md" 2>/dev/null || echo "")
PAGE_TYPES_CONTENT=$(cat "$KB_ROOT/wiki/_page-types.md" 2>/dev/null || echo "")
ORPHANS_CONTENT=$(cat "$KB_ROOT/wiki/_orphans.md" 2>/dev/null || echo "")
WEAK_LINKS_CONTENT=$(cat "$KB_ROOT/wiki/_weak-links.md" 2>/dev/null || echo "")

# Recent digests from NUC2 (last 48h)
RECENT_NUC2_DIGESTS=$(find "$KB_ROOT/raw/research" -name "*nuc2*" -name "*.md" -mtime -2 2>/dev/null | sort)

# Capture NUC2 state markdown (latest digest)
NUC2_MD_CONTENT=""
if [[ -n "$RECENT_NUC2_DIGESTS" ]]; then
    NUC2_MD_CONTENT=$(cat "$(echo "$RECENT_NUC2_DIGESTS" | tail -1)" 2>/dev/null || echo "")
fi

# ── NUC1 inbox — parse separately by type ────────────────────────────────────
NUC1_INBOX="$KB_ROOT/raw/inbox-nuc1"
NUC1_ITEM_COUNT=0
NUC1_JSON_CONTENT=""
NUC1_MD_CONTENT=""
NUC1_EVIDENCE_USED="NO"

if [[ -d "$NUC1_INBOX" ]]; then
    NUC1_ITEM_COUNT=$(find "$NUC1_INBOX" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [[ $NUC1_ITEM_COUNT -gt 0 ]]; then
        # Collect JSON files
        NUC1_JSON_CONTENT=$(find "$NUC1_INBOX" -name "*.json" -exec cat {} + 2>/dev/null || true)
        # Collect Markdown files
        NUC1_MD_CONTENT=$(find "$NUC1_INBOX" -name "*.md" -exec cat {} + 2>/dev/null || true)
        if [[ -n "$NUC1_JSON_CONTENT" || -n "$NUC1_MD_CONTENT" ]]; then
            NUC1_EVIDENCE_USED="YES"
        fi
        log_step "NUC1 inbox: $NUC1_ITEM_COUNT items — evidence used: $NUC1_EVIDENCE_USED"
    fi
fi

# Recent KB output
RECENT_OUTPUT=$(find "$KB_ROOT/output" -name '*.md' ! -name 'lint-report*' -mtime -2 2>/dev/null | sort | head -5)

# ── STEP 4: Generate todo queue ─────────────────────────────────────────────
log_step "Generating todo queue..."
python3 "$KB_TOOLS/wiki_manager_stage1.py" \
    --orphans "$ORPHANS_CONTENT" \
    --weak-links "$WEAK_LINKS_CONTENT" \
    --nuc1-json "$NUC1_JSON_CONTENT" \
    --nuc1-md "$NUC1_MD_CONTENT" \
    --nuc2-md "$NUC2_MD_CONTENT" \
    --backend "${KB_MANAGER_BACKEND:-stub}" \
    --model "${KB_MANAGER_MODEL:-qwen2.5:7b}" \
    >> "$PROOF_DIR/step4-todo.log" 2>&1 || {
        echo "WARNING: todo generation had issues" >> "$PROOF_DIR/step4-todo.log"
    }

TODO_JSON="$KB_ROOT/output/todo_queue.json"
TODO_MD="$KB_ROOT/output/todo_queue.md"
TODO_HISTORY="$KB_ROOT/output/todo_history.json"

# ── STEP 5: Log entry ────────────────────────────────────────────────────────
log_step "Appending log entry..."
TASK_COUNT=0
if [[ -f "$TODO_JSON" ]]; then
    TASK_COUNT=$(python3 -c "import json; print(len(json.load(open('$TODO_JSON'))['tasks']))" 2>/dev/null || echo 0)
fi
NOTE="stage1.86 run: todos=$TASK_COUNT nuc1_items=$NUC1_ITEM_COUNT nuc1_evidence=$NUC1_EVIDENCE_USED"
bash "$KB_TOOLS/kb-log-append.sh" "wiki_manager" "stage1.86 todo queue generation" "$NOTE" >> "$PROOF_DIR/step5-log.log" 2>&1 || EXIT_CODE=1

# ── STEP 6: Git commit (only if kb changed) ──────────────────────────────────
log_step "Checking git status..."
cd "$KB_ROOT"
git add -A

CHANGES=""
CHANGES=$(git --no-pager diff --cached --stat 2>/dev/null) || true
if [[ -n "$CHANGES" ]]; then
    log_step "Committing..."
    git --no-pager commit -m "kb: wiki-manager stage1.86 $(date +%Y-%m-%d-%H%M) from $HOST" >> "$PROOF_DIR/step6-commit.log" 2>&1 || {
        echo "WARNING: commit failed" >> "$PROOF_DIR/step6-commit.log"
        EXIT_CODE=1
    }
    DID_COMMIT=yes
else
    log_step "No changes to commit"
    DID_COMMIT=no
fi

# ── STEP 7: Push ─────────────────────────────────────────────────────────────
log_step "Pushing..."
bash "$KB_TOOLS/kb-sync.sh" push >> "$PROOF_DIR/step7-push.log" 2>&1 || {
    echo "WARNING: push failed" >> "$PROOF_DIR/step7-push.log"
    EXIT_CODE=1
}

# ── STEP 8: Proof bundle ─────────────────────────────────────────────────────
# Write proof bundle via Python to avoid complex bash quoting issues
PROOF_SCRIPT=$(cat <<'PYEOF'
import json
import os
import sys

run_ts = sys.argv[1]
host = sys.argv[2]
exit_code = sys.argv[3]
backend = sys.argv[4]
model = sys.argv[5]
nuc1_inbox = sys.argv[6]
nuc1_count = int(sys.argv[7])
nuc1_evidence = sys.argv[8]
nuc1_dirty_raw = sys.argv[9]
nuc1_diverged_raw = sys.argv[10]
todo_json = sys.argv[11]
todo_md = sys.argv[12]
todo_history = sys.argv[13]
manager_status = sys.argv[14]
proof_dir = sys.argv[15]
did_commit = sys.argv[16]
changes = sys.argv[17] if len(sys.argv) > 17 else ""

nuc1_dirty = json.loads(nuc1_dirty_raw) if nuc1_dirty_raw else []
nuc1_diverged = json.loads(nuc1_diverged_raw) if nuc1_diverged_raw else []

lines = []
lines.append("# Wiki Manager Stage 1.86 Proof Bundle")
lines.append("")
lines.append(f"- **Run TS:** {run_ts}")
lines.append(f"- **Host:** {host}")
lines.append(f"- **Exit Code:** {exit_code}")
lines.append(f"- **Backend:** {backend}")
lines.append(f"- **Model:** {model}")
lines.append("")
lines.append("## NUC1 Intake")
lines.append("")
inbox_present = "YES" if os.path.isdir(nuc1_inbox) else "NO"
lines.append(f"- inbox-nuc1 present: {inbox_present}")
lines.append(f"- NUC1 item count: {nuc1_count}")
lines.append(f"- NUC1 evidence consumed: {nuc1_evidence}")
lines.append(f"- NUC1 dirty repos: {json.dumps(nuc1_dirty)}")
lines.append(f"- NUC1 diverged repos: {json.dumps(nuc1_diverged)}")
lines.append("")
lines.append("## Stable Pages")
lines.append("")
kb_root = os.path.dirname(os.path.dirname(proof_dir))
nuc1_page = os.path.join(kb_root, 'wiki', 'architecture', 'nuc1-current-state.md')
nuc2_page = os.path.join(kb_root, 'wiki', 'architecture', 'nuc2-current-state.md')
repo_page = os.path.join(kb_root, 'wiki', 'projects', 'repo-health-overview.md')
harness_candidates_page = os.path.join(kb_root, 'output', 'harness_candidates.md')
lines.append(f"- nuc1-current-state.md: {'CREATED/UPDATED' if os.path.exists(nuc1_page) else 'SKIPPED'}")
lines.append(f"- nuc2-current-state.md: {'CREATED/UPDATED' if os.path.exists(nuc2_page) else 'SKIPPED'}")
lines.append(f"- repo-health-overview.md: {'CREATED/UPDATED' if os.path.exists(repo_page) else 'SKIPPED'}")
project_health_page = os.path.join(kb_root, 'wiki', 'projects', '_project-health-index.md')
candidate_rules_page = os.path.join(kb_root, 'wiki', '_candidate-promotion-rules.md')
lines.append(f"- _project-health-index.md: {'CREATED/UPDATED' if os.path.exists(project_health_page) else 'SKIPPED'}")
lines.append(f"- _candidate-promotion-rules.md: {'CREATED/UPDATED' if os.path.exists(candidate_rules_page) else 'SKIPPED'}")
lines.append(f"- harness_candidates.md: {'CREATED' if os.path.exists(harness_candidates_page) else 'none (no candidates)'}")
lines.append("")
lines.append("## Todo Queue")
lines.append("")

todo_json_exists = os.path.exists(todo_json)
todo_md_exists = os.path.exists(todo_md)
todo_history_exists = os.path.exists(todo_history)
manager_status_exists = os.path.exists(manager_status)

lines.append(f"- todo_queue.json: {'YES' if todo_json_exists else 'NO'}")
lines.append(f"- todo_queue.md: {'YES' if todo_md_exists else 'NO'}")
lines.append(f"- todo_history.json: {'YES' if todo_history_exists else 'NO'}")
lines.append(f"- _manager-status.md: {'YES' if manager_status_exists else 'NO'}")

if todo_json_exists:
    with open(todo_json) as f:
        d = json.load(f)
    sev = {}
    kind = {}
    state = {}
    for t in d.get('tasks', []):
        sev[t['severity']] = sev.get(t['severity'], 0) + 1
        kind[t['kind']] = kind.get(t['kind'], 0) + 1
        state[t.get('state', 'new')] = state.get(t.get('state', 'new'), 0) + 1
    lines.append(f"- by severity: {json.dumps(sev)}")
    lines.append(f"- by kind: {json.dumps(kind)}")
    lines.append(f"- by state: {json.dumps(state)}")
    lines.append(f"- total tasks: {len(d.get('tasks', []))}")
    lines.append(f"- nuc1_evidence_used: {d.get('nuc1_evidence_used', False)}")
    lines.append(f"- nuc1_host: {d.get('nuc1_host', 'unknown')}")
    prom_counts = d.get('promotion_counts', {})
    lines.append(f"- promotion: candidate={prom_counts.get('candidate', 0)} emerging={prom_counts.get('emerging', 0)} not_candidate={prom_counts.get('not_candidate', 0)}")
    proj_pages = d.get('project_pages_updated', [])
    lines.append(f"- project_pages_updated: {json.dumps(proj_pages)}")

lines.append("")
lines.append("## History")
lines.append("")
if todo_history_exists:
    with open(todo_history) as f:
        h = json.load(f)
    lines.append(f"- history_updated: {h.get('updated_at', 'unknown')}")
    lines.append(f"- history_task_count: {len(h.get('tasks', []))}")
else:
    lines.append("- history_updated: unknown")
    lines.append("- history_task_count: 0")

lines.append("")
lines.append("## Stage 1.8 Features")
lines.append("")
lines.append("### Promotion Counts")
if todo_json_exists:
    with open(todo_json) as f:
        d = json.load(f)
    prom_counts = d.get('promotion_counts', {})
    lines.append(f"- candidate: {prom_counts.get('candidate', 0)}")
    lines.append(f"- emerging: {prom_counts.get('emerging', 0)}")
    lines.append(f"- cooling_down: {prom_counts.get('cooling_down', 0)}")
    lines.append(f"- not_candidate: {prom_counts.get('not_candidate', 0)}")
    demotion_count = d.get('demotion_count', 0)
    lines.append(f"- demoted_this_run: {demotion_count}")
    freshness = d.get('freshness_counts', {})
    lines.append(f"- freshness: fresh={freshness.get('fresh', 0)} aging={freshness.get('aging', 0)} stale={freshness.get('stale', 0)}")
else:
    lines.append("- (no todo_queue.json)")
lines.append("")
lines.append("### Candidate Review Pack")
review_pack = os.path.join(os.path.dirname(todo_json), 'candidate_review_pack.md')
lines.append(f"- candidate_review_pack.md: {'CREATED' if os.path.exists(review_pack) else 'none'}")
lines.append("")
lines.append("### Project Pages Updated")
if todo_json_exists:
    with open(todo_json) as f:
        d = json.load(f)
    proj_pages = d.get('project_pages_updated', [])
    if proj_pages:
        for pg in proj_pages:
            lines.append(f"- {pg}")
    else:
        lines.append("- none")
else:
    lines.append("- (no todo_queue.json)")
lines.append("")

lines.append("## Git")
lines.append("")
lines.append(f"- did_commit: {did_commit}")
if changes.strip():
    lines.append("- changes:")
    for line in changes.strip().splitlines()[:20]:
        lines.append(f"  {line}")
else:
    lines.append("- changes: none")

lines.append("")
lines.append("## Files Changed")
lines.append("")
kb_root = os.path.dirname(os.path.dirname(proof_dir))  # up from proof to kb
research_dir = os.path.join(kb_root, 'raw', 'research')
if os.path.isdir(research_dir):
    for entry in os.listdir(research_dir):
        if host.lower() in entry.lower() and entry.endswith('.md'):
            lines.append(f"  - raw/research/{entry}")

lines.append("")
lines.append("## Proof Dir")
lines.append("")
for entry in sorted(os.listdir(proof_dir)):
    lines.append(f"  - {entry}")

report_path = os.path.join(proof_dir, 'REPORT.md')
with open(report_path, 'w') as f:
    f.write('\n'.join(lines))

print(f"Proof bundle written: {report_path}")
PYEOF
)

# Gather NUC1 dirty/diverged info from JSON if available
NUC1_DIRTY_RAW="[]"
NUC1_DIVERGED_RAW="[]"
if [[ -n "$NUC1_JSON_CONTENT" ]]; then
    # Write JSON to temp file to avoid quoting issues
    NUC1_JSON_TMP="$PROOF_DIR/nuc1_inbox.json"
    echo "$NUC1_JSON_CONTENT" > "$NUC1_JSON_TMP"
    NUC1_DIRTY_RAW=$(python3 -c "
import json,sys
with open('$NUC1_JSON_TMP') as f:
    data=json.load(f)
print(json.dumps([r['name'] for r in data.get('repos',[]) if r.get('dirty')]))
" 2>/dev/null || echo "[]")
    NUC1_DIVERGED_RAW=$(python3 -c "
import json,sys
with open('$NUC1_JSON_TMP') as f:
    data=json.load(f)
diverged=[]
for r in data.get('repos',[]):
    ab=r.get('ahead_behind') or {}
    if ab.get('ahead',0)>0 and ab.get('behind',0)>0:
        diverged.append(r['name'])
print(json.dumps(diverged))
" 2>/dev/null || echo "[]")
fi

# Run proof bundle generator
python3 -c "$PROOF_SCRIPT" \
    "$RUN_TS" \
    "$HOST" \
    "$EXIT_CODE" \
    "${KB_MANAGER_BACKEND:-stub}" \
    "${KB_MANAGER_MODEL:-qwen2.5:7b}" \
    "$NUC1_INBOX" \
    "$NUC1_ITEM_COUNT" \
    "$NUC1_EVIDENCE_USED" \
    "$NUC1_DIRTY_RAW" \
    "$NUC1_DIVERGED_RAW" \
    "$TODO_JSON" \
    "$TODO_MD" \
    "$TODO_HISTORY" \
    "$KB_ROOT/wiki/_manager-status.md" \
    "$PROOF_DIR" \
    "$DID_COMMIT" \
    "$CHANGES" \
    >> "$PROOF_DIR/step8-proof.log" 2>&1 || true

log_step "Stage 1.86 complete. Proof at $PROOF_DIR"
echo "EXIT_CODE=$EXIT_CODE"
echo "PROOF_DIR=$PROOF_DIR"
echo "TODO_JSON=${TODO_JSON:-none}"
echo "TODO_MD=${TODO_MD:-none}"
echo "TODO_HISTORY=${TODO_HISTORY:-none}"
echo "NUC1_EVIDENCE_USED=$NUC1_EVIDENCE_USED"
echo "BACKEND=${KB_MANAGER_BACKEND:-stub}"
echo "MANAGER_STATUS_PAGE=$KB_ROOT/wiki/_manager-status.md"
echo "NUC1_STATE_PAGE=$KB_ROOT/wiki/architecture/nuc1-current-state.md"
echo "NUC2_STATE_PAGE=$KB_ROOT/wiki/architecture/nuc2-current-state.md"
echo "REPO_HEALTH_PAGE=$KB_ROOT/wiki/projects/repo-health-overview.md"
