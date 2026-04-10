#!/usr/bin/env bash
# slimy-session-finish.sh
# Interrupt-aware session finish wrapper for Claude Code stop hook.
#
# Detects HOW the session ended:
#   - SIGINT (Ctrl+C): quiet exit — NO Discord ALERT, NO multi-repo sweep
#   - SUCCESS (exit 0): quiet finish — kb-compile, bounded cleanup, NO ALERT
#   - ERROR (exit !=0): bounded finish — kb-compile, cleanup, bounded ALERT
#
# Bounded means: only the actively-worked repo is touched, not a full repo scan.
#
# Usage (from Stop hook):
#   bash /home/slimy/kb/tools/slimy-session-finish.sh [--active-repo /path/to/repo]
#
# Exit code conventions used internally:
#   130 = SIGINT received (Ctrl+C)
set -euo pipefail

HOST=$(hostname -s)
TODAY=$(date +%Y-%m-%d)
INTERRUPTED=0
EXIT_CODE=0

# Detect SIGINT (Ctrl+C) received by this process
trap 'INTERRUPTED=1' INT

# Capture actual exit code when this script exits
trap 'EXIT_CODE=$?; handle_exit' EXIT

ACTIVE_REPO=""
DRY_RUN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --active-repo)
            ACTIVE_REPO="$2"; shift 2 ;;
        --dry-run)
            DRY_RUN="--dry-run"; shift ;;
        *)
            shift ;;
    esac
done

handle_exit() {
    local code=$EXIT_CODE

    if [[ "$INTERRUPTED" == "1" || "$code" -eq 130 ]]; then
        # Ctrl+C / SIGINT — quiet exit
        echo "[slimy-session-finish] INTERRUPTED (SIGINT/Ctrl+C) — skipping finish automation"
        return 0
    fi

    if [[ "$code" -eq 0 ]]; then
        # Normal successful finish
        echo "[slimy-session-finish] SUCCESS — running bounded quiet finish"
        run_quiet_finish
        return 0
    fi

    # Error exit — bounded finish with alerts
    echo "[slimy-session-finish] ERROR (exit $code) — running bounded finish with alerts"
    run_bounded_finish
}

run_quiet_finish() {
    # Bounded cleanup: only compile if needed (no alerts)
    # Only sync the active repo if specified
    if [[ -n "$ACTIVE_REPO" && -d "$ACTIVE_REPO" ]]; then
        echo "[slimy-session-finish] Syncing active repo: $ACTIVE_REPO"
        bash /home/slimy/kb/tools/kb-project-doc-sync.sh "$ACTIVE_REPO" "$DRY_RUN" || true
    fi

    # Run compile silently, don't let failures bubble up to Discord
    if [[ "$DRY_RUN" != "--dry-run" ]]; then
        bash /home/slimy/kb/tools/kb-compile-if-needed.sh 2>&1 || {
            echo "[slimy-session-finish] compile-if-needed failed (non-critical, skipping alert)"
        }
    fi

    echo "[slimy-session-finish] Quiet finish complete."
}

run_bounded_finish() {
    local finish_args=(
        --agent claude
        --skip-compile  # compile handled below with bounded scope
    )

    if [[ -n "$ACTIVE_REPO" && -d "$ACTIVE_REPO" ]]; then
        finish_args+=(--repo "$ACTIVE_REPO")
    fi

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        finish_args+=(--dry-run)
    fi

    # Run bounded finish automation
    bash /home/slimy/kb/tools/slimy-agent-finish.sh "${finish_args[@]}" && finish_rc=0 || finish_rc=$?

    # If finish automation itself failed, that's a real alert-worthy failure
    if [[ "$finish_rc" -ne 0 ]]; then
        echo "[slimy-session-finish] Finish automation failed (rc=$finish_rc) — posting ALERT"

        # Source webhook config
        if [[ -f ~/.config/slimy/webhooks.env ]]; then
            source ~/.config/slimy/webhooks.env
        fi

        if [[ -n "${DISCORD_WEBHOOK_ALERTS:-}" ]]; then
            local msg="[ALERT $HOST] slimy-session-finish: finish-automation failed (rc=$finish_rc) agent=claude active_repo=${ACTIVE_REPO:-none}"
            curl -s -X POST "${DISCORD_WEBHOOK_ALERTS}" \
                -H "Content-Type: application/json" \
                -d "{\"content\": \"$msg\"}" >/dev/null 2>&1 || true
        fi
    else
        echo "[slimy-session-finish] Bounded finish complete (rc=0)."
    fi
}
