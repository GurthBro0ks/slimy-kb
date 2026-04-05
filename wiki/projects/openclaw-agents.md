# OpenCLAW Agents
> Category: projects
> Sources: raw/decisions/2026-04-05-project-openclaw-agents-nuc1-state.md
> Created: 2026-04-05
> Status: draft

OpenCLAW workspace agents are the execution and research subagents managed by the OpenCLAW gateway on NUC1.

## Workspace Agents

### workspace-executor
- **Path:** `/home/slimy/.openclaw/workspace-executor`
- **Remote:** NONE (local-only)
- **Branch:** master (detached HEAD, no git commits)
- **Dirty:** YES — untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`

### workspace-researcher
- **Path:** `/home/slimy/.openclaw/workspace-researcher`
- **Remote:** NONE (local-only)
- **Branch:** master (detached HEAD, no git commits)
- **Dirty:** YES — untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`

## Gateway

### openclaw-gateway
- **Ports:** 18789, 18790, 18791, 18792 (localhost only)
- **Config:** `/home/slimy/.claude/openclaw.json`
- **Process owner:** Managed by ned-autonomous (PM2 agent-loop) and ned-clawd (cron registration)

## Active Cron Registration (ned-clawd)
- `register-agents.sh` runs: every hour, every 2 hours, and at reboot
- Registers workspace-executor and workspace-researcher with the gateway
- Source: `/home/slimy/ned-clawd/scripts/register-agents.sh`

## Architecture
```
ned-autonomous (PM2 agent-loop)
  └── openclaw-gateway (ports 18789-18792, localhost)
        ├── workspace-executor
        └── workspace-researcher

ned-clawd (cron) → register-agents.sh → registers with gateway
```

## Governance
Memory and session discipline for workspace agents is covered in [Clawd Workspace Governance](clawd-workspace-governance.md).

## See Also
- [Ned-Autonomous](ned-autonomous.md)
- [Clawd Workspace Governance](clawd-workspace-governance.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
