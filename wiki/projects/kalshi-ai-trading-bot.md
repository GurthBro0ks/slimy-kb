# Kalshi AI Trading Bot
> Category: projects
> Sources: raw/decisions/2026-04-09-project-kalshi-ai-trading-bot.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 19:36 UTC (git)
> Version: r2 / 98f6e61
KB METADATA -->

Autonomous trading bot for Kalshi prediction markets powered by a five-model AI ensemble. Five LLMs debate every trade; system only enters when they agree. Ships with discipline systems (category scoring, portfolio enforcement, risk guardrails).

## Runtime State (NUC1)
- **Path:** `/opt/slimy/research/kalshi-ai-trading-bot`
- **Remote:** `https://github.com/ryanfrigo/kalshi-ai-trading-bot.git`, branch `main`
- **Status:** ACTIVE — ahead of remote by 12 commits
- **Type:** Application (research/experimental)
- **Truth gate:** `cd /opt/slimy/research/kalshi-ai-trading-bot && python -c "import toml; print(toml.load(open('pyproject.toml'))['project']['name'])"` (verify pyproject.toml valid)

## Dependencies
- Python 3.12+, Kalshi API, CoinGecko, Finnhub

## Architecture
- **Five-model AI ensemble** — five LLMs debate every trade; system only enters on consensus
- Discipline systems: category scoring, portfolio enforcement, risk guardrails

## Risks
- External GitHub repo (ryanfrigo) — moves independently
- Experimental/research status

## See Also
- [PM UpDown Bot Bundle](pm-updown-bot-bundle.md)
