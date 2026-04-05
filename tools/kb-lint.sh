#!/usr/bin/env bash
# kb-lint.sh — Knowledge Base lint checker
# Scans KB and vault for structural issues and generates a lint report.
set -euo pipefail

KB_ROOT="/home/slimy/kb"
KB_WIKI="$KB_ROOT/wiki"
KB_RAW="$KB_ROOT/raw"
VAULT_ROOT="/home/slimy/obsidian/slimyai-vault"
REPORT_PATH="${1:-"$KB_ROOT/output/lint-report.md"}"
HOST=$(hostname -s)
RUN_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# ── helpers ──────────────────────────────────────────────────────────────────

find_conflicts() {
    local -a search_dirs=("$KB_ROOT")
    [[ -d "$VAULT_ROOT" ]] && search_dirs+=("$VAULT_ROOT")
    find "${search_dirs[@]}" -type f -iname '*conflict*' 2>/dev/null | sort
}

conflict_age_days() {
    local file="$1"
    local mod_sec now_sec age_days
    mod_sec=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null || echo 0)
    now_sec=$(date +%s)
    age_days=$(( (now_sec - mod_sec) / 86400 ))
    printf '%d' "$age_days"
}

conflict_device() {
    # Obsidian conflict files embed the remote device hostname/timestamp in parens.
    # e.g.  "filename (2026-04-05 10-30-22).md"  — timestamp from remote device
    # e.g.  "filename conflict abc123.md"         — git-style conflict marker
    local file="$1"
    local base
    base=$(basename "$file")

    if [[ "$base" =~ ^.+\ \(([0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}-[0-9]{2}-[0-9]{2})\)\..+$ ]]; then
        printf 'obsidian-remote@%s' "${BASH_REMATCH[1]}"
    elif [[ "$base" =~ conflict ]]; then
        printf 'git-obsidian-conflict'
    else
        printf 'unknown'
    fi
}

# ── CONFLICTS check ───────────────────────────────────────────────────────────

run_conflicts_check() {
    local -a lines=()
    local conflict_count=0

    while IFS= read -r file; do
        [[ -n "$file" ]] || continue
        conflict_count=$((conflict_count + 1))

        local zone rel_path device age_days
        if [[ "$file" == "$KB_ROOT"* ]]; then
            zone="KB"
            rel_path="${file#$KB_ROOT/}"
        else
            zone="Vault"
            rel_path="${file#$VAULT_ROOT/}"
        fi
        device=$(conflict_device "$file")
        age_days=$(conflict_age_days "$file")
        local age_str
        if [[ "$age_days" -eq 0 ]]; then
            age_str="today"
        elif [[ "$age_days" -eq 1 ]]; then
            age_str="1 day"
        else
            age_str="${age_days} days"
        fi

        lines+=("| $zone | \`$rel_path\` | $device | $age_str |")
    done < <(find_conflicts)

    {
        echo "## CONFLICTS"
        echo ""
        if [[ "$conflict_count" -eq 0 ]]; then
            echo "- **Status:** PASS — no conflict files found"
        else
            echo "- **Status:** FAIL — $conflict_count conflict file(s) found"
        fi
        echo ""
        if [[ ${#lines[@]} -gt 0 ]]; then
            echo "| Zone | File | Source Device | Age |"
            echo "|------|------|---------------|-----|"
            printf '%s\n' "${lines[@]}"
        fi
        echo ""
    } >> "$REPORT_PATH"
}

# ── REPORT header ─────────────────────────────────────────────────────────────

mkdir -p "$(dirname "$REPORT_PATH")"

{
    echo "# KB Lint Report"
    echo ""
    echo "- **Generated:** $RUN_TS"
    echo "- **Host:** $HOST"
    echo "- **KB Root:** \`$KB_ROOT\`"
    echo "- **Vault:** \`${VAULT_ROOT:-not configured}\`"
    echo ""
} > "$REPORT_PATH"

run_conflicts_check

echo "[kb-lint] Report written to $REPORT_PATH"
