# KB Autofinish Autocompile Fix
> Category: troubleshooting
> Sources: raw/research/2026-04-05-slimy-nuc2-autofinish-autocompile-fix.md, raw/research/2026-04-05-slimy-nuc2-autofinish-parity-check.md, raw/agent-learnings/2026-04-05-nuc2-no-pager-finish-hook-fix.md, raw/research/2026-04-05-slimy-nuc2-no-pager-finish-hook-fix.md, raw/research/2026-04-05-slimy-nuc1-wrapper-recursion-fix.md
> Created: 2026-04-05
> Updated: 2026-04-11
> Status: reviewed
> Note: Re-verified 2026-04-11 (compile 20260411-230740): all priority batch files already sourced or deferred. No new wiki content required. Status: reviewed.

<!-- KB METADATA
> Last edited: 2026-04-21 00:27 UTC (git)
> Version: r39 / 566450c
KB METADATA -->

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

## Problem 3: Git Pager Blocking Wrapper-Triggered Finish Hook

**Symptom:** When Codex or Claude wrappers triggered the finish hook, git commands (`git log`, `git diff`, `git status`, `git push`) would open an interactive pager, blocking automation indefinitely. Wrapper test files remained untracked; no autofile commits appeared.

**Root Cause:** Git's pager (`less` by default) is triggered when:
1. Output exceeds terminal height, or
2. Git detects a TTY (even a pseudo-TTY allocated by `claude -p` or wrapper subprocesses)

Wrapper-triggered runs on both NUCs allocate a pseudo-TTY. Without `GIT_PAGER=cat`, any multi-line git command hangs waiting for pager input.

**Fix Applied — Two Layers:**

### 1. Global pager disable (export) — added to all 4 automation scripts
```bash
export GIT_PAGER=cat
export PAGER=cat
```
Applied to: `slimy-agent-finish.sh`, `kb-project-doc-sync.sh`, `kb-compile-if-needed.sh`, `kb-sync.sh`

### 2. `--no-pager` flag on every git command
```bash
# Before
git -C "$repo" log -1 --format="%s"
git -C "$repo" status --porcelain
git push origin main

# After
git --no-pager -C "$repo" log -1 --format="%s"
git --no-pager -C "$repo" status --porcelain
git --no-pager push origin main
```

### Child Compile Guard
`kb-compile-if-needed.sh` exports `GIT_PAGER=cat PAGER=cat` before launching child `claude -p`. The compile prompt itself also uses `git --no-pager` directly for all operations.

**Scripts Changed:**

| File | Changes |
|---|---|
| `tools/slimy-agent-finish.sh` | `GIT_PAGER=cat` + `PAGER=cat` + all git commands with `--no-pager` |
| `tools/kb-project-doc-sync.sh` | `GIT_PAGER=cat` + `PAGER=cat` + all git commands with `--no-pager` |
| `tools/kb-compile-if-needed.sh` | `GIT_PAGER=cat` + `PAGER=cat` + `--no-pager` on child git calls + compile prompt hardened |
| `tools/kb-sync.sh` | `GIT_PAGER=cat` + `PAGER=cat` + all git commands with `--no-pager` |

**Validation:**
```bash
bash -n /home/slimy/kb/tools/*.sh  # all must pass
```

## NUC2 Autofinish Parity Check — End-to-End Validation

**Date:** 2026-04-05 | **Host:** slimy-nuc2

Validated that the complete write-through chain (autofile → auto-compile → wiki commit → push) operates correctly for both Claude and Codex wrapper exits, with proper recursion guards.

### Wrapper Paths

| Agent | Wrapper | Real Binary |
|-------|---------|-------------|
| Claude | `/home/slimy/.local/bin/claude` | `/home/slimy/.local/bin/claude-bin` |
| Codex | `/home/slimy/.npm-global/bin/codex` | `/home/slimy/.npm-global/bin/codex-bin.js` |

### Claude Wrapper Chain Results

| Stage | Expected | Actual |
|-------|----------|--------|
| Autofile commit triggered | YES | YES — `90415c0 kb: autofile claude 20260405-163411` |
| Wiki auto-compile triggered | YES | YES — child compile ran, `8fa2ecc kb: compile - obsidian vault automation...` |
| Wiki commit after compile | YES | YES — `18dbf31 kb: compile - nuc1 wrapper recursion article...` |
| KB pushed to origin | YES | YES |
| Recursion guard active | Blocks child compile loops | YES — `SLIMY_AUTOFINISH_ACTIVE=1`, `SLIMY_KB_CHILD_COMPILE=1` |

### Codex Wrapper Chain Results

| Stage | Expected | Actual |
|-------|----------|--------|
| Wrapper exits gracefully | YES | YES |
| Finish hook runs | YES | YES — `slimy-agent-finish.sh --agent codex` executed |
| Autofile commit triggered | YES | YES — `db26f18 kb: autofile codex 20260405-165301` |
| Wiki auto-compile triggered | YES | YES — child compile ran |
| Recursion guard active | YES | YES |
| Codex `--yolo` preserved | YES | YES — wrapper hardcodes `--yolo` before passing args |

### Observed Child Compile Chain
```
90415c0  autofile (includes new raw file)
   → kb-compile-if-needed.sh detects 11 uncompiled files
   → launches child claude -p with SLIMY_KB_CHILD_COMPILE=1
   → child updates wiki and pushes 8fa2ecc
   → parent clean
```

### Git Log Evidence (NUC2)
```
18dbf31 kb: compile - nuc1 wrapper recursion article + defer empty summaries  ← Codex finish + child compile
db26f18 kb: autofile codex 20260405-165301                                      ← Codex finish autofile
8fa2ecc kb: compile - obsidian vault automation + NUC1 anomalies articles      ← Claude finish + child compile
2b87f1f kb: autofile claude 20260405-163603                                     ← Claude finish autofile
90415c0 kb: autofile claude 20260405-163411                                     ← Claude session autofile
```

### Remaining NUC2 Differences
1. **Codex binary missing** — `@openai/codex-linux-x64` dependency not installed. Wrapper is correctly wired; automation is fully operational.
2. **Orphaned compile prompt files** — `output/prompts/auto-compile-prompt-*.md` written by parent, cleaned by child. Normal if parent process is killed.
3. **No `--yolo` flag visibility** — wrapper adds `--yolo` silently; not visible in logs.

### Conclusion
**NUC2 write-through automation is fully operational and matches NUC1 behavior.**

## Deferred Compile Candidates

The following compile candidates have been reviewed and deferred (no wiki-worthy content):

**Empty agent session summaries** — Auto-generated finish-hook summaries with no actual summary, notable changes, or next steps:
- `raw/agent-learnings/2026-04-05-nuc1-test.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-claude-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-codex-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-final-test-claude.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-wrapper-final-test-codex.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-claude-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-codex-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-test-validation-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-wrapper-final-test-claude.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc2-wrapper-final-test-codex.md`
- `raw/agent-learnings/2026-04-08-slimy-nuc1-claude-summary.md` — no summary, no repos, no changes
- `raw/agent-learnings/2026-04-08-slimy-nuc1-codex-summary.md` — no summary, no repos, no changes

**Thin/placeholder files** — No operational content:
- `raw/agent-learnings/2026-04-05-nuc2-wrapper-final-test-codex-repair.md` — wrapper test metadata only
- `raw/agent-learnings/2026-04-05-slimy-nuc1-repo-remote-test.md` — "Test entry — safe to delete"
- `raw/agent-learnings/test-1775424961.md` — empty 1-line file

**Obsidian test notes** — Human test artifacts with no operational content:
- `raw/research/obsidian-inbox-notes-test-note-for-commands.md`
- `raw/research/obsidian-inbox-notes-test-not-for-commands.md`

**Thin HTTPS guard test summaries** — Empty auto-generated session summaries from test agents:
- `raw/agent-learnings/2026-04-05-slimy-nuc1-test-https-guard-summary.md`
- `raw/agent-learnings/2026-04-05-slimy-nuc1-test-nuc1-ssh-validation-summary.md`

**2026-04-08 session summaries** — Empty auto-generated summaries with no actual summary, notable changes, or next steps (same pattern as earlier empty summaries):
- `raw/agent-learnings/2026-04-08-slimy-nuc1-claude-summary.md`
- `raw/agent-learnings/2026-04-08-slimy-nuc2-codex-summary.md`

**2026-04-09 session summaries** — Same pattern: empty auto-generated finish-hook summaries with no operational content:
- `raw/agent-learnings/2026-04-09-slimy-nuc1-claude-summary.md`

**2026-04-09 changelog** — Same pattern as 2026-04-08: auto-generated by finish hook, Agent Summary section empty ("—"), repos touched are all auto-sync doc commits with no notable changes:
- `raw/changelogs/2026-04-09-slimy-nuc1-project-changelog.md`

**2026-04-08 changelog** — Thin changelog with no substantive changes:
- `raw/changelogs/2026-04-08-slimy-nuc2-project-changelog.md` — Agent Summary section is empty ("—"); repos touched are all auto-sync doc commits with no notable changes.

**seed-progress-history.md** — Large (88KB, 1880 lines) NUC2 session progress log. Contains chronological agent session summaries (e.g., Bot OpenAI 401 Fix, Ollama CPU benchmarks). Operational rules (meta-learning loops, regressions, SLB-required actions, proof gate) already compiled into [Clawd Agent Rules](../../projects/clawd-agent-rules.md) and [Workspace Agent Rules](../../projects/workspace-agent-rules.md). Not an AGENTS.md. No standalone wiki article warranted. Deferred — re-evaluate if substantive operational content is added.

These will be re-evaluated if substantive content is added to the source files.

## See Also
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md)
- [Slimy KB](../projects/slimy-kb.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
