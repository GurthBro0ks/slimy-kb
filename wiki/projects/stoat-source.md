# Stoat Source
> Category: projects
> Sources: raw/decisions/2026-04-09-project-stoat-source.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 19:37 UTC (git)
> Version: r7 / 56f8615
KB METADATA -->

Rust-based backend services for the Revolt/Stoat chat platform. Powers the slimy-chat Docker stack on NUC1.

## Runtime State (NUC1)
- **Path:** `/home/slimy/stoat-source`
- **Remote:** `git@github.com:stoatchat/stoatchat.git`, branch `main`
- **Status:** ACTIVE — ahead of remote by 13 commits
- **Truth gate:** `cargo build --manifest-path /home/slimy/stoat-source/Cargo.toml` (verify Rust compiles)

## Crates
| Crate | Purpose |
|-------|---------|
| core/config | Configuration |
| core/database | Database access |
| core/files | File handling |
| core/models | Data models |
| core/permissions | Permission system |
| delta | REST API |
| bonfire | WebSocket server |
| services/january | January proxy |
| services/gifbox | GIF hosting |
| services/autumn | File server |
| services/crond | Cron daemon |

## Dependencies
- Rust, MongoDB, MySQL, RabbitMQ, MinIO, Redis

## Services
Docker containers in slimy-chat stack (16 containers including stoat services).

## Risks
- Upstream (stoatchat) moves independently — local branch is 13 commits ahead

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-16T12:23:09Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `020a4a0` — docs: auto-sync project docs from slimy-nuc1 2026-04-11
**Branch:** main

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: stoat-source (repo_drift, 3x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [Slimy Chat](slimy-chat.md)
- [Chat App (Slime.Chat)](chat-app.md)
