# NUC2 Current State

> Category: architecture
> Updated: 2026-04-15T17:25:51Z
> Status: active

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

## Host
- **Hostname:** slimy-nuc2
- **Last updated:** 2026-04-15T17:25:51Z

## Active Services
- │ 0  │ obsidian-headless-sync    │ default     │ N/A     │ fork    │ 5365     │ 2D     │ 190  │ online    │ 0%       │ 81.3mb   │ slimy    │ disabled │

## Network Ports
- `LISTEN 0      200                      127.0.0.1:5432       0.0.0.0:*`
- `LISTEN 0      128                        0.0.0.0:3850       0.0.0.0:*    users:(("python3",pid=1009,fd=3))`
- `LISTEN 0      511                        0.0.0.0:3838       0.0.0.0:*    users:(("next-server (v1",pid=2447,fd=21))`
- `LISTEN 0      511                        0.0.0.0:3000       0.0.0.0:*    users:(("next-server (v1",pid=2451,fd=21))`
- `LISTEN 0      511                      127.0.0.1:18792      0.0.0.0:*    users:(("openclaw-gatewa",pid=2448,fd=30))`
- `LISTEN 0      511                      127.0.0.1:18793      0.0.0.0:*    users:(("openclaw-gatewa",pid=2448,fd=31))`
- `LISTEN 0      511                      127.0.0.1:18790      0.0.0.0:*    users:(("openclaw-gatewa",pid=2448,fd=21))`
- `LISTEN 0      128                      127.0.0.1:3307       0.0.0.0:*    users:(("ssh",pid=2449,fd=5))`
- `LISTEN 0      128                          [::1]:3307          [::]:*    users:(("ssh",pid=2449,fd=4))`
- `LISTEN 0      511                          [::1]:18790         [::]:*    users:(("openclaw-gatewa",pid=2448,fd=24))`

## KB Health
- **Orphaned pages:** 30
- **Weak-linked pages:** 8

## Open Issues (from todo queue)
- **[HIGH/candidate]** Resolve 30 orphaned wiki pages — wiki_gap (fresh)
- **[HIGH/cooling_down]** Review orphaned page: architecture/nuc2-server-state.md — wiki_gap (stale)
- **[HIGH/candidate]** Review orphaned page: log.md — wiki_gap (fresh)
- **[HIGH/cooling_down]** Review orphaned page: projects/actionbook.md — wiki_gap (stale)
- **[HIGH/cooling_down]** Review orphaned page: projects/agents-backup-full.md — wiki_gap (stale)
- **[HIGH/cooling_down]** Review orphaned page: projects/apify-market-scanner.md — wiki_gap (stale)

<!-- END MACHINE MANAGED -->

## Human Notes

<!-- Add notes here — this section is preserved on machine-managed runs -->

## See Also
- [NUC Topology and Services](nuc-topology-and-services.md)
- [NUC1 Current State](nuc1-current-state.md)
- [Slimy KB](../projects/slimy-kb.md)