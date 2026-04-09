# NUC1 Runtime Truth Update — 2026-04-09

**Audience:** PM / operator
**Compiled by:** Claude Code (SlimyAI NUC1)
**Date:** 2026-04-09
**Status:** Authoritative

---

## 1. Discord Bot — Live Runtime

| Item | Value |
|------|-------|
| Bot name | `slimy-bot-v2` |
| Type | TypeScript Discord bot |
| Host | NUC1 |
| Supervisor | PM2 (id=1) |
| PID | 178717 |
| Uptime | 12h (since 2026-04-09T00:54) |
| PM2 restarts | 7 (historical — not a crash loop; see below) |
| Discord servers | 3 connected |
| Entry point | `node /opt/slimy/slimy-monorepo/apps/bot/dist/index.js` |
| Codebase | `/opt/slimy/slimy-monorepo/apps/bot/` |
| Branch | `main` |
| Health endpoint | `http://localhost:3000/health` |

**Verification:** `pm2 list` → `slimy-bot-v2` shows `online`

### Restart History (7 restarts / ~12h)
- **1 real incident:** 2026-04-05T23:01 — DNS failure (EAI_AGAIN) + MySQL transient unavailability. Auto-recovered. No action taken.
- **6 intentional:** PM2 `restart` commands during deploy windows (14:49 04-08 → 00:54 04-09). Clean logins confirmed every time.
- **Current state:** Stable since 2026-04-09T00:54, no new restarts.

**No crash loop.** PM2 `unstable_restarts: 0` confirms. All restarts produced clean Discord login.

### Non-Critical Observations (no action required)
- `DiscordAPIError[10062]: Unknown interaction` — Discord interaction timeout race condition, handled gracefully
- Missing `config/slimy_ai.persona.json` — falls back to defaults, not fatal
- `ephemeral` deprecation warning — Discord.js v14→v15 migration note, not fatal

---

## 2. Old Bot — Archived / Decommissioned

| Item | Value |
|------|-------|
| Old bot path | `/opt/slimy/app` — **removed** (directory does not exist) |
| Archive | `/opt/slimy/app-archive-20260408.tar.gz` (preserved cutover artifact) |
| Rollback script | `/home/slimy/rollback-bot.sh` (preserved but inactive) |
| PM2 entry | None — old bot fully removed from PM2 |
| Cutover date | 2026-04-03 |
| Predecessor repo | `GurthBro0ks/slimyai_setup` (JS Discord bot, deprecated) |

**The old JS bot is not running and should not be restarted.** The archive is for rollback reference only.

---

## 3. slimy-report.service — FAILED

| Item | Value |
|------|-------|
| Service | `slimy-report.service` (systemd) |
| Status | FAILED |
| Classification | Legacy / deprecated |
| Action | None required. This is a known dead service. |

This service is not critical. It was a reporting/healthcheck utility that is no longer maintained. Do not attempt to restart it without explicit instruction.

---

## 4. chriss-bridge — Port 3850 Status

**Note:** The chriss-agent/webhook-bridge on **port 3850 is a NUC2 service**, not NUC1.

- **Location:** NUC2 at `/home/slimy/chriss-agent`
- **Process:** `python3 /home/slimy/chriss-agent/scripts/webhook-bridge.py`
- **Port:** 3850 (NUC2)
- **Running since:** 2026-03-14
- **Managed by:** `chriss-bridge.service` (systemd --user on NUC2)
- **Status on NUC1:** Not present — no process on port 3850 on NUC1

NUC1 does **not** run chriss-bridge. Any port-3850 references in old KB pages are NUC2-specific.

---

## 5. Authoritative Docs — What to Read

The following docs reflect the current runtime truth (as of 2026-04-09):

| Doc | What It Covers | Authority |
|-----|----------------|-----------|
| `/home/slimy/server-state.md` | PM2 processes, systemd services, ports, host routing | **Primary** — maintained by agent at session close |
| `/home/slimy/kb/wiki/projects/slimy-discord-bot.md` | Bot architecture, runtime, cutover history | **Primary** — KB-compiled |
| `/home/slimy/kb/wiki/projects/slimyai-setup.md` | Old bot deprecation status | **Primary** — KB-compiled |
| `/home/slimy/kb/wiki/architecture/nuc-topology-and-services.md` | NUC1/NUC2 service placement matrix | **Primary** — KB-compiled |
| `/home/slimy/kb/wiki/projects/chriss-agent.md` | chriss-bridge on NUC2 port 3850 | **Primary** — NUC2-specific |
| `/home/slimy/kb/wiki/projects/mission-control.md` | Mission-control on NUC2 port 3838 | **Primary** — NUC2-specific |
| `/home/slimy/kb/wiki/projects/slimy-monorepo.md` | Monorepo structure and bot migration history | **Primary** |
| `/home/slimy/scan-report-bot-runtime-2026-04-09.md` | Full bot runtime scan | **Supporting** |
| `/home/slimy/scan-report-bot-restarts-2026-04-09.md` | Restart root-cause analysis | **Supporting** |

**Do not reference** older wiki pages that still describe the old JS bot at `/opt/slimy/app` as live — those have been superseded.

---

## 6. Low-Priority Follow-Ups

| Item | Priority | Notes |
|------|----------|-------|
| Discord.js `ephemeral` deprecation | Low | Fix before v15 migration. Not causing restarts. |
| Missing `config/slimy_ai.persona.json` | Low | Add if persona functionality is needed. Not causing restarts. |
| slimy-backup-pull.service FAILED | Low | Backup pull from NUC2 is failing. If backups are needed, investigate. |
| slimy-report.service FAILED | Low | Legacy service. Retire or document intentional deprecation. |
| 7 PM2 restarts (monitoring only) | Low | Watch restart count over next 48h. Re-investigate if count grows without intentional restarts. |

None of these require immediate action.

---

## Runtime Truth Summary (One Page)

```
PM2 (NUC1):
  slimy-bot-v2  — online, pid 178717, 12h uptime, 3 Discord servers
  agent-loop    — online, pid 1047, 3D uptime

SYSTEMD (NUC1):
  mission-control    — active, port 3838
  pm2-slimy         — active (PM2 daemon)
  slimy-backup-pull — FAILED (backup pull from NUC2, low priority)
  slimy-report      — FAILED (legacy, do not restart)

DOCKER (NUC1):
  slimy-mysql       — healthy, port 3306
  slimy-chat stack  — healthy, port 8080

PORT 3000:
  slimy-bot-v2 health server (not web)

PORT 3838:
  mission-control (NUC1 systemd)

CHRISS-BRIDGE:
  NOT on NUC1 — port 3850 is NUC2. See chriss-agent.md on NUC2.

DISCORD BOT CUTOVER:
  Old bot (/opt/slimy/app) — archived, removed, not running
  New bot (slimy-bot-v2) — live in monorepo TypeScript
  Cutover date: 2026-04-03
```
