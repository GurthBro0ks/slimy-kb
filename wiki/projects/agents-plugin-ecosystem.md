# Agents Plugin Ecosystem
> Category: projects
> Sources: raw/articles/seed-agents-backup-full-readme.md, raw/articles/nuc1-seed-actionbook-readme.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

This project packages focused plugins, specialized agents, skills, and workflow orchestrators for Claude Code operations.

## Scope
- Plugin-oriented architecture with composable, single-purpose modules.
- Agent and skill catalogs designed for progressive disclosure and lower context overhead.
- Tooling coverage for scaffolding, testing, security, and automation workflows.

## Operational Value
- Install only required capabilities for a task.
- Reduce token use by avoiding broad always-on context.
- Compose multiple narrow plugins for complex workflows.

## Browser Action Layer
- Actionbook is used as a browser action engine pattern for agents that need reliable website operation.
- The model is manual-first (site action manuals + DOM mappings) instead of heuristic scraping, reducing selector drift and token-heavy HTML parsing.
- In this ecosystem view, browser actions are treated like any other scoped plugin capability: explicitly loaded when needed, omitted otherwise.

## See Also
- [Mission Control](mission-control.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
