---
description: NUC1 apify-market-scanner — Apify-based market data scraping, UNKNOWN runtime status
type: reference
---

# Project: Apify Market Scanner — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Project name:** apify-market-scanner
- **GitHub:** GurthBro0ks/apify-market-scanner
- **Local path:** `/opt/slimy/apify-market-scanner`
- **Branch:** master
- **Last commit:** `dd8beb5` 2026-02-27
- **Dirty:** NO
- **README:** Yes

## Classification
- **UNKNOWN** — LOW confidence
- No direct runtime evidence found in cron, PM2, systemd, or Docker

## Runtime Evidence

### Cron: NOT FOUND
- No cron entries reference apify-market-scanner directly

### PM2: NOT FOUND
- No PM2 processes reference apify-market-scanner

### systemd: NOT FOUND
- No systemd services reference apify-market-scanner

### Docker: NOT FOUND
- No Docker containers reference apify-market-scanner

## Possible Integration
- Discovery report notes it "may be referenced by pm_updown_bot_bundle data collection"
- pm_updown_bot_bundle runs `ml/data_collector` every 2 hours — may invoke apify
- No direct grep evidence confirmed in discovery scan

## Relationship to pm_updown_bot_bundle
- If apify-market-scanner is used, it feeds market data into the trading bot's ML pipeline
- Last commit 2026-02-27 — older than active pm_updown_bot_bundle development (which had commits through 2026-04-05)

## Risks / Anomalies
- UNKNOWN classification — needs verification whether it's actively invoked
- Could be a data source for pm_updown_bot_bundle that was since replaced
- Recommend: grep pm_updown_bot_bundle for apify references to confirm or deny

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
