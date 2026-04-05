---
description: NUC2 runtime evidence for slimyai_setup — old JS Discord bot path, healthcheck failed, present not running
type: reference
---

# Project: Slimyai Setup — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** slimyai_setup (aka slimy-app, /opt/slimy/app)
- **GitHub:** GurthBro0ks/slimyai_setup
- **Local path:** `/opt/slimy/app`
- **Branch:** main
- **Last commit:** `2d7edbc1` 2026-03-31 (4 days ago)
- **Dirty:** YES — untracked `command-test-report.txt`

## Classification
- **PRESENT_NOT_RUNNING** — MEDIUM confidence
- Distinct from NUC1 classification (LEGACY_CANDIDATE — not running there either, but no systemd presence)
- On NUC2: has a healthcheck service and recent commit activity, just not currently running

## NUC2 Runtime Evidence

### systemd (--user)
- `slimy-web-health.service` — **FAILED**
  - One-shot health check targeting `/opt/slimy/ops/healthcheck.sh`
  - This service is currently failed
  - `ops/` directory not found at scan time (may have been cleaned up)

### Git State
- Dirty: `command-test-report.txt` untracked
- Has AGENTS.md and README

### Relationship to Other Projects
- **NUC1 classification**: LEGACY_CANDIDATE — cutover to slimy-bot-v2 (monorepo) completed 2026-04-03
- **NUC2 classification**: PRESENT_NOT_RUNNING — slightly different emphasis because NUC2 has an active (but failing) healthcheck service referencing it
- The healthcheck script likely checks if slimy-web or slimy-bot is running correctly
- `/opt/slimy/ops/healthcheck.sh` path no longer present — reason for failure

## Why PRESENT_NOT_RUNNING vs LEGACY_CANDIDATE
- Recent commits (4 days ago) suggest active work during cutover period
- Active systemd service (even if failed) suggests recent operational concern
- If truly abandoned, would be LEGACY_CANDIDATE on both NUCs
- Keep PRESENT_NOT_RUNNING on NUC2 to reflect the healthcheck systemd presence

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
