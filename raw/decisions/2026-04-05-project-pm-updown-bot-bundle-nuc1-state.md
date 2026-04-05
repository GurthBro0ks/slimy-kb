---
description: NUC1 runtime evidence for pm_updown_bot_bundle — heavy cron automation, ML pipeline, shadow scanner
type: reference
---

# Project: PM UpDown Bot Bundle — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Project name:** pm_updown_bot_bundle
- **GitHub:** GurthBro0ks/pm_updown_bot_bundle
- **Local path:** `/opt/slimy/pm_updown_bot_bundle`
- **Branch:** feat/ibkr-forecast-integration
- **Last commit:** `0a92d84` 2026-04-05 — "feat: get_ai_stock_sentiment stub + defensive import fix"
- **Dirty:** YES — uncommitted: `.venv/`, `data/holdout_pnl.db`, `data/ml_label_cache.json`

## Classification
- **ACTIVE** — HIGH confidence

## NUC1 Runtime Evidence

### Cron Jobs (20+ entries)
```
# Every-2-hour shadow scanning + optimization
0 */2 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 600 python3 strategies/kalshi_optimize.py --mode shadow
0 */2 * * * python3 scripts/knowledge-exporter.py

# Morning/evening full runs
0 8,20 * * * /opt/slimy/pm_updown_bot_bundle/run_with_monitoring.sh >> logs/cron.log
0 11,1 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 900 runner.py --phase all

# ML pipeline
30 */2 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 120 .venv/bin/python3 -m ml.data_collector
0 6 * * 0 cd /opt/slimy/pm_updown_bot_bundle && python3 scripts/bootstrap_validator.py
30 5 * * * cd /opt/slimy/pm_updown_bot_bundle && python3 scripts/shadow_resolver.py

# Strategy runs
0 6,14 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 600 runner.py --strategy weather --mode shadow
0 12 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 60 runner.py --mode micro-live

# Weekly
0 8 * * 0 /opt/slimy/pm_updown_bot_bundle/scripts/pnl-weekly-report.sh
```

### Process Manager
- NOT PM2 — runs via cron + runner.py directly
- `.venv` used for ML dependencies

### Ports
- NONE directly — no listening ports; purely batch/cron-driven

### Entry Points
- `runner.py` — primary process entrypoint
- `strategies/kalshi_optimize.py` — every-2-hour shadow optimization
- `scripts/knowledge-exporter.py` — every-2-hour export
- `ml/data_collector` — every-2-hour data collection
- `ml/label_resolver` — daily label resolution

## Relationship to Other Projects
- Supersedes `/opt/slimy/research/kalshi-ai-trading-bot` (LEGACY_CANDIDATE)
- `apify-market-scanner` may feed into data collection (UNCONFIRMED)
- PM2 NOT used — cron is primary scheduler

## Risks / Anomalies
- Dirty git state — .venv, holdout_pnl.db, ml_label_cache.json uncommitted
- Multiple concurrent cron entries with timeout guards (600s, 900s, 120s)
- QA work ongoing: 24 pytest tests passing (2026-04-05 session)

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
