# NUC Topology and Services
> Category: architecture
> Sources: raw/decisions/seed-server-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc1-state.md, raw/decisions/2026-04-05-project-openclaw-agents-nuc1-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc2-state.md, raw/decisions/2026-04-05-project-mission-control-nuc2-state.md, raw/decisions/2026-04-05-project-slimyai-setup-nuc2-state.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc2-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc2-state.md, raw/decisions/2026-04-05-project-chriss-agent-nuc2-state.md, raw/decisions/2026-04-05-project-obsidian-headless-sync-nuc2-state.md, raw/research/2026-04-05-nuc1-project-discovery.md, raw/research/2026-04-05-nuc1-project-state-matrix.md, raw/research/2026-04-05-nuc2-project-discovery.md, raw/research/2026-04-05-nuc2-project-state-matrix.md, raw/research/2026-04-05-nuc1-project-anomalies.md, raw/decisions/2026-04-05-nuc2-project-anomalies.md, raw/decisions/seed-agents-rules.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc1-state.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc1-state.md, raw/decisions/2026-04-05-project-openclaw-agents-nuc1-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc1-state.md, raw/decisions/2026-04-05-project-slimy-monorepo-nuc2-state.md, raw/decisions/2026-04-05-project-mission-control-nuc2-state.md, raw/decisions/2026-04-05-project-slimyai-setup-nuc2-state.md, raw/decisions/2026-04-05-project-pm-updown-bot-bundle-nuc2-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc2-state.md, raw/decisions/2026-04-05-project-chriss-agent-nuc2-state.md, raw/decisions/2026-04-05-project-obsidian-headless-sync-nuc2-state.md, raw/research/2026-04-05-nuc1-project-discovery.md, raw/research/2026-04-05-nuc1-project-state-matrix.md, raw/research/2026-04-05-nuc2-project-discovery.md, raw/research/2026-04-05-nuc2-project-state-matrix.md, raw/research/2026-04-05-nuc1-project-anomalies.md, raw/decisions/2026-04-05-nuc2-project-anomalies.md, raw/agent-learnings/2026-04-09-nuc1-discord-bot-runtime-truth.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 00:23 UTC (git)
> Version: r14 / f081b71
KB METADATA -->

SlimyAI is split across NUC1 and NUC2 with clear service boundaries.

## Placement Model
- NUC1 runs core infra dependencies (MySQL, Caddy, chat service, agent loop).
- NUC2 runs primary web workloads (Next.js web app, mission-control, legacy PostgreSQL).
- Bot process management uses PM2 where applicable; web supervision is systemd user service on NUC2.

## Repository Layout
- Canonical monorepo path: `/opt/slimy/slimy-monorepo`.
- `/home/slimy/slimy-monorepo` is a symlink and should not be replaced with a fresh clone.

## NUC2 Runtime Evidence (2026-04-05)
| Component | Manager | State | Port/Notes |
|---|---|---|---|
| slimy-web (monorepo) | systemd --user | active, running | Port 3000 (next-server v16.0.7, pid 3143002) |
| mission-control | systemd --user | active, running | Port 3838 (next-server v16.1.6, pid 2311610) |
| slimy-mysql-tunnel | systemd --user | active, running | SSH tunnel: localhost:3307 → NUC1:3306 |
| nuc-mailbox-ingest | systemd --user (timer + oneshot) | activating | Mailbox pull from mailbox.git |
| openclaw-gateway | systemd --user | active, running | Ports 18790/18792/18793 |
| slimy-web-health | systemd --user | FAILED | Healthcheck script missing |
| slimy-report | systemd --user | FAILED | — |
| obsidian-headless-sync | PM2 (id 0) | online | Only PM2 process; vault sync |
| chriss-agent | systemd (inferred) | running | Port 3850 (python webhook-bridge.py) |
| pm_updown_bot_bundle | cron (rsync only) | dormant | NUC1 is primary; NUC2 rsync consumer |
| slimyai_setup | ❌ ARCHIVED | Not present; old bot removed from NUC1; superseded by monorepo bot |
| KB | cron | active | `*/30 * * * *` kb-sync.sh pull |

## NUC1 Runtime Evidence (2026-04-05)
| Component | Manager | State | Port/Notes |
|---|---|---|---|
| slimy-chat | Docker Compose (16 containers) | Up 2-5 weeks | Port 8080 (api) |
| slimy-mysql | Docker | Up 2 weeks | Port 3306 |
| mission-control | systemd | active running | Port 3838 |
| pm2-slimy | systemd | active running | PM2 daemon |
| tailscaled | systemd | active running | VPN |
| slimy-bot-v2 | PM2 | online | PM2 id=1, pid 178717; entry `dist/index.js`; 3 Discord servers; 7 restarts in 12h (monitor) |
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
- [Slimy KB](../projects/slimy-kb.md)
- [Chriss Agent](../projects/chriss-agent.md)
- [Obsidian Headless Sync](../projects/obsidian-headless-sync.md)
- [Slimyai Setup](../projects/slimyai-setup.md)
