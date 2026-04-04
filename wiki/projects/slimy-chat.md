# Slimy Chat
> Category: projects
> Sources: raw/articles/seed-chat-app-readme.md, raw/articles/nuc1-seed-slimy-chat-readme.md, raw/articles/nuc1-seed-stoat-source-readme.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

Slimy Chat is a Revolt-based chat deployment with invite-only registration and email verification.

## Core Flow
- Invite-code gated account creation.
- Email verification before activation.
- Username/password login and password reset flow.

## Stack
- MongoDB for data storage.
- Redis/KeyDB for session and cache behavior.
- RabbitMQ for queueing and MinIO for file storage.

## Deployment Profile (NUC1)
- Public entrypoint: `chat.slimyai.xyz`.
- Internal stack runs via Docker Compose with Caddy, API/events services, media/file services, SMTP relay, and LiveKit voice/video.
- Port profile includes `8080`/`8443` (chat edge), `7881` (LiveKit), and UDP media range `50000-50100`.
- Backup path is automated via `/home/slimy/backups/stoat-chat/backup.sh` with daily cadence.

## Upstream Lineage
- Slimy Chat is based on Stoat/Revolt self-hosted components.
- Upstream backend includes `delta` (REST), `bonfire` (events), `autumn` (files), `january` (proxy), `gifbox` (Tenor), and daemon services.
- This lineage explains why Slimy Chat operations include both app-level and infrastructure-level service checks.

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Auth and Retired Services](../architecture/auth-and-retired-services.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
