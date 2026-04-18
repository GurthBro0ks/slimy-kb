# OpenCLAW Agents
> Category: projects
> Sources: raw/decisions/2026-04-05-project-openclaw-agents-nuc1-state.md, raw/decisions/seed-workspace-agents.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-18 00:24 UTC (git)
> Version: r12 / 2baf56b
KB METADATA -->

OpenCLAW workspace agents are the execution and research subagents managed by the OpenCLAW gateway on NUC1.

## Workspace Agents

### workspace-executor
- **Path:** `/home/slimy/.openclaw/workspace-executor`
- **Remote:** NONE (local-only)
- **Branch:** master (detached HEAD, no git commits)
- **Dirty:** YES — untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`

### workspace-researcher
- **Path:** `/home/slimy/.openclaw/workspace-researcher`
- **Remote:** NONE (local-only)
- **Branch:** master (detached HEAD, no git commits)
- **Dirty:** YES — untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`

## Gateway

### openclaw-gateway
- **Ports:** 18789, 18790, 18791, 18792 (localhost only)
- **Config:** `/home/slimy/.claude/openclaw.json`
- **Process owner:** Managed by ned-autonomous (PM2 agent-loop) and ned-clawd (cron registration)

## Active Cron Registration (ned-clawd)
- `register-agents.sh` runs: every hour, every 2 hours, and at reboot
- Registers workspace-executor and workspace-researcher with the gateway
- Source: `/home/slimy/ned-clawd/scripts/register-agents.sh`

## Architecture
```
ned-autonomous (PM2 agent-loop)
  └── openclaw-gateway (ports 18789-18792, localhost)
        ├── workspace-executor
        └── workspace-researcher

ned-clawd (cron) → register-agents.sh → registers with gateway
```

## Session Patterns

Workspace agents (executor and researcher) follow these operational disciplines:

### Startup Sequence
Every session, in order:
1. Read `SOUL.md` — agent identity
2. Read `USER.md` — user context
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) — recent context
4. **Main session only:** Also read `MEMORY.md`

### Memory Architecture
- **Daily logs:** `memory/YYYY-MM-DD.md` — raw session logs
- **Long-term memory:** `MEMORY.md` — curated, distilled learnings
- Memory tiers:

| Tier | Trust | Expiry | Use |
|------|-------|--------|-----|
| Constitutional | 1.0 | Never | Security, hard constraints |
| Strategic | 0.9 | Quarterly | Current projects, direction |
| Operational | 0.8 | 30d unused | Temporary bugs, workarounds |

### Heartbeat vs Cron
- **Heartbeat:** batch multiple checks, conversational context, timing drifts ~30 min
- **Cron:** exact timing, isolated tasks, one-shot reminders, standalone delivery

### Group Chat Discipline
- **Respond when:** directly mentioned, genuine value add, corrections, summaries
- **Stay silent when:** casual banter, already answered, would interrupt flow
- Use emoji reactions for lightweight acknowledgments (one per message max)

### Friction and Regression Tracking
Friction log entries track recurring issues:
```
- [YYYY-MM-DD] <issue> | <symptom> | <root cause> | <fix>
```
Regression list captures failures-to-guardrail:
```
- [YYYY-MM-DD] <failure description> | Pattern: <frequency> | Fix: <prescription>
```

### Proactive Heartbeat Checks
Rotate through during heartbeats (2-4x daily):
- Email (urgent unread)
- Calendar (next 24-48h)
- Mentions/notifications
- Project status (git status, health)

### Memory Maintenance
During heartbeats, periodically:
1. Review recent `memory/YYYY-MM-DD.md` files
2. Distill significant events into `MEMORY.md`
3. Remove outdated `MEMORY.md` entries

See [Memory Capture Pattern](../patterns/memory-capture-pattern.md) and [Clawd Workspace Governance](clawd-workspace-governance.md) for full governance rules.

## See Also
- [Ned-Autonomous](ned-autonomous.md)
- [Clawd Workspace Governance](clawd-workspace-governance.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
