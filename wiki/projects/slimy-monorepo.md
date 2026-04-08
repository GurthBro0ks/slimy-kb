# Slimy Monorepo
> Category: projects
> Sources: raw/articles/seed-slimy-monorepo-readme.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc2-state.md, raw/decisions/2026-04-07-bot-monorepo-migration-complete.md, raw/changelogs/2026-04-08-slimy-nuc1-project-changelog.md
> Created: 2026-04-04
> Updated: 2026-04-08
> Status: draft

The Slimy monorepo hosts web, bot, and supporting packages with shared CI and infrastructure documentation.

## Structure
- `apps/web` as primary Next.js application.
- Additional app/package directories for APIs, bot, and shared libraries.
- `docs/` provides infra, services matrix, and workflow references.

## Standard Workflow
- Install dependencies from repo root.
- Run scoped app commands for development.
- Run lint/tests/build before closeout.

## Constraints
- Respect project AGENTS startup sequence and truth gate.
- Do not re-clone over symlinked canonical path.

## Migration Complete (2026-04-07)

6-chunk bot migration from JS (`/opt/slimy/app`) to TypeScript (`/home/slimy/slimy-monorepo/apps/bot`) is complete. 18 commands, 31 lib modules, 45 Vitest tests. Live bot confirmed running monorepo build via PM2 `slimy-bot-v2`. Old bot gutted. `plan-spec.md` archived.

## NUC1 Runtime State (2026-04-08)
- **Canonical path:** `/opt/slimy/slimy-monorepo`; `/home/slimy/slimy-monorepo` is a symlink to it
- **PM2:** `slimy-bot-v2` online at port 3000/tcp (PM2 id 10, 110.7mb)
- **Branch:** main; latest commit `5a10499` 2026-04-08 — "feat: update default GLM model to glm-5 for coding plan compatibility"
- **Recent notable commits:**
  - `155bba7` — fix: default AI_PREMIUM_PROVIDER from grok_420 to grok_fast (pm_updown_bot_bundle on `feat/ibkr-forecast-integration`)
- **Successor to:** slimyai_setup (old JS Discord bot); cutover completed 2026-04-03

## See Also
- [Slimy Web](slimy-web.md)
- [SlimyAI Login and Session Flow](../architecture/slimyai-login-and-session-flow.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Truth Gate](../concepts/truth-gate.md)
