# Actionbook
> Category: projects
> Sources: raw/decisions/2026-04-09-project-actionbook.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-24 00:31 UTC (git)
> Version: r37 / 03d777e
KB METADATA -->

Browser Action Engine for AI Agents — provides website action manuals and DOM selectors via MCP protocol so AI agents can operate websites precisely without parsing HTML each time.

## Why It Matters

Actionbook solves a real problem for AI agents: instead of scraping and interpreting raw HTML on every interaction, agents get pre-built action manuals with exact DOM selectors. This makes automated web interaction reliable and repeatable. It is a dependency for any AI agent that needs to operate external websites.

## Runtime State (NUC1)
- **Path:** `/home/slimy/ned-clawd/actionbook` (subdirectory of ned-clawd workspace)
- **Remote:** `https://github.com/actionbook/actionbook`, branch `main`
- **Type:** Library / tool (not a standalone service)
- **Status:** ACTIVE — ahead of remote by 13 commits (local development outpaces upstream)
- **Truth gate:** `cd /home/slimy/ned-clawd/actionbook && pnpm test` (jest tests in .test.ts files)

## Architecture
- **Monorepo** with JS SDK, MCP server, CLI, and AI SDK tools
- **12 packages** under pnpm workspace
- **Node.js >= 18**, **pnpm >= 10** required
- **PostgreSQL** required for services/db and services/api-service
- Communicates via MCP protocol — AI agents call Actionbook as a tool

## Current Role in the System
- Lives inside the ned-clawd agent workspace on NUC1
- Provides browser automation capability to OpenCLAW workspace agents
- Ahead of upstream by 13 commits — local modifications have not been pushed
- No running service — consumed as a library/tool by agents on demand

## Dependencies
- Node.js >= 18, pnpm >= 10, PostgreSQL

## Risks
- No .env committed (`.env.example` per package only)
- 13 commits ahead of upstream — local work is not backed up to remote
- Third-party repo (not GurthBro0ks) — upstream moves independently

## See Also
- [OpenCLAW Agents](openclaw-agents.md) — primary consumers of Actionbook
- [Ned-Clawd](ned-clawd.md) — host workspace containing actionbook
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
