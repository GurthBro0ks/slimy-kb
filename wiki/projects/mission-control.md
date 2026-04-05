# Mission Control
> Category: projects
> Sources: raw/articles/seed-mission-control-readme.md, raw/decisions/2026-04-05-project-mission-control-nuc2-state.md
> Created: 2026-04-04
> Updated: 2026-04-05
> Status: draft

Mission Control is a coordination surface for tasks, agents, comms, calendar, memory, and webhook-triggered workflows.

## NUC2 Runtime State (2026-04-05)
- **Path:** `/home/slimy/mission-control`
- **Remote:** `git@github.com:GurthBro0ks/mission-control.git`, branch `main`
- **Last commit:** `78ff4be9` 2026-04-03 (2 days ago)
- **Dirty:** YES — modified `next.config.ts`
- **Supervisor:** `systemd --user` (`mission-control.service`)
- **State:** ACTIVE, running
- **Port:** **3838** — `next-server (v16.1.6)` pid 2311610, listening on 0.0.0.0:3838
- **Classification:** ACTIVE | Confidence: HIGH

## Surface Areas
- REST endpoints for task lifecycle and agent operations.
- Calendar and communication endpoints for orchestration.
- Memory endpoints for file listing, search, and retrieval.
- Webhook ingestion for external automation triggers.

## Startup
- Quick-start uses local package install and dev server launch.
- Health endpoint is the first operational probe.

## See Also
- [Agents Plugin Ecosystem](agents-plugin-ecosystem.md)
- [Truth Gate](../concepts/truth-gate.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
