# Apify Market Scanner
> Category: projects
> Sources: raw/decisions/2026-04-05-project-apify-market-scanner-nuc1-state.md, raw/agent-learnings/2026-04-09-nuc1-apify-market-scanner-update.md
> Created: 2026-04-05
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-19 00:25 UTC (git)
> Version: r16 / 2b8f6a1
KB METADATA -->

Apify-based market data scraping tool for the trading pipeline. Currently in MAINTENANCE/IDLE status — not actively deployed or running.

## Why It Matters

This tool was built to feed market data into the trading pipeline (pm_updown_bot_bundle). Its current dormancy means the trading pipeline may be missing a data source. If the trading bot resumes active trading, this scanner may need to be reactivated or replaced.

## Identification
- **GitHub:** GurthBro0ks/apify-market-scanner
- **Local path:** `/opt/slimy/apify-market-scanner` (NUC1)
- **Remote:** `git@github.com:GurthBro0ks/apify-market-scanner.git`
- **Branch:** master; last commit `51a84b0` ("docs: auto-sync")
- **Dirty:** YES (1 uncommitted)

## Runtime Status — MAINTENANCE/IDLE

No active service on NUC1 (confirmed 2026-04-09):
- No PM2 process
- No systemd service
- No Docker container
- No cron entries referencing this repo directly

## Current Role in the System
- **Dormant.** Last commits are auto-sync docs only.
- May have been a data source for `pm_updown_bot_bundle` data collection (`ml/data_collector` runs every 2h on NUC1), but this integration is unconfirmed.
- No services to monitor, no health checks needed.

## Known Status
- 1 uncommitted change in working tree
- No active development
- Repo receives auto-sync docs commits passively

## Relationships / Dependencies
- **Downstream of:** Apify platform (external)
- **Upstream of:** Possibly pm_updown_bot_bundle (unconfirmed)
- **Related:** [PM UpDown Bot Bundle](pm-updown-bot-bundle.md)

## Operational Notes
- If trading pipeline resumes, check whether Apify actors need reactivation
- The dirty working tree should be investigated if this project is reactivated
- Consider archiving or removing if trading pipeline moves to different data sources

## See Also
- [PM UpDown Bot Bundle](pm-updown-bot-bundle.md)
- [Kalshi AI Trading Bot](kalshi-ai-trading-bot.md) — other trading project
- [NUC1 Current State](../architecture/nuc1-current-state.md)
