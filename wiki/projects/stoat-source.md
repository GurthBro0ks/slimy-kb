# Stoat Source
> Category: projects
> Sources: raw/decisions/2026-04-09-project-stoat-source.md, raw/research/2026-04-09-nuc1-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 20:38 UTC (git)
> Version: r9 / 217f421
KB METADATA -->

Rust-based backend services for the Revolt/Stoat chat platform. Powers the slimy-chat Docker stack — the 16-container self-hosted chat system at chat.slimyai.xyz on NUC1.

## Why It Matters

Stoat Source is the critical infrastructure behind the SlimyAI chat platform. Every message, voice call, file upload, and user session at chat.slimyai.xyz flows through Stoat's Rust backend. It is a fork of the Revolt chat platform with custom modifications. Being 13 commits ahead of upstream means significant local customization that must be maintained during any upstream merges.

## Runtime State (NUC1)
- **Path:** `/home/slimy/stoat-source`
- **Remote:** `git@github.com:stoatchat/stoatchat.git`, branch `main`
- **Status:** ACTIVE — ahead of remote by 13 commits
- **Priority:** CRITICAL (powers the chat platform)
- **Truth gate:** `cargo build --manifest-path /home/slimy/stoat-source/Cargo.toml` (verify Rust compiles)

## Architecture

Stoat is a Rust monorepo with multiple crates providing different backend services:

| Crate | Purpose |
|-------|---------|
| core/config | Configuration management |
| core/database | Database access layer |
| core/files | File handling |
| core/models | Data models |
| core/permissions | Permission system |
| delta | REST API server |
| bonfire | WebSocket server (real-time messaging) |
| services/january | January proxy service |
| services/gifbox | GIF hosting service |
| services/autumn | File server |
| services/crond | Cron daemon |

## Current Role in the System
- Powers the entire chat.slimyai.xyz platform
- Docker containers are built from this source
- 13 commits ahead of upstream (stoatchat/stoatchat) — local customization not pushed
- When chat services need updates, this repo is rebuilt and redeployed

## Docker Stack Integration
The compiled Stoat binaries run inside the slimy-chat Docker stack (16 containers on NUC1):
- `slimy-chat_api_1` — Stoat API (delta crate)
- `slimy-chat_events_1` — Event processing (bonfire crate)
- `slimy-chat_autumn_1` — File server (services/autumn)
- `slimy-chat_gifbox_1` — GIF hosting (services/gifbox)
- `slimy-chat_crond_1` — Cron daemon (services/crond)

Plus supporting services: MongoDB, Redis (KeyDB), RabbitMQ, MinIO, Caddy, Postfix, LiveKit.

## Dependencies
- Rust (stable toolchain)
- MongoDB (primary database)
- MySQL (secondary)
- RabbitMQ (message queue)
- MinIO (S3-compatible file storage)
- Redis (caching/sessions)

## Relationships / Dependencies
- **Powers:** [Chat App (Slime.Chat)](chat-app.md) and [Slimy Chat](slimy-chat.md)
- **Upstream:** stoatchat/stoatchat on GitHub
- **Deployed via:** Docker Compose on NUC1
- **Dependencies:** MongoDB, Redis, RabbitMQ, MinIO, Caddy

## Risks
- Upstream (stoatchat) moves independently — local branch is 13 commits ahead
- Merging upstream changes requires careful conflict resolution
- No CI/CD mentioned — builds are manual (`cargo build`)
- Critical infrastructure — if Stoat breaks, chat.slimyai.xyz goes down

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
- [Slimy Chat](slimy-chat.md) — the running chat platform
- [Chat App (Slime.Chat)](chat-app.md) — Docker stack and operational details
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
