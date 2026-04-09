# Agents Backup Full
> Category: projects
> Sources: raw/decisions/2026-04-09-project-agents-backup-full.md, raw/research/2026-04-09-nuc2-project-inventory.md
> Created: 2026-04-09
> Status: draft

Full mirror of wshobson/agents — Claude Code plugin marketplace backup. Not actively used on NUC2.

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

## Note
`/home/slimy/.claude/agents` symlink does not exist — only `agents-backup-full` exists at this path.

## See Also
- [Agents Plugin Ecosystem](agents-plugin-ecosystem.md)
