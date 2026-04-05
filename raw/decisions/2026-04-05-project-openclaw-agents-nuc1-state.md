---
description: NUC1 OpenCLAW workspace agents — workspace-executor, workspace-researcher, openclaw-gateway
type: reference
---

# Project: OpenCLAW Agents — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
Two workspace agents exist as local-only repos (no git remote):

### workspace-executor
- **Local path:** `/home/slimy/.openclaw/workspace-executor`
- **Branch:** master (detached HEAD, no commits)
- **Dirty:** YES — untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`
- **AGENTS.md:** Yes

### workspace-researcher
- **Local path:** `/home/slimy/.openclaw/workspace-researcher`
- **Branch:** master (detached HEAD, no commits)
- **Dirty:** YES — untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`
- **AGENTS.md:** Yes

### openclaw-gateway
- **Local path:** Not a git repo — gateway process
- **Ports:** 18789, 18790, 18791, 18792 (localhost only)
- **Process owner:** Managed by ned-autonomous / ned-clawd registration

## Classification
- **ACTIVE** — HIGH confidence

## Runtime Evidence

### openclaw-gateway (ports 18789-18792)
- Listens on localhost only
- Manages lifecycle of workspace-executor and workspace-researcher
- Referenced in `/home/slimy/.claude/openclaw.json`

### ned-clawd Registration (cron-driven)
- `register-agents.sh` runs at: every hour, every 2 hours, and at reboot
- Registers workspace agents with openclaw-gateway
- Source: `/home/slimy/ned-clawd/scripts/register-agents.sh`

### ned-autonomous (PM2: agent-loop)
- PM2 id 0, online, 17.4mb
- Core autonomous orchestrator that drives OpenCLAW workspace agents

## Architecture
```
ned-autonomous (PM2 agent-loop)
  └── openclaw-gateway (ports 18789-18792, localhost)
        ├── workspace-executor (local-only repo)
        └── workspace-researcher (local-only repo)

ned-clawd (cron) → register-agents.sh → registers above with gateway
```

## Relationship to Clawd Workspace Governance
- The `clawd-workspace-governance.md` wiki article covers the governance model for these agents
- This doc covers the NUC1 runtime state and evidence for the actual workspace agent processes

## KB Gap
- No wiki/projects article exists specifically for openclaw-agents
- Clawd Workspace Governance (projects/clawd-workspace-governance.md) covers the governance model but not the runtime state of the specific workspace agents
- This raw doc should feed a new or updated wiki/projects article

## Risks / Anomalies
- workspace-executor and workspace-researcher have no git remotes — local-only
- Detached HEAD with no commits — managed by openclaw-gateway, not git
- Both have dirty untracked files (AGENTS.md, BOOTSTRAP.md, .openclaw/)

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
