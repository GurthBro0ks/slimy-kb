# NUC2 Project State Matrix
**Generated:** 2026-04-05 | **Scope:** NUC2 /home/slimy + /opt/slimy

| project | nuc2_path | remote | branch | dirty | pm2 | systemd | cron | docker | ports | classification | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| slimy-kb | /home/slimy/kb | git@github.com:GurthBro0ks/slimy-kb.git | main | yes | no | no | yes pull | no | none | ACTIVE | cron pull every 30min; last commit today |
| slimy-monorepo | /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | main | yes qa-report.md | no | yes (slimy-web, slimy-mysql-tunnel, nuc-mailbox-ingest) | yes (morning-brief, sync-repos) | yes (docker-compose.yml, multiple Dockerfiles) | :3000 (next-server v16.0.7) | ACTIVE | slimy-web.service serves from monorepo apps/web; morning-brief cron |
| mission-control | /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git | main | yes next.config.ts | no | yes (mission-control.service) | no | no | :3838 (next-server v16.1.6) | ACTIVE | next-server listening 0.0.0.0:3838; last commit 2d ago |
| slimyai_setup | /opt/slimy/app | git@github.com:GurthBro0ks/slimyai_setup.git | main | yes command-test-report.txt | no | yes (slimy-web-health.service FAILED) | no | yes (docker-compose.yml, Dockerfile) | none | PRESENT_NOT_RUNNING | healthcheck script references; last commit 4d ago |
| slimyai-web | /opt/slimy/web/slimyai-web | git@github.com:GurthBro0ks/slimyai-web.git | fix/runtime-envs-check-2025-11-11-nuc2-snapshot | no | no | no | no | yes (docker-compose.yml, Dockerfile) | none | LEGACY_CANDIDATE | monorepo serves web instead; monorepo infra removes stale containers; last commit Nov2025 |
| pm_updown_bot_bundle | /home/slimy/pm_updown_bot_bundle | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git | main | yes claude-progress.md | no | no | yes rsync from NUC1 | no | none | DORMANT on NUC2 | NUC1 is primary; NUC2 rsync consumer only; last commit 15d ago |
| slime.chat | /opt/slimy/chat-app | git@github.com:GurthBro0ks/slime.chat.git | main | no | no | no | no | yes (compose.yml) | none | DORMANT | last commit Feb25; no runtime refs anywhere |
| agents (harness) | /home/slimy/.claude/agents | https://github.com/wshobson/agents.git | main | no | no | no | no | no | none | ACTIVE | primary Claude Code harness repo |
| agents-backup-full | /home/slimy/.claude/agents-backup-full | https://github.com/wshobson/agents.git | main | yes (D in index) | no | no | no | no | none | LEGACY_CANDIDATE | superseded by .claude/agents |
| clawd | /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git | main | yes AGENTS.md | no | no | no | no | none | ACTIVE | last commit today; AGENTS.md present |
| workspace (openclaw) | /home/slimy/.openclaw/workspace | local-only | master | yes .openclaw/ | no | no | no | no | none | ACTIVE | last commit 2d ago; AGENTS.md present |
| mailbox_ingest | /home/slimy/nuc-comms/mailbox_ingest | /home/slimy/nuc-comms/mailbox.git (local) | main | yes report.json | no | yes (nuc-mailbox-ingest.service activating) | no | no | none | ACTIVE | systemd service activating; NUC1-NUC2 comms |
| mailbox bare repo | /home/slimy/.mcp_agent_mail_git_mailbox_repo | local-only | master | no | no | no | no | no | none | DORMANT | MCP agent bare repo; last commit Feb26 |
| git-notes-ledger | /home/slimy/.openclaw/memory/git-notes-ledger | local-only | master | no | no | no | no | no | none | UNKNOWN | OpenCLAW internal; last commit Jan28; no active refs |
| .codex plugins cache | /home/slimy/.codex/.tmp/plugins | https://github.com/openai/plugins.git | main | no | no | no | no | no | none | UNKNOWN | temp cache dir; unclear integration |
| ned-clawd | /home/slimy/ned-clawd | none | none (not git) | unknown | no | no | no | no | none | UNKNOWN | operational dir; ARCHITECTURE.md references monorepo/bot-bundle |
| chriss-agent | /home/slimy/chriss-agent | none | none (not git) | unknown | no | yes (chriss-bridge.service) | no | no | :3850 (python3 webhook-bridge.py) | ACTIVE | webhook-bridge.py running since Mar14; no KB article |
| octoeverywhere-config | /home/slimy/octoeverywhere-config | none | none (not git) | no | no | no | no | yes (docker-compose.yml) | none | PRESENT_NOT_RUNNING | docker compose present; printer integration |
| obsidian-headless-sync | N/A | N/A | N/A | N/A | yes (only pm2 process) | no | no | no | none | ACTIVE | pm2 pid 3258479; ob sync running since 10:02 |

## Runtime Services Summary

### PM2
- `obsidian-headless-sync` — online (only PM2 process)

### systemd (--user)
- `mission-control.service` — ACTIVE, running, port 3838
- `slimy-web.service` — ACTIVE, running, port 3000
- `slimy-mysql-tunnel.service` — ACTIVE, running (SSH tunnel to NUC1 MySQL)
- `nuc-mailbox-ingest.service` — ACTIVATING
- `openclaw-gateway.service` — ACTIVE, running (ports 18790/18792/18793)
- `slimy-report.service` — FAILED
- `chriss-bridge.service` — (inferred from ps)

### Listening Ports of Interest
| Port | Process | Project |
|---|---|---|
| 3000 | next-server v16.0.7 (pid 3143002) | slimy-web (monorepo) |
| 3838 | next-server v16.1.6 (pid 2311610) | mission-control |
| 3850 | python3 webhook-bridge.py (pid 1178942) | chriss-agent |
| 18790/18792/18793 | openclaw-gateway (pid 1425811) | openclaw |
| 3306 | MySQL | slimy-monorepo |
| 3307 | SSH tunnel | NUC1 MySQL tunnel |

## KB wiki/projects/ Coverage
| Article | Status |
|---|---|
| agents-plugin-ecosystem.md | exists |
| capture-dashboard.md | exists |
| clawd-workspace-governance.md | exists |
| mission-control.md | exists |
| operator-console.md | exists |
| pm-updown-bot-bundle.md | exists |
| slimy-chat.md | exists |
| slimy-discord-bot.md | exists |
| slimy-monorepo.md | exists |
| slimy-web.md | exists |
| slimy-kb.md | **MISSING** |
| slimyai_setup.md | **MISSING** |
| slimyai-web.md | **MISSING** |
| slime-chat.md | **MISSING** |
| ned-clawd.md | **MISSING** |
| chriss-agent.md | **MISSING** |
| octoeverywhere.md | **MISSING** |
| mailbox.md | **MISSING** |
| git-notes-ledger.md | **MISSING** |
| codex-plugins.md | **MISSING** |
