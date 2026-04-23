# Mailbox Outbox
> Category: projects
> Sources: raw/decisions/2026-04-09-project-mailbox-outbox.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-22 12:29 UTC (git)
> Version: r32 / a285643
KB METADATA -->

NUC communication module — message outbox for inter-NUC communication via SSH/git-based sync. NUC1 push side of the mailbox transport.

## Runtime State (NUC1)
- **Path:** `/home/slimy/nuc-comms/mailbox_outbox`
- **Remote:** `ssh://slimy@192.168.68.65:4422/home/slimy/nuc-comms/mailbox.git` (local network, NUC2)
- **Branch:** main
- **Status:** ACTIVE
- **Truth gate:** `git -C /home/slimy/nuc-comms/mailbox_outbox log -1 --oneline`
- **Cron:** `0 4 * * * /home/slimy/sync-repos.sh` — pushes reports to NUC2 mailbox.git
- **Risks:** local-only SSH remote (not on GitHub); depends on NUC1→NUC2 SSH reachability

## Cross-NUC Flow
```
NUC1 (mailbox_outbox) --git push over SSH--> NUC2 (mailbox.git)
                                                      |
                                                      v
                                              NUC2 nuc-mailbox-ingest.timer
```

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-22T12:29:09Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `668ae78` — docs: auto-sync project docs from slimy-nuc1 2026-04-11
**Branch:** main

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: mailbox_outbox (repo_drift, 15x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [Mailbox NUC Comms](mailbox-nuc-comms.md)
- [Mailbox Ingest (NUC Comms)](mailbox-ingest.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
