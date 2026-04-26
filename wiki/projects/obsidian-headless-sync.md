# Obsidian Headless Sync
> Category: projects
> Sources: raw/decisions/2026-04-05-project-obsidian-headless-sync-nuc2-state.md
> Created: 2026-04-05
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-26 00:35 UTC (git)
> Version: r43 / 35740c1
KB METADATA -->

Obsidian Headless Sync is the sole PM2-managed process on NUC2, providing vault synchronization for Obsidian notes.

## Runtime State (NUC2 — 2026-04-05)
- **PM2 name:** `obsidian-headless-sync`
- **PM2 id:** 0
- **Status:** online
- **Mode:** fork
- **PID:** 3258479
- **Memory:** 72.4mb
- **CPU:** 0%
- **Restarts:** 0
- **Uptime:** 105 minutes (at scan time)
- **User:** slimy
- **PM2 startup:** disabled (process running but startup resurrection is off)

## Significance
- This is the **only PM2 process** on NUC2
- All other services on NUC2 use systemd --user
- PM2 daemon is present but manages no other applications

## KB Gap
- No wiki/projects/ article existed before this session
- Only runtime presence is PM2 list output; no git repo, no systemd unit

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
