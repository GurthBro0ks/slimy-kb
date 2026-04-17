# Mission Control
> Category: projects
> Sources: raw/articles/seed-mission-control-readme.md, raw/decisions/2026-04-05-project-mission-control-nuc2-state.md, raw/research/2026-04-09-nuc2-project-inventory.md, raw/agent-learnings/2026-04-09-nuc2-mission-control-update.md, raw/agent-learnings/2026-04-09-nuc1-mission-control-update.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 12:24 UTC (git)
> Version: r15 / 0fb4601
KB METADATA -->

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

## NUC2 Runtime State (2026-04-09)
- **Path:** `/home/slimy/mission-control`
- **Remote:** `git@github.com:GurthBro0ks/mission-control.git`, branch `main`
- **Last 3 commits:**
  - `8d33bd3` — docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `573d7a3` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `6cb0e02` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **Supervisor:** `systemd --user` (`mission-control.service`)
- **State:** ACTIVE, running
- **Port:** **3838** — `next-server (v16.1.6)` pid 2311610, listening on 0.0.0.0:3838
- **API:** `/api/health`, `/api/tasks`, `/api/agents`, `/api/calendar`, `/api/comms`, `/api/memory`
- **Truth gate:** `curl http://localhost:3838/api/health`
- **Classification:** ACTIVE | Confidence: HIGH

## NUC1 Runtime State (2026-04-09)
- **Path:** `/home/slimy/mission-control`
- **Remote:** `git@github.com:GurthBro0ks/mission-control.git`, branch `main`
- **Last 3 commits:** `12fc26f`, `0f9c025`, `9d8e028` (all "docs: auto-sync")
- **Dirty:** YES (1 uncommitted)
- **Supervisor:** systemd system service (`mission-control.service`)
- **State:** ACTIVE, running
- **Port:** **3838** — `next-server` pid 4017813, listening on `0.0.0.0:3838`
- **Classification:** ACTIVE | Confidence: HIGH
- **Note:** Same service runs on NUC2 port 3838 (separate deployment). Caddy on NUC1 routes traffic to mission-control at its domain routes.

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-17T12:24:09Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `b106eb1` — chore: install agent harness from slimy-harness
**Branch:** main

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: mission-control (repo_drift, 5x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [Agents Plugin Ecosystem](agents-plugin-ecosystem.md)
- [Truth Gate](../concepts/truth-gate.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
