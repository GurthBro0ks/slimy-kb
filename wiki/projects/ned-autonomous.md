# Ned Autonomous
> Category: projects
> Sources: raw/articles/nuc1-seed-ned-autonomous-readme.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

Ned Autonomous is the NUC1-side orchestration project that keeps an autonomous agent loop running and routes background work.

## Core Systems
- Agent loop with a heartbeat cadence.
- Task router with skill-based scoring.
- Prioritization and anomaly detection components.
- Federation routing for NUC1 <-> NUC2 coordination.

## Role in the Stack
- Acts as a long-running coordination runtime, distinct from request/response app services.
- Connects naturally with mailbox and cross-NUC transport patterns by handling persistent operational loops.

## See Also
- [Harness Runtime Topology](../architecture/harness-runtime-topology.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
- [Clawd Workspace Governance](clawd-workspace-governance.md)
