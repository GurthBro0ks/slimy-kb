# Apify Market Scanner — NUC1 Runtime Update
- Host: nuc1
- Project: apify-market-scanner
- Date: 2026-04-09
- Type: supplemental

## Gap: Wiki Article Missing Runtime Details

The existing wiki article (`projects/apify-market-scanner.md`) marks runtime status as UNKNOWN. Updated findings below.

## NUC1 Runtime State (2026-04-09)
- **Path:** `/opt/slimy/apify-market-scanner`
- **Remote:** `git@github.com:GurthBro0ks/apify-market-scanner.git`
- **Branch:** master; last commit `51a84b0` ("docs: auto-sync")
- **Dirty:** YES (1 uncommitted)
- **Status:** MAINTENANCE — not actively run as a service
- **No PM2 process, no systemd service, no Docker container**
- **No cron entries found** referencing this repo directly

## Integration Point
May be invoked by `pm_updown_bot_bundle` data collection (`ml/data_collector` every 2h), but unconfirmed.

## Recommendation
Classify as MAINTENANCE/IDLE rather than UNKNOWN. Not actively deployed on NUC1.