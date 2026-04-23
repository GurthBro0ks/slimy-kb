# Ned-Autonomous
> Category: projects
> Sources: raw/decisions/2026-04-05-project-ned-autonomous-nuc1-state.md
> Created: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-23 12:30 UTC (git)
> Version: r40 / f998985
KB METADATA -->

Ned-Autonomous is the PM2-managed core autonomous orchestrator on NUC1, running the `agent-loop` process.

## Overview
- **GitHub:** GurthBro0ks/ned-autonomous
- **Local path:** `/home/slimy/ned-autonomous`
- **Branch:** main; last commit `09353c8` 2026-03-18
- **Dirty:** NO

## NUC1 Runtime State (2026-04-05)
- **PM2 id:** 0 (first process — indicates primary orchestrator role)
- **Process name:** `agent-loop`
- **Status:** online
- **Memory:** 17.4mb
- **CPU:** 0%

## Architecture
```
ned-autonomous (PM2 agent-loop, id=0, online)
  └── openclaw-gateway (ports 18789-18792, localhost)
        ├── workspace-executor (local-only repo)
        └── workspace-researcher (local-only repo)

ned-clawd (cron) → register-agents.sh → registers workspace agents with gateway
```

## Relationship to Ned-Clawd
- ned-autonomous is the PM2-managed persistent loop
- ned-clawd scripts (cron-driven) handle agent registration, heartbeat, watchdog, and lifecycle
- Both are required for full autonomous operation

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-23T12:30:10Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `fb5ff79` — chore: auto-sync 2026-04-07
**Branch:** main

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: ned-autonomous (repo_drift, 39x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [Clawd Workspace Governance](clawd-workspace-governance.md)
- [OpenCLAW Agents](openclaw-agents.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
