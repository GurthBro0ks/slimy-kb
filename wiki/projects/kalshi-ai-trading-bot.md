# Kalshi AI Trading Bot
> Category: projects
> Sources: raw/decisions/2026-04-09-project-kalshi-ai-trading-bot.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 00:23 UTC (git)
> Version: r7 / 3f6aea2
KB METADATA -->

Autonomous trading bot for Kalshi prediction markets powered by a five-model AI ensemble. Five LLMs debate every trade; system only enters when they agree. Ships with discipline systems (category scoring, portfolio enforcement, risk guardrails).

## Why It Matters

This is an experimental research project exploring multi-LLM consensus for prediction market trading. It represents a novel approach to AI-driven trading where no single model makes the decision — consensus is required. The discipline systems (category scoring, portfolio enforcement) are guardrails that prevent reckless trading behavior.

## Runtime State (NUC1)
- **Path:** `/opt/slimy/research/kalshi-ai-trading-bot`
- **Remote:** `https://github.com/ryanfrigo/kalshi-ai-trading-bot.git`, branch `main`
- **Status:** ACTIVE — ahead of remote by 12 commits (local development outpaces upstream)
- **Type:** Application (research/experimental)
- **Truth gate:** `cd /opt/slimy/research/kalshi-ai-trading-bot && python -c "import toml; print(toml.load(open('pyproject.toml'))['project']['name'])"` (verify pyproject.toml valid)

## Architecture
- **Five-model AI ensemble** — five independent LLMs analyze each trade opportunity
- **Consensus gate** — system only enters a trade when models agree
- **Discipline systems:**
  - Category scoring — rates trade quality by category
  - Portfolio enforcement — prevents over-concentration
  - Risk guardrails — limits exposure per trade and per session
- Python-based, uses `pyproject.toml` for configuration

## Current Role in the System
- Experimental/research project on NUC1
- No running service — likely executed manually or via ad-hoc scripts
- Ahead of upstream by 12 commits — significant local modifications
- Not integrated with pm_updown_bot_bundle or other trading infrastructure

## Dependencies
- Python 3.12+
- Kalshi API (prediction market access)
- CoinGecko (crypto price data)
- Finnhub (financial data)

## Risks
- External GitHub repo (ryanfrigo) — not a GurthBro0ks repo, moves independently
- Experimental/research status — not production-hardened
- 12 commits ahead of upstream — local work not backed up
- No automated tests or CI mentioned in truth gate

## See Also
- [PM UpDown Bot Bundle](pm-updown-bot-bundle.md) — other trading project (Polymarket)
- [Apify Market Scanner](apify-market-scanner.md) — potential data source for trading pipeline
- [NUC1 Current State](../architecture/nuc1-current-state.md)
