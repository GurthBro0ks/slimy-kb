# Session Closeout Pattern
> Category: patterns
> Sources: raw/decisions/seed-agents-rules.md, raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-08
> Status: reviewed

This pattern standardizes how a SlimyAI agent session is opened and closed.

## Required Session Startup Steps (per AGENTS.md)
1. Read `SOUL.md` — agent identity and purpose.
2. Read `USER.md` — who is being helped.
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context.
4. **If in MAIN SESSION** (direct chat with human): Also read `MEMORY.md`.

## Required Session Closeout Steps
1. Run the repo truth gate (lint/tests/build or equivalent).
2. Update `feature_list.json` with pass/fail and notes.
3. Update `claude-progress.md` with a dated execution record.
4. Commit repo changes with a scoped message.
5. Update `server-state.md` only when infrastructure changed.

## Core Agent Behavioral Rules

### Safety
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever).
- When in doubt, ask.

### External Actions (ask first)
- Sending emails, tweets, public posts.
- Anything that leaves the machine.
- Anything you're uncertain about.

### Group Chat Etiquette
**Respond when:** directly mentioned, can add genuine value, witty/funny fits naturally, correcting misinformation, summarizing when asked.

**Stay silent when:** casual banter, already answered, would just be "yeah", conversation flowing fine.

**Use emoji reactions** for lightweight acknowledgment (👍, ❤️, 🙌, 💀, 🤔).

### Heartbeat vs Cron Selection
**Use heartbeat when:** multiple checks can batch, need conversational context, timing can drift (~30 min), want to reduce API calls.

**Use cron when:** exact timing matters, task needs isolation, different model/thinking level, one-shot reminders.

## Meta-Learning Loops

### Regression Guardrails
Every significant failure becomes a named rule in AGENTS.md:
```
- [YYYY-MM-DD] failure_description: symptom → fix_rule
```

### Friction Log
New friction between instructions gets logged, not silently overridden. Surface at next natural break.

## Quality Checks
- Confirm notes reference real command outcomes.
- Confirm unresolved blockers are explicitly recorded.
- Confirm no unrelated services were modified.

CONFLICT TEST NUC2 $(date)

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Truth Gate](../concepts/truth-gate.md)
- [Clawd Agent Rules](../projects/clawd-agent-rules.md)
- [Workspace Agent Rules](../projects/workspace-agent-rules.md)
