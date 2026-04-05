# PM UpDown Bot Bundle
> Category: projects
> Sources: raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc1-state.md
> Created: 2026-04-04
> Updated: 2026-04-05
> Status: draft

This bundle hosts trading bot strategy code, venue connectors, and operations scripts.

## Structure
- `runner.py` as process entrypoint.
- `strategies/` and `venues/` for decision logic and exchange integration.
- `utils/`, `scripts/`, `docs/`, and `notes/` for support and operations.

## Guardrails
- Truth gate is required before considering work complete.
- Secret-bearing zones (`.env*`, `secrets/**`, production infra material) are off-limits.

## NUC1 Runtime State (2026-04-05)
- **Path:** `/opt/slimy/pm_updown_bot_bundle`
- **Branch:** `feat/ibkr-forecast-integration`; last commit `0a92d84` 2026-04-05
- **Dirty:** YES — uncommitted `.venv/`, `data/holdout_pnl.db`, `data/ml_label_cache.json`
- **Scheduler:** CRON (20+ entries), NOT PM2
- **Key cron entries:**
  - Every 2h: `strategies/kalshi_optimize.py --mode shadow` (timeout 600s), `scripts/knowledge-exporter.py`
  - Daily 8am/8pm: `run_with_monitoring.sh`
  - Daily 11am/1am: `runner.py --phase all` (timeout 900s)
  - Every 2h: `ml.data_collector` (timeout 120s)
  - Daily 6am Sunday: `scripts/bootstrap_validator.py`
  - Daily 6am/2pm: `runner.py --strategy weather --mode shadow` (timeout 600s)
  - Daily noon: `runner.py --mode micro-live` (timeout 60s)
- **ML pipeline:** data collection, label resolution, shadow resolution
- **Supersedes:** `research/kalshi-ai-trading-bot` (LEGACY_CANDIDATE)

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Truth Gate](../concepts/truth-gate.md)
