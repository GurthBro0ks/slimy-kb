# PM UpDown Bot Bundle
> Category: projects
> Sources: raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc1-state.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc2-state.md, raw/decisions/2026-04-09-project-proofs.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 12:24 UTC (git)
> Version: r12 / 0f1f90b
KB METADATA -->

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

## NUC2 Runtime State (2026-04-05)
- **Path:** `/home/slimy/pm_updown_bot_bundle`
- **Remote:** `git@github.com:GurthBro0ks/pm_updown_bot_bundle.git`, branch `main`
- **Last commit:** `a49674bc` 2026-03-21 (15 days ago)
- **Dirty:** YES — untracked `claude-progress.md`
- **Role on NUC2:** DORMANT — NUC1 is primary; NUC2 is rsync data consumer only
- **NUC2 cron (rsync consumer):**
  - `*/15 * * * *` rsync paper_trading/*.db from NUC1 → `/opt/slimy/trading-data-mirror/paper_trading/`
  - `*/15 * * * *` rsync bootstrap_validation_*.json proofs from NUC1 → mirror target
- **Classification:** DORMANT on NUC2 | Confidence: HIGH

## Proofs Subdirectory
- **Path:** `/opt/slimy/pm_updown_bot_bundle/proofs`
- **GitHub remote:** same as parent (`git@github.com:GurthBro0ks/pm_updown_bot_bundle.git`)
- **Branch:** main
- **Type:** tool (proof-gated workflows subdirectory)
- **Status:** ACTIVE_DIRTY
- **Priority:** low
- **Purpose:** Proof storage for trading bot bundle. Proof-gated workflows require validated proofs before execution.
- **Truth gate:** `git -C /opt/slimy/pm_updown_bot_bundle/proofs log -1 --oneline`
- **Risks:** no independent remote; subdirectory of pm_updown_bot_bundle
- **NUC2 rsync mirror:** `*/15 * * * *` rsync `bootstrap_validation_*.json` proofs from NUC1 → mirror target

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Truth Gate](../concepts/truth-gate.md)
