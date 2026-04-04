# NUC Topology and Services
> Category: architecture
> Sources: raw/decisions/seed-server-state.md, raw/decisions/seed-agents-rules.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

SlimyAI is split across NUC1 and NUC2 with clear service boundaries.

## Placement Model
- NUC1 runs core infra dependencies (MySQL, Caddy, chat service, agent loop).
- NUC2 runs primary web workloads (Next.js web app, mission-control, legacy PostgreSQL).
- Bot process management uses PM2 where applicable; web supervision is systemd user service on NUC2.

## Repository Layout
- Canonical monorepo path: `/opt/slimy/slimy-monorepo`.
- `/home/slimy/slimy-monorepo` is a symlink and should not be replaced with a fresh clone.

## Operational Implications
- Service ownership and ports must be validated against server-state before restarts.
- Cross-host DB access requires explicit grants and tunnel validation.

## See Also
- [Auth and Retired Services](auth-and-retired-services.md)
- [Cross-NUC Communication Matrix](cross-nuc-communication-matrix.md)
- [Harness Runtime Topology](harness-runtime-topology.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
