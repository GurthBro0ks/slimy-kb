# Slimyai Setup
> Category: projects
> Sources: raw/decisions/2026-04-05-project-slimyai-setup-nuc1-state.md, raw/decisions/2026-04-05-project-slimyai-setup-nuc2-state.md, raw/decisions/2026-04-07-bot-monorepo-migration-complete.md, raw/agent-learnings/2026-04-09-nuc1-discord-bot-runtime-truth.md, raw/agent-learnings/2026-04-09-nuc2-slimyai-setup-update.md
> Created: 2026-04-05
> Updated: 2026-04-09
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-21 12:28 UTC (git)
> Version: r27 / c6ba87a
KB METADATA -->

Slimyai Setup is the **deprecated JS Discord bot** (GurthBro0ks/slimyai_setup). It has been superseded by `slimy-bot-v2` in the slimy-monorepo and is **not running on any NUC**.

## Status Summary
| NUC | Status | Notes |
|-----|--------|-------|
| NUC1 | ❌ ARCHIVED | Removed; archived to `app-archive-20260408.tar.gz`; no PM2, systemd, Docker, or cron entry |
| NUC2 | ❌ NOT_RUNNING | No active process; healthcheck service was FAILED at last scan |

## NUC1 State (Current — 2026-04-09)
- **Path:** `/opt/slimy/app` — **directory does not exist**
- **Archive:** `/opt/slimy/app-archive-20260408.tar.gz` (preserved cutover artifact)
- **Rollback script:** `/home/slimy/rollback-bot.sh` (preserved but not active)
- **PM2:** No entry for old bot
- **Supervisor:** None — fully retired

## NUC2 State (Current — 2026-04-09)
- **Path:** `/opt/slimy/app` (Discord bot super-snail)
- **Branch:** main; HEAD `c1fbf1b` 2026-04-05
- **Supervisor:** PM2 (ecosystem.config.js) or direct node
- **Classification:** ACTIVE | Confidence: HIGH
- **Key scripts:** `scripts/ingest-club-screenshots.js` for club screenshot OCR ingest
- **Services:** slimy-mysql-tunnel.service (port 3307) for SSH tunnel to NUC1 MySQL
- **Primary commands:** `/club analyze`, `/club stats`, `/club-admin`
- **MySQL:** via SSH tunnel (port 3307 to NUC1)
- **Google Sheets:** API integration for club member tracking

## Supersession
- **Successor:** `slimy-bot-v2` in slimy-monorepo (`/opt/slimy/slimy-monorepo/apps/bot/`)
- Cutover completed **2026-04-03**
- Live bot is now PM2-managed on NUC1, not slimyai_setup

## See Also
- [Slimy Discord Bot](slimy-discord-bot.md)
- [Slimy Monorepo](slimy-monorepo.md)
