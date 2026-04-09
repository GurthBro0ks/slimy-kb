#!/usr/bin/env bash
# kb-lint.sh — Knowledge Base lint checker
# Scans KB and vault for structural issues and generates a lint report.
# Also generates _orphans.md and _weak-links.md in the wiki root.
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

# ── LINK ANALYSIS ─────────────────────────────────────────────────────────────

# Build a map: TARGET_FILE → list of SOURCE_FILES that link to it
build_link_map() {
    local wiki_dir="$1"
    # Associative array: target_rel_path → count of inbound links
    # We use awk to parse markdown links: [text](path) where path ends in .md
    #
    # Strategy: for each wiki .md file, extract all [text](target.md) links
    # and record that target as being linked-to by this source file.

    # Get all wiki markdown files (non-index)
    local -a wiki_files
    mapfile -t wiki_files < <(find "$wiki_dir" -type f -name '*.md' ! -name '_*.md' 2>/dev/null)

    local src_file target rel_target
    for src_file in "${wiki_files[@]}"; do
        # Extract all .md links from this file
        grep -ohE '\[([^]]+)\]\(([^)]+\.md)\)' "$src_file" 2>/dev/null | while read -r match; do
            # Parse [text](path.md)
            target=$(echo "$match" | sed -E 's/\[([^]]+)\]\(([^)]+)\)/\2/')
            # Make target relative to wiki root
            if [[ "$target" == /* ]]; then
                rel_target="${target#$wiki_dir/}"
            elif [[ "$target" != /* ]]; then
                # relative link — resolve from src_file's directory
                rel_target=$(realpath --relative-to="$wiki_dir" "$(dirname "$src_file")/$target" 2>/dev/null || echo "$target")
            fi
            # Normalize: remove leading ./
            rel_target=${rel_target#./}
            # Store in temp file for processing
            [[ -n "$rel_target" ]] && echo "$rel_target"
        done
    done | sort | uniq -c | sort -rn
}

# Find orphaned pages (no inbound links from other non-index wiki pages)
run_link_analysis() {
    local orphans_file="$KB_WIKI/_orphans.md"
    local weaklinks_file="$KB_WIKI/_weak-links.md"

    echo "[kb-lint] Running link analysis..."

    # Get all non-index wiki pages
    local all_pages_str
    all_pages_str=$(find "$KB_WIKI" -type f -name '*.md' ! -name '_*.md' 2>/dev/null | sort)
    local -a all_pages=()
    while IFS= read -r p; do [[ -n "$p" ]] && all_pages+=("$p"); done <<< "$all_pages_str"

    # Associative array for inbound link counts
    local -A inbound_count
    local page rel_path

    # Initialize all pages with 0 inbound links
    for page in "${all_pages[@]}"; do
        rel_path=${page#$KB_WIKI/}
        inbound_count[$rel_path]=0
    done

    # For each page, find all .md links it contains (outbound) and increment target's inbound count
    # Use temp file to avoid subshell array capture issue
    local link_temp
    link_temp=$(mktemp)
    > "$link_temp"
    for page in "${all_pages[@]}"; do
        local src_dir
        src_dir=$(dirname "$page")

        # Extract all markdown links to other .md files (suppress errors for missing files)
        # Use .+? non-greedy to avoid backtracking that corrupts links with many ] chars
        local match target resolved
        while IFS= read -r match; do
            target=$(echo "$match" | sed -E 's/\[.+?\]\(([^)]+)\)/\1/')

            # Resolve relative links
            if [[ "$target" == /* ]]; then
                # Absolute path within wiki
                target="${target#$KB_WIKI}"
                target=${target#/}
            else
                # Relative link
                resolved=$(realpath --relative-to="$KB_WIKI" "$src_dir/$target" 2>/dev/null || echo "$target")
                target=${resolved#./}
            fi

            [[ -n "$target" ]] && echo "$target" >> "$link_temp"
        done < <(grep -ohE '\[.+?\]\([^)]+\.md\)' "$page" 2>/dev/null || true)
    done

    # Now process the collected links to update inbound counts
    while IFS= read -r target; do
        [[ -n "${inbound_count[$target]:-}" ]] && inbound_count[$target]=$((inbound_count[$target] + 1))
    done < "$link_temp"

    rm -f "$link_temp"

    # Categorize pages
    local -a orphan_pages=()
    local -a weak_pages=()
    local -a normal_pages=()

    for page in "${all_pages[@]}"; do
        rel_path=${page#$KB_WIKI/}
        local count
        count=${inbound_count[$rel_path]:-0}
        if [[ "$count" -eq 0 ]]; then
            orphan_pages+=("$rel_path")
        elif [[ "$count" -le 1 ]]; then
            weak_pages+=("$rel_path (${count} inbound link)")
        else
            normal_pages+=("$rel_path")
        fi
    done

    # Write _orphans.md
    {
        echo "# Orphaned Pages"
        echo ""
        echo "> Pages with zero inbound links from other non-index wiki pages."
        echo "> Generated: $RUN_TS by kb-lint.sh"
        echo ""
        echo "**Total orphans: ${#orphan_pages[@]}**"
        echo ""
        if [[ ${#orphan_pages[@]} -eq 0 ]]; then
            echo "- No orphaned pages found."
        else
            echo "## Likely Parent Pages"
            echo ""
            for orphan in "${orphan_pages[@]}"; do
                echo "- \`$orphan\`"
            done
        fi
        echo ""
        echo "## All Orphaned Pages"
        if [[ ${#orphan_pages[@]} -eq 0 ]]; then
            echo "- (none)"
        else
            for orphan in "${orphan_pages[@]}"; do
                echo "- \`$orphan\`"
            done
        fi
    } > "$orphans_file"

    # Write _weak-links.md
    {
        echo "# Low-Connectivity Pages"
        echo ""
        echo "> Pages with only 1 inbound link (weak connectivity). These may need more cross-linking."
        echo "> Generated: $RUN_TS by kb-lint.sh"
        echo ""
        echo "**Total weak links: ${#weak_pages[@]}**"
        echo ""
        if [[ ${#weak_pages[@]} -eq 0 ]]; then
            echo "- No weak links found."
        else
            for wp in "${weak_pages[@]}"; do
                echo "- \`$wp\`"
            done
        fi
        echo ""
        echo "## Connectivity Summary"
        echo ""
        echo "| Connectivity | Count |"
        echo "|--------------|-------|"
        echo "| 0 inbound (orphan) | ${#orphan_pages[@]} |"
        echo "| 1 inbound (weak) | ${#weak_pages[@]} |"
        echo "| 2+ inbound (normal) | ${#normal_pages[@]} |"
    } > "$weaklinks_file"

    echo "[kb-lint] Link analysis complete: ${#orphan_pages[@]} orphans, ${#weak_pages[@]} weak links"
    echo "[kb-lint] Wrote $orphans_file and $weaklinks_file"
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
run_link_analysis

echo "[kb-lint] Report written to $REPORT_PATH"