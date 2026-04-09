# Slimyai Setup
> Category: projects
> Sources: raw/decisions/2026-04-05-project-slimyai-setup-nuc1-state.md, raw/decisions/2026-04-05-project-slimyai-setup-nuc2-state.md, raw/decisions/2026-04-07-bot-monorepo-migration-complete.md, raw/agent-learnings/2026-04-09-nuc1-discord-bot-runtime-truth.md
> Created: 2026-04-05
> Updated: 2026-04-09
> Status: stale

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

## NUC2 State (Historical — 2026-04-05 scan)
- slimy-web-health.service was FAILED at scan time (referenced missing `/opt/slimy/ops/healthcheck.sh`)
- `/opt/slimy/app` path present but **not running** — bot had already been migrated
- Classification noted as PRESENT_NOT_RUNNING at time of scan

## Supersession
- **Successor:** `slimy-bot-v2` in slimy-monorepo (`/opt/slimy/slimy-monorepo/apps/bot/`)
- Cutover completed **2026-04-03**
- Live bot is now PM2-managed on NUC1, not slimyai_setup

## See Also
- [Slimy Discord Bot](slimy-discord-bot.md)
- [Slimy Monorepo](slimy-monorepo.md)
