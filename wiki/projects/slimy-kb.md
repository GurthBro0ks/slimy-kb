# Slimy KB
> Category: projects
> Sources: raw/decisions/2026-04-05-project-slimy-kb-nuc2-state.md
> Created: 2026-04-05
> Status: draft

Slimy KB is the SlimyAI knowledge base — a git-based, cross-NUC synced wiki with a raw-to-compiled build pipeline and CLI tooling.

## Overview
- **GitHub:** GurthBro0ks/slimy-kb
- **Local path:** `/home/slimy/kb`
- **Branch:** main; last commit `d149605` 2026-04-05 (today)
- **Dirty:** YES — untracked `output/lint-report.md`

## KB Structure
```
kb/
  raw/          — source documents (decisions/, research/, articles/, agent-learnings/)
  wiki/         — compiled articles (auto-maintained, do not edit directly)
  tools/        — CLI tooling
  output/       — build artifacts (lint reports, etc.)
  KB_AGENTS.md  — KB-specific agent operating rules
```

## KB Tools
- `tools/wiki` — CLI with subcommands:
  - `wiki prompt-query` — generates sync-aware prompt for KB queries
  - `wiki prompt-compile` — generates sync-aware prompt for KB compile
  - `wiki daily` — daily status: conflicts, inbox, uncompiled raw, stale articles, last sync
  - `wiki conflicts` — lists conflicted files across KB and vault
- `tools/kb-sync.sh` — cross-NUC KB sync (push/pull/resolve subcommands)
- `tools/kb-search.sh` — full-text wiki search

## Runtime State (NUC2)
- **Sync cron:** `*/30 * * * * cd /home/slimy/kb && bash tools/kb-sync.sh pull`
  - Active: KB pulls from remote every 30 minutes; log output piped to `logger -t kb-sync`
- NUC1 pushes to the same remote; NUC2 is the pull consumer

## Cross-NUC Sync
- NUC1 is the push side (creates and pushes wiki changes)
- NUC2 is the pull side (pulls and compiles)
- Sync is bidirectional for raw/ → wiki/ compilation results
- Conflict resolution handled by `kb-sync.sh resolve`

## See Also
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md)
- [Operator Console](operator-console.md)
- [Capture Dashboard](capture-dashboard.md)
