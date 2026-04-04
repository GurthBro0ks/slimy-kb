# Memory Capture Pattern
> Category: patterns
> Sources: raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

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

## See Also
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Session Closeout Pattern](session-closeout-pattern.md)
