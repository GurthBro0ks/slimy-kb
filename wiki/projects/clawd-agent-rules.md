# Clawd Agent Rules
> Category: projects
> Sources: raw/decisions/seed-clawd-agents.md
> Created: 2026-04-08
> Updated: 2026-04-08
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-27 00:36 UTC (git)
> Version: r54 / 934c004
KB METADATA -->

SlimyAI workspace agent operating rules, compiled from the canonical `AGENTS.md` found in the Clawd workspace directory.

## Session Startup
1. Read `SOUL.md` — agent identity and purpose.
2. Read `USER.md` — who is being helped.
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context.
4. **If in MAIN SESSION** (direct chat with human): Also read `MEMORY.md`.

## Memory Tiers

| Tier | Trust | Expiry | Use |
|------|-------|--------|-----|
| Constitutional | 1.0 | Never | Security, hard constraints |
| Strategic | 0.9 | Quarterly | Current projects, direction |
| Operational | 0.8 | 30d unused | Temporary bugs, workarounds |

Format: `[trust:X|src:direct|used:YYYY-MM-DD|hits:N]`

## Safety
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever).
- When in doubt, ask.

## External vs Internal

**Safe freely:** Read files, explore, organize, learn, search web, check calendars, work within workspace.

**Ask first:** Sending emails, tweets, public posts, anything leaving the machine, anything uncertain.

## Group Chats
- **Speak when:** directly mentioned, can add genuine value, witty/funny fits, correcting misinformation, summarizing when asked.
- **Stay silent when:** casual banter, already answered, would just be "yeah", conversation flowing fine.
- **One reaction per message max.**

## Heartbeats
Use for: batching inbox + calendar + notifications, conversational context, drifting timing, reducing API calls.

Use cron for: exact timing, isolated tasks, different model, one-shot reminders, output to channel without main session.

## Meta-Learning Loops

### Regressions (Failure → Guardrail)
Every significant failure becomes a named rule loaded every session:
```
- [YYYY-MM-DD] sessions_spawn race condition: ... → fix_rule
```

### Friction Log
When new instructions contradict old ones, log here. Don't silently comply.

### Prediction Log
Before significant decisions, write a prediction. Fill in Outcome/Delta after results:
```
### YYYY-MM-DD — [decision]
Prediction: ...
Confidence: H/M/L
Outcome: [fill in after]
Delta: [what surprised you]
Lesson: [what to update]
```

## Proof Gate
All task results MUST pass through the proof gate before being written to results or reported.

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-27T00:36:10Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `9692845` — fix(clawd): make executor scripts workspace-portable
**Branch:** main

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: clawd (repo_drift, 24x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Truth Gate](../concepts/truth-gate.md)
