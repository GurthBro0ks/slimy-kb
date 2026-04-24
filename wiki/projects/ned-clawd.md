# Ned-Clawd
> Category: projects
> Sources: raw/decisions/2026-04-09-project-ned-clawd.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-24 12:32 UTC (git)
> Version: r40 / 7cf9103
KB METADATA -->

AI agent workspace with session management, memory protocols, heartbeats, and group chat safety. Acts as the host workspace for the Actionbook subdirectory and provides Mission Control integration scripts. NUC1.

## Why It Matters

Ned-Clawd is the primary agent workspace on NUC1. It is not just a passive workspace — it actively manages the OpenCLAW agent ecosystem through cron-based registration scripts. When workspace-executor and workspace-researcher need to be registered with the OpenCLAW gateway, ned-clawd's cron jobs handle it. It also contains the Actionbook project as a subdirectory, making it a hub for browser automation capabilities.

## Runtime State (NUC1)
- **Path:** `/home/slimy/ned-clawd`
- **Remote:** `git@github.com:GurthBro0ks/ned-clawd.git`, branch `master`
- **Status:** ACTIVE
- **AGENTS.md:** YES — SOUL.md/USER.md/MEMORY.md based personal agent workspace
- **Truth gate:** `git -C /home/slimy/ned-clawd log -1 --oneline`
- **Services:** none (workspace-only)
- **Note:** Has its own AGENTS.md with session rules

## Current Role in the System
- Host workspace for the Actionbook browser automation engine (`/home/slimy/ned-clawd/actionbook`)
- Manages OpenCLAW agent registration via cron scripts
- Contains `scripts/mc-notify.sh` for Mission Control integration (notifications to NUC2)
- Runs 12+ cron jobs: heartbeat, mc-comms, watchdog, step-executor, agent registration

## Active Cron Registration
- `register-agents.sh` runs: every hour, every 2 hours, and at reboot
- Registers workspace-executor and workspace-researcher with the OpenCLAW gateway
- Source: `/home/slimy/ned-clawd/scripts/register-agents.sh`

## Important Files / Services
| Path | Purpose |
|------|---------|
| `AGENTS.md` | Session rules for agents operating in this workspace |
| `SOUL.md` | Agent identity and personality |
| `USER.md` | User context and preferences |
| `MEMORY.md` | Long-term curated memory |
| `memory/` | Daily session logs |
| `scripts/register-agents.sh` | Registers executor + researcher with OpenCLAW gateway |
| `scripts/mc-notify.sh` | Sends notifications to Mission Control on NUC2 |
| `actionbook/` | Actionbook browser automation engine (subdirectory) |

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-24T12:32:09Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `d6bada4` — docs: auto-sync project docs from slimy-nuc1 2026-04-11
**Branch:** master

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: ned-clawd (repo_drift, 19x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## Relationships / Dependencies
- **Contains:** Actionbook (subdirectory)
- **Registers:** workspace-executor, workspace-researcher (via cron)
- **Notifies:** Mission Control on NUC2 (via mc-notify.sh)
- **Related workspaces:** Clawd (similar but separate workspace)

## See Also
- [Clawd](clawd.md) — similar agent workspace on NUC1
- [OpenCLAW Agents](openclaw-agents.md) — the agents ned-clawd registers
- [Ned-Autonomous](ned-autonomous.md) — parent PM2 process
- [Actionbook](actionbook.md) — browser automation engine hosted here
- [Mission Control](mission-control.md) — receives notifications from mc-notify.sh
