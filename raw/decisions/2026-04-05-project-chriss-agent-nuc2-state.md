---
description: NUC2 chriss-agent — webhook bridge service running on port 3850, active since Mar14
type: reference
---

# Project: Chriss Agent — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** chriss-agent
- **GitHub:** none (no remote)
- **Local path:** `/home/slimy/chriss-agent`
- **Remote:** none (not a git repo)
- **Dirty:** unknown

## Classification
- **ACTIVE** — HIGH confidence

## NUC2 Runtime Evidence

### Process (no systemd/PM2 — raw process)
```
python3 /home/slimy/chriss-agent/scripts/webhook-bridge.py
```
- PID: 1178942
- Running since: 2026-03-14
- Port: **3850**

### systemd (inferred)
- `chriss-bridge.service` — systemd unit inferred from ps/process naming (not confirmed active in systemctl output at scan time)
- If chriss-bridge.service exists, it manages this process

### Ports
| Port | Process |
|------|---------|
| 3850 | python3 webhook-bridge.py (chriss-agent) |

## KB Gap
- **No wiki/projects/ article exists** — chriss-agent was explicitly listed as a HIGH-priority missing article in the discovery report
- No references found in Cross-NUC Communication Matrix or NUC Topology

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
