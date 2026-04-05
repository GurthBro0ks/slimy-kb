# NUC2 Project Discovery and Current State

**Date:** 2026-04-05
**Scanner:** Claude (autonomous agent)
**Scope:** NUC2 only — /home/slimy, /opt/slimy, runtime evidence (PM2, systemd, cron, ports)

---

## 1. Executive Summary

NUC2 hosts **14 git repos** across `/home/slimy` and `/opt/slimy`, plus several local-only git working trees. Of the 6 canonical GitHub repos referenced in the task:

- **5 are confirmed locally present and active:** slimy-kb, slimy-monorepo, pm_updown_bot_bundle, mission-control, slimyai-web
- **slimyai_setup** is present as `/opt/slimy/app` (maps to `GurthBro0ks/slimyai_setup`)
- **slime.chat** (chat-app) is also present locally but not in the canonical GitHub list

Two Next.js services are **actively serving on public ports**:
- `slimy-web.service` → Next.js on port **3000** (systemd --user, active)
- `mission-control.service` → Next.js on port **3838** (systemd --user, active)

PM2 is running exactly **one** process: `obsidian-headless-sync`.

---

## 2. Canonical GitHub Repo Correlation

| GitHub Repo | Local Path(s) | Matched | Running on NUC2 | Classification |
|---|---|---|---|---|
| GurthBro0ks/slimy-kb | `/home/slimy/kb` | ✅ yes | KB tools + cron pull | ACTIVE |
| GurthBro0ks/slimy-monorepo | `/opt/slimy/slimy-monorepo` (canonical); `/home/slimy/slimy-monorepo` → symlink | ✅ yes | slimy-web (port 3000) via systemd; admin-api referenced in docs | ACTIVE |
| GurthBro0ks/pm_updown_bot_bundle | `/home/slimy/pm_updown_bot_bundle` | ✅ yes | Referenced by cron rsync from NUC1 | DORMANT on NUC2 (shadow/consumer) |
| GurthBro0ks/mission-control | `/home/slimy/mission-control` | ✅ yes | mission-control.service (port 3838) | ACTIVE |
| GurthBro0ks/slimyai_setup | `/opt/slimy/app` | ✅ yes | Referenced in systemd healthcheck script | PRESENT_NOT_RUNNING |
| GurthBro0ks/slimyai-web | `/opt/slimy/web/slimyai-web` | ✅ yes | NOT the live web — served from monorepo instead | LEGACY_CANDIDATE |
| GurthBro0ks/slime.chat | `/opt/slimy/chat-app` | ⚠️ extra | No active runtime references | DORMANT |
| wshobson/agents | `/home/slimy/.claude/agents` (main); `/home/slimy/.claude/agents-backup-full` (backup) | ✅ main present | Used by Claude Code harness | ACTIVE (harness) |

---

## 3. Local Repos Found on NUC2

### 3.1 /home/slimy/.claude/agents
- **Remote:** `https://github.com/wshobson/agents.git`
- **Branch:** main | **Hash:** d24e4e81 | **Last commit:** 2026-03-18
- **Status:** clean
- **Has:** README (AGENTS.md implied by CLAUDE.md)
- **Role:** Primary Claude Code agent harness repo
- **Runtime:** Referenced by Claude Code CLI directly
- **Classification:** ACTIVE | **Confidence:** HIGH

### 3.2 /home/slimy/.claude/agents-backup-full
- **Remote:** `https://github.com/wshobson/agents.git` (same as above)
- **Branch:** main | **Hash:** d24e4e81 | **Last commit:** 2026-03-18
- **Status:** D (deleted file in index)
- **Has:** README only
- **Role:** Stale backup of agents repo; no active use
- **Classification:** LEGACY_CANDIDATE | **Confidence:** MEDIUM
- **Why:** No systemd, cron, PM2, or script references; superseded by the live `.claude/agents`

### 3.3 /home/slimy/clawd
- **Remote:** `git@github.com:GurthBro0ks/clawd.git`
- **Branch:** main | **Hash:** ef76f425 | **Last commit:** 2026-04-05 (today!)
- **Status:** M (AGENTS.md modified)
- **Has:** AGENTS.md
- **Role:** Workspace governance / operational repo
- **Classification:** ACTIVE | **Confidence:** HIGH

### 3.4 /home/slimy/.codex/.tmp/plugins
- **Remote:** `https://github.com/openai/plugins.git`
- **Branch:** main | **Hash:** f78e3ad4 | **Last commit:** 2026-03-30
- **Status:** clean
- **Has:** README
- **Role:** Codex/OpenAI plugin ecosystem cache (temporary directory)
- **Classification:** UNKNOWN | **Confidence:** LOW
- **Why:** Not clearly integrated into NUC2 workflows; appears to be a temp cache

### 3.5 /home/slimy/kb
- **Remote:** `git@github.com:GurthBro0ks/slimy-kb.git`
- **Branch:** main | **Hash:** d149605 | **Last commit:** 2026-04-05 11:20 (today!)
- **Status:** untracked `output/lint-report.md`
- **Has:** no AGENTS.md (KB_AGENTS.md exists at KB root)
- **Role:** Knowledge base — canonical wiki source
- **Runtime:** `*/30 * * * * cd /home/slimy/kb && bash tools/kb-sync.sh pull` cron entry active
- **Classification:** ACTIVE | **Confidence:** HIGH

### 3.6 /home/slimy/.mcp_agent_mail_git_mailbox_repo
- **Remote:** none (local-only mailbox git)
- **Branch:** master | **Hash:** 43033211 | **Last commit:** 2026-02-26
- **Status:** clean
- **Has:** no README, no AGENTS.md
- **Role:** MCP agent mail git mailbox (local bare repo)
- **Classification:** DORMANT | **Confidence:** MEDIUM
- **Why:** Local bare repo; no recent commits; used by MCP agent framework

### 3.7 /home/slimy/mission-control
- **Remote:** `git@github.com:GurthBro0ks/mission-control.git`
- **Branch:** main | **Hash:** 78ff4be9 | **Last commit:** 2026-04-03
- **Status:** M (next.config.ts modified)
- **Has:** README
- **Role:** Operations / mission control dashboard
- **Runtime:** `mission-control.service` (systemd --user, active, port 3838)
- **Classification:** ACTIVE | **Confidence:** HIGH
- **Proof:** `ss -lntup | grep 3838` → `next-server (v16.1.6)` listening on 0.0.0.0:3838

### 3.8 /home/slimy/nuc-comms/mailbox_ingest
- **Remote:** `/home/slimy/nuc-comms/mailbox.git` (local)
- **Branch:** main | **Hash:** f1e690f8 | **Last commit:** 2026-01-30
- **Status:** M (report.json modified)
- **Role:** NUC1↔NUC2 mailbox ingest pipeline
- **Runtime:** `nuc-mailbox-ingest.service` (systemd --user, activating)
- **Classification:** ACTIVE | **Confidence:** HIGH
- **Why:** systemd service is present and activating; handles NUC inter-communication

### 3.9 /home/slimy/.openclaw/memory/git-notes-ledger
- **Remote:** none (local-only)
- **Branch:** master | **Hash:** 02e7c763 | **Last commit:** 2026-01-28
- **Status:** clean
- **Role:** OpenCLAW git notes persistence
- **Classification:** UNKNOWN | **Confidence:** LOW
- **Why:** Local-only; last commit Jan 2026; unclear if actively written

### 3.10 /home/slimy/.openclaw/workspace
- **Remote:** none (local-only)
- **Branch:** master | **Hash:** 4f5e485a | **Last commit:** 2026-04-03
- **Status:** untracked `.openclaw/` directory
- **Has:** AGENTS.md
- **Role:** OpenCLAW workspace
- **Classification:** ACTIVE | **Confidence:** MEDIUM
- **Why:** Recent commit (2 days ago); AGENTS.md present; but no systemd/cron evidence

### 3.11 /home/slimy/pm_updown_bot_bundle
- **Remote:** `git@github.com:GurthBro0ks/pm_updown_bot_bundle.git`
- **Branch:** main | **Hash:** a49674bc | **Last commit:** 2026-03-21
- **Status:** untracked `claude-progress.md`
- **Has:** AGENTS.md, init.sh
- **Role:** Trading bot (paper trading / proof validation)
- **Runtime:** NUC1 is primary; NUC2 cron rsync pulls data from NUC1:
  ```
  */15 * * * * rsync -az nuc1:/opt/slimy/pm_updown_bot_bundle/paper_trading/*.db /opt/slimy/trading-data-mirror/paper_trading/
  */15 * * * * rsync -az nuc1:/opt/slimy/pm_updown_bot_bundle/proofs/bootstrap_validation_*.json /opt/slimy/trading-data-mirror/proofs/
  ```
- **Classification:** DORMANT on NUC2 (shadow/consumer only) | **Confidence:** HIGH

### 3.12 /opt/slimy/app (slimyai_setup)
- **Remote:** `git@github.com:GurthBro0ks/slimyai_setup.git`
- **Branch:** main | **Hash:** 2d7edbc1 | **Last commit:** 2026-03-31
- **Status:** M (command-test-report.txt modified)
- **Has:** AGENTS.md, README
- **Role:** slimy-web/bot backend; referenced by healthcheck script
- **Runtime:** Referenced in `/opt/slimy/ops/healthcheck.sh` (if it existed); systemd healthcheck service `slimy-web-health.service` (failed)
- **Classification:** PRESENT_NOT_RUNNING | **Confidence:** MEDIUM
- **Why:** systemd unit is failed; not in PM2; but last commit is recent (4 days ago) and healthcheck script references it

### 3.13 /opt/slimy/chat-app (slime.chat)
- **Remote:** `git@github.com:GurthBro0ks/slime.chat.git`
- **Branch:** main | **Hash:** ffcb8138 | **Last commit:** 2026-02-25
- **Status:** clean
- **Has:** README
- **Role:** Revolt-based chat deployment
- **Runtime:** No PM2, systemd, cron, or port references found
- **Classification:** DORMANT | **Confidence:** MEDIUM
- **Why:** Last commit Feb 25; no active runtime references on NUC2

### 3.14 /opt/slimy/slimy-monorepo
- **Remote:** `git@github.com:GurthBro0ks/slimy-monorepo.git`
- **Branch:** main | **Hash:** 5142d4a4 | **Last commit:** 2026-04-03 (2 days ago)
- **Status:** untracked `qa-report.md`
- **Has:** AGENTS.md, init.sh, README
- **Role:** Primary application monorepo (web, admin-api, bot packages)
- **Runtime:**
  - `slimy-web.service` (systemd --user, active) serving on port **3000** ← `next-server (v16.0.7)` process 3143002
  - Multiple Dockerfiles and docker-compose.yml for infra
  - morning-brief cron: `30 8 * * * /opt/slimy/slimy-monorepo/scripts/brief/morning-brief.sh`
  - `sync-repos.sh` references it
- **Classification:** ACTIVE | **Confidence:** HIGH

### 3.15 /opt/slimy/web/slimyai-web
- **Remote:** `git@github.com:GurthBro0ks/slimyai-web.git`
- **Branch:** `fix/runtime-envs-check-2025-11-11-nuc2-snapshot` (non-maintenance branch)
- **Hash:** 1c87d787 | **Last commit:** 2025-11-16 (5 months ago)
- **Status:** clean
- **Has:** README, Dockerfile, docker-compose.yml
- **Role:** Legacy standalone web project
- **Runtime:** NOT actively served — slimy-web.service uses monorepo's `apps/web` instead
  - Evidence: monorepo `infra/docker/NUC2_STACK_STARTUP_FIX.md` explicitly removes stale `slimyai-web-*` containers before starting the new stack
- **Classification:** LEGACY_CANDIDATE | **Confidence:** HIGH
- **Why:** Branch is a fix snapshot from Nov 2025, not main; monorepo is now authoritative for slimy-web; Dockerfile and compose exist but are superseded by monorepo stack

---

## 4. Runtime Evidence (PM2 / systemd / cron / docker / ports)

### PM2
```
@limy:~$ pm2 list
┌────┬───────────────────────────┬─────────┬──────┐
│ id │ name                  │ status  │ uptime │
├────┼───────────────────────────┼─────────┼──────┤
│ 0  │ obsidian-headless-sync │ online  │ 105m   │
```
Only one PM2 process. `slimy-bot` is NOT running under PM2 on NUC2.

### systemd (system-wide)
```
● pm2-slimy.service          loaded    failed   failed  PM2 process manager
● slimy-web-health.service   loaded    failed   failed  Slimy Web Health Check
```
Both system-level services are **failed**. These are legacy; actual services run under `--user` systemd.

### systemd (--user)
```
mission-control.service   loaded  active   running   Mission Control (port 3838)
slimy-mysql-tunnel.service loaded active   running   SSH tunnel for MySQL to NUC1
slimy-web.service        loaded  active   running   Slimy Web (port 3000)
● slimy-report.service    loaded  failed   failed    Slimy Repo Health Report Generator
nuc-mailbox-ingest.service loaded activating start start NUC2 Mailbox Ingest Verify
openclaw-gateway.service   loaded active   running   OpenClaw Gateway
```

### Listening Ports
```
0.0.0.0:3838  → next-server (pid 2311610, v16.1.6)  ← mission-control
0.0.0.0:3000  → next-server (pid 3143002, v16.0.7)  ← slimy-web (monorepo)
127.0.0.1:3306 → MySQL
127.0.0.1:3307 → SSH tunnel to NUC1 MySQL
127.0.0.1:5432 → PostgreSQL
0.0.0.0:4422  → SSH
```

### Docker
Docker is not running (`docker ps` returned empty). However docker-compose files exist at:
- `/opt/slimy/slimy-monorepo/docker-compose.yml` (monorepo infra)
- `/opt/slimy/slimy-monorepo/apps/web/docker-compose.yml` (legacy slimyai-web stack)
- `/opt/slimy/app/docker-compose.yml` (slimyai_setup)
- `/opt/slimy/chat-app/compose.yml` (slime.chat)
- `/opt/slimy/web/slimyai-web/docker-compose.yml` (legacy standalone)
- `/home/slimy/octoeverywhere-config/docker-compose.yml` (octoeverywhere, separate)

### Cron
```
*/30 * * * * cd /home/slimy/kb && bash tools/kb-sync.sh pull          # KB sync
*/15 * * * * rsync -az nuc1:.../pm_updown_bot_bundle/...              # trading data mirror
0 4 * * * /home/slimy/sync-repos.sh                                    # repo sync
*/5 * * * * curl .../api/owner/notifications/discord-push             # Discord push
30 8 * * * /opt/slimy/slimy-monorepo/scripts/brief/morning-brief.sh   # morning brief
```

---

## 5. Project-by-Project State Assessment

### ACTIVE
| Project | Path | Key Evidence |
|---|---|---|
| slimy-kb | `/home/slimy/kb` | Active cron pull; last commit today |
| slimy-monorepo | `/opt/slimy/slimy-monorepo` | slimy-web.service running port 3000; morning-brief cron; monorepo infra |
| mission-control | `/home/slimy/mission-control` | mission-control.service running port 3838; last commit 2 days ago |
| agents (harness) | `/home/slimy/.claude/agents` | Used by Claude Code directly |
| clawd | `/home/slimy/clawd` | Last commit today; AGENTS.md |
| workspace | `/home/slimy/.openclaw/workspace` | Last commit 2 days ago; AGENTS.md |
| nuc-comms/mailbox_ingest | `/home/slimy/nuc-comms/mailbox_ingest` | nuc-mailbox-ingest.service activating |

### PRESENT_NOT_RUNNING
| Project | Path | Key Evidence |
|---|---|---|
| slimyai_setup | `/opt/slimy/app` | Last commit 4 days ago; healthcheck references it; systemd service failed |

### DORMANT
| Project | Path | Key Evidence |
|---|---|---|
| pm_updown_bot_bundle | `/home/slimy/pm_updown_bot_bundle` | NUC1 is primary; NUC2 only rsyncs from NUC1; last commit 15 days ago |
| slime.chat | `/opt/slimy/chat-app` | No runtime references; last commit Feb 25 |
| .mcp_agent_mail_git_mailbox_repo | `/home/slimy/.mcp_agent_mail_git_mailbox_repo` | Local bare repo; last commit Feb 26 |
| git-notes-ledger | `/home/slimy/.openclaw/memory/git-notes-ledger` | Last commit Jan 28; no active references |

### LEGACY_CANDIDATE
| Project | Path | Key Evidence |
|---|---|---|
| slimyai-web | `/opt/slimy/web/slimyai-web` | Old branch (Nov 2025 snapshot); monorepo serves web now; explicit stale-container cleanup in monorepo infra |
| agents-backup-full | `/home/slimy/.claude/agents-backup-full` | Superseded by main agents repo |

### UNKNOWN
| Project | Path | Key Evidence |
|---|---|---|
| .codex/.tmp/plugins | `/home/slimy/.codex/.tmp/plugins` | OpenAI plugins cache; no active runtime references |

---

## 6. Extra Local Projects Not In Canonical Repo List

### 6.1 ned-clawd (`/home/slimy/ned-clawd`)
- **Remote:** none found
- **Last commit:** 2026-02-26 (ARCHITECTURE.md)
- **Role:** Appears to be a nested CLAWD operational directory — reports, config, memory, ops
- **References:** Mentions slimy-monorepo and pm_updown_bot_bundle in ARCHITECTURE.md
- **Classification:** UNKNOWN | **Confidence:** LOW
- **KB Gap:** No wiki/projects article exists

### 6.2 octoeverywhere-config (`/home/slimy/octoeverywhere-config`)
- **Remote:** none
- **Role:** OctoEverywhere printer integration config (docker-compose.yml with `COMPANION_MODE=klipper`)
- **Classification:** PRESENT_NOT_RUNNING | **Confidence:** MEDIUM
- **KB Gap:** No wiki/projects article (MISSING from wiki/projects/)

### 6.3 chriss-agent (`/home/slimy/chriss-agent`)
- **Remote:** none found
- **Role:** Bridge service — running `webhook-bridge.py` on port 3850
- **Runtime:** `ps aux` shows `python3 /home/slimy/chriss-agent/scripts/webhook-bridge.py` (pid 1178942, running since Mar14)
- **Classification:** ACTIVE | **Confidence:** HIGH
- **KB Gap:** No wiki/projects article (MISSING)

### 6.4 slimy-web-health.service systemd unit
- **Role:** One-shot health check via `/opt/slimy/ops/healthcheck.sh`
- **State:** failed (systemd)
- **Note:** `ops/` directory not found at scan time; may have been cleaned up
- **Classification:** LEGACY_CANDIDATE | **Confidence:** MEDIUM

---

## 7. Legacy-Candidate or Ambiguous Items

### slimyai-web (standalone) — LEGACY_CANDIDATE
Strong evidence of supersession:
- Branch is a fix-snapshot from Nov 2025, not main
- Monorepo infra docs explicitly remove `slimyai-web-*` containers as "stale"
- slimy-web.service (systemd --user) serves from monorepo's `apps/web`
- Last commit 5 months ago; no recent activity
- **Confidence: HIGH**

### agents-backup-full — LEGACY_CANDIDATE
- Superseded by `/home/slimy/.claude/agents` (the active harness repo)
- No active references anywhere
- **Confidence: MEDIUM** (could be a valid backup someone wants to keep)

### slimyai_setup (/opt/slimy/app) — AMBIGUOUS
- Last commit was 4 days ago (recent)
- Has a healthcheck service that currently fails
- But appears to still be worked on
- **Classification: PRESENT_NOT_RUNNING** — not ready to call LEGACY

---

## 8. KB Gaps / Missing wiki project articles

### Missing wiki/projects/ articles (confirmed by `ls wiki/projects/` vs. actual local repos):

| Missing Article | Local Project | KB Gap Severity |
|---|---|---|
| `slimy-kb.md` | `/home/slimy/kb` | HIGH — KB is a core project |
| `slimyai_setup.md` | `/opt/slimy/app` | MEDIUM — active project, recent commits |
| `slimyai-web.md` | `/opt/slimy/web/slimyai-web` | MEDIUM — legacy-candidate, should document |
| `slime-chat.md` | `/opt/slimy/chat-app` | LOW — dormant, but still a project |
| `ned-clawd.md` | `/home/slimy/ned-clawd` | MEDIUM — operational directory with architecture |
| `chriss-agent.md` | `/home/slimy/chriss-agent` | HIGH — running service, no article |
| `octoeverywhere.md` | `/home/slimy/octoeverywhere-config` | LOW — printer integration |
| `mailbox.md` | `/home/slimy/nuc-comms/mailbox.git` | MEDIUM — NUC comms infrastructure |
| `git-notes-ledger.md` | `/home/slimy/.openclaw/memory/git-notes-ledger` | LOW — OpenCLAW internal |
| `codex-plugins.md` | `/home/slimy/.codex/.tmp/plugins` | LOW — unclear if needed |

**Existing articles (10):** agents-plugin-ecosystem, capture-dashboard, clawd-workspace-governance, mission-control, operator-console, pm-updown-bot-bundle, slimy-chat, slimy-discord-bot, slimy-monorepo, slimy-web

---

## 9. Recommended Next Actions

1. **HIGH:** Write `chriss-agent.md` wiki article — running service with no KB documentation
2. **HIGH:** Write `slimy-kb.md` wiki article — core KB project with no wiki/projects/ article
3. **MEDIUM:** Write `ned-clawd.md` — operational directory with architecture docs, no wiki coverage
4. **MEDIUM:** Clarify slimyai_setup vs slimy-monorepo relationship — slimyai_setup appears to be the legacy path for the bot/backend, but monorepo is now primary
5. **MEDIUM:** Investigate `slimy-web-health.service` failure — healthcheck script references `/opt/slimy/ops/healthcheck.sh` which was not found
6. **LOW:** Determine if `agents-backup-full` should be archived or deleted
7. **LOW:** Determine if `slimyai-web` (standalone) should be archived or migrated fully to monorepo
8. **INFO:** slimy-discord-bot article exists in KB but the actual bot runs on NUC1 — confirm where the canonical bot code lives and whether the NUC2 `app/` is the bot or something else

---

## Summary Table

| project | local path | github match | runtime status | classification | confidence | proof |
|---|---|---|---|---|---|---|
| slimy-kb | /home/slimy/kb | GurthBro0ks/slimy-kb | cron pull active | ACTIVE | HIGH | last commit today; cron entry |
| slimy-monorepo | /opt/slimy/slimy-monorepo | GurthBro0ks/slimy-monorepo | slimy-web.service port 3000; morning-brief cron | ACTIVE | HIGH | next-server pid 3143002 on :3000; cron entry |
| mission-control | /home/slimy/mission-control | GurthBro0ks/mission-control | mission-control.service port 3838 | ACTIVE | HIGH | next-server pid 2311610 on :3838; systemd active |
| slimyai_setup | /opt/slimy/app | GurthBro0ks/slimyai_setup | systemd healthcheck failed | PRESENT_NOT_RUNNING | MEDIUM | last commit 4 days ago; healthcheck script reference |
| slimyai-web | /opt/slimy/web/slimyai-web | GurthBro0ks/slimyai-web | NOT running; monorepo serves web instead | LEGACY_CANDIDATE | HIGH | monorepo infra doc removes stale containers; last commit Nov 2025 |
| pm_updown_bot_bundle | /home/slimy/pm_updown_bot_bundle | GurthBro0ks/pm_updown_bot_bundle | NUC2 rsync consumer only | DORMANT on NUC2 | HIGH | cron rsync from NUC1; no local PM2/systemd |
| slime.chat | /opt/slimy/chat-app | GurthBro0ks/slime.chat (extra) | no runtime refs | DORMANT | MEDIUM | last commit Feb 25; no systemd/cron/PM2 |
| agents (harness) | /home/slimy/.claude/agents | wshobson/agents | used by Claude Code harness | ACTIVE | HIGH | harness files present; active use by CLI |
| agents-backup-full | /home/slimy/.claude/agents-backup-full | wshobson/agents (backup) | superseded | LEGACY_CANDIDATE | MEDIUM | no active refs; replaced by .claude/agents |
| clawd | /home/slimy/clawd | GurthBro0ks/clawd | no direct runtime; CLAUDE.md referenced | ACTIVE | HIGH | last commit today; AGENTS.md |
| workspace | /home/slimy/.openclaw/workspace | local-only | no runtime refs; recent commit | ACTIVE | MEDIUM | last commit 2 days ago; AGENTS.md |
| mailbox_ingest | /home/slimy/nuc-comms/mailbox_ingest | local mailbox.git | nuc-mailbox-ingest.service activating | ACTIVE | HIGH | systemd user service present and activating |
| mailbox bare repo | /home/slimy/.mcp_agent_mail_git_mailbox_repo | local-only | MCP agent mail bare repo | DORMANT | MEDIUM | local-only; last commit Feb 26 |
| git-notes-ledger | /home/slimy/.openclaw/memory/git-notes-ledger | local-only | OpenCLAW internal memory | UNKNOWN | LOW | last commit Jan 28; no active refs |
| .codex plugins | /home/slimy/.codex/.tmp/plugins | openai/plugins (cache) | unclear | UNKNOWN | LOW | temp cache dir; no active refs |
| ned-clawd | /home/slimy/ned-clawd | none | operational directory; architecture docs | UNKNOWN | LOW | ARCHITECTURE.md references monorepo/bot-bundle |
| chriss-agent | /home/slimy/chriss-agent | none | webhook-bridge.py running on port 3850 | ACTIVE | HIGH | ps shows running process since Mar14; no KB article |
| octoeverywhere-config | /home/slimy/octoeverywhere-config | none | docker compose present; not running | PRESENT_NOT_RUNNING | MEDIUM | docker compose exists; not in pm2/systemd |
