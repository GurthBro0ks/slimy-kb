# Memory Capture Pattern
> Category: patterns
> Sources: raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-26 00:35 UTC (git)
> Version: r44 / cc157bd
KB METADATA -->

This pattern separates short-term logs from durable knowledge.

## Pattern
- Write daily session logs in dated files.
- Maintain curated long-term memory in stable documents.
- Convert repeated lessons into reusable operating docs.

## Benefits
- Prevents context loss between sessions.
- Reduces repeated mistakes by documenting decisions and failure modes.
- Makes handoffs and audits faster across agents.

## Implementation Notes
- Record mistakes and recoveries in plain language.
- Promote recurring operational rules into AGENTS.md or KB concept pages.
- Keep sensitive context isolated from shared or public channels.

## Memory Tier System
Three-tier trust model for persisted knowledge:

| Tier | Trust | Expiry | Use |
|------|-------|--------|-----|
| Constitutional | 1.0 | Never | Security, hard constraints |
| Strategic | 0.9 | Quarterly | Current projects, direction |
| Operational | 0.8 | 30d unused | Temporary bugs, workarounds |

Format: `[trust:X|src:direct|used:YYYY-MM-DD|hits:N]`

## Friction and Regression Tracking
**Friction log** — recurring operational friction:
```
## Friction Log
- [YYYY-MM-DD] <issue> | <symptom> | <root cause> | <fix>
```

**Regression list** — failure-to-guardrail transforms:
```
## Regressions
- [YYYY-MM-DD] <failure description> | Pattern: <frequency> | Fix: <prescription>
```

## Daily Log Structure
- **Path:** `memory/YYYY-MM-DD.md`
- **Content:** raw session events, decisions, outcomes
- **Curated promotion:** distill significant events → `MEMORY.md` (long-term)

## See Also
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Session Closeout Pattern](session-closeout-pattern.md)
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md)
