# NUC Topology and Services
> Category: architecture
> Sources: raw/decisions/seed-server-state.md, raw/decisions/seed-agents-rules.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc1-state.md, raw/decisions/2026-04-05-project-openclaw-agents-nuc1-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc1-state.md
> Created: 2026-04-04
> Updated: 2026-04-05
> Status: draft

SlimyAI is split across NUC1 and NUC2 with clear service boundaries.

## Placement Model
- NUC1 runs core infra dependencies (MySQL, Caddy, chat service, agent loop).
- NUC2 runs primary web workloads (Next.js web app, mission-control, legacy PostgreSQL).
- Bot process management uses PM2 where applicable; web supervision is systemd user service on NUC2.

## Repository Layout
- Canonical monorepo path: `/opt/slimy/slimy-monorepo`.
- `/home/slimy/slimy-monorepo` is a symlink and should not be replaced with a fresh clone.

## NUC1 Runtime Evidence (2026-04-05)
| Component | Manager | State | Port/Notes |
|---|---|---|---|
| slimy-chat | Docker Compose (16 containers) | Up 2-5 weeks | Port 8080 (api) |
| slimy-mysql | Docker | Up 2 weeks | Port 3306 |
| mission-control | systemd | active running | Port 3838 |
| pm2-slimy | systemd | active running | PM2 daemon |
| tailscaled | systemd | active running | VPN |
| slimy-bot-v2 | PM2 | online | Port 3000 (id 10, 110.7mb) |
| agent-loop | PM2 | online | id 0, 17.4mb |
| ned-clawd cron | cron | 12+ active jobs | heartbeat, mc-comms, watchdog, step-executor, etc. |
| pm_updown_bot_bundle cron | cron | 20+ entries | shadow scanner, data collection, ML pipeline |
| openclaw-gateway | openclaw | active | Ports 18789-18792 (localhost) |

## Operational Implications
- Service ownership and ports must be validated against server-state before restarts.
- Cross-host DB access requires explicit grants and tunnel validation.

## See Also
- [Auth and Retired Services](auth-and-retired-services.md)
- [SlimyAI Login and Session Flow](slimyai-login-and-session-flow.md)
- [Cross-NUC Communication Matrix](cross-nuc-communication-matrix.md)
- [Harness Runtime Topology](harness-runtime-topology.md)
- [Source of Truth Ledgers](../concepts/source-of-truth-ledgers.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
