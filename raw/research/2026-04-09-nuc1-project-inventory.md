# NUC1 Full Project Inventory
> Date: 2026-04-09
> Host: nuc1
> Sources: live git repos, pm2, systemctl, docker, netstat

## Discovery

Found 17 git repos across `/home/slimy` and `/opt/slimy`:

| # | Name | Path | Remote | Branch |
|---|------|------|--------|--------|
| 1 | clawd | /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git | master |
| 2 | kb | /home/slimy/kb | git@github.com:GurthBro0ks/slimy-kb.git | main |
| 3 | mission-control | /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git | main |
| 4 | ned-autonomous | /home/slimy/ned-autonomous | git@github.com:GurthBro0ks/ned-autonomous.git | main |
| 5 | ned-clawd | /home/slimy/ned-clawd | git@github.com:GurthBro0ks/ned-clawd.git | master |
| 6 | actionbook | /home/slimy/ned-clawd/actionbook | https://github.com/actionbook/actionbook | main |
| 7 | mailbox_outbox | /home/slimy/nuc-comms/mailbox_outbox | ssh://slimy@192.168.68.65:4422/.../mailbox.git (local) | main |
| 8 | workspace-executor | /home/slimy/.openclaw/workspace-executor | none (local-only) | master |
| 9 | workspace-researcher | /home/slimy/.openclaw/workspace-researcher | none (local-only) | master |
| 10 | slimy-chat | /home/slimy/slimy-chat | git@github.com:GurthBro0ks/slime.chat.git | main |
| 11 | apify-market-scanner | /opt/slimy/apify-market-scanner | git@github.com:GurthBro0ks/apify-market-scanner.git | master |
| 12 | pm_updown_bot_bundle | /opt/slimy/pm_updown_bot_bundle | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git | feat/ibkr-forecast-integration |
| 13 | proofs | /opt/slimy/pm_updown_bot_bundle/proofs | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git (same) | main |
| 14 | kalshi-ai-trading-bot | /opt/slimy/research/kalshi-ai-trading-bot | https://github.com/ryanfrigo/kalshi-ai-trading-bot.git | main |
| 15 | slimy-monorepo | /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | main |
| 16 | stoat-source | /home/slimy/stoat-source | git@github.com:stoatchat/stoatchat.git | main |
| 17 | slimy-monorepo (qoder) | /home/slimy/.qoder-server/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | (rebasing) |

## Host-Level Services

### PM2
| Process | PID | Uptime | Status |
|---------|-----|--------|--------|
| agent-loop | 1047 | 3D | online |
| slimy-bot-v2 | 178717 | 10h | online (7 restarts) |

### Systemd
| Service | Status |
|---------|--------|
| mission-control.service | running |
| ollama.service | running |
| pm2-slimy.service | running |
| webhook-server.service | activating/auto-restart |
| trading-dashboard-api.service | running |
| caddy.service | running |

### Docker
slimy-chat 16-container stack: caddy, web, smtp, api, pushd, autumn, events, crond, minio, rabbitmq, livekit-server, mongo, proxy, gifbox, redis, database

### Listening Ports
22 (SSH), 80, 443, 3000 (slimy-bot-v2), 3306 (MySQL), 3838 (mission-control), 8080/8443 (slimy-chat/Caddy), 8510 (trading-dashboard-api), 11434 (Ollama), 7881 (LiveKit), 18789-18792 (openclaw-gateway)

## Wiki Coverage

### Already documented
- apify-market-scanner ✓
- mailbox-nuc-comms ✓ (mailbox_outbox context)
- mission-control ✓
- ned-autonomous ✓
- pm-updown-bot-bundle ✓
- slimy-chat ✓
- slimy-monorepo ✓
- clawd-agent-rules ✓ (clawd context)
- workspace-agent-rules ✓ (workspace-executor/researcher context)

### Missing wiki articles
- clawd (no dedicated project article)
- kb
- mission-control (exists but check coverage)
- ned-clawd
- actionbook
- mailbox_outbox
- workspace-executor
- workspace-researcher
- stoat-source
- apify-market-scanner (exists, check coverage)
- kalshi-ai-trading-bot
- proofs (subdir of pm_updown_bot_bundle)

## Status Key
- **active**: commits in last 30 days
- **maintenance**: no recent commits,偶尔偶尔偶尔 occasionally touched
- **archived**: no commits >6 months
- **migrating**: branch rebasing/sync in progress
- **retired**: intentionally killed (see AGENTS.md Intentionally Dead)