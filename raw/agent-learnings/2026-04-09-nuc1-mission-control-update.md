# Mission Control — NUC1 Runtime Update
- Host: nuc1
- Project: mission-control
- Date: 2026-04-09
- Type: supplemental

## Gap: NUC1 Runtime State Missing from Wiki Article

The existing wiki article (`projects/mission-control.md`) only covers NUC2 runtime state. Here is the NUC1 complement:

## NUC1 Runtime State (2026-04-09)
- **Path:** `/home/slimy/mission-control`
- **Remote:** `git@github.com:GurthBro0ks/mission-control.git`
- **Branch:** main
- **Last 3 commits:** `12fc26f`, `0f9c025`, `9d8e028` (all "docs: auto-sync")
- **Dirty:** YES (1 uncommitted)
- **Supervisor:** systemd system service (`mission-control.service`)
- **State:** ACTIVE, running
- **Port:** **3838** — `next-server` pid 4017813, listening on `0.0.0.0:3838`
- **Classification:** ACTIVE | Confidence: HIGH

## Missing from Wiki Article
The wiki article is missing:
- NUC1 systemd service details (port 3838, pid 4017813)
- NUC1 git state (branch, commits)
- Services: Caddy routes traffic to mission-control on 3838

## Related
- Same service runs on NUC2 port 3838 (separate deployment)
- Caddy on NUC1 serves mission-control at its domain routes