# Workspace Executor
> Category: projects
> Sources: raw/decisions/2026-04-09-project-workspace-executor.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-22 12:29 UTC (git)
> Version: r30 / a285643
KB METADATA -->

OpenClaw workspace executor — the execution-focused subagent in the OpenCLAW agent hierarchy. Handles task execution, session management, memory protocols, heartbeat scheduling, and group chat safety. Part of the .openclaw agent framework.

## Why It Matters

The workspace executor is one of two active subagents (alongside workspace-researcher) that perform real work in the OpenCLAW agent system. While the researcher gathers information, the executor carries out tasks. It is registered with the OpenCLAW gateway and activated by the agent loop. Without it, the agent system cannot execute delegated work.

## Runtime State (NUC1)
- **Path:** `/home/slimy/.openclaw/workspace-executor`
- **Remote:** none (local-only — no git remote)
- **Branch:** master
- **Status:** ACTIVE
- **Truth gate:** `git -C /home/slimy/.openclaw/workspace-executor log -1 --oneline`
- **Services:** none (workspace — activated by OpenCLAW gateway on demand)

## Architecture
```
ned-autonomous (PM2 agent-loop)
  └── openclaw-gateway (ports 18789-18792, localhost)
        └── workspace-executor  ← this project
```

The executor registers with the OpenCLAW gateway via `register-agents.sh` (runs every hour, every 2 hours, and at reboot from ned-clawd cron).

## Current Role in the System
- Execution agent in the OpenCLAW multi-agent setup on NUC1
- Activated by the gateway when tasks require execution (vs research)
- Maintains its own memory: daily logs (`memory/YYYY-MM-DD.md`) and curated long-term memory (`MEMORY.md`)
- Reads SOUL.md and USER.md on session start for identity and context

## Memory Architecture
- **Daily logs:** `memory/YYYY-MM-DD.md` — raw session activity
- **Long-term memory:** `MEMORY.md` — curated, distilled learnings
- Memory tiers: Constitutional (never expires), Strategic (quarterly), Operational (30d unused)

## Relationships / Dependencies
- **Managed by:** OpenCLAW gateway (ports 18789-18792)
- **Registered by:** ned-clawd cron (`register-agents.sh`)
- **Sibling agent:** [Workspace Researcher](workspace-researcher.md)
- **Parent process:** ned-autonomous PM2 agent-loop
- **Framework:** .openclaw agent framework

## Risks
- No remote backup — local-only, if NUC1 disk fails this is lost
- Detached HEAD state with untracked files

## See Also
- [OpenCLAW Agents](openclaw-agents.md) — parent overview of all workspace agents
- [Workspace Researcher](workspace-researcher.md) — sibling research agent
- [Workspace Agent Rules](workspace-agent-rules.md) — operational rules for this agent
- [Ned-Autonomous](ned-autonomous.md) — parent PM2 process
- [Ned-Clawd](ned-clawd.md) — agent workspace that runs registration cron
