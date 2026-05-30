#!/usr/bin/env bash
# game-kb-compile.sh
# Automated game knowledge compilation pipeline.
# Finds uncompiled raw files (discord-exports + game-notes), uses Gemini 2.5 Flash
# to extract structured wiki articles into wiki/game/.
# Idempotent, lockfile-guarded, graceful on API failures.
set -euo pipefail

export GIT_PAGER=cat
export PAGER=cat

LOCKFILE="/tmp/game-kb-compile.lock"
KB_ROOT="/home/slimy/kb"
RAW_DISCORD="$KB_ROOT/raw/discord-exports"
RAW_NOTES="$KB_ROOT/raw/game-notes"
WIKI_GAME="$KB_ROOT/wiki/game"
LOGS_DIR="$KB_ROOT/logs"
LOG_FILE="$LOGS_DIR/game-compile.log"
HOST=$(hostname -s)
TODAY=$(date +%Y-%m-%d)

mkdir -p "$LOGS_DIR" "$WIKI_GAME"

acquire_lock() {
    exec 200>"$LOCKFILE"
    if ! flock -n 200; then
        echo "[game-kb-compile] $(date -Iseconds) Another instance is running (lockfile: $LOCKFILE). Exiting."
        exit 0
    fi
}

release_lock() {
    flock -u 200 2>/dev/null || true
    rm -f "$LOCKFILE" 2>/dev/null || true
}

trap release_lock EXIT

log() {
    local msg="[$(date -Iseconds)] [game-kb-compile] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

acquire_lock
log "Starting game KB compile on $HOST"

source_env() {
    local env_files=(
        /home/slimy/.env
        /opt/slimy/slimy-monorepo/.env
    )
    for env_file in "${env_files[@]}"; do
        [[ -f "$env_file" ]] || continue
        while IFS='=' read -r key val; do
            [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
            val="${val%\"}"
            val="${val#\"}"
            export "$key=$val"
        done < "$env_file"
    done
}

source_env

GEMINI_KEY="${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}"
if [[ -z "$GEMINI_KEY" ]]; then
    log "ERROR: No GEMINI_API_KEY or GOOGLE_API_KEY found in /home/slimy/.env"
    exit 0
fi

GEMINI_MODEL="gemini-2.5-flash"
GEMINI_URL="https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent"

get_uncompiled_files() {
    local refs_file
    refs_file=$(mktemp)
    trap 'rm -f "$refs_file"' RETURN

    local wiki_file ref_line
    while IFS= read -r wiki_file; do
        [[ -f "$wiki_file" ]] || continue
        while IFS= read -r ref_line; do
            grep -oE 'raw/[A-Za-z0-9._/-]+\.md' <<< "$ref_line" 2>/dev/null || true
        done < <(grep -hE '(sources:|> Sources:)' "$wiki_file" 2>/dev/null || true)
        while IFS= read -r ref_line; do
            grep -oE 'raw/[A-Za-z0-9._/-]+\.md' <<< "$ref_line" 2>/dev/null || true
        done < <(grep -hE '^\s+-' "$wiki_file" 2>/dev/null || true)
    done < <(find "$WIKI_GAME" -type f -name '*.md' ! -name '_index.md' ! -name 'README.md' 2>/dev/null) | sort -u > "$refs_file"

    local raw_file raw_rel
    while IFS= read -r raw_file; do
        [[ -f "$raw_file" ]] || continue
        raw_rel="${raw_file#$KB_ROOT/}"

        if grep -qxF "$raw_rel" "$refs_file" 2>/dev/null; then
            continue
        fi

        local base_rel
        base_rel=$(printf '%s' "$raw_rel" | sed -E 's/-[0-9]{8}T[0-9]+\.(md)$/\.\1/')
        if [[ "$base_rel" != "$raw_rel" ]] && grep -qxF "$base_rel" "$refs_file" 2>/dev/null; then
            continue
        fi

        printf '%s\n' "$raw_file"
    done < <(find "$RAW_DISCORD" "$RAW_NOTES" -type f -name '*.md' ! -name 'README.md' 2>/dev/null | sort)
}

infer_subcategory() {
    local content="$1"
    local lower
    lower=$(printf '%s' "$content" | tr '[:upper:]' '[:lower:]')

    if printf '%s' "$lower" | grep -qE 'relic|biozilla|dung.beetle|goldfish|clam|hamster|mantis'; then
        echo "relics"
    elif printf '%s' "$lower" | grep -qE 'organ|liver|heart|brain|kidney|lung'; then
        echo "organs"
    elif printf '%s' "$lower" | grep -qE 'minion|army|rocket|cabin|skin|species.war'; then
        echo "minions"
    elif printf '%s' "$lower" | grep -qE 'gear|soul|leveling|rift|persia|equipment'; then
        echo "gear"
    elif printf '%s' "$lower" | grep -qE 'glorium|fervor|biome|apostle|faith'; then
        echo "mechanics"
    elif printf '%s' "$lower" | grep -qE 'compass|farm|push|gene.sim|arena|civ'; then
        echo "guides"
    else
        echo "guides"
    fi
}

infer_title() {
    local filepath="$1"
    local basename
    basename=$(basename "$filepath" .md)
    local title
    title=$(printf '%s' "$basename" | sed -E 's/slimyinvertabrates-[0-9-]*//; s/slimyinvertabrates-//; s/^[0-9]+-[0-9]+-//; s/-thread-//; s/-command-tests.*//; s/-[0-9]+T[0-9]+.*//; s/-[0-9]+$//; s/-+/ /g; s/^ +//; s/ +$//')

    if [[ -z "$title" || "$title" == "$basename" ]]; then
        head -5 "$filepath" 2>/dev/null | grep -oP 'title:\s*"\K[^"]+' | head -1 || echo "$basename"
    else
        printf '%s' "$title" | sed -E 's/\b(.)/\u\1/g'
    fi
}

slugify() {
    printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
}

extract_tags() {
    local content="$1"
    local lower
    lower=$(printf '%s' "$content" | tr '[:upper:]' '[:lower:]')

    local -a tags=()
    local words=(relic biozilla dung-beetle goldfish clam hamster mantis compass farm push arena gear soul
        glorium fervor biome apostle organ liver heart brain kidney minion army rocket cabin
        skin species-war rift persia civ enuma elish rush f2p p2w unispark golden-bird
        stamps tech faith gene-sim crit def-ignore crit-damage orange)

    for word in "${words[@]}"; do
        if printf '%s' "$lower" | grep -q "$word"; then
            tags+=("$word")
        fi
    done

    printf '%s\n' "${tags[@]:0:8}" | tr '\n' ',' | sed 's/,$//; s/^/[/; s/$/]/'
}

call_gemini() {
    local raw_content="$1"
    local system_prompt='You are a Super Snail mobile game knowledge extractor. Given raw Discord messages or notes about the game, extract and structure the game knowledge into a clean wiki article. Strip Discord usernames, timestamps, reactions, and chat noise. Preserve player tips, formulas, tier lists, specific numbers/percentages, and game terminology. If users disagree, note both perspectives. Output ONLY the article body in markdown (no frontmatter — that will be added separately). Use ## headers to organize. End with a "## Key Takeaways" section with 3-5 bullet points.'

    local payload
    payload=$(jq -n \
        --arg sys "$system_prompt" \
        --arg content "$raw_content" \
        '{
            system_instruction: { parts: [{ text: $sys }] },
            contents: [{ parts: [{ text: $content }] }],
            generationConfig: {
                temperature: 0.3,
                maxOutputTokens: 4096
            }
        }')

    local response
    local http_code
    response=$(curl -s -w '\n%{http_code}' \
        "$GEMINI_URL?key=$GEMINI_KEY" \
        -H 'Content-Type: application/json' \
        -d "$payload" 2>/dev/null) || {
        log "ERROR: curl request to Gemini API failed"
        return 1
    }

    http_code=$(echo "$response" | tail -1)
    response=$(echo "$response" | sed '$d')

    if [[ "$http_code" != "200" ]]; then
        log "ERROR: Gemini API returned HTTP $http_code: $(echo "$response" | head -c 200)"
        return 1
    fi

    local article_body
    article_body=$(echo "$response" | jq -r '.candidates[0].content.parts[0].text' 2>/dev/null) || {
        log "ERROR: Failed to parse Gemini response JSON"
        return 1
    }

    if [[ -z "$article_body" || "$article_body" == "null" ]]; then
        log "ERROR: Empty article body from Gemini"
        return 1
    fi

    printf '%s' "$article_body"
    return 0
}

update_index() {
    local index_file="$WIKI_GAME/_index.md"
    [[ -f "$index_file" ]] || return 0

    local -a guides=() gear=() relics=() organs=() minions=() mechanics=()

    local f title summary subcat line
    while IFS= read -r f; do
        [[ -f "$f" ]] || continue
        [[ "$(basename "$f")" == "_index.md" || "$(basename "$f")" == "README.md" ]] && continue

        title=$(grep -oP '^title:\s*"\K[^"]+' "$f" 2>/dev/null | head -1 || basename "$f" .md)
        local first_h
        first_h=$(grep -m1 '^#' "$f" 2>/dev/null | sed 's/^#+ *//')
        [[ -n "$first_h" ]] && summary="$first_h" || summary="Game knowledge article"
        summary=$(printf '%s' "$summary" | sed 's/\.$//' | cut -c1-120)
        subcat=$(grep -oP '^subcategory:\s*\K.*' "$f" 2>/dev/null | head -1 || echo "guides")
        [[ -z "$summary" ]] && summary="Game knowledge article"
        line="| [$title]($(basename "$f")) | $summary |"

        case "$subcat" in
            relics)    relics+=("$line") ;;
            organs)    organs+=("$line") ;;
            minions)   minions+=("$line") ;;
            gear)      gear+=("$line") ;;
            mechanics) mechanics+=("$line") ;;
            *)         guides+=("$line") ;;
        esac
    done < <(find "$WIKI_GAME" -type f -name '*.md' ! -name '_index.md' ! -name 'README.md' 2>/dev/null | sort)

    local tmp_index
    tmp_index=$(mktemp)

    {
        echo "# Super Snail Game Knowledge Index"
        echo ""
        echo "> Compiled from SlimyInvertabrates Discord player guides and discussions."
        echo "> Last compiled: $TODAY"
        echo ""
        echo "---"
        echo ""

        if [[ ${#guides[@]} -gt 0 ]]; then
            echo "## Guides"
            echo ""
            echo "| Article | Summary |"
            echo "|---------|---------|"
            printf '%s\n' "${guides[@]}"
            echo ""
        fi

        if [[ ${#gear[@]} -gt 0 ]]; then
            echo "## Gear"
            echo ""
            echo "| Article | Summary |"
            echo "|---------|---------|"
            printf '%s\n' "${gear[@]}"
            echo ""
        fi

        if [[ ${#relics[@]} -gt 0 ]]; then
            echo "## Relics"
            echo ""
            echo "| Article | Summary |"
            echo "|---------|---------|"
            printf '%s\n' "${relics[@]}"
            echo ""
        fi

        if [[ ${#organs[@]} -gt 0 ]]; then
            echo "## Organs"
            echo ""
            echo "| Article | Summary |"
            echo "|---------|---------|"
            printf '%s\n' "${organs[@]}"
            echo ""
        fi

        if [[ ${#minions[@]} -gt 0 ]]; then
            echo "## Minions"
            echo ""
            echo "| Article | Summary |"
            echo "|---------|---------|"
            printf '%s\n' "${minions[@]}"
            echo ""
        fi

        if [[ ${#mechanics[@]} -gt 0 ]]; then
            echo "## Mechanics"
            echo ""
            echo "| Article | Summary |"
            echo "|---------|---------|"
            printf '%s\n' "${mechanics[@]}"
            echo ""
        fi

        echo "---"
        echo ""
        echo "## Source Material"
        echo ""
        echo "Auto-compiled by game-kb-compile.sh on $TODAY."
        echo "Raw sources in \`raw/discord-exports/\` and \`raw/game-notes/\`."
    } > "$tmp_index"

    if cmp -s "$tmp_index" "$index_file"; then
        rm -f "$tmp_index"
        return 0
    fi
    mv "$tmp_index" "$index_file"
}

compile_file() {
    local raw_file="$1"
    local raw_rel="${raw_file#$KB_ROOT/}"
    local basename_raw
    basename_raw=$(basename "$raw_file")

    if [[ "$basename_raw" == *"command-tests"* ]]; then
        log "SKIP (command-tests): $raw_rel"
        return 2
    fi

    log "Processing: $raw_rel"

    local raw_content
    raw_content=$(cat "$raw_file") || {
        log "ERROR: Cannot read $raw_file"
        return 1
    }

    local title subcategory tags slug wiki_file
    title=$(infer_title "$raw_file")
    subcategory=$(infer_subcategory "$raw_content")
    tags=$(extract_tags "$raw_content")
    slug=$(slugify "$title")
    wiki_file="$WIKI_GAME/${slug}.md"

    if [[ -f "$wiki_file" ]]; then
        log "SKIP (already exists): $wiki_file"
        return 2
    fi

    log "Calling Gemini API for: $title"
    local article_body
    article_body=$(call_gemini "$raw_content") || {
        log "ERROR: Gemini API failed for $raw_rel — skipping"
        return 1
    }

    local first_line summary
    first_line=$(echo "$article_body" | grep -v '^$' | head -1 | sed 's/^#* //; s/\.$//')
    [[ -z "$first_line" ]] && first_line="$title"
    summary=$(printf '%s' "$first_line" | cut -c1-120)

    {
        echo "---"
        echo "title: \"$title\""
        echo "category: game"
        echo "subcategory: $subcategory"
        echo "sources:"
        echo "  - \"$raw_rel\""
        echo "created: \"$TODAY\""
        echo "updated: \"$TODAY\""
        echo "tags: $tags"
        echo "---"
        echo ""
        echo "# $title"
        echo ""
        echo "$article_body"
    } > "$wiki_file"

    log "CREATED: $wiki_file"
    return 0
}

mapfile -t uncompiled < <(get_uncompiled_files)
count=${#uncompiled[@]}

log "Found $count uncompiled file(s)"

if [[ "$count" -eq 0 ]]; then
    log "No new files to compile. KB is up-to-date."
    log "Finished."
    exit 0
fi

compiled_count=0

for f in "${uncompiled[@]}"; do
    compile_file "$f" && compiled_count=$((compiled_count + 1)) || true
done

if [[ "$compiled_count" -gt 0 ]]; then
    update_index
    log "Updating _index.md with $compiled_count new article(s)"
fi

cd "$KB_ROOT"
git add -A wiki/game/
if git diff --cached --quiet; then
    log "No git changes to commit."
else
    git commit -m "kb: auto-compile game knowledge $(date +%Y-%m-%d-%H%M)" --quiet
    log "Committed: kb: auto-compile game knowledge $(date +%Y-%m-%d-%H%M)"
fi

log "Finished."
exit 0
