# Slimy Discord Bot
> Category: projects
> Sources: raw/articles/seed-app-readme.md, raw/decisions/seed-app-agents.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

The Slimy Discord Bot is a Node.js bot focused on AI chat, memory workflows, and operations tooling.

## Key Capabilities
- AI chat with context retention and mention support.
- Memory pipeline with persistence and export paths.
- Image generation and utility automation command set.
- Operational scripts for deployment and dependency checks.

## Engineering Notes
- `index.js` is integration entrypoint and should stay lean.
- Core services live in `lib/`; command and handler boundaries are explicit.
- CommonJS style and repository naming conventions are enforced.

## Verification Baseline
- `npm start` for runtime validation.
- `npm run deploy` after slash command changes.
- `npm run test:memory` and smoke scripts for regression checks.

## See Also
- [Truth Gate](../concepts/truth-gate.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
- [Slimy Monorepo](slimy-monorepo.md)
