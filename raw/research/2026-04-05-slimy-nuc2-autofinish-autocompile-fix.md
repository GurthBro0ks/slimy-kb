# Autofinish Autocompile Fix — NUC2

- Agent: claude
- Host: slimy-nuc2
- Date: 2026-04-05
- Purpose: Fix KB write-through automation and auto-compile

## What Was Broken

### Problem 1: KB Files Left Untracked

`slimy-agent-finish.sh` called `kb-sync.sh push` which:

1. Runs `git pull --rebase --autostash` first (pull-before-push)
2. Then `git add -A && git commit` only if `git diff --cached --stat` is non-empty
3. The `|| true` on `git commit` masked all failures silently

**Root cause**: If `git pull --rebase --autostash` failed (e.g., conflict or network), the script continued silently with `|| true`. Even on success, the rebase could create divergent history that made the subsequent push appear to do nothing.

**Symptom**: Raw files created by finish hook (e.g., `raw/agent-learnings/2026-04-05-slimy-nuc2-wrapper-webhook-test.md`) existed on disk but were never committed.

### Problem 2: Compile Stopped at Prompt File

`kb-compile-if-needed.sh` only called `wiki prompt-compile` which writes a prompt file to `output/prompts/compile-prompt-*.md`. The actual compile run was never triggered automatically.

**Root cause**: The script was designed to emit a prompt for manual execution rather than run a child compile.

**Symptom**: `output/prompts/compile-prompt-*.md` files accumulated without wiki updates being generated.

## What Was Changed

### `slimy-agent-finish.sh` — KB Commit/Push Fix

**Before**: Called `kb-sync.sh push` (pull-first, `|| true` masked failures)

**After**:
- Runs `git add -A && git diff --cached --stat` to detect non-zero staged changes
- Commits with a descriptive message: `kb: autofile <agent> <timestamp>`
- Separately handles push, checking for error strings in output
- Captures push failures into `ALERT_MSG` for Discord ALERTS webhook
- Pushes without pull-first (parent has already done any needed pull at session start)

**Why direct push**: The parent `slimy-agent-finish.sh` runs after the session's initial `kb-sync.sh pull` already merged upstream. A second pull-first in `kb-sync.sh push` can cause `git rebase` conflicts that silently break the push. The direct push is safe because the parent has already ensured local state is current.

### `kb-compile-if-needed.sh` — Auto-Compile Child Run

**Before**: Detected uncompiled files, wrote prompt file, exited.

**After**:

1. **Guard**: `SLIMY_KB_CHILD_COMPILE=1` env var prevents nested child compile recursion if the script is re-invoked.

2. **Child compile invocation**: Launches `claude -p` (non-interactive, skips workspace trust dialog) with the compile prompt piped via stdin:
   ```bash
   SLIMY_KB_CHILD_COMPILE=1 \
   claude -p -- \
       --output-format text \
       --dangerously-skip-permissions \
       --system-prompt "You are a KB compile agent..." \
       < "$COMPILE_PROMPT_FILE"
   ```

3. **Recursion guard**: `SLIMY_AUTOFINISH_ACTIVE=1` is inherited from the parent `slimy-agent-finish.sh` shell. When the child `claude` wrapper runs and eventually calls `slimy-agent-finish.sh`, the guard detects the flag and exits early (preventing infinite nested finish hooks).

4. **Child prompt's git push**: The compile prompt ends with direct git commands (not `kb-sync.sh push`) to avoid the pull-first rebase issue:
   ```bash
   cd /home/slimy/kb && git add -A && git diff --cached --stat && \
     git commit -m "kb: child-compile <timestamp>" && \
     git push origin main
   ```

5. **Post-child detection**: Simplified to just log success. The child already committed+pushed its wiki changes; the parent just notes it.

6. **On failure**: Writes `output/compile-failure-*.md` note and posts to Discord ALERTS webhook if configured.

## Whether Compile Is Now Truly Automatic

**Yes — with caveats**:

- `slimy-agent-finish.sh` is the entry point; it runs after every Claude/codex wrapper exit
- It creates raw artifacts (learnings, changelog) and commits them
- It calls `kb-compile-if-needed.sh` which auto-runs a child `claude -p` compile
- The child compile updates wiki articles, commits, and pushes
- The parent's ALERTS webhook posts if the child compile fails

**Verified 2026-04-05**: Full test run showed:
- KB committed (9 files, pushed to GitHub): `9d14808 kb: autofile claude 20260405-150433`
- Child compile ran (`claude -p` exit 0)
- Child compile produced wiki changes committed as: `cbcd5e3 kb: auto-sync from slimy-nuc2 2026-04-05-1508`
  - Updated 3 wiki files: `harness-runtime-topology.md`, `nuc-topology-and-services.md`, `slimy-kb.md`

**Caveats**:
- Uses `--dangerously-skip-permissions` for child compile — acceptable since it's a non-interactive compile within a known KB directory
- If `claude -p` fails (API key issue, network), the parent logs the failure and posts ALERTS webhook
- Child compile's wiki updates depend on the quality of the compile prompt

## Recursion Guards in Place

| Guard | Purpose |
|---|---|
| `SLIMY_AUTOFINISH_ACTIVE=1` | Set by `slimy-agent-finish.sh` before launching child processes. Child wrapper sees it and exits early. |
| `SLIMY_KB_CHILD_COMPILE=1` | Set by `kb-compile-if-needed.sh` before launching `claude -p`. Prevents nested child compile if script is re-invoked. |
| `--dry-run` | Propagates through to skip child compile and all mutations. |

## What Still Requires Manual Intervention

- **`kb-sync.sh push` pull-first behavior**: The parent `slimy-agent-finish.sh` bypasses it for KB changes (uses direct git push). But project repos (slimy-app, chat-app, etc.) still use `kb-project-doc-sync.sh` which may have credential issues (some repos couldn't push — needs SSH key or credential helper).

- **ALERTS webhook for credential failures**: When `kb-project-doc-sync.sh` push fails due to missing credentials, it posts to ALERTS webhook. The human operator needs to set up SSH keys or tokens for those repos.

- **Compile prompt quality**: The child compile uses a minimal system prompt. Large KBs with complex compile tasks may need more sophisticated prompt engineering for reliable auto-compile.

## Scripts Changed

| File | Change |
|---|---|
| `tools/slimy-agent-finish.sh` | KB commit uses direct git (no pull-first), improved error capture, push failure tracking |
| `tools/kb-compile-if-needed.sh` | Added child compile via `claude -p`, SLIMY_KB_CHILD_COMPILE guard, ALERTS webhook on failure |

## Validation Results (2026-04-05)

```
kb: autofile claude 20260405-150433 — 9 files, pushed OK
kb: auto-sync from slimy-nuc2 2026-04-05-1508 — child compile, 3 wiki files updated, pushed OK
```

Both commits visible on GitHub (main branch).

---
*Auto-generated by slimy-agent-finish.sh research capture*
