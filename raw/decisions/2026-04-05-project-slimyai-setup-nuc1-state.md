---
description: NUC1 slimyai_setup — old JS Discord bot, LEGACY_CANDIDATE, superseded by slimy-bot-v2
type: reference
---

# Project: Slimyai Setup — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Project name:** slimyai_setup (aka slimy-app, /opt/slimy/app)
- **GitHub:** GurthBro0ks/slimyai_setup
- **Local path:** `/opt/slimy/app`
- **Branch:** main
- **Last commit:** `33f4a61` 2026-03-29
- **Dirty:** NO
- **AGENTS.md:** Yes

## Classification
- **LEGACY_CANDIDATE** — HIGH confidence
- NOT actively running
- Rollback script preserved at `/home/slimy/rollback-bot.sh`

## NUC1 Runtime Evidence

### Process Manager: NONE
- No PM2 process
- No cron entries
- No systemd service
- No Docker container

### Evidence of Supersession
- Cutover to slimy-bot-v2 (slimy-monorepo) completed 2026-04-03
- Rollback script exists: `/home/slimy/rollback-bot.sh`
- Recent commits (2026-03-29) suggest maintenance until cutover

### Git State
- Clean working tree — no uncommitted changes
- Preserved as rollback target, not active development

## Why Not ARCHIVE
- Rollback script exists — could be reverted to if slimy-bot-v2 has issues
- Keep as LEGACY_CANDIDATE (not ARCHIVE) to signal it is recoverable

## Relationship to Slimy Discord Bot (wiki article)
- `projects/slimy-discord-bot.md` covers the Discord bot architecture
- This was the JS implementation; slimy-bot-v2 (TypeScript in slimy-monorepo) is the successor

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
