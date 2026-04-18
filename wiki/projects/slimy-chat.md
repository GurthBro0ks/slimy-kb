# Slimy Chat
> Category: projects
> Sources: raw/articles/seed-chat-app-readme.md, raw/agent-learnings/2026-04-09-nuc1-slimy-chat-update.md
> Created: 2026-04-04
> Updated: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-17 12:24 UTC (git)
> Version: r13 / 0f1f90b
KB METADATA -->

Slimy Chat is a Revolt-based self-hosted chat platform at chat.slimyai.xyz. Invite-only registration with email verification.

## Core Flow
- Invite-code gated account creation.
- Email verification before activation.
- Username/password login and password reset flow.

## Stack
- MongoDB for data storage.
- Redis/KeyDB for session and cache behavior.
- RabbitMQ for queueing and MinIO for file storage.

## NUC1 Runtime State (2026-04-09)
- **Path:** `/home/slimy/slimy-chat`
- **Remote:** `git@github.com:GurthBro0ks/slime.chat.git` (origin), `https://github.com/stoatchat/self-hosted` (upstream)
- **Branch:** main
- **Dirty:** YES (1 uncommitted)
- **Supervisor:** Docker (16-container stack via docker-compose)
- **Ports:** 8080 (Caddy HTTP), 8443 (Caddy HTTPS), 7881 (LiveKit), 50000-50100 (LiveKit UDP)

## Docker Stack Containers
`slimy-chat_caddy_1`, `slimy-chat_web_1`, `slimy-chat_smtp_1`, `slimy-chat_api_1`, `slimy-chat_pushd_1`, `slimy-chat_autumn_1`, `slimy-chat_events_1`, `slimy-chat_crond_1`, `slimy-chat_minio_1`, `slimy-chat_rabbit_1`, `slimy-chat_livekit_1`, `slimy-chat_database_1` (MongoDB), `slimy-chat_proxy_1`, `slimy-chat_gifbox_1`, `slimy-chat_redis_1` (KeyDB), `slimy-mysql` (MySQL 8, port 3306)

## Powered By
- [Stoat Source](stoat-source.md) — Rust backend for Revolt/Stoat platform (`/home/slimy/stoat-source`)

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

**Last updated:** 2026-04-17T12:24:09Z
**NUC1 status:** DIRTY, synced
**NUC1 commit:** `482c773` — docs: auto-sync project docs from slimy-nuc1 2026-04-11
**Branch:** main

### Open Issues
- **[HIGH/candidate]** NUC1 repo has uncommitted changes: slimy-chat (repo_drift, 5x, fresh)

### Evidence
- `raw/inbox-nuc1/`

### Related Pages
- [Repo Health Overview](./_project-health-index.md)
- [NUC1 Current State](../architecture/nuc1-current-state.md)

<!-- END MACHINE MANAGED -->

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Auth and Retired Services](../architecture/auth-and-retired-services.md)
