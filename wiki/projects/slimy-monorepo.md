# Slimy Monorepo
> Category: projects
> Sources: raw/articles/seed-slimy-monorepo-readme.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc2-state.md, raw/decisions/2026-04-07-bot-monorepo-migration-complete.md, raw/changelogs/2026-04-08-slimy-nuc1-project-changelog.md, raw/research/2026-04-09-nuc2-project-inventory.md, raw/agent-learnings/2026-04-09-nuc2-slimy-monorepo-update.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 19:37 UTC (git)
> Version: r18 / 56f8615
KB METADATA -->

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

## NUC2 Runtime State (2026-04-09)
- **Canonical path:** `/opt/slimy/slimy-monorepo` (symlink: `/home/slimy/slimy-monorepo`)
- **Remote:** `git@github.com:GurthBro0ks/slimy-monorepo.git`, branch `main`
- **Last 3 commits:**
  - `a910a9a` — fix: /snail/club sort order — highest power now shows rank 1 at top
  - `2fcf024` — feat: /snail/stats QA fixes — debug dock visibility, refresh feedback, empty movers
  - `fa3788b` — docs: auto-sync project docs from slimy-nuc2 2026-04-08
- **Supervisor:** `systemd --user` (`slimy-web.service`)
- **State:** ACTIVE, running
- **Port:** **3000** — Next.js standalone, pid 215978
- **Key subdirs:** `apps/web` (Next.js), `apps/bot` (slimy-bot-v2 TypeScript), `packages/`, `lib/`
- **AGENTS.md:** YES — monorepo agent rules, `pnpm lint`/`pnpm test:all` truth gate
- **Dependencies:** MySQL (NUC1 via tunnel port 3307), Prisma, Next.js, Tailwind
- **Classification:** ACTIVE | Confidence: HIGH

### NUC2 Services
| Service | Type | Port | Status |
|---------|------|------|--------|
| slimy-web | systemd (`slimy-web.service`) | 3000 | active |
| slimy-mysql-tunnel | systemd | 3307 | active |
| postgres | systemd | 5432 | active |

### Truth Gate (NUC2)
```bash
pnpm --filter web lint && pnpm --filter web build
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/snail/club
systemctl --user status slimy-web.service
```

### Dead Ports (do not use)
- Port **3080** (admin-api) — DEAD since 2026-03-19, do not start
- Port **3081** (admin-ui) — DEAD since 2026-03-19, do not start
- `/api/* → 3080` rewrite — removed, Next.js API routes handle all

### Key Routes
- `/owner/crypto` — crypto dashboard
- `/snail/club` — club power rankings
- `/snail/stats` — club movers (gainers/losers)
- `/trader/*` — trader dashboard with mock/http adapter

### Trader Adapter Env Vars
- `NEXT_PUBLIC_TRADER_ADAPTER` — "mock" (default) or "http"
- `NEXT_PUBLIC_TRADER_API_BASE` — API base URL when using http adapter

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-16T12:23:09Z
**NUC1 status:** clean, DIVERGED
**NUC1 commit:** `a004f10` — docs: auto-sync project docs from slimy-nuc1 2026-04-11
**Branch:** detached

### Open Issues
- **[HIGH/candidate]** NUC1 repo diverged from remote: slimy-monorepo (repo_drift, 25x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [Slimy Web](slimy-web.md)
- [SlimyAI Login and Session Flow](../architecture/slimyai-login-and-session-flow.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Truth Gate](../concepts/truth-gate.md)
