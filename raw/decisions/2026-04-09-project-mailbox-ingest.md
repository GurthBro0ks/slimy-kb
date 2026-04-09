# Mailbox Ingest (NUC Comms)
- Host: nuc2
- Repo path: /home/slimy/nuc-comms/mailbox_ingest
- GitHub remote: /home/slimy/nuc-comms/mailbox.git (bare local repo, not GitHub)
- Branch: main
- Type: tool (NUC-to-NUC communication)
- Status: active
- Priority: medium
- Purpose: Mailbox-based NUC-to-NUC communication ingest. Synchronizes messages between NUCs via a shared git mailbox repository.
- Dependencies: git, standard shell tools
- Services: none (runs as cron or manual script)
- Truth gate: `git -C /home/slimy/nuc-comms/mailbox_ingest log -1 --oneline`
- Risks: depends on NUC1 being reachable; bare repo at `/home/slimy/nuc-comms/mailbox.git` must be accessible
- Current work: auto-sync docs only

## Wiki coverage
mailbox-nuc-comms.md exists but may be thin. Check if it has services, truth gate.