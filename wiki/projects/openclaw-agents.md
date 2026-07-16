---
title: "OpenCLAW Agents"
page_type: "overview"
status: "active"
tags: ["nuc1", "ai", "openclaw", "agent", "executor", "researcher"]
updated: 2026-06-10
source_count: 2
aliases: ["openclaw-agents", "workspace subagents"]
---

# OpenCLAW Agents
> Category: projects
> Sources: raw/decisions/2026-04-09-project-workspace-executor.md, raw/decisions/2026-04-09-project-workspace-researcher.md
> Created: 2026-06-10
> Updated: 2026-06-10
> Status: draft

<!-- KB METADATA
> Last edited: 2026-07-16 03:32 UTC (git)
> Version: r249 / e68cc448
KB METADATA -->

The OpenCLAW agent framework on NUC1 hosts two workspace subagents — `workspace-executor` and `workspace-researcher` — managed by the OpenCLAW gateway and registered by [Ned-Clawd](ned-clawd.md) cron scripts.

## Subagents

### Workspace Executor
- **Path:** `/home/slimy/.openclaw/workspace-executor`
- **Branch:** master
- **Remote:** none (local-only — no GitHub push URL)
- **Role:** Execution subagent — runs tasks, writes files, executes code, performs actions
- **Gateway registration:** registered with openclaw-gateway (ports 18789-18792)

### Workspace Researcher
- **Path:** `/home/slimy/.openclaw/workspace-researcher`
- **Branch:** master
- **Remote:** none (local-only — no GitHub push URL)
- **Role:** Research subagent — gathers information, analyzes data, produces research outputs
- **Gateway registration:** registered with openclaw-gateway (ports 18789-18792)

## Gateway Architecture

```
openclaw-gateway (localhost, ports 18789-18792)
  ├── workspace-executor  — executes tasks
  └── workspace-researcher — researches tasks

ned-clawd register-agents.sh → registers both agents at startup
ned-autonomous PM2 agent-loop → orchestrates requests
```

## Agent Framework
Both agents follow the OpenCLAW workspace agent rules. Each workspace has:
- `SOUL.md` — agent identity
- `USER.md` — who is being helped
- `memory/YYYY-MM-DD.md` — daily session logs
- `MEMORY.md` — curated long-term memory (main session only)

See [Workspace Agent Rules](workspace-agent-rules.md) for the full operating contract.

## Risks
- Both repos are local-only (no remote). Loss of NUC1 disk means loss of these repos.
- If gateway ports 18789-18792 are blocked, agents cannot be dispatched.

## See Also
- [Workspace Executor](workspace-executor.md) — Executor subagent detail page
- [Workspace Researcher](workspace-researcher.md) — Researcher subagent detail page
- [Workspace Agent Rules](workspace-agent-rules.md) — Operating contract all agents follow
- [Ned-Clawd](ned-clawd.md) — Cron scripts that register these agents
- [Ned-Autonomous](ned-autonomous.md) — PM2 orchestrator; full architecture diagram
- [Clawd](clawd.md) — OpenCLAW daemon
