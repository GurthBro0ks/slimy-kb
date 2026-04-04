# Server State — slimy-nuc2
> Last updated: 2026-03-31T20:01:00Z

## Machine
- **Hostname:** slimy-nuc2
- **OS:** Ubuntu 24.04.3 LTS
- **Disk:** 85G/219G (41% used)

## Repos
| Repo | Path | Remote |
|------|------|--------|
| agents | /home/slimy/.claude/agents | https://github.com/wshobson/agents.git |
| clawd | /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git |
| .mcp_agent_mail_git_mailbox_repo | /home/slimy/.mcp_agent_mail_git_mailbox_repo | local-only |
| mission-control | /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git |
| mailbox_ingest | /home/slimy/nuc-comms/mailbox_ingest | /home/slimy/nuc-comms/mailbox.git |
| git-notes-ledger | /home/slimy/.openclaw/memory/git-notes-ledger | local-only |
| workspace | /home/slimy/.openclaw/workspace | local-only |
| pm_updown_bot_bundle | /home/slimy/pm_updown_bot_bundle | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git |
| slimy-monorepo | /home/slimy/slimy-monorepo → /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git |

> **Canonical repo path:** `/opt/slimy/slimy-monorepo`. `/home/slimy/slimy-monorepo` is a symlink to it.
> **Canonical supervisor for web:** `systemd --user` service `slimy-web.service`. PM2 is not authoritative for web.

## PM2 Status
- **slimy-bot:** running under PM2 (name: slimy-bot, online, managed at `/opt/slimy/app/`)
- **PM2 save:** done — process list persisted

## MySQL (slimyai_prod)
- `snail_codes` table created (columns: code PK, rewards, source, verified, status, created_at, updated_at)
- Some legacy tables missing (mode_configs, guild_settings, club_latest) — non-critical, bot still functional
- Club tables in slimyai_prod: club_analyses, club_analysis_images, club_metrics, club_sheets (club_latest not present locally)
- SSH tunnel to NUC1 MySQL: slimy-mysql-tunnel.service on port 3307 (active)
- slimy-web.service now uses EnvironmentFile for CLUB_MYSQL_* vars (real creds injected)
- **Blocker:** MySQL user `slimy` denied from tunnel IP 172.18.0.1 — needs NUC1 GRANT fix
