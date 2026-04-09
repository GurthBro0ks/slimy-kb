# NUC2 Project Inventory — 2026-04-09

> Host: slimy-nuc2 | Generated: 2026-04-09T0000Z

## System Overview

**Ports in use:** 3000 (slimy-web), 3838 (mission-control), 5432 (postgres), 22, 631, 443 (nginx/Caddy), 3306 (local MySQL via socket), 3307 (SSH tunnel to NUC1 MySQL), 18790-18793 (openclaw-gateway), 3850 (unknown), 37725 (unknown)

**Systemd services running:** slimy-web.service, mission-control.service, openclaw-gateway.service, slimy-mysql-tunnel.service, slimy-report.service (FAILED)

**PM2 processes:** obsidian-headless-sync (online)

**Repositories:** 13 git repos across /home/slimy and /opt/slimy

---

## Repository Inventory

### 1. slimy-monorepo
- **Path:** `/opt/slimy/slimy-monorepo` (symlink: `/home/slimy/slimy-monorepo`)
- **Remote:** `git@github.com:GurthBro0ks/slimy-monorepo.git`
- **Branch:** main
- **Last 3 commits:**
  - `a910a9a` fix: /snail/club sort order — highest power now shows rank 1 at top
  - `2fcf024` feat: /snail/stats QA fixes — debug dock visibility, refresh feedback, empty movers
  - `fa3788b` docs: auto-sync project docs from slimy-nuc2 2026-04-08
- **AGENTS.md:** YES — monorepo agent rules, `pnpm lint`/`pnpm test:all` truth gate
- **README.md:** YES — pnpm workspace, apps/web (port 3000), apps/admin-api (port 3080), apps/admin-ui (port 3081)
- **package.json:** YES
- **Tests:** Yes (shared-auth tests, node_modules test files)
- **Services:** `slimy-web.service` (systemd) — Next.js on port 3000
- **Purpose:** Primary web application — owner panel, snail club/stats, crypto trading tab, trader dashboard
- **Status:** active
- **Key subdirs:** apps/web (Next.js), apps/admin-api, apps/admin-ui, packages/, lib/
- **Dependencies:** MySQL (NUC1 via tunnel 3307), Prisma, Next.js, Tailwind
- **Ports:** 3000 (web), 3080 (admin-api — DEAD), 3081 (admin-ui — DEAD)
- **Truth gate:** `pnpm --filter web lint && pnpm --filter web build`

---

### 2. chat-app (slime.chat)
- **Path:** `/opt/slimy/chat-app`
- **Remote:** `git@github.com:GurthBro0ks/slime.chat.git`
- **Branch:** main
- **Last 3 commits:**
  - `988df00` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `6d0060b` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `9e0e769` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **README.md:** YES — Self-hosted chat platform at chat.slimyai.xyz, Revolt fork (Stoat), MongoDB, Redis, RabbitMQ, MinIO, Caddy, Postfix
- **Status:** active — Docker-based, 16 container services, invite-only registration
- **Services:** Docker containers (database/MongoDB, redis/KeyDB, rabbit/RabbitMQ, minio, caddy, api/Stoat)
- **Ports:** chat.slimyai.xyz (443 via Caddy)
- **Purpose:** Self-hosted chat — not integrated with slimy-web auth, no user management overlap

---

### 3. app (slimyai_setup)
- **Path:** `/opt/slimy/app`
- **Remote:** `git@github.com:GurthBro0ks/slimyai_setup.git`
- **Branch:** main
- **Last 3 commits:**
  - `c1fbf1b` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `62efd54` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `8de37f4` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** YES — Node.js bot project agent rules
- **README.md:** YES — Super Snail Discord bot with club analytics, GPT-4 vision, DALL-E image gen, sheet sync
- **package.json:** YES
- **Purpose:** Primary Discord bot (super-snail) — club analytics, /club commands, sheet syncing, OCR vision
- **Status:** active — Node.js Discord bot, PM2 managed, SSH tunnel for MySQL
- **Key scripts:** scripts/ingest-club-screenshots.js, bot deployment via ecosystem.config.js
- **Dependencies:** MySQL (slimyai_prod), Google Sheets API, OpenAI GPT-4 Vision
- **Ports:** 3307 (MySQL tunnel to NUC1)
- **Truth gate:** `node -e "require('./index.js')"` smoke test

---

### 4. slimyai-web (standalone legacy)
- **Path:** `/opt/slimy/web/slimyai-web`
- **Remote:** `git@github.com:GurthBro0ks/slimyai-web.git`
- **Branch:** `fix/runtime-envs-check-2025-11-11-nuc2-snapshot`
- **Last 3 commits:**
  - `132b391` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `8de37f4` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `62efd54` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **README.md:** YES — Next.js 16 with App Router, Admin API proxies, codes aggregator, MDX docs, Playwright tests
- **Status:** archived — superseded by slimy-monorepo apps/web, has VERSION.md snapshot from 2026-04-08
- **Purpose:** Legacy standalone web app — admin API integration, codes aggregator
- **Not running:** no systemd/PM2 services, no listening ports

---

### 5. mission-control
- **Path:** `/home/slimy/mission-control`
- **Remote:** `git@github.com:GurthBro0ks/mission-control.git`
- **Branch:** main
- **Last 3 commits:**
  - `8d33bd3` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `573d7a3` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `6cb0e02` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **README.md:** YES — Retro-styled agent command center, `npm run start -- -p 3838`
- **package.json:** YES
- **Status:** active — `mission-control.service` systemd running on port 3838
- **Purpose:** Agent command center — tasks, agents, calendar, comms, memory endpoints
- **Ports:** 3838
- **API:** `/api/health`, `/api/tasks`, `/api/agents`, `/api/calendar`, `/api/comms`, `/api/memory`
- **Truth gate:** `curl http://localhost:3838/api/health`

---

### 6. pm_updown_bot_bundle
- **Path:** `/home/slimy/pm_updown_bot_bundle`
- **Remote:** `git@github.com:GurthBro0ks/pm_updown_bot_bundle.git`
- **Branch:** main
- **Last 3 commits:**
  - `28c2d41` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `3852be3` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `546fae1` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** YES — Polymarket trading bot rules, `./scripts/run_tests.sh` truth gate
- **README.md:** YES — Polymarket trading bot (Python), strategies/, venues/, scripts/, Ralph automation
- **.env:** YES
- **Status:** active — trading bot
- **Purpose:** Polymarket prediction market trading bot — runner.py, strategies/, venues/
- **No services:** not running as a daemon on NUC2, likely runs on NUC1 or another machine
- **Truth gate:** `./scripts/run_tests.sh`

---

### 7. clawd
- **Path:** `/home/slimy/clawd`
- **Remote:** `git@github.com:GurthBro0ks/clawd.git`
- **Branch:** main
- **Last 3 commits:**
  - `03f949c` chore: update memory - compound nightly review 2026-04-09
  - `950a020` docs: add NUC1 unreachable issue to MEMORY.md
  - `50175b6` docs: daily memory Apr 3-8, 2026
- **AGENTS.md:** YES — OpenClaw daemon rules
- **README.md:** YES — OpenClaw workspace governance
- **Status:** active — has uncommitted changes (dirty)
- **Purpose:** OpenClaw CLAWD daemon — workspace governance, autonomous agent, memory
- **No services:** runs as Claude Code subprocess, not a daemon
- **Truth gate:** `git -C /home/slimy/clawd log -1 --oneline`

---

### 8. workspace (openclaw workspace agent)
- **Path:** `/home/slimy/.openclaw/workspace`
- **Remote:** local-only
- **Branch:** master
- **Last 3 commits:**
  - `8e1b7a8` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `59c57d9` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `c32e95b` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** YES — SOUL.md/USER.md/MEMORY.md based personal agent workspace
- **README.md:** YES
- **Status:** active — personal Claude Code workspace, reads SOUL.md/USER.md on start
- **Purpose:** OpenClaw workspace agent — personal agent home directory with memory

---

### 9. kb (slimy-kb)
- **Path:** `/home/slimy/kb`
- **Remote:** `git@github.com:GurthBro0ks/slimy-kb.git`
- **Branch:** main
- **Last 3 commits:**
  - `49c97af` kb: child-compile 20260409-112520
  - `aa93d69` kb: autofile claude 20260409-112519
  - `e48d189` kb: child-compile 20260409-110242
- **AGENTS.md:** NO
- **README.md:** YES
- **Status:** active — knowledge base shared between NUC1 and NUC2
- **Structure:** wiki/ (compiled articles), raw/ (source docs), output/, tools/
- **Tools:** kb-sync.sh pull/push, wiki CLI, kb-search.sh
- **Purpose:** Cross-NUC knowledge base — wiki articles compiled from raw agent learnings and project docs

---

### 10. agents (wshobson/agents)
- **Path:** `/home/slimy/.claude/agents-backup-full`
- **Remote:** `git@github.com:wshobson/agents.git`
- **Branch:** main
- **Last 3 commits:**
  - `56db49e` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `109ab6e` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `9cd45cc` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **README.md:** YES — Claude Code plugins marketplace (112 specialized agents, 146 skills, 72 plugins)
- **Status:** archived — backup/full mirror of wshobson/agents, not actively used on NUC2
- **Purpose:** Claude Code agent plugin marketplace backup

---

### 11. .mcp_agent_mail_git_mailbox_repo
- **Path:** `/home/slimy/.mcp_agent_mail_git_mailbox_repo`
- **Remote:** local-only (no push URL)
- **Branch:** master
- **Last 3 commits:**
  - `cbbf096` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `f2b6716` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `b2ce327` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **README.md:** YES
- **Status:** active — MCP agent mail git mailbox
- **Purpose:** MCP agent mail git mailbox repository

---

### 12. mailbox_ingest
- **Path:** `/home/slimy/nuc-comms/mailbox_ingest`
- **Remote:** `/home/slimy/nuc-comms/mailbox.git` (bare git repo)
- **Branch:** main
- **Last 3 commits:**
  - `e7c80a6` docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `e31b937` docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `56b5034` docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **AGENTS.md:** NO
- **README.md:** YES — NUC-to-NUC communication ingest
- **Status:** active — NUC comms mailbox ingest
- **Purpose:** Mailbox-based NUC-to-NUC communication ingest

---

### 13. agents (original symlink)
- **Path:** `/home/slimy/.claude/agents` (referenced in AGENTS.md project map)
- **Status:** NOT FOUND at this path — only agents-backup-full exists

---

## Service Map

| Service | Type | Port | Status | Project |
|---------|------|------|--------|---------|
| slimy-web | systemd | 3000 | active | slimy-monorepo |
| mission-control | systemd | 3838 | active | mission-control |
| openclaw-gateway | systemd | 18790-18793 | active | workspace/clawd |
| slimy-mysql-tunnel | systemd | 3307 | active | app (slimyai_setup) |
| slimy-report | systemd | — | FAILED | ? |
| obsidian-headless-sync | PM2 | — | online | kb |
| postgres | systemd | 5432 | active | ? |
| nginx | systemd | 443/80 | active | system |
| Caddy (local) | systemd | 443 | active | chat-app |
| SSH tunnel (NUC1 MySQL) | systemd | 3307 | active | app |

---

## Wiki Coverage Status

**Existing wiki project articles (22 total):**
- agents-plugin-ecosystem.md
- apify-market-scanner.md
- capture-dashboard.md
- chriss-agent.md
- clawd-agent-rules.md
- clawd-workspace-governance.md
- mailbox-nuc-comms.md
- mission-control.md
- ned-autonomous.md
- nuc1-project-anomalies.md
- obsidian-headless-sync.md
- obsidian-vault-automation.md
- openclaw-agents.md
- operator-console.md
- pm-updown-bot-bundle.md
- slimyai-setup.md
- slimy-chat.md
- slimy-discord-bot.md
- slimy-kb.md
- slimy-monorepo.md
- slimy-web.md
- workspace-agent-rules.md

**Projects NOT covered (need raw KB docs):**
- slimy-monorepo (apps/web subcomponent) — has `slimy-monorepo.md` but lacks services/ports/truth gate
- chat-app (slime.chat) — no wiki article at all
- app (slimyai_setup) — has `slimyai-setup.md` but lacks services/ports/truth gate details
- slimyai-web (legacy) — has `slimy-web.md` but refers to dead admin-api/admin-ui
- mission-control — has `mission-control.md` but missing truth gate details
- pm_updown_bot_bundle — has `pm-updown-bot-bundle.md`
- clawd — has `clawd-agent-rules.md`
- workspace — has `workspace-agent-rules.md` but it's thin
- kb — has `slimy-kb.md`
- mailbox_ingest — has `mailbox-nuc-comms.md` (partial coverage)
- agents-backup-full — no article (archived)
- .mcp_agent_mail_git_mailbox_repo — no article (minor)

---

## Priority Projects for KB Documentation

1. **chat-app** — No wiki article exists at all, large Docker-based app
2. **slimy-monorepo** — Primary production app, needs truth gate + services documented
3. **app (slimyai_setup)** — Discord bot, primary services, needs more detail
4. **mission-control** — Running service, needs truth gate
5. **slimyai-web** — Legacy archived, needs status annotation

---

## Notes

- `/home/slimy/.claude/agents` symlink does not exist — only `agents-backup-full`
- `/opt/slimy/app` is the Discord bot (super-snail), NOT to be confused with slack app
- Several repos are only documentation mirrors (auto-sync project docs from NUC2)
- slimy-report.service is failed — needs investigation
- port 3850 open by python3 — unknown process