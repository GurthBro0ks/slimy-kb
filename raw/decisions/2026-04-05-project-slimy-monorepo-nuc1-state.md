---
description: NUC1 runtime evidence for slimy-monorepo — active PM2 services, port bindings, git state
type: reference
---

# Project: Slimy Monorepo — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Project name:** slimy-monorepo
- **GitHub:** GurthBro0ks/slimy-monorepo
- **Canonical path:** `/opt/slimy/slimy-monorepo`
- **Alt path:** `/home/slimy/slimy-monorepo` (symlink → `/opt/slimy/slimy-monorepo`, not a separate repo)
- **Branch:** main
- **Last commit:** `cad0803` 2026-04-05 — "Merge branch 'feature/merge-chat-app'"
- **Dirty:** YES — uncommitted: `apps/bot/data_store.json`, `apps/web/app/trader/`, `apps/web/components/trader/`

## Classification
- **ACTIVE** — HIGH confidence

## NUC1 Runtime Evidence

### PM2
- `slimy-bot-v2` — online, port 3000/tcp, 110.7mb memory
- PM2 id: 10

### Ports
| Port | Process |
|------|---------|
| 3000 | Node/PM2 (slimy-bot-v2) |

### systemd
None directly referencing slimy-monorepo; mission-control runs as separate systemd service.

### Git State
- Dirty working tree — uncommitted changes in bot data store and trader app directories
- Symlink at `/home/slimy/slimy-monorepo` should NOT be replaced with a fresh clone

## Relationship to Other Projects
- Slimy Discord Bot (slimy-bot-v2) is the TypeScript successor to old JS bot in slimyai_setup
- Cutover from slimyai_setup to slimy-bot-v2 completed 2026-04-03
- Web app served at port 3000 alongside mission-control at 3838

## Risks / Anomalies
- Dirty git state — agent should advise running truth gate before work
- Trader app (`apps/web/app/trader/`, `apps/web/components/trader/`) has uncommitted work — likely active development

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
