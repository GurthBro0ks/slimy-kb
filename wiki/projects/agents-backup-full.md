# Agents Backup Full
> Category: projects
> Sources: raw/decisions/2026-04-09-project-agents-backup-full.md, raw/research/2026-04-09-nuc2-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-25 00:33 UTC (git)
> Version: r40 / f9c7f6a
KB METADATA -->

Full mirror of wshobson/agents — the Claude Code plugin marketplace. Archived and not actively used on NUC2.

## Why It Matters

This is a safety net backup of the Claude Code plugin ecosystem (112 specialized agents, 146 skills, 72 plugins, 16 multi-agent orchestrators). While not actively used in day-to-day operations, it represents a library of pre-built agent capabilities that could be referenced or adapted for SlimyAI agent development.

## Runtime State (NUC2)
- **Path:** `/home/slimy/.claude/agents-backup-full`
- **Remote:** `git@github.com:wshobson/agents.git`, branch `main`
- **Last 3 commits:**
  - `56db49e` — docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `109ab6e` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `9cd45cc` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **Status:** ARCHIVED — backup mirror, not actively used
- **AGENTS.md:** NO
- **README.md:** YES — Claude Code plugins marketplace (112 specialized agents, 146 skills, 72 plugins)
- **Truth gate:** `git -C /home/slimy/.claude/agents-backup-full log -1 --oneline`
- **Services:** none
- **Risks:** none (read-only backup)

## Current Role in the System
- Passive backup — receives auto-sync docs commits but nothing else
- No services, no daemons, no integration with active infrastructure
- Could be used as reference material for building SlimyAI agents

## Important Note
`/home/slimy/.claude/agents` symlink does not exist — only `agents-backup-full` exists at this path. Do not expect a symlink.

## Operational Notes
- Safe to ignore during routine operations
- No maintenance required beyond the auto-sync docs that land via cron
- If disk space is needed, this is a low-risk candidate for removal (content exists on GitHub)

## See Also
- [Agents Plugin Ecosystem](agents-plugin-ecosystem.md) — plugin/agent/skill orchestration system
- [NUC2 Server State](../architecture/nuc2-server-state.md)
