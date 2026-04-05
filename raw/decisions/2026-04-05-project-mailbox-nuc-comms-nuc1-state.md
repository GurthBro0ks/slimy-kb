---
description: NUC1 inter-NUC git mailbox — mailbox_outbox (mailbox_ingest NOT FOUND on NUC1)
type: reference
---

# Project: Mailbox NUC Comms — NUC1 Runtime State

**Compiled from:** 2026-04-05-nuc1-project-discovery.md, 2026-04-05-nuc1-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC1

## Canonical Identification
- **Local path:** `/home/slimy/nuc-comms/mailbox_outbox`
- **Remote:** `ssh://slimy@192.168.68.65:4422/home/slimy/nuc-comms/mailbox.git` (NUC2 local git)
- **Branch:** main
- **Last commit:** `9eb07cc` 2026-03-18
- **Dirty:** YES — untracked: `report.json`, `report.sha256`, `report_20260319T121234Z.json`

## CRITICAL DISCREPANCY: mailbox_ingest NOT FOUND
- Project map lists `mailbox_ingest` at `/home/slimy/nuc-comms/mailbox_ingest`
- **FIND CONFIRMS:** Only `mailbox_outbox/.git` exists in `/home/slimy/nuc-comms/`
- `mailbox_ingest` does NOT exist on NUC1
- The NUC2 side has `mailbox.git` which NUC1 pushes to via mailbox_outbox

## Classification
- **PRESENT_NOT_RUNNING** — HIGH confidence
- (The git sync cron runs but the process itself is a git push-only; not a persistent daemon)

## Runtime Evidence

### Cron References
```
# sync-repos.sh runs daily at 4am
0 4 * * * /home/slimy/sync-repos.sh

# pm_updown_bot_bundle's push-sync may also reference this
```

### sync-repos.sh
- Git-based inter-NUC communication script
- Pushes reports to NUC2's mailbox.git over ssh
- Source: `/home/slimy/sync-repos.sh`

### Cross-NUC Flow
```
NUC1 (mailbox_outbox) --git push--> NUC2 (mailbox.git)
                                      |
                                      v
                              NUC2 mailbox_ingest pulls/processes
```

## Relationship to Cross-NUC Communication Matrix
- Part of the cross-NUC mailbox transport — see architecture/cross-nuc-communication-matrix.md
- NUC2 side implements the ingest/pulll side via `nuc-mailbox-ingest.service`

## Anomaly
- mailbox_ingest (canonical name per project map) does NOT exist on NUC1
- mailbox_outbox (actual local name) is the NUC1 side of the mailbox transport
- Project map should be corrected to reflect mailbox_outbox as the NUC1 mailbox component

## Sources
- 2026-04-05-nuc1-project-discovery.md
- 2026-04-05-nuc1-project-state-matrix.md
