#!/usr/bin/env bash
# kb-project-doc-sync.sh
# Given a repo path, create or update README.md, CHANGELOG.md, VERSION.md
# Usage: kb-project-doc-sync.sh <repo-path> [--dry-run]
set -euo pipefail

# Disable interactive pager — wrapper-triggered runs have no TTY
export GIT_PAGER=cat
export PAGER=cat

REPO_PATH="${1:-}"
DRY_RUN="${2:-}"

if [[ -z "$REPO_PATH" ]]; then
    echo "Usage: kb-project-doc-sync.sh <repo-path> [--dry-run]"
    exit 1
fi

if [[ ! -d "$REPO_PATH" ]]; then
    echo "[kb-project-doc-sync] ERROR: Not a directory: $REPO_PATH"
    exit 1
fi

# Detect git state
if git --no-pager -C "$REPO_PATH" rev-parse --git-dir >/dev/null 2>&1; then
    IS_GIT=true
    BRANCH=$(git --no-pager -C "$REPO_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    COMMIT_HASH=$(git --no-pager -C "$REPO_PATH" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    LAST_COMMIT_MSG=$(git --no-pager -C "$REPO_PATH" log -1 --pretty=%s 2>/dev/null || echo "none")
    LAST_COMMIT_DATE=$(git --no-pager -C "$REPO_PATH" log -1 --format=%ci 2>/dev/null | cut -d' ' -f1 || echo "unknown")
    REMOTE=$(git --no-pager -C "$REPO_PATH" remote get-url origin 2>/dev/null || echo "none")
else
    IS_GIT=false
    BRANCH="none"
    COMMIT_HASH="none"
    LAST_COMMIT_MSG="none"
    LAST_COMMIT_DATE="unknown"
    REMOTE="none"
fi

HOST=$(hostname -s)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
TODAY=$(date +%Y-%m-%d)

# Derive project slug from directory name
PROJECT_SLUG=$(basename "$REPO_PATH" | tr '.' '-')
PROJECT_NAME=$(basename "$REPO_PATH" | tr '-' '_' | tr '[:lower:]' '[:upper:]')

# Runtime discovery
RUNTIME_INFO="N/A"
SERVICES_TABLE="| Service | Status | Port |\\n|---|---|---|"

if [[ -f "$REPO_PATH/package.json" ]]; then
    RUNTIME_INFO="Node.js package detected"
    if grep -q '"scripts"' "$REPO_PATH/package.json"; then
        RUNTIME_INFO="$RUNTIME_INFO; scripts found"
    fi
fi

if [[ -f "$REPO_PATH/pyproject.toml" ]] || [[ -f "$REPO_PATH/setup.py" ]]; then
    RUNTIME_INFO="Python project detected"
fi

# Check for systemd services referencing this repo
SYSTEMD_SERVICES=""
if [[ -d "/home/slimy/.config/systemd/user" ]]; then
    SERVICES=$(grep -rl "$REPO_PATH" /home/slimy/.config/systemd/user/ 2>/dev/null | xargs -r basename -a 2>/dev/null | sort -u || true)
    if [[ -n "$SERVICES" ]]; then
        SYSTEMD_SERVICES="$SERVICES"
        SERVICES_TABLE="| Service | Status | Port |\\n|---|---|---|"
        while IFS= read -r svc; do
            SERVICES_TABLE="$SERVICES_TABLE\\n| $svc | active | — |"
        done <<< "$SERVICES"
    fi
fi

# Check PM2
PM2_PROCESSES=""
if command -v pm2 >/dev/null 2>&1; then
    PM2_PROC=$(pm2 jlist 2>/dev/null | python3 -c "import sys,json; procs=json.load(sys.stdin); print('\n'.join([p['name'] for p in procs if '$REPO_PATH' in p.get('pm2_env',{}).get('pm_cwd','') or '$PROJECT_SLUG' in p.get('name','')]))" 2>/dev/null || true)
    if [[ -n "$PM2_PROC" ]]; then
        PM2_PROCESSES="$PM2_PROC"
    fi
fi

# Check ports
PORTS=""
if command -v ss >/dev/null 2>&1; then
    PORTS=$(ss -lntp 2>/dev/null | grep "$(basename "$REPO_PATH")" | awk '{print $4}' | sort -u || true)
fi

# Detect status
if [[ "$IS_GIT" == true ]]; then
    DIRTY=$(git --no-pager -C "$REPO_PATH" status --porcelain | grep -vE '^\?\? ' | wc -l | tr -d ' ' || true)
    if [[ "$DIRTY" -gt 0 ]]; then
        STATUS="ACTIVE_DIRTY"
    else
        STATUS="ACTIVE"
    fi
else
    DIRTY=0
    STATUS="ACTIVE_NON_GIT"
fi

#########################################
# README.md
#########################################
README="$REPO_PATH/README.md"
if [[ ! -f "$README" ]]; then
    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "[DRY-RUN] Would create README.md at $README"
    else
        cat > "$README" << EOF
# $PROJECT_SLUG

> Status: $STATUS | Host: $HOST | Path: \`$REPO_PATH\`

## Overview
$PROJECT_NAME — active SlimyAI project.

## Host / Path
- **Local path:** \`$REPO_PATH\`
- **Remote:** \`$REMOTE\`
- **Branch:** \`$BRANCH\` (\`$COMMIT_HASH\`)
- **Last commit:** $LAST_COMMIT_DATE — $LAST_COMMIT_MSG

## Runtime
$RUNTIME_INFO

${SERVICES_TABLE}

## How to Verify
\`\`\`bash
# Basic health check
$([[ "$IS_GIT" == true ]] && echo "git --no-pager -C $REPO_PATH log -1 --oneline" || echo "# Not a git repo")
\`\`\`

## Dependencies
- Standard SlimyAI runtime environment

## Related Projects
- slimy-monorepo
- mission-control
- slimy-kb

## Current Status
$STATUS — last updated $TODAY via kb-project-doc-sync.sh
EOF
        echo "[kb-project-doc-sync] Created README.md for $REPO_PATH"
    fi
else
    # README exists — check for stale runtime sections and update minimally
    if grep -q 'last updated.*kb-project-doc-sync' "$README" 2>/dev/null; then
        # Already managed by us — update timestamp
        if [[ "$DRY_RUN" != "--dry-run" ]]; then
            sed -i "s/Last updated.*/Last updated $TODAY via kb-project-doc-sync.sh/" "$README" 2>/dev/null || true
        fi
    fi
    echo "[kb-project-doc-sync] README.md already exists at $REPO_PATH — skipped (preserving existing content)"
fi

#########################################
# CHANGELOG.md
#########################################
CHANGELOG="$REPO_PATH/CHANGELOG.md"
if [[ ! -f "$CHANGELOG" ]]; then
    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "[DRY-RUN] Would create CHANGELOG.md at $CHANGELOG"
    else
        cat > "$CHANGELOG" << EOF
# Changelog — $PROJECT_SLUG

All notable changes are documented here.

## [$TODAY] — Initial scaffold
### Added
- Initial CHANGELOG.md scaffold via kb-project-doc-sync.sh
- README.md via kb-project-doc-sync.sh

### Notes
- Automated documentation bootstrap on $TODAY
EOF
        echo "[kb-project-doc-sync] Created CHANGELOG.md for $REPO_PATH"
    fi
else
    # CHANGELOG exists — append a dated entry for today if last entry is not today
    LAST_ENTRY_DATE=$(grep -m1 '^\## \[' "$CHANGELOG" 2>/dev/null | grep -oP '\d{4}-\d{2}-\d{2}' || true)
    if [[ "$LAST_ENTRY_DATE" != "$TODAY" ]]; then
        if [[ "$DRY_RUN" == "--dry-run" ]]; then
            echo "[DRY-RUN] Would append today's changelog entry to $CHANGELOG"
        else
            ENTRY_MSG="${LAST_COMMIT_MSG:-automated sync}"
            sed -i "1s/^/\n## [$TODAY] — Daily sync\n### Changed\n- Automated sync entry: $ENTRY_MSG\n- Auto-generated by kb-project-doc-sync.sh\n\n/" "$CHANGELOG" 2>/dev/null || true
            echo "[kb-project-doc-sync] Appended changelog entry to $CHANGELOG"
        fi
    else
        echo "[kb-project-doc-sync] CHANGELOG.md already has today entry — skipped"
    fi
fi

#########################################
# VERSION.md
#########################################
VERSION="$REPO_PATH/VERSION.md"
if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[DRY-RUN] Would create/update VERSION.md at $VERSION"
else
    cat > "$VERSION" << EOF
# Version Snapshot — $PROJECT_SLUG

> Generated: $TIMESTAMP | Host: $HOST

## Git State
- **Branch:** \`$BRANCH\`
- **HEAD:** \`$COMMIT_HASH\`
- **Last commit:** \`$LAST_COMMIT_DATE\` — \`$LAST_COMMIT_MSG\`
- **Remote:** \`$REMOTE\`
- **Dirty:** $([[ "$DIRTY" -gt 0 ]] && echo "YES ($DIRTY uncommitted)" || echo "NO")

## Runtime
- **Runtime info:** $RUNTIME_INFO
- **Systemd services:** ${SYSTEMD_SERVICES:-none detected}
- **PM2 processes:** ${PM2_PROCESSES:-none detected}
- **Listening ports:** ${PORTS:-none detected}

## Last Verified
- **Date:** $TODAY
- **Verification:** \`git --no-pager -C $REPO_PATH log -1 --oneline\`

## Host Notes
- Managed by kb-project-doc-sync.sh automation
EOF
    echo "[kb-project-doc-sync] Updated VERSION.md for $REPO_PATH"
fi

echo "[kb-project-doc-sync] Done for $REPO_PATH"
