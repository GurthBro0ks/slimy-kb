---
description: NUC2 runtime evidence for pm_updown_bot_bundle — rsync consumer from NUC1, no local runtime, dormant on NUC2
type: reference
---

# Project: PM UpDown Bot Bundle — NUC2 Runtime State

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Canonical Identification
- **Project name:** pm_updown_bot_bundle
- **GitHub:** GurthBro0ks/pm_updown_bot_bundle
- **Local path:** `/home/slimy/pm_updown_bot_bundle`
- **Branch:** main
- **Last commit:** `a49674bc` 2026-03-21 (15 days ago)
- **Dirty:** YES — untracked `claude-progress.md`

## Classification
- **DORMANT on NUC2** — HIGH confidence
- Primary runtime is on NUC1; NUC2 only consumes rsync data

## NUC2 Runtime Evidence

### Cron (rsync consumer)
```
*/15 * * * * rsync -az nuc1:/opt/slimy/pm_updown_bot_bundle/paper_trading/*.db /opt/slimy/trading-data-mirror/paper_trading/
*/15 * * * * rsync -az nuc1:/opt/slimy/pm_updown_bot_bundle/proofs/bootstrap_validation_*.json /opt/slimy/trading-data-mirror/proofs/
```
NUC2 mirrors trading data from NUC1 every 15 minutes. No local execution of bot strategies.

### Process Manager
- None (no PM2, no systemd service)

### Git State
- Dirty: `claude-progress.md` untracked
- Has AGENTS.md, init.sh

## Contrast with NUC1
| Aspect | NUC1 | NUC2 |
|--------|------|------|
| Runtime | ACTIVE — 20+ cron entries, runner.py, ML pipeline | DORMANT — rsync consumer only |
| Strategy execution | Yes | No |
| paper_trading/*.db | Source | Mirror target |
| proofs/ | Source | Mirror target |

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
