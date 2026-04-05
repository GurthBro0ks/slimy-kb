#!/usr/bin/env bash
# kb-compile-if-needed.sh
# Check whether new raw files exist that are not yet referenced; run compile if yes.
# Usage: kb-compile-if-needed.sh [--dry-run] [--force]
set -euo pipefail

# Disable interactive pager — wrapper-triggered runs have no TTY
export GIT_PAGER=cat
export PAGER=cat

DRY_RUN="${1:-}"
FORCE="${2:-}"
HOST=$(hostname -s)
TODAY=$(date +%Y-%m-%d)
KB_ROOT="/home/slimy/kb"
KB_TOOLS="$KB_ROOT/tools"

# Guard: if already in a child compile, exit to avoid recursion
if [[ "${SLIMY_KB_CHILD_COMPILE:-0}" == "1" ]]; then
    echo "[kb-compile-if-needed] SLIMY_KB_CHILD_COMPILE=1 — already in child compile, exiting to prevent recursion"
    exit 0
fi

# Source webhook config if present (category: ALERTS for failures)
if [[ -f ~/.config/slimy/webhooks.env ]]; then
    source ~/.config/slimy/webhooks.env
fi

# Collect compile candidates (same logic as wiki CLI)
collect_compile_candidates() {
    local -A referenced=()
    local wiki_file ref
    local -a source_lines=()

    while IFS= read -r wiki_file; do
        [[ -f "$wiki_file" ]] || continue
        mapfile -t source_lines < <(grep -hE '^> Sources:' "$wiki_file" 2>/dev/null || true)
        for ref in "${source_lines[@]}"; do
            grep -oE 'raw/[A-Za-z0-9._/-]+\.md' <<< "$ref" 2>/dev/null
        done
    done < <(find "$KB_ROOT/wiki" -type f -name '*.md' ! -name '_*.md' 2>/dev/null)

    find "$KB_ROOT/raw" -type f -name '*.md' -printf '%P\n' 2>/dev/null | sort | while IFS= read -r raw_rel; do
        if [[ -z "${referenced[$raw_rel]:-}" ]]; then
            printf '%s\n' "$raw_rel"
        fi
    done
}

echo "[kb-compile-if-needed] Checking for uncompiled raw files..."

mapfile -t candidates < <(collect_compile_candidates)
count=${#candidates[@]}

echo "[kb-compile-if-needed] Found $count uncompiled raw file(s)"

if [[ "$count" -eq 0 ]]; then
    echo "[kb-compile-if-needed] No compile needed — all raw files are referenced. Exiting cleanly."
    echo "[kb-compile-if-needed] Summary: KB is up-to-date as of $TODAY $HOST"
    exit 0
fi

echo "[kb-compile-if-needed] Compile candidates:"
for c in "${candidates[@]}"; do
    echo "  - $c"
done

if [[ "$FORCE" != "--force" && "$DRY_RUN" == "--dry-run" ]]; then
    echo "[kb-compile-if-needed] DRY-RUN: would trigger compile for $count file(s)"
    exit 0
fi

# --- AUTO-COMPILE: launch child Claude run ---
# SLIMY_KB_CHILD_COMPILE=1 signals child wrapper to skip its finish hook (recursion guard)
# SLIMY_AUTOFINISH_ACTIVE=1 is already exported by slimy-agent-finish.sh parent and inherited
if [[ "$DRY_RUN" != "--dry-run" && "$FORCE" != "--skip-child" ]]; then
    echo "[kb-compile-if-needed] Launching child Claude compile run..."

    # Build compile prompt
    COMPILE_PROMPT_FILE="$KB_ROOT/output/prompts/auto-compile-prompt-$(date -u +%Y%m%d-%H%M%S).md"
    mkdir -p "$KB_ROOT/output/prompts"

    {
        echo "bash /home/slimy/kb/tools/kb-sync.sh pull"
        echo ""
        echo "cat /home/slimy/AGENTS.md"
        echo "cat /home/slimy/claude-progress.md"
        echo "source /home/slimy/init.sh"
        echo "cat /home/slimy/kb/KB_AGENTS.md"
        echo ""
        echo "TASK: KB Compile"
        echo ""
        echo "Goal:"
        echo "- Compile raw knowledge into canonical wiki updates following KB_AGENTS rules."
        echo ""
        echo "Priority Raw Inputs:"
        for c in "${candidates[@]}"; do
            echo "- /home/slimy/kb/$c"
        done
        echo ""
        echo "Required updates:"
        echo "- Update or create wiki articles as needed"
        echo "- Update /home/slimy/kb/wiki/_index.md"
        echo "- Update /home/slimy/kb/wiki/_concepts.md if concepts changed"
        echo "- Preserve source attribution in each article"
        echo ""
        echo "Validation:"
        echo "- Confirm compile candidates are fully handled or explicitly deferred with reason"
        echo ""
        echo "# Direct push without pull-first (avoids rebase conflicts in child compile)"
        echo "cd /home/slimy/kb && git --no-pager add -A && git --no-pager diff --cached --stat && git --no-pager commit -m \"kb: child-compile $(date +%Y%m%d-%H%M%S)\" && git --no-pager push origin main"
    } > "$COMPILE_PROMPT_FILE"

    echo "[kb-compile-if-needed] Compile prompt written to: $COMPILE_PROMPT_FILE"

    # Pipe prompt to claude -p (non-interactive, skips trust dialog)
    # SLIMY_AUTOFINISH_ACTIVE=1 is inherited by child — its wrapper will exit early (recursion guard)
    # SLIMY_KB_CHILD_COMPILE=1 tells kb-compile-if-needed.sh (if re-invoked) to skip
    # GIT_PAGER=cat ensures child git commands never open interactive pager
    COMPILE_OUTPUT=$(
        export GIT_PAGER=cat PAGER=cat
        SLIMY_KB_CHILD_COMPILE=1 \
        claude -p -- \
            --output-format text \
            --dangerously-skip-permissions \
            --system-prompt "You are a KB compile agent. Run the provided task exactly. Use Bash, Read, Write, Edit tools freely. After completing wiki updates, exit cleanly." \
            < "$COMPILE_PROMPT_FILE" 2>&1 || true
    )
    COMPILE_EXIT=$?

    if [[ "$COMPILE_EXIT" -eq 0 ]] && [[ -n "$COMPILE_OUTPUT" ]]; then
        echo "[kb-compile-if-needed] Child compile SUCCEEDED (exit $COMPILE_EXIT)"
        echo "[kb-compile-if-needed] Compile output preview: ${COMPILE_OUTPUT:0:200}"
        # Note: child already committed and pushed via its kb-sync.sh equivalent
        echo "[kb-compile-if-needed] Child handled KB commit/push (check git log for child-compile commits)"
    else
        echo "[kb-compile-if-needed] Child compile FAILED (exit $COMPILE_EXIT)"
        echo "[kb-compile-if-needed] Failure output: ${COMPILE_OUTPUT:0:300}"

        # Write failure note
        FAILURE_NOTE="$KB_ROOT/output/compile-failure-$(date -u +%Y%m%d-%H%M%S).md"
        cat > "$FAILURE_NOTE" << EOF
# Compile Failure — $TODAY $HOST

> Exit code: $COMPILE_EXIT
> Timestamp: $(date -u +%Y%m%d-%H%M%S)

## Candidates That Were Not Compiled
$(for c in "${candidates[@]}"; do echo "- $c"; done)

## Child Compile Output (last 500 chars)
\`\`\`
${COMPILE_OUTPUT:0:500}
\`\`\`

## Next Steps
- Run \`wiki prompt-compile\` manually
- Review the failure output above
- Check API key and network connectivity
EOF
        echo "[kb-compile-if-needed] Wrote failure note: $FAILURE_NOTE"

        # Alert via ALERTS webhook
        if [[ -n "${DISCORD_WEBHOOK_ALERTS:-}" ]]; then
            msg="[ALERT $HOST] kb-compile-if-needed child compile failed (exit $COMPILE_EXIT). Candidates: ${candidates[*]:-none}. See $FAILURE_NOTE"
            curl -s -X POST "$DISCORD_WEBHOOK_ALERTS" \
                -H "Content-Type: application/json" \
                -d "{\"content\": \"$msg\"}" >/dev/null 2>&1 \
                && echo "[kb-compile-if-needed] Posted ALERTS webhook" \
                || echo "[kb-compile-if-needed] ALERTS webhook post failed (non-critical)"
        fi
    fi

    # Clean up prompt file
    rm -f "$COMPILE_PROMPT_FILE"
    echo "[kb-compile-if-needed] Auto-compile phase complete."
    exit 0
fi

# Fallback: --dry-run or --skip-child — just write the prompt file
echo "[kb-compile-if-needed] Triggering KB compile prompt..."
bash "$KB_ROOT/tools/wiki" prompt-compile >/dev/null 2>&1 || true
latest_prompt=$(ls -t "$KB_ROOT/output/prompts/compile-prompt-"*.md 2>/dev/null | head -1 || true)

if [[ -n "$latest_prompt" ]]; then
    echo "[kb-compile-if-needed] Compile prompt written to: $latest_prompt"
    echo "[kb-compile-if-needed] To run compile, execute the prompt or run: wiki prompt-compile"
else
    echo "[kb-compile-if-needed] WARNING: compile prompt file not found"
fi
