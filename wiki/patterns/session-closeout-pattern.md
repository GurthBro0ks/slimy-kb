# Session Closeout Pattern
> Category: patterns
> Sources: raw/decisions/seed-agents-rules.md, raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-16
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-25 00:33 UTC (git)
> Version: r45 / f9c7f6a
KB METADATA -->

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

## Session Finish Behavior

The harness Stop hook (`slimy-session-finish.sh`) runs automatically at session end. It dispatches based on exit type:

- **INTERRUPTED** (Ctrl+C / SIGINT): skip all finish automation, exit 0 — no Discord ALERT, no repo sync
- **SUCCESS** (exit 0): bounded quiet finish — kb-compile, sync active repo only, no Discord ALERT
- **ERROR** (exit ≠0): bounded finish with alerts — sync active repo, post bounded Discord ALERT on failure

Bounded scope = active repo only. `--quiet` on `slimy-agent-finish.sh` suppresses ALERT; `--repo /path` activates bounded mode (no multi-repo scan).

### Doc-Sync Hygiene (Phases 1–4, Complete 2026-04-16)

The session finish doc-sync subsystem now has four guardrail layers preventing noisy multi-repo auto-sync:

1. **Allowlist** (`kb/config/doc-sync-allowlist.txt`): only listed repos are eligible for doc-sync. 6 repos currently allowed.
2. **Skip guards**: dirty trees with non-doc changes, repos with no remote, and already-synced-today repos are all skipped.
3. **Session-scoped default**: `slimy-agent-finish.sh` without `--repo` or `--scan-all` touches zero repos. Broad sweep requires explicit `--scan-all`.
4. **Daily dedupe**: if HEAD is already today's auto-sync commit and no doc files are dirty, skip entirely.

Result: the broad/noisy multi-repo doc-sync behavior that previously caused mission-control divergence (15/4) is no longer the default.

See [Harness Runtime Topology](../architecture/harness-runtime-topology.md) for the full dispatch matrix and detailed phase documentation.

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Truth Gate](../concepts/truth-gate.md)
- [Clawd Agent Rules](../projects/clawd-agent-rules.md)
- [Workspace Agent Rules](../projects/workspace-agent-rules.md)
