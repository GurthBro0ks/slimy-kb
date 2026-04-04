# PM UpDown Bot Bundle
> Category: projects
> Sources: raw/decisions/seed-pm_updown_bot_bundle-agents.md
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

## See Also
- [Agent Session Contract](../concepts/agent-session-contract.md)
- [Truth Gate](../concepts/truth-gate.md)
