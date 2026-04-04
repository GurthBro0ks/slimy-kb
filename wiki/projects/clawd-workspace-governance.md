# Clawd Workspace Governance
> Category: projects
> Sources: raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

The Clawd/workspace agent docs define memory governance and session discipline for local autonomous workflows.

## Governance Model
- Every-session checklists are explicit and repeatable.
- Memory is split between daily logs and curated long-term memory.
- Security posture forbids loading private long-term memory in shared contexts.

## Practical Outcome
- Agents maintain continuity across resets.
- Lessons become persistent operations guidance instead of one-off chat context.

## See Also
- [Memory Capture Pattern](../patterns/memory-capture-pattern.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
