# Stoat Source
> Category: projects
> Sources: raw/decisions/2026-04-09-project-stoat-source.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

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

## See Also
- [Slimy Chat](slimy-chat.md)
- [Chat App (Slime.Chat)](chat-app.md)
