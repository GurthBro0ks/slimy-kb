---
title: "Clawd"
page_type: "entity"
status: "active"
tags: ["nuc1", "ai", "openclaw", "daemon", "agent"]
updated: 2026-06-10
source_count: 2
aliases: ["clawd", "OpenCLAW daemon"]
---

# Clawd
> Category: projects
> Sources: raw/agent-learnings/2026-04-09-slimy-nuc1-claude-summary.md, raw/decisions/seed-workspace-agents.md
> Created: 2026-06-10
> Updated: 2026-06-10
> Status: draft

<!-- KB METADATA
> Last edited: 2026-06-21 09:09 UTC (git)
> Version: r163 / 1d2ed0e7
KB METADATA -->

Clawd is the OpenCLAW daemon on NUC1 — the workspace governance agent responsible for autonomous task execution, memory management, and lifecycle coordination of the `.openclaw` agent framework.

## Overview
- **GitHub:** GurthBro0ks/clawd
- **Local path:** `/home/slimy/clawd`
- **Branch:** main
- **Role:** OpenCLAW daemon — manages workspace agent lifecycle, governs memory tiers, and runs scheduled autonomous work on NUC1

## Responsibilities
- Workspace governance: enforces session startup, SLB peer approval, and closeout rules
- Autonomous agent execution: runs scheduled tasks (heartbeats, cron-driven maintenance)
- Memory management: curates MEMORY.md (long-term) and daily `memory/YYYY-MM-DD.md` files
- Agent oversight: coordinates workspace-executor and workspace-researcher subagents via the OpenCLAW gateway

## Architecture Position

```
clawd (OpenCLAW daemon, /home/slimy/clawd)
  ├── openclaw-gateway (ports 18789-18792, localhost)
  │     ├── workspace-executor (/home/slimy/.openclaw/workspace-executor)
  │     └── workspace-researcher (/home/slimy/.openclaw/workspace-researcher)
  └── memory/ (daily notes + MEMORY.md)

ned-autonomous (PM2 agent-loop) ← orchestrator
ned-clawd (cron scripts) ← registration, heartbeat, watchdog
```

## Agent Rules
Clawd follows the OpenCLAW workspace agent rules. See [Workspace Agent Rules](workspace-agent-rules.md) for the full operating contract.

Key rules:
- Session startup: read `SOUL.md`, `USER.md`, today's memory
- SLB peer approval required for destructive ops (rm -rf, cron edits, sudo, production changes)
- Heartbeat vs cron: heartbeat for batched periodic checks; cron for isolated/exact-time tasks
- Memory tiers: daily files = raw log; MEMORY.md = curated long-term

## Memory Model
See [Clawd Workspace Governance](clawd-workspace-governance.md) for the full memory/session governance model.

## See Also
- [Workspace Agent Rules](workspace-agent-rules.md) — Operating rules clawd enforces
- [Clawd Workspace Governance](clawd-workspace-governance.md) — Memory tiers and governance
- [Clawd Agent Rules](clawd-agent-rules.md) — Session contract specifics
- [OpenCLAW Agents](openclaw-agents.md) — Subagents managed by clawd
- [Ned-Autonomous](ned-autonomous.md) — PM2 persistent loop that hosts agent-loop
- [Ned-Clawd](ned-clawd.md) — Cron-driven scripts for agent registration and watchdog
