# Slimy Monorepo
> Category: projects
> Sources: raw/articles/seed-slimy-monorepo-readme.md, raw/decisions/seed-slimy-monorepo-agents.md
> Created: 2026-04-04
> Updated: 2026-04-04
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

## See Also
- [Slimy Web](slimy-web.md)
- [SlimyAI Login and Session Flow](../architecture/slimyai-login-and-session-flow.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Truth Gate](../concepts/truth-gate.md)
