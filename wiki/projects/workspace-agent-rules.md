# Workspace Agent Rules
> Category: projects
> Sources: raw/decisions/seed-workspace-agents.md
> Created: 2026-04-08
> Updated: 2026-04-08
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-22 12:29 UTC (git)
> Version: r29 / a285643
KB METADATA -->

OpenCLAW workspace agent operating rules, compiled from the canonical `AGENTS.md` found in the workspace root.

## Session Startup
1. Read `SOUL.md` — agent identity and purpose.
2. Read `USER.md` — who is being helped.
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context.
4. **If in MAIN SESSION** (direct chat with human): Also read `MEMORY.md`.

## Safety
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever).
- When in doubt, ask.

## Heartbeat vs Cron: When to Use Each

**Use heartbeat when:**
- Multiple checks can batch together (inbox + calendar + notifications in one turn).
- You need conversational context from recent messages.
- Timing can drift slightly (every ~30 min is fine, not exact).
- You want to reduce API calls by combining periodic checks.

**Use cron when:**
- Exact timing matters ("9:00 AM sharp every Monday").
- Task needs isolation from main session history.
- You want a different model or thinking level for the task.
- One-shot reminders ("remind me in 20 minutes").
- Output should deliver directly to a channel without main session involvement.

**Tip:** Batch similar periodic checks into `HEARTBEAT.md` instead of creating multiple cron jobs.

## SLB-Required Actions (Two-Person Rule)
Before executing any of these, invoke `slb` for peer approval:
- Any `rm -rf` or mass delete operation.
- Modifying cron jobs (adding/removing/editing).
- Changing system config files outside `~/clawd/`.
- Any command using sudo.
- Deploying to production or modifying live services.
- Modifying MEMORY.md constitutional rules.

If SLB is unavailable or times out after 5 minutes, HOLD the action and notify Jason via Telegram with the exact command and reason.

## Meta-Learning Loops

### Regressions
Every significant failure becomes a named rule in AGENTS.md:
```
- [YYYY-MM-DD] sessions_spawn race condition: spawned sub-agent completes but process(poll) returns "No session found" → Always verify session existence via sessions_list before process(poll), or add delay, or treat "No session found" as success if output file exists
```

### Friction Log
When new instructions contradict old ones, log here. Don't silently comply. Surface at next natural break point.

### Memory Tiers

| Tier | Trust | Expiry | Use |
|------|-------|--------|-----|
| Constitutional | 1.0 | Never | Security, hard constraints |
| Strategic | 0.9 | Quarterly | Current projects, direction |
| Operational | 0.8 | 30d unused | Temporary bugs, workarounds |

## Three Mistakes That Kill Learning
1. **RAG ≠ Learning** — Retrieval gives info, not behavior change.
2. **Within vs Across Sessions** — Prompt engineering vs multi-session architecture.
3. **Open Loops** — Logs nobody reads, predictions never filled in.

## See Also
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Memory Capture Pattern](../patterns/memory-capture-pattern.md)
