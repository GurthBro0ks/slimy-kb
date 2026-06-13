---
title: "Clawd Workspace Governance"
page_type: "concept"
status: "active"
tags: ["nuc1", "ai", "openclaw", "memory", "governance", "session"]
updated: 2026-06-10
source_count: 1
aliases: ["clawd-workspace-governance", "openclaw memory governance"]
---

# Clawd Workspace Governance
> Category: projects
> Sources: raw/decisions/seed-workspace-agents.md
> Created: 2026-06-10
> Updated: 2026-06-10
> Status: draft

<!-- KB METADATA
> Last edited: 2026-06-13 06:15 UTC (git)
> Version: r149 / 42d3b42d
KB METADATA -->

Memory and session governance model for Clawd and the OpenCLAW workspace agents. Defines the two-tier memory architecture, session isolation rules, and continuity strategy for agents that restart fresh each session.

## The Continuity Problem
AI agents start each session with no memory of prior work. The clawd workspace solves this through a structured file-based memory system — agents read files at session start to reconstruct context.

## Two-Tier Memory Architecture

| Tier | File | Purpose | Who Writes |
|------|------|---------|-----------|
| **Daily notes** | `memory/YYYY-MM-DD.md` | Raw session log — what happened, what was tried | Agent writes freely during session |
| **Long-term** | `MEMORY.md` | Curated wisdom — decisions, lessons, important context | Agent curates periodically |

### Daily Notes
- Created fresh each session day
- Raw log format — not curated
- Read at session start (today + yesterday) for recent context
- Kept long-term for audit/history

### MEMORY.md
- Curated long-term memory
- Distilled from daily notes periodically
- **Only loaded in main session** (direct human chat) — NOT in Discord/group/shared contexts
- Security reason: contains personal context that should not leak to others
- Agents can freely read, edit, and update MEMORY.md in main sessions
- Outdated entries should be pruned over time

## Session Isolation Rule
```
Main session (direct chat with human):
  → Load: SOUL.md + USER.md + memory/today.md + memory/yesterday.md + MEMORY.md

Shared context (Discord, group, other humans present):
  → Load: SOUL.md + USER.md + memory/today.md + memory/yesterday.md
  → DO NOT load MEMORY.md
```

## Memory Maintenance Protocol
During heartbeats or end-of-session:
1. Read recent `memory/YYYY-MM-DD.md` files
2. Identify: decisions, lessons, important context worth keeping
3. Update `MEMORY.md` with distilled learnings
4. Remove stale entries from `MEMORY.md`
5. Goal: MEMORY.md = curated wisdom, not an archive

## Heartbeat State Tracking
The gateway agents track periodic check state in `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "email": <unix_timestamp>,
    "calendar": <unix_timestamp>,
    "weather": null
  }
}
```

## See Also
- [Clawd Agent Rules](clawd-agent-rules.md) — Session startup and SLB rules
- [Workspace Agent Rules](workspace-agent-rules.md) — Full compiled workspace operating contract
- [Clawd](clawd.md) — OpenCLAW daemon
- [OpenCLAW Agents](openclaw-agents.md) — Subagents governed by this model
