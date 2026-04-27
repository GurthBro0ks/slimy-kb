# Slimy Web
> Category: projects
> Sources: raw/articles/seed-slimyai-web-readme.md, raw/research/2026-04-09-nuc2-project-inventory.md, raw/agent-learnings/2026-04-09-nuc2-slimyai-web-update.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-26 12:36 UTC (git)
> Version: r47 / 85c0860
KB METADATA -->

Slimy Web is the Next.js front-end with role-aware routing, API proxies, and docs integration.

## Highlights
- Next.js App Router with TypeScript and Tailwind.
- API proxy routes for secure backend integration.
- Codes aggregation and MDX docs ingestion workflows.
- Test coverage with Vitest and Playwright.

## Runtime Expectations
- Local dev serves on port 3000.
- Environment variables control API wiring and auth behavior.
- CI pipeline validates lint, tests, build, and docs sync.

## NUC2 Runtime State (2026-04-09)
- **Canonical path:** `/opt/slimy/slimy-monorepo/apps/web` (part of slimy-monorepo, not standalone)
- **Supervisor:** `systemd --user` (`slimy-web.service`)
- **Port:** **3000**
- **Status:** ACTIVE (running)

## Legacy Standalone (Archived — Not Running)
- **Path:** `/opt/slimy/web/slimyai-web`
- **Branch:** `fix/runtime-envs-check-2025-11-11-nuc2-snapshot`
- **Status:** ARCHIVED — superseded by slimy-monorepo `apps/web`
- **No systemd/PM2 services**, no listening ports
- **VERSION.md** snapshot from 2026-04-08

## Auth Stack (Current)
- Email/password login via `lib/slimy-auth/` (argon2 + MySQL sessions via Prisma)
- httpOnly cookies, owner gate at `/owner/*`
- See [Auth and Retired Services](../architecture/auth-and-retired-services.md) for intentionally dead services

## See Also
- [Slimy Monorepo](slimy-monorepo.md)
- [Auth and Retired Services](../architecture/auth-and-retired-services.md)
- [SlimyAI Login and Session Flow](../architecture/slimyai-login-and-session-flow.md)
