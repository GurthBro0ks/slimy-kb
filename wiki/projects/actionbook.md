# Actionbook
> Category: projects
> Sources: raw/decisions/2026-04-09-project-actionbook.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-09 11:53 UTC (git)
> Version: r2 / 758e457
KB METADATA -->

Browser Action Engine for AI Agents — provides website action manuals and DOM selectors via MCP protocol so AI agents can operate websites precisely without parsing HTML each time.

## Runtime State (NUC1)
- **Path:** `/home/slimy/ned-clawd/actionbook`
- **Remote:** `https://github.com/actionbook/actionbook`, branch `main`
- **Type:** Library / tool
- **Status:** ACTIVE — ahead of remote by 13 commits
- **Truth gate:** `cd /home/slimy/ned-clawd/actionbook && pnpm test` (jest tests in .test.ts files)

## Architecture
- **Monorepo** with JS SDK, MCP server, CLI, and AI SDK tools
- **12 packages** under pnpm workspace
- **Node.js >= 18**, **pnpm >= 10** required
- **PostgreSQL** required for services/db and services/api-service

## Dependencies
- Node.js >= 18, pnpm >= 10, PostgreSQL

## Risks
- No .env committed (`.env.example` per package only)

## See Also
- [OpenCLAW Agents](openclaw-agents.md)
