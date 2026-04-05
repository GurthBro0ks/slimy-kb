---
description: NUC2 runtime evidence for slimy-kb — KB repo, cron pull, active sync
type: reference
---

# Project: Slimy KB — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** slimy-kb
- **GitHub:** GurthBro0ks/slimy-kb
- **Local path:** `/home/slimy/kb`
- **Branch:** main
- **Last commit:** `d149605` 2026-04-05 11:20 (today)
- **Dirty:** YES — untracked `output/lint-report.md`

## Classification
- **ACTIVE** — HIGH confidence

## NUC2 Runtime Evidence

### Cron (primary)
```
*/30 * * * * cd /home/slimy/kb && bash tools/kb-sync.sh pull 2>&1 | logger -t kb-sync
```
Active cron entry: pulls from remote every 30 minutes. Established during 2026-04-05 KB tooling session.

### Git State
- Working tree: untracked `output/lint-report.md` only
- No AGENTS.md — uses `KB_AGENTS.md` at KB root instead

### KB Tools
- `tools/wiki` — CLI with subcommands: `prompt-query`, `prompt-compile`, `daily`, `conflicts`
- `tools/kb-sync.sh` — sync with push/pull/resolve subcommands
- `tools/kb-search.sh` — wiki full-text search

### Related Local Files
- `/home/slimy/init.sh` — sources kb → sets `REPO_kb`
- Harness files reference KB path directly

## Relationship to Other Projects
- Cross-NUC sync: NUC1 pushes to same remote; NUC2 pulls
- `wiki/projects/slimy-kb.md` — MISSING from wiki (this session creates it)
- Referenced by: harness-runtime-topology, operator-console

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
