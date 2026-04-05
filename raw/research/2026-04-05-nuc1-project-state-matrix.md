# NUC1 Project State Matrix
> Generated: 2026-04-05 by Claude agent
> Machine: slimy-nuc1

## Format Legend
- **dirty** = uncommitted changes (git status --porcelain non-empty)
- **docker** = has Docker containers running on NUC1
- **pm2** = PM2 process running on NUC1
- **systemd** = systemd service running on NUC1
- **cron** = cron jobs referencing this project on NUC1
- **ports** = listening TCP ports by this project's processes
- **classification**: ACTIVE | PRESENT_NOT_RUNNING | DORMANT | LEGACY_CANDIDATE | UNKNOWN | NOT_FOUND | UNRELATED

## Matrix

| project | nuc1_path | remote | branch | dirty | docker | pm2 | systemd | cron | ports | classification | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| slimy-monorepo | /opt/slimy/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | main | YES | NO | YES (slimy-bot-v2) | NO | NO | 3000/tcp | ACTIVE | Primary bot+web stack; symlink /home/slimy/slimy-monorepo -> here |
| pm_updown_bot_bundle | /opt/slimy/pm_updown_bot_bundle | git@github.com:GurthBro0ks/pm_updown_bot_bundle.git | feat/ibkr-forecast-integration | YES | NO | NO | NO | YES (20+ entries) | NONE | ACTIVE | Trading automation; runner.py, ML pipeline, shadow scanner |
| mission-control | /home/slimy/mission-control | git@github.com:GurthBro0ks/mission-control.git | main | NO | NO | NO | YES | NO | 3838/tcp | ACTIVE | Next.js systemd service |
| ned-clawd | /home/slimy/ned-clawd | git@github.com:GurthBro0ks/ned-clawd.git | master | YES | NO | NO | NO | YES (12+ entries) | NONE | ACTIVE | Autonomous orchestration; heartbeat, watchdog, mc-comms-bot |
| ned-autonomous | /home/slimy/ned-autonomous | git@github.com:GurthBro0ks/ned-autonomous.git | main | NO | NO | YES (agent-loop, id=0) | NO | NO | NONE | ACTIVE | PM2 managed autonomous orchestrator |
| kb | /home/slimy/kb | git@github.com:GurthBro0ks/slimy-kb.git | main | NO | NO | NO | NO | NO (git-sync) | NONE | ACTIVE | Shared KB; syncs with NUC2 via git |
| slimy-chat | /home/slimy/slimy-chat | git@github.com:GurthBro0ks/slime.chat.git | main | NO | YES (16 containers) | NO | NO | NO | 8080/tcp | ACTIVE | StoatChat Docker Compose; api, web, caddy, redis, rabbitmq, livekit, etc |
| workspace-executor | /home/slimy/.openclaw/workspace-executor | NONE (local-only) | master (detached) | YES | NO | NO | NO | NO | NONE | ACTIVE | OpenCLAW subagent; managed by openclaw-gateway (18789-18792) |
| workspace-researcher | /home/slimy/.openclaw/workspace-researcher | NONE (local-only) | master (detached) | YES | NO | NO | NO | NO | NONE | ACTIVE | OpenCLAW subagent; managed by openclaw-gateway (18789-18792) |
| mailbox_outbox | /home/slimy/nuc-comms/mailbox_outbox | ssh://slimy@192.168.68.65:4422/home/slimy/nuc-comms/mailbox.git (NUC2) | main | YES | NO | NO | NO | YES (sync-repos.sh) | NONE | PRESENT_NOT_RUNNING | Inter-NUC git mailbox; push-only; NOT mailbox_ingest per project map |
| stoat-source | /home/slimy/stoat-source | https://github.com/stoatchat/stoatchat | main | NO | NO | NO | NO | NO | NONE | PRESENT_NOT_RUNNING | Upstream source for slimy-chat; not deployed directly |
| clawd | /home/slimy/clawd | git@github.com:GurthBro0ks/clawd.git | master | NO | NO | NO | NO | NO | NONE | DORMANT | Has AGENTS.md but no runtime hooks found |
| slimy-monorepo (qoder) | /home/slimy/.qoder-server/slimy-monorepo | git@github.com:GurthBro0ks/slimy-monorepo.git | main | YES | NO | NO | NO | NO | NONE | UNKNOWN | Separate clone; purpose unclear; not referenced in runtime |
| slimyai_setup (app) | /opt/slimy/app | git@github.com:GurthBro0ks/slimyai_setup.git | main | NO | NO | NO | NO | NO | NONE | LEGACY_CANDIDATE | Old JS Discord bot; cutover to slimy-bot-v2 completed 2026-04-03; rollback script preserved |
| research/kalshi-ai-trading-bot | /opt/slimy/research/kalshi-ai-trading-bot | (implied: GurthBro0ks/kalshi-ai-trading-bot) | (git present) | NO | NO | NO | NO | NO | NONE | LEGACY_CANDIDATE | No runtime evidence; appears superseded by pm_updown_bot_bundle |
| apify-market-scanner | /opt/slimy/apify-market-scanner | git@github.com:GurthBro0ks/apify-market-scanner.git | master | NO | NO | NO | NO | NO | NONE | UNKNOWN | No direct runtime refs; may be called indirectly by pm_updown_bot_bundle |
| DynaTech | /home/slimy/src/plugins/DynaTech | https://github.com/ProfElements/DynaTech.git | main | NO | NO | NO | NO | NO | NONE | ARCHIVE | Minecraft Paper plugin source; /opt/slimy/minecraft server present |
| PrivateStorage | /home/slimy/src/plugins/PrivateStorage | https://github.com/Slimefun-Addon-Community/PrivateStorage.git | master | NO | NO | NO | NO | NO | NONE | ARCHIVE | Minecraft Paper plugin source |
| Slimefun4 | /home/slimy/src/plugins/Slimefun4 | https://github.com/Slimefun/Slimefun4.git | (none/HEAD) | NO | NO | NO | NO | NO | NONE | ARCHIVE | Minecraft Paper plugin source |
| OpenAI plugins | /home/slimy/.codex/.tmp/plugins | https://github.com/openai/plugins.git | main | NO | NO | NO | NO | NO | NONE | UNRELATED | OpenAI codex/plugin tooling; not SlimyAI |
| slimyai-web | NOT ON NUC1 | git@github.com:GurthBro0ks/slimyai-web.git | (N/A) | (N/A) | (N/A) | (N/A) | (N/A) | (N/A) | (N/A) | NOT_FOUND | NUC2 project; runs on NUC2 port 3000 |
| mailbox_ingest | NOT FOUND | GurthBro0ks/mailbox_ingest.git | (N/A) | (N/A) | (N/A) | (N/A) | (N/A) | (N/A) | (N/A) | NOT_FOUND | Per project map at /home/slimy/nuc-comms/mailbox_ingest; find confirms only mailbox_outbox exists |
| agents | /home/slimy/.claude/agents | https://github.com/wshobson/agents.git | main | NO | NO | NO | NO | NO | NONE | UNRELATED | Claude Code agent harness config; not a runtime service |
| git-notes-ledger | /home/slimy/.openclaw/memory/git-notes-ledger | (local-only) | (unknown) | UNKNOWN | NO | NO | NO | NO | NONE | UNKNOWN | Listed in project map; verify if still exists |
| workspace | /home/slimy/.openclaw/workspace | (local-only) | (unknown) | UNKNOWN | NO | NO | NO | NO | NONE | UNKNOWN | Listed in project map; verify if still exists |

---

## Canonical GitHub Repo Set — NUC1 Coverage

| Canonical Repo | On NUC1? | Path | Active? |
|---|---|---|---|
| GurthBro0ks/slimy-kb | ✅ YES | /home/slimy/kb | ✅ YES |
| GurthBro0ks/slimy-monorepo | ✅ YES | /opt/slimy/slimy-monorepo | ✅ YES |
| GurthBro0ks/pm_updown_bot_bundle | ✅ YES | /opt/slimy/pm_updown_bot_bundle | ✅ YES |
| GurthBro0ks/slimyai_setup | ✅ YES | /opt/slimy/app | ⚠️ LEGACY (superseded) |
| GurthBro0ks/mission-control | ✅ YES | /home/slimy/mission-control | ✅ YES |
| GurthBro0ks/slimyai-web | ❌ NO | — | N/A (NUC2 project) |
| GurthBro0ks/clawd | ✅ YES | /home/slimy/clawd | ⚠️ DORMANT |
| GurthBro0ks/ned-clawd | ✅ YES | /home/slimy/ned-clawd | ✅ YES |
| GurthBro0ks/ned-autonomous | ✅ YES | /home/slimy/ned-autonomous | ✅ YES |
| GurthBro0ks/mailbox_ingest | ❌ NO | mailbox_outbox found instead | ⚠️ MISMATCH |
| GurthBro0ks/git-notes-ledger | ⚠️ UNCLEAR | needs verification | UNCLEAR |
| GurthBro0ks/workspace | ⚠️ UNCLEAR | needs verification | UNCLEAR |
| GurthBro0ks/agents | ✅ YES | /home/slimy/.claude/agents | ⚠️ HARNESS only |
| GurthBro0ks/clawd (workspace) | ✅ YES | /home/slimy/.openclaw/workspace-* | ✅ YES |

---

## Active Runtime Count by Project Type

| Type | Count | Projects |
|---|---|---|
| ACTIVE | 10 | slimy-monorepo, pm_updown_bot_bundle, mission-control, ned-clawd, ned-autonomous, kb, slimy-chat, workspace-executor, workspace-researcher, agents |
| PRESENT_NOT_RUNNING | 2 | mailbox_outbox, stoat-source |
| DORMANT | 1 | clawd |
| LEGACY_CANDIDATE | 2 | slimyai_setup (app), research/kalshi-ai-trading-bot |
| UNKNOWN | 3 | .qoder-server/slimy-monorepo, apify-market-scanner, git-notes-ledger, workspace |
| ARCHIVE | 3 | DynaTech, PrivateStorage, Slimefun4 |
| NOT_FOUND | 2 | slimyai-web, mailbox_ingest |
| UNRELATED | 1 | OpenAI plugins |
