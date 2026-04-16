# Apify Market Scanner
> Category: projects
> Sources: raw/decisions/2026-04-05-project-apify-market-scanner-nuc1-state.md, raw/agent-learnings/2026-04-09-nuc1-apify-market-scanner-update.md
> Created: 2026-04-05
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 19:36 UTC (git)
> Version: r4 / bc27293
KB METADATA -->

Apify Market Scanner is an Apify-based market data scraping tool for the trading pipeline.

## Identification
- **GitHub:** GurthBro0ks/apify-market-scanner
- **Local path:** `/opt/slimy/apify-market-scanner`
- **Remote:** `git@github.com:GurthBro0ks/apify-market-scanner.git`
- **Branch:** master; last commit `51a84b0` ("docs: auto-sync")
- **Dirty:** YES (1 uncommitted)

## Runtime Status — MAINTENANCE/IDLE

No active service on NUC1 (confirmed 2026-04-09):
- No PM2 process
- No systemd service
- No Docker container
- No cron entries referencing this repo directly

**Integration point:** May be invoked by `pm_updown_bot_bundle` data collection (`ml/data_collector` every 2h), but unconfirmed.

## Classification
- **MAINTENANCE/IDLE** — Not actively deployed as a service
- Last commit predates active pm_updown_bot_bundle development
- Runtime evidence: absent; integration unconfirmed

## See Also
- [PM UpDown Bot Bundle](pm-updown-bot-bundle.md)
