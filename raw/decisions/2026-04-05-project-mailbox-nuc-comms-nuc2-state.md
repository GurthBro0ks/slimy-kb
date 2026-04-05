---
description: NUC2 side of mailbox-nuc-comms — receive side (bare repo + ingest service), distinct from NUC1 push side
type: reference
---

# Project: Mailbox NUC Comms — NUC2 Receive/Ingest Side

**Compiled from:** 2026-04-05-nuc2-project-discovery.md, 2026-04-05-nuc2-project-state-matrix.md
**Date:** 2026-04-05
**NUC:** NUC2

## Relationship to Existing NUC1 Doc
This is the **NUC2 ingest/receive companion** to the existing `2026-04-05-project-mailbox-nuc-comms-nuc1-state.md` which covers the push side (mailbox_outbox on NUC1).

The existing wiki article `projects/mailbox-nuc-comms.md` covers both sides. This doc provides the NUC2-specific runtime evidence.

## NUC2 Receive Side Components

### Component 1: Bare git repo (mailbox.git)
- **Path:** `/home/slimy/nuc-comms/mailbox.git`
- **Remote:** none (local bare repo)
- **Branch:** main
- **Role:** NUC2 receives NUC1 pushes here via SSH

### Component 2: mailbox_ingest (working tree)
- **Path:** `/home/slimy/nuc-comms/mailbox_ingest`
- **Remote:** `/home/slimy/nuc-comms/mailbox.git` (local)
- **Branch:** main
- **Last commit:** `f1e690f8` 2026-01-30
- **Dirty:** YES — untracked `report.json`

### Component 3: nuc-mailbox-ingest.service
- **systemd (--user):** `nuc-mailbox-ingest.service` — **ACTIVATING**
- Timer likely triggers: `nuc-mailbox-ingest.timer`
- Ingest script: `/home/slimy/nuc-comms/bin/nuc2_mailbox_ingest.sh`

## Classification
- **ACTIVE** on NUC2 — ingest service is present and activating

## NUC2 Runtime Evidence

### systemd (--user)
- `nuc-mailbox-ingest.service` — ACTIVATING (start)
- `openclaw-gateway.service` — ACTIVE, running (ports 18790/18792/18793)

### Ports
| Port | Process |
|------|---------|
| 18790/18792/18793 | openclaw-gateway |

## Cross-NUC Flow (full)
```
NUC1 (mailbox_outbox) --git push over SSH--> NUC2 (mailbox.git)
                                                      |
                                                      v
                                              nuc-mailbox-ingest.timer
                                              nuc-mailbox-ingest.service
                                                      |
                                                      v
                                              /home/slimy/nuc-comms/bin/nuc2_mailbox_ingest.sh
                                                      |
                                                      v
                                              mailbox_ingest/report.json (verified)
```

## Sources
- 2026-04-05-nuc2-project-discovery.md
- 2026-04-05-nuc2-project-state-matrix.md
