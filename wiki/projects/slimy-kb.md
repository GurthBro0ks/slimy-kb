# Slimy KB
> Category: projects
> Sources: raw/decisions/2026-04-05-project-slimy-kb-nuc2-state.md, raw/research/2026-04-05-obsidian-calendar-automation-options.md, raw/research/obsidian-projects-kb-workflow.md, raw/research/2026-04-05-slimy-nuc2-webhook-codex-yolo-normalization.md, raw/changelogs/2026-04-05-slimy-nuc1-project-changelog.md, raw/changelogs/2026-04-05-slimy-nuc2-project-changelog.md, raw/decisions/2026-04-09-project-kb.md
> Created: 2026-04-05
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-24 00:31 UTC (git)
> Version: r38 / aa2e4da
KB METADATA -->

Slimy KB is the SlimyAI knowledge base — a git-based, cross-NUC synced wiki with a raw-to-compiled build pipeline and CLI tooling.

## Project Metadata
- **Truth gate:** `bash /home/slimy/kb/tools/kb-sync.sh pull` (verify sync succeeds before any KB read; verify sync succeeds after any KB write)
- **Risks:** Conflict files from Obsidian Sync or cross-NUC git operations

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
  - `wiki todo` — operator checklist for today
  - `wiki recommend` — AI-generated recommendations for KB improvements
  - `wiki versions` — version scan across all known projects
  - `wiki changelog` — recent changes rollup (1d/7d)
  - `wiki ideas-ingest` — ingest vault Ideas/ into KB raw
  - `wiki calendar-sync` — create/update today's vault Daily/ note
- `tools/kb-sync.sh` — cross-NUC KB sync (push/pull/resolve subcommands)
- `tools/kb-search.sh` — full-text wiki search
- `tools/slimy-agent-finish.sh` — end-of-run automation for Claude/Codex agents
- `tools/kb-project-doc-sync.sh` — scaffold README/CHANGELOG/VERSION for project repos
- `tools/kb-version-scan.sh` — scan version state across all known projects
- `tools/kb-changelog-rollup.sh` — roll up recent commits by project
- `tools/kb-idea-ingest.sh` — ingest vault Ideas/ into KB raw/
- `tools/kb-calendar-sync.sh` — sync daily note to vault Daily/
- `tools/kb-recommend.sh` — generate recommendation output and vault notes
- `tools/kb-todo.sh` — generate operator todo checklist
- `tools/kb-compile-if-needed.sh` — check for uncompiled raw and trigger compile

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
