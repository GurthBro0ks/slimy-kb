# PM UpDown Bot Bundle
> Category: projects
> Sources: raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/articles/nuc1-seed-apify-market-scanner-readme.md, raw/articles/nuc1-seed-kalshi-ai-trading-bot-readme.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

This bundle hosts trading bot strategy code, venue connectors, and operations scripts.

## Structure
- `runner.py` as process entrypoint.
- `strategies/` and `venues/` for decision logic and exchange integration.
- `utils/`, `scripts/`, `docs/`, and `notes/` for support and operations.

## Guardrails
- Truth gate is required before considering work complete.
- Secret-bearing zones (`.env*`, `secrets/**`, production infra material) are off-limits.

## Related Trading Tooling on NUC1
- A prediction-market data scanner is maintained as an Apify actor profile, combining Kalshi market snapshots, CoinGecko pricing, and optional Finnhub sentiment inputs.
- A separate Kalshi-focused ensemble bot reference exists in the environment as strategy research context (multi-model consensus, risk controls, dashboarding).
- Operational rule: these are reference implementations, while canonical production workflow remains the `pm_updown_bot_bundle` truth-gated repo flow.

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Truth Gate](../concepts/truth-gate.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
