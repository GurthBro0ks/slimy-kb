# Slimy Monorepo
> Category: projects
> Sources: raw/articles/seed-slimy-monorepo-readme.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc2-state.md
> Created: 2026-04-04
> Updated: 2026-04-05
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

## NUC1 Runtime State (2026-04-05)
- **Canonical path:** `/opt/slimy/slimy-monorepo`; `/home/slimy/slimy-monorepo` is a symlink to it
- **PM2:** `slimy-bot-v2` online at port 3000/tcp (PM2 id 10, 110.7mb)
- **Branch:** main; last commit `cad0803` 2026-04-05 — "Merge branch 'feature/merge-chat-app'"
- **Dirty:** YES — uncommitted `apps/bot/data_store.json`, `apps/web/app/trader/`, `apps/web/components/trader/`
- **Successor to:** slimyai_setup (old JS Discord bot); cutover completed 2026-04-03

## See Also
- [Slimy Web](slimy-web.md)
- [SlimyAI Login and Session Flow](../architecture/slimyai-login-and-session-flow.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Truth Gate](../concepts/truth-gate.md)
