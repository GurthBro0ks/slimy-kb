# Slimy Discord Bot
> Category: projects
> Sources: raw/agent-learnings/2026-04-09-nuc1-discord-bot-runtime-truth.md, raw/decisions/2026-04-07-bot-monorepo-migration-complete.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-16 19:37 UTC (git)
> Version: r6 / b744522
KB METADATA -->

The Slimy Discord Bot is a TypeScript Discord bot powered by the slimy-monorepo, serving AI chat, memory workflows, club analytics, and operations tooling across 3 Discord servers.

## Live Runtime (2026-04-09)
- **Codebase:** `/opt/slimy/slimy-monorepo/apps/bot/` (TypeScript source in `src/`, compiled output in `dist/`)
- **Host:** NUC1
- **Supervisor:** PM2 — process name `slimy-bot-v2`, PM2 id=1
- **PID:** 178717
- **Uptime:** ~12h with 7 restarts (monitor for crash loop)
- **Entry point:** `node /opt/slimy/slimy-monorepo/apps/bot/dist/index.js`
- **Connections:** 3 Discord servers
- **Runtime state:** `data_store.json` (3850 bytes) written periodically — confirms active state management

## Architecture
- TypeScript Discord.js v14 bot in monorepo apps/bot/
- Compiled with `tsc` → `dist/index.js` is what PM2 executes
- Environment via `.env` (Discord token, MySQL, etc.)
- `ecosystem.config.cjs` defines PM2 process: name `slimy-bot-v2`, cwd `apps/bot`
- Supports: AI chat, memory pipeline, image generation, club analytics, sheet sync

## Engineering Notes
- `src/index.ts` is the integration entrypoint and should stay lean.
- Core services live in `lib/`; command and handler boundaries are explicit.
- 18 commands, 31 lib modules, 45 Vitest tests as of migration completion (2026-04-07).
- CommonJS style and repository naming conventions enforced.

## Verification Baseline
- `pnpm --filter @slimy/bot build` — compile TypeScript
- `pnpm --filter @slimy/bot start` — run compiled bot
- `pnpm --filter @slimy/bot test` — vitest run
- PM2 status: `pm2 list` → `slimy-bot-v2` shows `online`

## Cutover History
- Old bot was JS at `/opt/slimy/app` (GurthBro0ks/slimyai_setup)
- Cutover to monorepo TypeScript completed **2026-04-03**
- Old bot archived: `/opt/slimy/app-archive-20260408.tar.gz`
- Rollback script: `/home/slimy/rollback-bot.sh`

## Supersession
- **Predecessor:** `slimyai_setup` (JS Discord bot at `/opt/slimy/app`) — archived, not running
- **Current:** `slimy-bot-v2` in slimy-monorepo (TypeScript)

## See Also
- [Slimy Monorepo](slimy-monorepo.md)
- [Slimyai Setup](slimyai-setup.md)
- [Truth Gate](../concepts/truth-gate.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
