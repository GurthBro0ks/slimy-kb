# KB Autofinish Autocompile Fix
> Category: troubleshooting
> Sources: raw/research/2026-04-05-slimy-nuc2-autofinish-autocompile-fix.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

Fix for the KB write-through automation where `slimy-agent-finish.sh` left raw files uncommitted and `kb-compile-if-needed.sh` only wrote prompt files without triggering actual wiki compilation.

## Problem 1: KB Files Left Untracked

**Symptom:** Raw files created by finish hook (e.g., `raw/agent-learnings/`) existed on disk but were never committed.

**Root Cause:** `slimy-agent-finish.sh` called `kb-sync.sh push` which runs `git pull --rebase --autostash` first. The `|| true` on `git commit` masked all failures silently.

**Fix:** `slimy-agent-finish.sh` now uses direct `git add -A` + `git commit` without pull-first. Push is separate with error capture; failures tracked in `ALERT_MSG` for Discord webhook.

## Problem 2: Compile Stopped at Prompt File

**Symptom:** `output/prompts/compile-prompt-*.md` files accumulated without wiki updates being generated.

**Root Cause:** `kb-compile-if-needed.sh` only called `wiki prompt-compile` which writes a prompt file; the actual compile run was never triggered automatically.

**Fix:** `kb-compile-if-needed.sh` now launches a child `claude -p` compile with `SLIMY_KB_CHILD_COMPILE=1` guard. Child compile updates wiki, commits, and pushes directly (no `kb-sync.sh` pull-first).

## Recursion Guards

| Guard | Purpose |
|---|---|
| `SLIMY_AUTOFINISH_ACTIVE=1` | Set by `slimy-agent-finish.sh` before launching child processes. Child wrapper sees it and exits early. |
| `SLIMY_KB_CHILD_COMPILE=1` | Set by `kb-compile-if-needed.sh` before launching `claude -p`. Prevents nested child compile if script is re-invoked. |

## Write-Through Flow (2026-04-05)

```
finish hook runs
  → slimy-agent-finish.sh creates raw artifacts
  → commits KB with direct git (no pull-first)
  → kb-compile-if-needed.sh detects uncompiled raw
  → launches child claude -p compile
  → child updates wiki articles, commits, pushes
  → parent ALERTS webhook fires on child failure
```

## Scripts Changed

| File | Change |
|---|---|
| `tools/slimy-agent-finish.sh` | KB commit uses direct git (no pull-first), improved error capture, push failure tracking |
| `tools/kb-compile-if-needed.sh` | Added child compile via `claude -p`, SLIMY_KB_CHILD_COMPILE guard, ALERTS webhook on failure |

## Validation (2026-04-05)

```
kb: autofile claude 20260405-150433 — 9 files committed+pushed
kb: auto-sync from slimy-nuc2 2026-04-05-1508 — child compile, 3 wiki files updated
```

Both commits visible on GitHub (main branch).

## Deferred Compile Candidates

The following compile candidates have been reviewed and deferred (no wiki-worthy content):

**Empty agent session summaries** — Auto-generated finish-hook summaries with no actual summary, notable changes, or next steps:
- `raw/agent-learnings/2026-04-05-nuc1-test.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-claude-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-codex-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-final-test-claude.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-final-test-codex.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-test-claude.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-claude-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-codex-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-wrapper-final-test-claude.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-wrapper-final-test-codex.md`

**Obsidian test notes** — Human test artifacts with no operational content:
- `raw/research/obsidian-inbox-notes-test-note-for-commands.md`
- `raw/research/obsidian-inbox-notes-test-not-for-commands.md`

These will be re-evaluated if substantive content is added to the source files.

## See Also
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md)
- [Slimy KB](../projects/slimy-kb.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
