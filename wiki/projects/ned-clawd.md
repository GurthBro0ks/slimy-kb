---
title: "Ned-Clawd"
page_type: "entity"
status: "active"
tags: ["nuc1", "ai", "cron", "agent", "openclaw"]
updated: 2026-06-10
source_count: 2
aliases: ["ned-clawd"]
---

# Ned-Clawd
> Category: projects
> Sources: raw/agent-learnings/2026-04-09-slimy-nuc1-claude-summary.md, wiki/projects/ned-autonomous.md
> Created: 2026-06-10
> Updated: 2026-06-10
> Status: draft

<!-- KB METADATA
> Last edited: 2026-07-16 03:32 UTC (git)
> Version: r253 / 9869bbcd
KB METADATA -->

Ned-Clawd is the cron-driven scripting layer on NUC1 that handles agent registration, heartbeat scheduling, watchdog checks, and lifecycle management for the OpenCLAW agent framework. It is the companion to [Ned-Autonomous](ned-autonomous.md), which manages the persistent PM2 `agent-loop` process.

## Overview
- **GitHub:** GurthBro0ks/ned-clawd
- **Local path:** `/home/slimy/ned-clawd`
- **Type:** Cron scripts / lifecycle management
- **Host:** NUC1

## Relationship to Ned-Autonomous

| Component | Type | Role |
|-----------|------|------|
| ned-autonomous | PM2 `agent-loop` | Persistent process — always running |
| ned-clawd | Cron scripts | Periodic registration, heartbeat, watchdog |

Both are required for full autonomous operation:
- ned-autonomous is the persistent loop
- ned-clawd scripts handle registration, heartbeat polls, and watchdog recovery

## Key Responsibilities
- **Agent registration:** `register-agents.sh` — registers workspace-executor and workspace-researcher with the OpenCLAW gateway
- **Heartbeat:** Periodic health signals to Mission Control
- **Watchdog:** Checks agent-loop health; restarts if needed
- **Actionbook subdirectory:** `ned-clawd/actionbook` hosts the Browser Action Engine subproject

## Subdirectory: Actionbook
The `actionbook` project lives as a subdirectory of ned-clawd. See [Actionbook](actionbook.md) for details on the Browser Action Engine for AI agents.

## See Also
- [Ned-Autonomous](ned-autonomous.md) — Persistent PM2 agent-loop; architecture diagram
- [Clawd](clawd.md) — OpenCLAW daemon that clawd governs
- [OpenCLAW Agents](openclaw-agents.md) — Workspace subagents registered by these scripts
- [Actionbook](actionbook.md) — Browser Action Engine (ned-clawd subdirectory)
