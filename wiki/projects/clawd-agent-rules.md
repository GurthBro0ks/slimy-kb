---
title: "Clawd Agent Rules"
page_type: "concept"
status: "active"
tags: ["nuc1", "ai", "openclaw", "agent", "rules", "session"]
updated: 2026-06-10
source_count: 2
aliases: ["clawd-agent-rules", "openclaw agent rules"]
---

# Clawd Agent Rules
> Category: projects
> Sources: raw/decisions/seed-workspace-agents.md, wiki/projects/workspace-agent-rules.md
> Created: 2026-06-10
> Updated: 2026-06-10
> Status: draft

<!-- KB METADATA
> Last edited: 2026-06-10 00:00 UTC (git)
> Version: r1 / new
KB METADATA -->

Operating rules for the Clawd OpenCLAW workspace agent system on NUC1. These rules govern session startup, memory discipline, safety, heartbeats, and the meta-learning loop. See [Workspace Agent Rules](workspace-agent-rules.md) for the full compiled article — this page captures the clawd-specific framing.

## Session Startup (Every Session)
1. Read `SOUL.md` — agent identity and purpose
2. Read `USER.md` — who is being helped
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with human): Also read `MEMORY.md`

Do not ask permission — just execute the startup sequence.

## SLB-Required Actions (Two-Person Rule)
Before executing any of these, invoke `slb` for peer approval:
- Any `rm -rf` or mass delete
- Modifying cron jobs
- Changing system config files outside `~/clawd/`
- Any command using `sudo`
- Deploying to production or modifying live services

## Safety Rules
- Never exfiltrate private data
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask

## Heartbeat vs Cron

**Use heartbeat when:**
- Multiple checks can batch together
- Conversational context from recent messages is needed
- Timing can drift slightly (every ~30 min is fine)

**Use cron when:**
- Exact timing matters
- Task needs isolation from main session history
- One-shot reminders

## Memory Discipline
- **Daily notes** (`memory/YYYY-MM-DD.md`): raw logs of what happened — write freely
- **Long-term** (`MEMORY.md`): curated memories, distilled essence — update periodically, not every session
- "Mental notes" don't survive session restarts. **Files do.** Write it down.
- Load `MEMORY.md` **only in main session** — never in shared/group contexts (security)

## Meta-Learning Loop
Periodically (during heartbeats or session ends):
1. Review recent `memory/YYYY-MM-DD.md` files
2. Identify significant events, lessons, insights worth keeping
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated info from MEMORY.md

## See Also
- [Workspace Agent Rules](workspace-agent-rules.md) — Full compiled version of these rules
- [Clawd Workspace Governance](clawd-workspace-governance.md) — Memory/session governance model
- [Clawd](clawd.md) — OpenCLAW daemon that enforces these rules
- [OpenCLAW Agents](openclaw-agents.md) — Subagents that follow these rules
