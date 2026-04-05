# Apify Market Scanner
> Category: projects
> Sources: raw/decisions/2026-04-05-project-apify-market-scanner-nuc1-state.md
> Created: 2026-04-05
> Status: draft

Apify Market Scanner is an Apify-based market data scraping tool for the trading pipeline.

## Identification
- **GitHub:** GurthBro0ks/apify-market-scanner
- **Local path:** `/opt/slimy/apify-market-scanner`
- **Branch:** master; last commit `dd8beb5` 2026-02-27
- **Dirty:** NO

## Runtime Status — UNKNOWN

No direct runtime evidence found on NUC1:
- No cron entries reference it
- No PM2 process
- No systemd service
- No Docker container

**Possible integration:** May be invoked by pm_updown_bot_bundle data collection (`ml/data_collector` every 2h), but this has not been confirmed by grep.

## Classification
- **UNKNOWN** — LOW confidence as active component
- Last commit predates active pm_updown_bot_bundle development
- Recommend: grep pm_updown_bot_bundle for apify references to confirm or deny

## See Also
- [PM UpDown Bot Bundle](pm-updown-bot-bundle.md)
