# NUC1 Project Discovery and Current State

**Date:** 2026-04-05
**Scanner:** Claude agent
**Scope:** NUC1 only — /home/slimy, /opt/slimy, runtime evidence

---

## 1. Executive Summary

NUC1 is the **agent contributor / trading / Docker-heavy side** of the SlimyAI stack. It hosts:
- Active trading automation via **pm_updown_bot_bundle** (heavy cron, multiple strategies, ML pipeline)
- Autonomous agent orchestration via **ned-clawd + openclaw** (PM2 + cron + openclaw-gateway)
- SlimyAI web stack via **slimy-monorepo** (slimy-bot-v2 TypeScript + Next.js web app, PM2)
- Mission control as a **systemd service** on port 3838
- Chat infrastructure via **slimy-chat** (StoatChat Docker Compose stack, 16 containers)
- Shared knowledge base **kb** (git-synced with NUC2)
- The old JS Discord bot (**slimyai_setup/slimy-app**) is present but replaced (cutover 2026-04-03)

**Total git repos found:** 19 (including symlinks, excluding Minecraft plugins)
**Actively running on NUC1:** 14+ distinct services/daemons
**Canonical GitHub repos missing locally:** slimy-kb (KB present), mailbox_ingest (NOT FOUND — see §6)

---

## 2. Canonical GitHub Repo Correlation

| Canonical GitHub Repo | Local Path | Found? | Running? | Notes |
|---|---|---|---|---|
| GurthBro0ks/slimy-kb | /home/slimy/kb | ✅ Yes | ✅ Yes (git sync) | KB is the canonical source; git-pulled from NUC2 |
| GurthBro0ks/slimy-monorepo | /opt/slimy/slimy-monorepo (+ symlink at /home/slimy/slimy-monorepo) | ✅ Yes | ✅ Yes | PM2: slimy-bot-v2 (port 3000) + Next.js web (mission-control via systemd) |
| GurthBro0ks/pm_updown_bot_bundle | /opt/slimy/pm_updown_bot_bundle | ✅ Yes | ✅ Yes (cron) | Heavy cron automation; not PM2, runs via cron + runner.py |
| GurthBro0ks/slimyai_setup | /opt/slimy/app | ✅ Yes | ⚠️ Superseded (2026-04-03) | Old JS Discord bot; cutover to slimy-bot-v2 TypeScript complete |
| GurthBro0ks/mission-control | /home/slimy/mission-control | ✅ Yes | ✅ Yes (systemd) | systemd service on port 3838 |
| GurthBro0ks/slimyai-web | NOT on NUC1 | ❌ No | N/A | This is a NUC2 project; slimyai.xyz/web runs on NUC2 port 3000 |
| GurthBro0ks/clawd | /home/slimy/clawd | ✅ Yes | ⚠️ Dormant | Last commit 2026-03-18; no cron, no PM2, no Docker reference found |
| GurthBro0ks/ned-clawd | /home/slimy/ned-clawd | ✅ Yes | ✅ Yes (cron) | 12+ cron jobs active; mc-comms-bot, heartbeat, watchdog, step-executor |
| GurthBro0ks/ned-autonomous | /home/slimy/ned-autonomous | ✅ Yes | ✅ Yes (PM2: agent-loop) | PM2 id 0 "agent-loop" — core autonomous orchestrator |

**Extra local-only projects not in canonical list (see §6 for details):**
- /home/slimy/.openclaw/workspace-executor (local, no remote)
- /home/slimy/.openclaw/workspace-researcher (local, no remote)
- /opt/slimy/research/kalshi-ai-trading-bot (GitHub: GurthBro0ks/kalshi-ai-trading-bot — LEGACY_CANDIDATE)
- /opt/slimy/apify-market-scanner (GitHub: GurthBro0ks/apify-market-scanner)
- /home/slimy/nuc-comms/mailbox_outbox (local-only git, NUC2 remote mailbox.git)
- /home/slimy/.codex/.tmp/plugins (OpenAI plugins git, not SlimyAI)
- /home/slimy/slimy-chat (GitHub: GurthBro0ks/slime.chat — Docker Compose stack)
- /home/slimy/stoat-source (GitHub: stoatchat/stoatchat — source for slimy-chat)

---

## 3. Local Repos Found on NUC1

### A. SlimyAI Core Stack

#### `/opt/slimy/slimy-monorepo` (canonical path)
- **Remote:** git@github.com:GurthBro0ks/slimy-monorepo.git
- **Branch:** main
- **Last commit:** `cad0803` on 2026-04-05 — "Merge branch 'feature/merge-chat-app'"
- **Dirty:** YES — uncommitted `apps/bot/data_store.json`, `apps/web/app/trader/`, `apps/web/components/trader/`
- **AGENTS.md:** Yes
- **Runtime:** PM2 (slimy-bot-v2 online, port 3000/tcp)
- **Symlink:** `/home/slimy/slimy-monorepo` → `/opt/slimy/slimy-monorepo` (symlink, not a separate repo)
- **Classification:** **ACTIVE** — primary Discord bot + Next.js web app

#### `/opt/slimy/pm_updown_bot_bundle`
- **Remote:** git@github.com:GurthBro0ks/pm_updown_bot_bundle.git
- **Branch:** feat/ibkr-forecast-integration
- **Last commit:** `0a92d84` on 2026-04-05 — "feat: get_ai_stock_sentiment stub + defensive import fix"
- **Dirty:** YES — `.venv/`, `data/holdout_pnl.db`, `data/ml_label_cache.json`
- **AGENTS.md:** Yes
- **Runtime:** CRON (dozens of cron entries; see §4)
- **Classification:** **ACTIVE** — primary trading automation

#### `/home/slimy/mission-control`
- **Remote:** git@github.com:GurthBro0ks/mission-control.git
- **Branch:** main
- **Last commit:** `d1cc4a2` on 2026-04-05
- **Dirty:** No
- **README:** Yes
- **Runtime:** systemd (mission-control.service on port 3838/tcp)
- **Classification:** **ACTIVE** — Next.js app serving mission control

#### `/home/slimy/ned-clawd`
- **Remote:** git@github.com:GurthBro0ks/ned-clawd.git
- **Branch:** master
- **Last commit:** `6c73dae` on 2026-03-23
- **Dirty:** YES (untracked `comms/`)
- **AGENTS.md:** Yes
- **Runtime:** CRON (12+ cron jobs; see §4)
- **Classification:** **ACTIVE** — autonomous agent orchestration

#### `/home/slimy/ned-autonomous`
- **Remote:** git@github.com:GurthBro0ks/ned-autonomous.git
- **Branch:** main
- **Last commit:** `09353c8` on 2026-03-18
- **Dirty:** No
- **README:** Yes
- **Runtime:** PM2 id 0 "agent-loop" (online)
- **Classification:** **ACTIVE** — PM2 managed autonomous loop

#### `/home/slimy/kb`
- **Remote:** git@github.com:GurthBro0ks/slimy-kb.git
- **Branch:** main
- **Last commit:** `b2f1e70` on 2026-04-05 (today)
- **Dirty:** No
- **Runtime:** Git sync only; not a running service
- **Classification:** **ACTIVE** — shared knowledge base across NUCs

#### `/home/slimy/clawd`
- **Remote:** git@github.com:GurthBro0ks/clawd.git
- **Branch:** master
- **Last commit:** `f67c37d` on 2026-03-18
- **Dirty:** No
- **AGENTS.md:** Yes
- **Runtime:** No evidence of cron, PM2, systemd, or Docker reference
- **Classification:** **DORMANT** — present but no active runtime hooks

### B. Chat Infrastructure (StoatChat)

#### `/home/slimy/slimy-chat`
- **Remote:** git@github.com:GurthBro0ks/slime.chat.git
- **Branch:** main
- **Last commit:** `d1c4cb7` on 2026-03-18
- **Dirty:** No
- **Runtime:** Docker Compose stack — 16 containers active (api, web, caddy, smtp, redis, rabbitmq, minio, livekit, voice-ingress, pushd, events, autumn, crond, gifbox, january)
- **Classification:** **ACTIVE** — full chat platform Docker Compose

#### `/home/slimy/stoat-source`
- **Remote:** https://github.com/stoatchat/stoatchat (same as slimy-chat source)
- **Branch:** main
- **Last commit:** `6bd045e` on 2026-02-20
- **Dirty:** No
- **Runtime:** None directly — source code for slimy-chat
- **Classification:** **PRESENT_NOT_RUNNING** — upstream source, not deployed directly

### C. Agent / OpenCLAW Infrastructure

#### `/home/slimy/.openclaw/workspace-executor`
- **Remote:** None (no git remote)
- **Branch:** master (detached HEAD, no commits)
- **Dirty:** YES (untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`)
- **AGENTS.md:** Yes
- **Runtime:** OpenCLAW workspace agent
- **Classification:** **ACTIVE** — workspace executor agent

#### `/home/slimy/.openclaw/workspace-researcher`
- **Remote:** None (no git remote)
- **Branch:** master (detached HEAD, no commits)
- **Dirty:** YES (untracked `.openclaw/`, `AGENTS.md`, `BOOTSTRAP.md`)
- **AGENTS.md:** Yes
- **Runtime:** OpenCLAW workspace agent
- **Classification:** **ACTIVE** — workspace researcher agent

### D. NUC Communication

#### `/home/slimy/nuc-comms/mailbox_outbox`
- **Remote:** ssh://slimy@192.168.68.65:4422/home/slimy/nuc-comms/mailbox.git (NUC2 local)
- **Branch:** main
- **Last commit:** `9eb07cc` on 2026-03-18
- **Dirty:** YES (untracked `report.json`, `report.sha256`, `report_20260319T121234Z.json`)
- **Runtime:** Used by cron scripts for cross-NUC communication
- **Classification:** **PRESENT_NOT_RUNNING** — git mailbox for inter-NUC sync

### E. Research / Trading Tools

#### `/opt/slimy/research/kalshi-ai-trading-bot`
- **Remote:** git@github.com:GurthBro0ks/kalshi-ai-trading-bot.git (presumed — path implies)
- **Branch:** (git present)
- **Last commit:** `fd65404` on 2026-03-19
- **Dirty:** No
- **README:** Yes
- **Runtime:** None found — NOT referenced in cron, PM2, or Docker
- **Classification:** **LEGACY_CANDIDATE** — appears superseded by pm_updown_bot_bundle; no active runtime evidence; last commit predates active pm_updown_bot_bundle work
- **Confidence:** Medium — path suggests active research but no runtime hooks found

#### `/opt/slimy/apify-market-scanner`
- **Remote:** git@github.com:GurthBro0ks/apify-market-scanner.git
- **Branch:** master
- **Last commit:** `dd8beb5` on 2026-02-27
- **Dirty:** No
- **README:** Yes
- **Runtime:** None found in cron/PM2/systemd
- **Classification:** **UNKNOWN** — Apify data collection tool; not seen in active cron; may be referenced by pm_updown_bot_bundle data collection

### F. Legacy / Superseded

#### `/opt/slimy/app` (slimyai_setup)
- **Remote:** git@github.com:GurthBro0ks/slimyai_setup.git
- **Branch:** main
- **Last commit:** `33f4a61` on 2026-03-29
- **Dirty:** No
- **AGENTS.md:** Yes
- **Runtime:** NONE — old JS Discord bot, cutover to slimy-bot-v2 completed 2026-04-03
- **Classification:** **LEGACY_CANDIDATE** — replaced by slimy-bot-v2 in slimy-monorepo

#### `/home/slimy/.qoder-server/slimy-monorepo`
- **Note:** This is a separate clone of slimy-monorepo at a different path (not symlinked). Last commit `4e893be` 2026-04-04. Could be stale or used by a specific tool (e.g., qoder).
- **Classification:** **UNKNOWN** — verify if this is a duplicate that should be removed or is actively used

### G. External / Not SlimyAI

#### `/home/slimy/src/plugins/DynaTech`, `PrivateStorage`, `Slimefun4`
- Minecraft plugins (Paper server at /opt/slimy/minecraft)
- **Classification:** **PRESENT_NOT_RUNNING** — Minecraft server not actively managed by SlimyAI agents (per server-state.md); these are plugin sources

#### `/home/slimy/.codex/.tmp/plugins`
- **Remote:** https://github.com/openai/plugins.git
- **Last commit:** `f78e3ad` on 2026-03-30
- **Classification:** **UNKNOWN** — OpenAI plugins code; not SlimyAI; may be used by .continue or codex tooling

---

## 4. Runtime Evidence

### Docker Containers (17 running)
```
slimy-mysql        mysql:8                  Up 2 weeks (healthy)
database           mongo                     Up 5 weeks
slimy-chat_caddy_1 caddy                     Up 2 weeks
slimy-chat_web_1   ghcr.io/stoatchat/for-web:addb6b7  Up 5 weeks
slimy-chat_smtp_1  boky/postfix             Up 5 weeks (healthy)
slimy-chat_voice-ingress_1  ghcr.io/stoatchat/voice-ingress:v0.11.1  Up 5 weeks
slimy-chat_api_1   ghcr.io/stoatchat/api:v0.11.1  Up 5 weeks
slimy-chat_pushd_1  ghcr.io/stoatchat/pushd:v0.11.1  Up 5 weeks
slimy-chat_autumn_1  ghcr.io/stoatchat/file-server:v0.11.1  Up 5 weeks
slimy-chat_events_1 ghcr.io/stoatchat/events:v0.11.1  Up 5 weeks
slimy-chat_crond_1 ghcr.io/stoatchat/crond:v0.11.1  Up 5 weeks
slimy-chat_minio_1 minio/minio             Up 5 weeks
slimy-chat_rabbit_1 rabbitmq:4             Up 5 weeks (healthy)
slimy-chat_livekit_1 ghcr.io/stoatchat/livekit-server:v1.9.6  Up 5 weeks
slimy-chat_january_1 ghcr.io/stoatchat/proxy:v0.11.1  Up 5 weeks
slimy-chat_gifbox_1 ghcr.io/stoatchat/gifbox:v0.11.1  Up 5 weeks
slimy-chat_redis_1  eqalpha/keydb           Up 5 weeks
```

### systemd Services
- `mission-control.service` — **active running** — Mission Control Next.js on port 3838
- `pm2-slimy.service` — **active running** — PM2 process manager
- `tailscaled.service` — **active running** — Tailscale VPN
- `postfix.service` — **inactive dead**
- `slimy-backup-pull.service` — **failed** — Pull backups from nuc2

### PM2
```
id  │ name           │ status │ cpu  │ memory   │
 0  │ agent-loop     │ online │ 0%   │ 17.4mb   │  ned-autonomous orchestrator
10  │ slimy-bot-v2   │ online │ 0%   │ 110.7mb  │  TypeScript Discord bot (monorepo)
```

### Listening TCP Ports (selected)
| Port | Process |
|------|---------|
| 22 | sshd |
| 80/443 | Caddy (TLS) |
| 11434 | Ollama (localhost only) |
| 3000 | Node/PM2 (slimy-bot-v2) |
| 3306 | MySQL Docker |
| 3838 | next-server (mission-control systemd) |
| 3840 | python3 (uvicorn?) |
| 3850 | python3 (uvicorn?) |
| 8080 | slimy-chat API |
| 8510 | python3 |
| 18789-18792 | openclaw-gateway (localhost only) |
| 27017 | MongoDB |
| 7881 | ? (TCP6) |

### Active Cron Jobs (key entries for project tracking)
```
# pm_updown_bot_bundle — heavy trading automation
0 8,20 * * * /opt/slimy/pm_updown_bot_bundle/run_with_monitoring.sh >> logs/cron.log
0 11,1 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 900 runner.py --phase all
0 */2 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 600 python3 strategies/kalshi_optimize.py --mode shadow
0 */2 * * * python3 scripts/knowledge-exporter.py
30 */2 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 120 .venv/bin/python3 -m ml.data_collector
0 6 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 300 .venv/bin/python3 -m ml.label_resolver
0 6 * * 0 cd /opt/slimy/pm_updown_bot_bundle && python3 scripts/bootstrap_validator.py
30 5 * * * cd /opt/slimy/pm_updown_bot_bundle && python3 scripts/shadow_resolver.py
0 12 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 60 runner.py --mode micro-live
0 6,14 * * * cd /opt/slimy/pm_updown_bot_bundle && timeout 600 runner.py --strategy weather --mode shadow
0 8 * * 0 /opt/slimy/pm_updown_bot_bundle/scripts/pnl-weekly-report.sh

# ned-clawd — autonomous agent orchestration
*/5 * * * * /home/slimy/ned-clawd/scripts/heartbeat.sh
* * * * * /home/slimy/ned-clawd/scripts/mc-comms-bot.sh
*/2 * * * * /home/slimy/ned-clawd/scripts/step-executor.sh
*/15 * * * * /home/slimy/ned-clawd/scripts/watchdog.sh
0 8 * * * /home/slimy/ned-clawd/triggers/daily-briefing.sh
0 23 * * * /home/slimy/ned-clawd/scripts/nightly-memory-extract.sh
0 */2 * * * /home/slimy/ned-clawd/scripts/register-agents.sh
0 * * * * /home/slimy/ned-clawd/scripts/register-agents.sh
@reboot /home/slimy/ned-clawd/scripts/register-agents.sh
*/5 * * * * /home/slimy/ned-clawd/scripts/resource-monitor.py
@reboot /home/slimy/ned-clawd/scripts/agent-health-monitor.py

# Other
0 4 * * * /home/slimy/sync-repos.sh  # git repo sync
0 3 * * * /home/slimy/backups/stoat-chat/backup.sh
```

---

## 5. Project-by-Project State Assessment

| Project | Path | GitHub Match | Runtime | Last Commit | Dirty | Classification | Confidence |
|---|---|---|---|---|---|---|---|
| slimy-monorepo | /opt/slimy/slimy-monorepo | GurthBro0ks/slimy-monorepo | PM2 (slimy-bot-v2, web) | 2026-04-05 | YES | ACTIVE | HIGH |
| pm_updown_bot_bundle | /opt/slimy/pm_updown_bot_bundle | GurthBro0ks/pm_updown_bot_bundle | CRON | 2026-04-05 | YES | ACTIVE | HIGH |
| mission-control | /home/slimy/mission-control | GurthBro0ks/mission-control | systemd:3838 | 2026-04-05 | NO | ACTIVE | HIGH |
| ned-clawd | /home/slimy/ned-clawd | GurthBro0ks/ned-clawd | CRON (12+ jobs) | 2026-03-23 | YES | ACTIVE | HIGH |
| ned-autonomous | /home/slimy/ned-autonomous | GurthBro0ks/ned-autonomous | PM2:agent-loop | 2026-03-18 | NO | ACTIVE | HIGH |
| kb | /home/slimy/kb | GurthBro0ks/slimy-kb | git-sync | 2026-04-05 | NO | ACTIVE | HIGH |
| slimy-chat | /home/slimy/slimy-chat | GurthBro0ks/slime.chat | Docker (16 containers) | 2026-03-18 | NO | ACTIVE | HIGH |
| workspace-executor | /home/slimy/.openclaw/workspace-executor | NONE | OpenCLAW | N/A | YES | ACTIVE | HIGH |
| workspace-researcher | /home/slimy/.openclaw/workspace-researcher | NONE | OpenCLAW | N/A | YES | ACTIVE | HIGH |
| mailbox_outbox | /home/slimy/nuc-comms/mailbox_outbox | local-only (NUC2 mailbox.git) | CRON sync | 2026-03-18 | YES | PRESENT_NOT_RUNNING | HIGH |
| stoat-source | /home/slimy/stoat-source | stoatchat/stoatchat | None | 2026-02-20 | NO | PRESENT_NOT_RUNNING | MEDIUM |
| clawd | /home/slimy/clawd | GurthBro0ks/clawd | None | 2026-03-18 | NO | DORMANT | HIGH |
| slimy-monorepo (qoder) | /home/slimy/.qoder-server/slimy-monorepo | GurthBro0ks/slimy-monorepo | None | 2026-04-04 | YES | UNKNOWN | MEDIUM |
| slimyai_setup (app) | /opt/slimy/app | GurthBro0ks/slimyai_setup | None (superseded) | 2026-03-29 | NO | LEGACY_CANDIDATE | HIGH |
| research/kalshi-ai-trading-bot | /opt/slimy/research/kalshi-ai-trading-bot | GurthBro0ks/kalshi-ai-trading-bot | None | 2026-03-19 | NO | LEGACY_CANDIDATE | MEDIUM |
| apify-market-scanner | /opt/slimy/apify-market-scanner | GurthBro0ks/apify-market-scanner | None | 2026-02-27 | NO | UNKNOWN | LOW |
| DynaTech | /home/slimy/src/plugins/DynaTech | external (Minecraft) | None | 2024-12-29 | NO | ARCHIVE | HIGH |
| PrivateStorage | /home/slimy/src/plugins/PrivateStorage | external (Minecraft) | None | 2021-09-06 | NO | ARCHIVE | HIGH |
| Slimefun4 | /home/slimy/src/plugins/Slimefun4 | external (Minecraft) | None | 2024-11-09 | NO | ARCHIVE | HIGH |
| OpenAI plugins | /home/slimy/.codex/.tmp/plugins | openai/plugins | None | 2026-03-30 | NO | UNRELATED | HIGH |

---

## 6. Extra Local Projects Not In Canonical Repo List

### `workspace-executor` / `workspace-researcher` (`/home/slimy/.openclaw/`)
- **What they are:** OpenCLAW workspace agents — subagents that execute and research tasks
- **Not in canonical GitHub list** — they are local-only workspaces with no git remote
- **Part of active SlimyAI stack:** YES — managed by openclaw-gateway (ports 18789-18792), referenced in openclaw configuration at `/home/slimy/.claude/openclaw.json`
- **KB gap:** No wiki article exists for OpenCLAW workspace agents
- **Recommendation:** Write a new wiki/projects article for `openclaw-agents.md`

### `mailbox_outbox` (`/home/slimy/nuc-comms/mailbox_outbox`)
- **What it is:** Git-based inter-NUC communication — pushes reports to NUC2's mailbox.git
- **Remote:** `ssh://slimy@192.168.68.65:4422/home/slimy/nuc-comms/mailbox.git` (NUC2)
- **Project map says `mailbox_ingest` at `/home/slimy/nuc-comms/mailbox_ingest` — this does NOT exist**
- **Evidence:** `find /home/slimy/nuc-comms -maxdepth 2 -name ".git"` only finds `mailbox_outbox/.git`
- **Active cron references:** `0 4 * * * /home/slimy/sync-repos.sh` and pm_updown_bot_bundle's `push-sync.sh`
- **Recommendation:** Clarify in project map whether `mailbox_ingest` was renamed to `mailbox_outbox` or if there's a deployment discrepancy

### `/opt/slimy/research/kalshi-ai-trading-bot`
- **What it is:** Research trading bot, last commit 2026-03-19
- **NOT referenced in any active cron, PM2, or Docker**
- **pm_updown_bot_bundle is the active trading bot** — `research/kalshi-ai-trading-bot` predates and appears superseded by the pm_updown_bot_bundle work
- **Part of active SlimyAI stack:** No evidence of active use
- **Recommendation:** Consider archiving or confirm if still used for reference

### `apify-market-scanner` (`/opt/slimy/apify-market-scanner`)
- **Last commit:** 2026-02-27
- **Purpose:** Apify-based market data scraping
- **No direct cron/PM2 references found** — may be called indirectly by pm_updown_bot_bundle data collection
- **Part of active SlimyAI stack:** Possible — needs further grep to confirm invocation from pm_updown_bot_bundle

### `/home/slimy/.qoder-server/slimy-monorepo` (duplicate clone)
- **What it is:** Separate clone of slimy-monorepo at a different path
- **Last commit:** 2026-04-04 (vs /opt/slimy/slimy-monorepo which has today's commit)
- **Not referenced in cron, PM2, or systemd**
- **May be a stale qoder-specific artifact**
- **Recommendation:** Investigate whether this should be removed or is used by the qoder tooling

---

## 7. Legacy-Candidate or Ambiguous Items

### LEGACY_CANDIDATE: `slimyai_setup` (`/opt/slimy/app`)
- **Evidence:** Old JS Discord bot repo; server-state.md says cutover to slimy-bot-v2 completed 2026-04-03
- **Why not just ARCHIVE:** Still has recent commits (2026-03-29) and rollback script exists at `/home/slimy/rollback-bot.sh`
- **Decision:** Keep as LEGACY_CANDIDATE — not actively running but preserved for rollback

### LEGACY_CANDIDATE: `research/kalshi-ai-trading-bot`
- **Evidence:** No runtime hooks, superseded by pm_updown_bot_bundle which has far more complete trading automation
- **Decision:** LEGACY_CANDIDATE — was likely a prototype; pm_updown_bot_bundle is the production system

### AMBIGUOUS: `clawd`
- **Evidence:** Git repo present, has AGENTS.md, but no cron/PM2/systemd/Docker references
- **Last commit:** 2026-03-18
- **The init.sh script shows it as one of the 16 discovered repos**
- **Decision:** DORMANT — repo is present but no active runtime

---

## 8. KB Gaps / Missing Wiki Project Articles

Based on the wiki/projects/ listing:
- `agents-plugin-ecosystem.md` ✅
- `capture-dashboard.md` ✅
- `clawd-workspace-governance.md` ✅
- `mission-control.md` ✅
- `operator-console.md` ✅
- `pm-updown-bot-bundle.md` ✅
- `slimy-chat.md` ✅
- `slimy-discord-bot.md` ✅
- `slimy-monorepo.md` ✅
- `slimy-web.md` ✅

**Missing articles:**
1. **`openclaw-agents.md`** — workspace-executor and workspace-researcher have no wiki coverage; these are active OpenCLAW subagents
2. **`ned-autonomous.md`** — no wiki article; agent-loop PM2 is actively running
3. **`mailbox-nuc-comms.md`** — mailbox_outbox / inter-NUC git mailbox communication has no wiki article
4. **`apify-market-scanner.md`** — may be worth an article if it feeds into pm_updown_bot_bundle

---

## 9. Recommended Next Actions

1. **Clarify mailbox_ingest vs mailbox_outbox** in project map — confirm if this is a renamed deployment or missing component
2. **Investigate `/home/slimy/.qoder-server/slimy-monorepo`** — determine if it's a stale duplicate or has a specific purpose
3. **Write missing KB articles** for: openclaw-agents, ned-autonomous, mailbox-nuc-comms
4. **Verify apify-market-scanner** is still called by pm_updown_bot_bundle or mark as LEGACY_CANDIDATE
5. **Archive or confirm** `research/kalshi-ai-trading-bot` — no active runtime evidence
6. **Do NOT touch** `/opt/slimy/app` (slimyai_setup) — rollback target, keep as LEGACY_CANDIDATE

---

## Summary Table

| project | local path | github match | runtime status | classification | confidence | proof |
|---|---|---|---|---|---|---|
| slimy-monorepo | /opt/slimy/slimy-monorepo | GurthBro0ks/slimy-monorepo | PM2: slimy-bot-v2 (port 3000) | ACTIVE | HIGH | PM2 list + port 3000 listening |
| pm_updown_bot_bundle | /opt/slimy/pm_updown_bot_bundle | GurthBro0ks/pm_updown_bot_bundle | CRON (20+ entries) | ACTIVE | HIGH | crontab entries |
| mission-control | /home/slimy/mission-control | GurthBro0ks/mission-control | systemd:3838 | ACTIVE | HIGH | systemctl + port 3838 |
| ned-clawd | /home/slimy/ned-clawd | GurthBro0ks/ned-clawd | CRON (12+ jobs) | ACTIVE | HIGH | crontab entries |
| ned-autonomous | /home/slimy/ned-autonomous | GurthBro0ks/ned-autonomous | PM2: agent-loop | ACTIVE | HIGH | PM2 id 0 |
| kb | /home/slimy/kb | GurthBro0ks/slimy-kb | git-sync | ACTIVE | HIGH | git last commit today |
| slimy-chat | /home/slimy/slimy-chat | GurthBro0ks/slime.chat | Docker (16 containers) | ACTIVE | HIGH | docker ps (16 containers) |
| workspace-executor | /home/slimy/.openclaw/workspace-executor | NONE (local) | openclaw-gateway | ACTIVE | HIGH | openclaw.json + AGENTS.md |
| workspace-researcher | /home/slimy/.openclaw/workspace-researcher | NONE (local) | openclaw-gateway | ACTIVE | HIGH | openclaw.json + AGENTS.md |
| mailbox_outbox | /home/slimy/nuc-comms/mailbox_outbox | local-only (NUC2 mailbox) | CRON sync | PRESENT_NOT_RUNNING | HIGH | git remote + sync-repos.sh |
| stoat-source | /home/slimy/stoat-source | stoatchat/stoatchat | None | PRESENT_NOT_RUNNING | MEDIUM | source of slimy-chat |
| clawd | /home/slimy/clawd | GurthBro0ks/clawd | None | DORMANT | HIGH | no cron/PM2/systemd |
| .qoder-server/slimy-monorepo | /home/slimy/.qoder-server/slimy-monorepo | GurthBro0ks/slimy-monorepo | None | UNKNOWN | MEDIUM | duplicate clone, purpose unclear |
| slimyai_setup (app) | /opt/slimy/app | GurthBro0ks/slimyai_setup | None (superseded 2026-04-03) | LEGACY_CANDIDATE | HIGH | rollback-bot.sh exists |
| research/kalshi-ai-trading-bot | /opt/slimy/research/kalshi-ai-trading-bot | GurthBro0ks/kalshi-ai-trading-bot | None | LEGACY_CANDIDATE | MEDIUM | no runtime hooks |
| apify-market-scanner | /opt/slimy/apify-market-scanner | GurthBro0ks/apify-market-scanner | None | UNKNOWN | LOW | no direct runtime refs |
| slimyai-web | NOT ON NUC1 | GurthBro0ks/slimyai-web | N/A | NOT PRESENT | HIGH | confirmed absent from NUC1 |
| mailbox_ingest | NOT FOUND | GurthBro0ks/mailbox_ingest | N/A | MISSING | HIGH | find confirms only mailbox_outbox |
