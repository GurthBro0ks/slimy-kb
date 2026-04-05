# Clawd Workspace Governance
> Category: projects
> Sources: raw/decisions/seed-clawd-agents.md, raw/decisions/seed-workspace-agents.md, raw/decisions/2026-04-05-project-ned-clawd-nuc1-state.md
> Created: 2026-04-04
> Updated: 2026-04-05
> Status: draft

The Clawd/workspace agent docs define memory governance and session discipline for local autonomous workflows.

## Governance Model
- Every-session checklists are explicit and repeatable.
- Memory is split between daily logs and curated long-term memory.
- Security posture forbids loading private long-term memory in shared contexts.

## Practical Outcome
- Agents maintain continuity across resets.
- Lessons become persistent operations guidance instead of one-off chat context.

## NUC1 Runtime State — Ned-Clawd (2026-04-05)
- **Path:** `/home/slimy/ned-clawd`
- **GitHub:** GurthBro0ks/ned-clawd; branch `master`; last commit `6c73dae` 2026-03-23
- **Dirty:** YES — untracked `comms/` directory
- **Active cron jobs (12+):**
  - `*/5 * * * *` — heartbeat.sh
  - `* * * * *` — mc-comms-bot.sh (every minute, primary comms agent)
  - `*/2 * * * *` — step-executor.sh
  - `*/15 * * * *` — watchdog.sh
  - `0 8 * * *` — daily-briefing.sh
  - `0 23 * * *` — nightly-memory-extract.sh
  - `0 */2 * * *` + `0 * * * *` + `@reboot` — register-agents.sh (overlapping schedules)
  - `*/5 * * * *` — resource-monitor.py
  - `@reboot` — agent-health-monitor.py
- **OpenCLAW gateway:** Ports 18789-18792 (localhost); manages workspace-executor and workspace-researcher
- See also: [Ned-Autonomous](ned-autonomous.md), [OpenCLAW Agents](openclaw-agents.md)

## See Also
- [Memory Capture Pattern](../patterns/memory-capture-pattern.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
