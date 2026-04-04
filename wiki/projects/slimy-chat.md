# Slimy Chat
> Category: projects
> Sources: raw/articles/seed-chat-app-readme.md
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

## See Also
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Auth and Retired Services](../architecture/auth-and-retired-services.md)
