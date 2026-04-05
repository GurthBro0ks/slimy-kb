---
description: NUC2 runtime evidence for slimy-monorepo — slimy-web.service on port 3000, morning-brief cron, SSH tunnel
type: reference
---

# Project: Slimy Monorepo — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** slimy-monorepo
- **GitHub:** GurthBro0ks/slimy-monorepo
- **Canonical path:** `/opt/slimy/slimy-monorepo` (also symlinked at `/home/slimy/slimy-monorepo`)
- **Branch:** main
- **Last commit:** `5142d4a4` 2026-04-03 (2 days ago)
- **Dirty:** YES — untracked `qa-report.md`

## Classification
- **ACTIVE** — HIGH confidence

## NUC2 Runtime Evidence

### systemd (--user)
- `slimy-web.service` — **ACTIVE, running**, port **3000**
  - Process: `next-server (v16.0.7)` pid 3143002
  - Serves `apps/web` from the monorepo
- `slimy-mysql-tunnel.service` — **ACTIVE, running**
  - SSH tunnel forwarding NUC1 MySQL (port 3306) to NUC2 localhost:3307

### Cron
```
30 8 * * * /opt/slimy/slimy-monorepo/scripts/brief/morning-brief.sh
```

### Ports
| Port | Process |
|------|---------|
| 3000 | next-server v16.0.7 (pid 3143002) — slimy-web (monorepo) |
| 3306 | MySQL (local) |
| 3307 | SSH tunnel → NUC1 MySQL |

### Docker
- `docker-compose.yml` at monorepo root
- Additional Dockerfiles within `apps/web` and `infra/docker/`
- Docker not currently running (ps returned empty at scan time)

### NUC2 Role vs NUC1
- NUC1: slimy-bot-v2 PM2 process at port 3000 (bot API)
- NUC2: slimy-web Next.js app at port 3000 (web frontend)
- Both use same monorepo but different entrypoints/services

## Relationship to Other Projects
- **Slimyai_setup** successor: monorepo's `apps/bot` (slimy-bot-v2) is the TypeScript successor to the old JS bot at `/opt/slimy/app` (slimyai_setup). Cutover completed 2026-04-03.
- **Slimyai-web**: Legacy standalone web app at `/opt/slimy/web/slimyai-web` — superseded; monorepo infra explicitly removes stale slimyai-web-* containers before starting new stack.
- **Mission-control**: Separate Next.js app on port 3838, also systemd-managed on NUC2.

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
