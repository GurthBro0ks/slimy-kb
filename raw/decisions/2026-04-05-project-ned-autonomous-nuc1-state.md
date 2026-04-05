---
description: NUC1 runtime evidence for ned-autonomous — PM2 agent-loop orchestrator
type: reference
---

# Project: Ned-Autonomous — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Project name:** ned-autonomous
- **GitHub:** GurthBro0ks/ned-autonomous
- **Local path:** `/home/slimy/ned-autonomous`
- **Branch:** main
- **Last commit:** `09353c8` 2026-03-18
- **Dirty:** NO
- **README:** Yes

## Classification
- **ACTIVE** — HIGH confidence

## NUC1 Runtime Evidence

### PM2
- **PM2 id:** 0 (first process)
- **Process name:** `agent-loop`
- **Status:** online
- **Memory:** 17.4mb
- **CPU:** 0%
- **Role:** Core autonomous orchestrator — primary loop for autonomous agent operation

### Relationship to ned-clawd
- ned-autonomous is the PM2-managed core autonomous loop
- ned-clawd manages workspace subagents (workspace-executor, workspace-researcher) via cron
- agent-loop (ned-autonomous) is the parent/orchestrator; ned-clawd scripts handle registration and lifecycle

### Relationship to OpenCLAW
- agent-loop registers with openclaw-gateway (ports 18789-18792)
- openclaw-gateway manages workspace-executor and workspace-researcher

## Risks / Anomalies
- Low memory footprint (17.4mb) — suggests lightweight orchestration loop
- Last commit 2026-03-18 — stable, no recent churn
- No git dirty state — clean working tree

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
