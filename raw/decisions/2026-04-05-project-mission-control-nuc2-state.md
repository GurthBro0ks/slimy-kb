---
description: NUC2 runtime evidence for mission-control — systemd service on port 3838, separate from monorepo
type: reference
---

# Project: Mission Control — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** mission-control
- **GitHub:** GurthBro0ks/mission-control
- **Local path:** `/home/slimy/mission-control`
- **Branch:** main
- **Last commit:** `78ff4be9` 2026-04-03 (2 days ago)
- **Dirty:** YES — modified `next.config.ts`

## Classification
- **ACTIVE** — HIGH confidence

## NUC2 Runtime Evidence

### systemd (--user)
- `mission-control.service` — **ACTIVE, running**, port **3838**
  - Process: `next-server (v16.1.6)` pid 2311610
  - Listening on 0.0.0.0:3838

### Ports
| Port | Process |
|------|---------|
| 3838 | next-server v16.1.6 (pid 2311610) — mission-control |

### Git State
- Dirty: `next.config.ts` modified locally

### Role on NUC2
- Operations / mission control dashboard
- Separate from slimy-web (monorepo) which serves on port 3000
- Referenced in Cross-NUC Communication Matrix (edge reverse-proxy hop from NUC1 → NUC2 mission-control:3838)

## Relationship to Other Projects
- Slimy-monorepo serves web on port 3000; mission-control is a separate Next.js app on port 3838
- Both use systemd --user on NUC2
- Referenced in: cross-nuc-communication-matrix.md, nuc-topology-and-services.md, harness-runtime-topology.md

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
