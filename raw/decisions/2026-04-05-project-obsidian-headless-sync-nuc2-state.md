---
description: NUC2 obsidian-headless-sync — only PM2 process on NUC2, vault sync service
type: reference
---

# Project: Obsidian Headless Sync — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** obsidian-headless-sync
- **GitHub:** unknown
- **Local path:** N/A (PM2-managed only, not a git repo in standard sense)
- **PM2 name:** obsidian-headless-sync

## Classification
- **ACTIVE** — HIGH confidence

## NUC2 Runtime Evidence

### PM2 (only PM2 process on NUC2)
```
@limy:~$ pm2 list
┌────┬───────────────────────────┬─────────┬──────┐
│ id │ name                    │ status  │ uptime │
├────┼───────────────────────────┼─────────┼──────┤
│ 0  │ obsidian-headless-sync │ online  │ 105m   │
```
- PM2 id: 0
- Status: online
- Uptime: 105 minutes at time of scan
- Memory: 72.4mb
- Restarts: 0
- CPU: 0%
- PID: 3258479
- Mode: fork
- User: slimy
- Disabled: yes (PM2 disabled, but process still online)

### PM2 Configuration
- `pm2 disabled` — means startup resurrection is disabled, but process is still running
- This is the **only PM2 process** on NUC2

## KB Gap
- No wiki/projects/ article exists
- No raw/ source doc exists
- Should be documented given it is the sole PM2-managed service on NUC2

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
