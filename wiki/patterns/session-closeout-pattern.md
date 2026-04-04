# Session Closeout Pattern
> Category: patterns
> Sources: raw/decisions/seed-agents-rules.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

This pattern standardizes how a work session is closed.

## Required Closeout Steps
1. Run the repo truth gate (lint/tests/build or equivalent).
2. Update `feature_list.json` with pass/fail and notes.
3. Update `claude-progress.md` with a dated execution record.
4. Commit repo changes with a scoped message.
5. Update `server-state.md` only when infrastructure changed.

## Quality Checks
- Confirm notes reference real command outcomes.
- Confirm unresolved blockers are explicitly recorded.
- Confirm no unrelated services were modified.

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Truth Gate](../concepts/truth-gate.md)
