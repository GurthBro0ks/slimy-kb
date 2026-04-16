# Workspace Researcher
> Category: projects
> Sources: raw/decisions/2026-04-09-project-workspace-researcher.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 19:36 UTC (git)
> Version: r2 / 98f6e61
KB METADATA -->

OpenClaw workspace researcher — AI agent workspace with session management, memory protocols, heartbeat scheduling, and group chat safety. Part of the .openclaw agent framework.

## Runtime State (NUC1)
- **Path:** `/home/slimy/.openclaw/workspace-researcher`
- **Remote:** none (local-only)
- **Branch:** master
- **Status:** ACTIVE
- **Truth gate:** `git -C /home/slimy/.openclaw/workspace-researcher log -1 --oneline`
- **Services:** none (workspace)

## Architecture
```
ned-autonomous (PM2 agent-loop)
  └── openclaw-gateway (ports 18789-18792, localhost)
        └── workspace-researcher
```

## See Also
- [OpenCLAW Agents](openclaw-agents.md)
- [Workspace Agent Rules](workspace-agent-rules.md)
- [Ned-Autonomous](ned-autonomous.md)
