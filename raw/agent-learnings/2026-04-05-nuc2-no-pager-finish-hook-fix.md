---
name: 2026-04-05-nuc2-no-pager-finish-hook-fix
description: Fix NUC2 autofinish automation pager issue
type: agent-learning
---

# NUC2 Finish Hook — No-Pager Fix

## Problem
When the Codex wrapper triggered the finish hook on NUC2, git commands would open an interactive pager, blocking the automation. This caused:
- Wrapper test files to remain untracked
- No autofile commits appearing

## Root Cause
Git's pager is triggered when:
1. Output exceeds terminal height
2. Git detects a TTY

Wrapper-triggered runs via `claude -p` or wrapper scripts can still allocate a pseudo-TTY, causing `git log`, `git diff`, `git status`, and `git push` to hang waiting for pager input.

## Fix Applied

### Added to all KB automation scripts:
```bash
export GIT_PAGER=cat
export PAGER=cat
```

### Replaced all git commands with `--no-pager`:
```bash
# Before
git -C "$repo" log ...
git -C "$repo" status --porcelain
git push origin main
git add -A
git commit -m "..."

# After
git --no-pager -C "$repo" log ...
git --no-pager -C "$repo" status --porcelain
git --no-pager push origin main
git --no-pager add -A
git --no-pager commit -m "..."
```

### Scripts Fixed
- `/home/slimy/kb/tools/slimy-agent-finish.sh`
- `/home/slimy/kb/tools/kb-project-doc-sync.sh`
- `/home/slimy/kb/tools/kb-compile-if-needed.sh`
- `/home/slimy/kb/tools/kb-sync.sh`

### Child Compile Guard
- `kb-compile-if-needed.sh` now exports `GIT_PAGER=cat PAGER=cat` before launching the child `claude -p` process
- Compile prompt itself uses `git --no-pager` for all operations

## Why It Matters
The autofinish pipeline is the backbone of KB write-through: every session creates raw artifacts → finish hook commits → child compile compiles wiki → wiki changes committed and pushed. If any step hangs on a pager, the entire chain breaks silently.

## Validation
```bash
bash -n /home/slimy/kb/tools/*.sh  # all must pass
```
