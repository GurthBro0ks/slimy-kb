# NUC1 Discord Bot Runtime Truth — 2026-04-09

## Status: ✅ VERIFIED ACCURATE (no KB correction needed)

## Live Runtime
- **Bot:** `slimy-bot-v2` — monorepo TypeScript Discord bot
- **Supervisor:** PM2 (pm2 id=1, pid=178717)
- **Codebase:** `/opt/slimy/slimy-monorepo/apps/bot/` (symlinked from `/home/slimy/slimy-monorepo`)
- **Entry point:** `node /opt/slimy/slimy-monorepo/apps/bot/dist/index.js`
- **Branch:** `main`, latest commit `38ba3bb` (2026-04-09)
- **Uptime:** 12h, 7 restarts — worth monitoring
- **Connections:** 3 Discord servers

## Old Bot (Archive)
- `/opt/slimy/app` — **removed**, not a directory
- Archive: `/opt/slimy/app-archive-20260408.tar.gz` (preserved from 2026-04-08)
- No systemd service, no PM2 entry for old bot

## Cutover
- **Completed:** 2026-04-03 (per server-state.md)
- **Rollback script:** `/home/slimy/rollback-bot.sh`
- **Cutover entry in server-state.md:** ✅ accurate

## Supervision
| Type | Present |
|------|---------|
| PM2 `slimy-bot-v2` | ✅ Yes |
| systemd Discord service | ❌ None |
| Docker Discord container | ❌ None |

## KB/Wiki State
- No Discord bot articles in `kb/wiki/`
- No Discord bot agent-learnings in `kb/raw/agent-learnings/`
- `server-state.md` is accurate — no corrections needed

## Notes
- 7 PM2 restarts in 12h may indicate crash/reconnect loop — monitor
- `data_store.json` (3850 bytes) updated 2026-04-09 00:54 — periodic state writes working
