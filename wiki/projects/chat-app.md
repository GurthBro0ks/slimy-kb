# Chat App (Slime.Chat)
> Category: projects
> Sources: raw/decisions/2026-04-09-project-chat-app.md, raw/research/2026-04-09-nuc2-project-inventory.md
> Created: 2026-04-09
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-20 00:26 UTC (git)
> Version: r19 / c7808b6
KB METADATA -->

Self-hosted invite-only chat platform at chat.slimyai.xyz. Based on Stoat (Revolt fork). Not integrated with slimy-web auth — separate user management.

## Runtime State (NUC2)
- **Path:** `/opt/slimy/chat-app`
- **Remote:** `git@github.com:GurthBro0ks/slime.chat.git`, branch `main`
- **Last 3 commits:**
  - `988df00` — docs: auto-sync project docs from slimy-nuc2 2026-04-08
  - `6d0060b` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
  - `9e0e769` — docs: auto-sync project docs from slimy-nuc2 2026-04-05
- **Status:** ACTIVE — Docker-based, 16 container services

## Architecture
- **Platform:** Stoat (Revolt fork) — self-hosted alternative to Discord/Slack
- **Invite-only registration** with email verification via SMTP
- **JWT sessions** with Redis (KeyDB)
- **WebSocket** real-time messaging
- **WebRTC** via LiveKit for voice/video

## Docker Stack (16 Containers)
| Container | Purpose |
|-----------|---------|
| database | MongoDB |
| redis | KeyDB (Redis fork) |
| rabbit | RabbitMQ |
| minio | S3-compatible object storage |
| caddy | TLS reverse proxy |
| api | Stoat API v0.11.1 |
| proxy | Reverse proxy |
| gifbox | GIF hosting |
| crond | Cron daemon |
| autumn | File server |
| livekit-server | WebRTC voice/video |
| events | Event processing |
| pushd | Push notifications |
| smtp | Postfix mail relay |
| web | Stoat frontend |
| database | MongoDB primary |

## Ports & Access
- **URL:** chat.slimyai.xyz (443 via Caddy)
- **Ports exposed:** 443, 8080 (internal)

## Dependencies
- MongoDB, Redis (KeyDB), RabbitMQ, MinIO (S3), Caddy, Postfix, LiveKit

## Truth Gate
- `docker ps` — verify all 16 containers running
- `curl https://chat.slimyai.xyz/api/health` — API health check

## Risks
- 16 container services to maintain
- Email/SMTP dependency for user registration
- No auth integration with slimy-web

## See Also
- [Slimy Chat](slimy-chat.md)
- [Stoat Source](stoat-source.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
