# Mailbox Ingest (NUC Comms)
> Category: projects
> Sources: raw/decisions/2026-04-09-project-mailbox-ingest.md, raw/research/2026-04-09-nuc2-project-inventory.md
> Created: 2026-04-09
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-20 12:27 UTC (git)
> Version: r21 / 51be377
KB METADATA -->

Mailbox-based NUC-to-NUC communication ingest. Synchronizes reports from NUC1 to NUC2 via a shared git bare repository.

## Runtime State (NUC2)
- **Path:** `/home/slimy/nuc-comms/mailbox_ingest`
- **Remote:** `/home/slimy/nuc-comms/mailbox.git` (bare local repo, not GitHub)
- **Branch:** main
- **Status:** ACTIVE
- **AGENTS.md:** NO
- **README.md:** YES — NUC-to-NUC communication ingest
- **Truth gate:** `git -C /home/slimy/nuc-comms/mailbox_ingest log -1 --oneline`
- **Services:** none (runs as systemd timer or manual)
- **Dependencies:** git; bare repo at `/home/slimy/nuc-comms/mailbox.git` must be accessible
- **Risks:** depends on NUC1 being reachable

## See Also
- [Mailbox NUC Comms](mailbox-nuc-comms.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
