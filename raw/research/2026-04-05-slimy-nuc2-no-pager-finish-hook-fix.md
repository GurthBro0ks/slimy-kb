# NUC2 Finish Hook — No-Pager Fix

**Date:** 2026-04-05
**Host:** slimy-nuc2
**Issue:** git pager blocking wrapper-triggered finish hook automation

## Symptoms
- Codex wrapper runs finish hook
- git commands (log/diff/status/push) open interactive pager
- Automation blocks indefinitely
- Wrapper test file remains untracked
- No new autofile commit appears

## Root Cause
Git's pager (default: `less`) is triggered when:
1. Output is taller than the terminal
2. Git detects a TTY (even a pseudo-TTY from `claude -p` or wrapper subprocess)

Wrapper-triggered runs on NUC2 allocate a pseudo-TTY. When `GIT_PAGER` is not set to `cat`, any `git log`/`git diff`/`git status` with multi-line output opens `less`, which waits for user input.

## Fix Applied

### 1. Global pager disable (export) — added to all 4 scripts
```bash
export GIT_PAGER=cat
export PAGER=cat
```
Files: `slimy-agent-finish.sh`, `kb-project-doc-sync.sh`, `kb-compile-if-needed.sh`, `kb-sync.sh`

### 2. `--no-pager` flag on every git command
```bash
# Before
git -C "$repo" log -1 --format="%s"
git -C "$repo" status --porcelain
git push origin main
git add -A && git commit -m "..." && git push

# After
git --no-pager -C "$repo" log -1 --format="%s"
git --no-pager -C "$repo" status --porcelain
git --no-pager push origin main
git --no-pager add -A && git --no-pager commit -m "..." && git --no-pager push
```

### 3. Child compile guard
- `kb-compile-if-needed.sh` now exports `GIT_PAGER=cat PAGER=cat` before launching child `claude -p`
- Compile prompt uses `git --no-pager` directly

## Scripts Changed
- `tools/slimy-agent-finish.sh` — export GIT_PAGER=cat + all git commands with --no-pager
- `tools/kb-project-doc-sync.sh` — export GIT_PAGER=cat + all git commands with --no-pager
- `tools/kb-compile-if-needed.sh` — export GIT_PAGER=cat + --no-pager on child git calls + compile prompt git commands hardened
- `tools/kb-sync.sh` — export GIT_PAGER=cat + all git commands with --no-pager

## Validation
```bash
bash -n /home/slimy/kb/tools/*.sh  # all pass
```

## Related Prior Fixes
- 2026-04-05: autofinish/autocompile fix — child compile write-through (kb-sync.sh push no longer does pull-first)
- This fix: pager blocking in all automation scripts on NUC2 wrapper-triggered runs
