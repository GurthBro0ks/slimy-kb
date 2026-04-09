# Ned-Clawd
> Category: projects
> Sources: raw/decisions/2026-04-09-project-ned-clawd.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

AI agent workspace similar to clawd with session management, memory protocols, heartbeats, and group chat safety. Contains scripts/mc-notify.sh for Mission Control integration.

## Runtime State (NUC1)
- **Path:** `/home/slimy/ned-clawd`
- **Remote:** `git@github.com:GurthBro0ks/ned-clawd.git`, branch `master`
- **Status:** ACTIVE
- **AGENTS.md:** YES — SOUL.md/USER.md/MEMORY.md based personal agent workspace
- **Truth gate:** `git -C /home/slimy/ned-clawd log -1 --oneline`
- **Services:** none (workspace-only)
- **Note:** Has its own AGENTS.md with session rules

## Active Cron Registration
- `register-agents.sh` runs: every hour, every 2 hours, and at reboot
- Registers workspace-executor and workspace-researcher with the OpenCLAW gateway
- Source: `/home/slimy/ned-clawd/scripts/register-agents.sh`

## See Also
- [Clawd](clawd.md)
- [OpenCLAW Agents](openclaw-agents.md)
- [Ned-Autonomous](ned-autonomous.md)
