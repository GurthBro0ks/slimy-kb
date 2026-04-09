# Chat App (Slime.Chat)
- Host: nuc2
- Repo path: /opt/slimy/chat-app
- GitHub remote: git@github.com:GurthBro0ks/slime.chat.git
- Branch: main
- Type: application (self-hosted chat platform)
- Status: active
- Priority: medium
- Purpose: Self-hosted chat at chat.slimyai.xyz. Based on Stoat (Revolt fork). Invite-only registration, email verification via SMTP, JWT sessions with Redis. WebSocket real-time messaging.
- Dependencies: MongoDB, Redis (KeyDB), RabbitMQ, MinIO (S3), Caddy, Postfix, LiveKit (WebRTC — voice/video)
- Services: Docker compose (16 containers: database/MongoDB, redis/KeyDB, rabbit/RabbitMQ, minio, caddy, api/Stoat v0.11.1)
- Ports: chat.slimyai.xyz on 443 via Caddy
- Truth gate: `docker ps` to check all containers running; curl https://chat.slimyai.xyz/api/health
- Risks: 16 container services to maintain; email/SMTP dependency for user registration; no auth integration with slimy-web
- Current work: No active development, auto-sync docs only

## Wiki article needed
No wiki article exists for chat-app. Needs compilation once chat-app.md raw doc is reviewed.