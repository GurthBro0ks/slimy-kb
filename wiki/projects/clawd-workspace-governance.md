# Clawd Workspace Governance
> Category: projects
> Sources: raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, raw/decisions/nuc1-seed-ned-clawd-agents.md, raw/decisions/nuc1-seed-workspace-executor-agents.md, raw/decisions/nuc1-seed-workspace-researcher-agents.md
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

## Role Split in the Workspace Family
- `ned-clawd` defines memory and heartbeat behavior for the main personal workspace context.
- `workspace-executor` and `workspace-researcher` share the same session/memory contract, enabling consistent behavior across execution and research roles.
- Common policy across all three: preload identity and recent memory files, keep durable notes on disk, and avoid cross-context leakage of curated long-term memory.
- This makes operator expectations portable when workflows move between autonomous, research, and execution contexts.

## See Also
- [Memory Capture Pattern](../patterns/memory-capture-pattern.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Ned Autonomous](ned-autonomous.md)
