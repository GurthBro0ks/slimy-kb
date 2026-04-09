# Workspace Executor
> Category: projects
> Sources: raw/decisions/2026-04-09-project-workspace-executor.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

OpenClaw workspace executor — AI agent workspace with session management, memory protocols, heartbeat scheduling, and group chat safety. Part of the .openclaw agent framework.

## Runtime State (NUC1)
- **Path:** `/home/slimy/.openclaw/workspace-executor`
- **Remote:** none (local-only)
- **Branch:** master
- **Status:** ACTIVE
- **Truth gate:** `git -C /home/slimy/.openclaw/workspace-executor log -1 --oneline`
- **Services:** none (workspace)

## Architecture
```
ned-autonomous (PM2 agent-loop)
  └── openclaw-gateway (ports 18789-18792, localhost)
        └── workspace-executor
```

## See Also
- [OpenCLAW Agents](openclaw-agents.md)
- [Workspace Agent Rules](workspace-agent-rules.md)
- [Ned-Autonomous](ned-autonomous.md)
