# Source of Truth Ledgers
> Category: concepts
> Sources: raw/decisions/seed-agents-rules.md, raw/agent-learnings/seed-progress-history.md, raw/decisions/seed-server-state.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-22 00:28 UTC (git)
> Version: r28 / d9b49c6
KB METADATA -->

SlimyAI operations rely on three ledgers that must remain current every session.

## Primary Ledgers
- `/home/slimy/claude-progress.md`: chronological execution history and outcomes.
- `/home/slimy/feature_list.json`: feature backlog and pass/fail status.
- `/home/slimy/server-state.md`: current infra topology, health, and service ownership.

## Operating Use
- Read all three at session start.
- Update relevant records at session close.
- Keep entries concrete (what changed, what passed, what remains blocked).

## Data Integrity Rules
- Do not overwrite historical context; append new dated records.
- Keep pass/fail states aligned with actual verification output.
- Record blockers explicitly when a task is partial or externally blocked.

## See Also
- [Agent Session Contract](agent-session-contract.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Harness Runtime Topology](../architecture/harness-runtime-topology.md)
- [Knowledge Base Build Pipeline](../architecture/knowledge-base-build-pipeline.md)
