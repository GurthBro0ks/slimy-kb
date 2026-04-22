# Mailbox NUC Comms
> Category: projects
> Sources: raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc1-state.md, raw/decisions/2026-04-05-project-mailbox-nuc-comms-nuc2-state.md, raw/research/2026-04-05-nuc1-project-anomalies.md
> Created: 2026-04-05
> Updated: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-22 00:28 UTC (git)
> Version: r28 / 83a6a85
KB METADATA -->

Mailbox NUC Comms is the git-based inter-NUC communication transport used to push machine reports from NUC1 to NUC2 for ingest.

## NUC1 Side — mailbox_outbox

**Path:** `/home/slimy/nuc-comms/mailbox_outbox`
**Remote:** `ssh://slimy@192.168.68.65:4422/home/slimy/nuc-comms/mailbox.git` (NUC2 local git)
**Branch:** main; last commit `9eb07cc` 2026-03-18
**Dirty:** YES — untracked `report.json`, `report.sha256`, `report_20260319T121234Z.json`

**Cron:** `0 4 * * * /home/slimy/sync-repos.sh` — pushes reports to NUC2 mailbox.git

> **Anomaly:** Project map names this `mailbox_ingest` but the actual local path is `mailbox_outbox`. NUC1 only has mailbox_outbox (push side); NUC2 has the ingest side. See [NUC1 Project Anomalies](../research/2026-04-05-nuc1-project-anomalies.md).

## Cross-NUC Flow
```
NUC1 (mailbox_outbox) --git push over SSH--> NUC2 (mailbox.git)
                                                      |
                                                      v
                                              NUC2 nuc-mailbox-ingest.timer
                                                      |
                                                      v
                                              Ingest script verifies SHA + schema
                                                      |
                                                      v
                                              /home/slimy/nuc-comms/mailbox_ingest/report.json
```

## Security
- Restricted SSH guard (`mailbox-ssh-guard.sh`) limits the mailbox key to `git-receive-pack`/`git-upload-pack` only
- JSON schema validation on ingest
- SHA256 checksum verification
- Source: See [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)

## NUC2 Side — Receive / Ingest

**Path:** `/home/slimy/nuc-comms/mailbox_ingest`
**Remote:** `/home/slimy/nuc-comms/mailbox.git` (local bare repo)
**Branch:** main; last commit `f1e690f8` 2026-01-30
**Dirty:** YES — untracked `report.json`

**Supervisor:** `systemd --user` (`nuc-mailbox-ingest.service` → ACTIVATING)
- Timer: `nuc-mailbox-ingest.timer` triggers ingest every ~10 minutes after boot
- Script: `/home/slimy/nuc-comms/bin/nuc2_mailbox_ingest.sh`
- Flow: bare repo clone → SHA verify → schema validate → atomically update `mailbox_ingest/report.json`

**State:** ACTIVE on NUC2 (ingest side running/activating)

## See Also
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
- [Harness Runtime Topology](../architecture/harness-runtime-topology.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
