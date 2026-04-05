---
description: NUC1 runtime evidence for ned-clawd — 12+ cron jobs, autonomous orchestration agents
type: reference
---

# Project: Ned-Clawd — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Project name:** ned-clawd
- **GitHub:** GurthBro0ks/ned-clawd
- **Local path:** `/home/slimy/ned-clawd`
- **Branch:** master
- **Last commit:** `6c73dae` 2026-03-23
- **Dirty:** YES — untracked `comms/` directory

## Classification
- **ACTIVE** — HIGH confidence

## NUC1 Runtime Evidence

### Active Cron Jobs (12+ entries)
```
# heartbeat — every 5 minutes
*/5 * * * * /home/slimy/ned-clawd/scripts/heartbeat.sh

# mc-comms-bot — every minute (primary comms agent)
* * * * * /home/slimy/ned-clawd/scripts/mc-comms-bot.sh

# step-executor — every 2 minutes
*/2 * * * * /home/slimy/ned-clawd/scripts/step-executor.sh

# watchdog — every 15 minutes
*/15 * * * * /home/slimy/ned-clawd/scripts/watchdog.sh

# daily briefing — 8am daily
0 8 * * * /home/slimy/ned-clawd/triggers/daily-briefing.sh

# nightly memory extract — 11pm daily
0 23 * * * /home/slimy/ned-clawd/scripts/nightly-memory-extract.sh

# register-agents — every 2 hours AND every hour AND at reboot
0 */2 * * * /home/slimy/ned-clawd/scripts/register-agents.sh
0 * * * * /home/slimy/ned-clawd/scripts/register-agents.sh
@reboot /home/slimy/ned-clawd/scripts/register-agents.sh

# resource monitoring — every 5 minutes
*/5 * * * * /home/slimy/ned-clawd/scripts/resource-monitor.py

# agent health monitor — at reboot
@reboot /home/slimy/ned-clawd/scripts/agent-health-monitor.py
```

### Agent Scripts
- `heartbeat.sh` — liveness ping for autonomous agents
- `mc-comms-bot.sh` — mission control communications bot
- `step-executor.sh` — step execution agent
- `watchdog.sh` — health watchdog
- `register-agents.sh` — agent registration with openclaw-gateway
- `resource-monitor.py` — resource usage monitoring
- `agent-health-monitor.py` — reboot-persistent agent health check
- `triggers/daily-briefing.sh` — daily briefing trigger

### Relationship to OpenCLAW
- ned-clawd orchestrates OpenCLAW workspace agents via openclaw-gateway (ports 18789-18792)
- The workspace-executor and workspace-researcher (`.openclaw/workspace-*`) are the actual agent processes
- ned-clawd's scripts manage their lifecycle and registration

### Open Ports
- Ports 18789-18792: openclaw-gateway (localhost only)

## Risks / Anomalies
- Dirty: untracked `comms/` directory
- Last commit 2026-03-23 — no commits since then, but runtime evidence shows active use
- Multiple overlapping cron schedules (register-agents at both `/2` and hourly + reboot)

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
