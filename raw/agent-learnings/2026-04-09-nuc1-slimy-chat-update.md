# Slimy Chat — NUC1 Runtime Update
- Host: nuc1
- Project: slimy-chat
- Date: 2026-04-09
- Type: supplemental

## Gap: Wiki Article Missing Full Runtime Details

The existing wiki article (`projects/slimy-chat.md`) covers the app flow but is missing Docker stack specifics.

## NUC1 Runtime State (2026-04-09)
- **Path:** `/home/slimy/slimy-chat`
- **Remote:** `git@github.com:GurthBro0ks/slime.chat.git` (origin), `https://github.com/stoatchat/self-hosted` (upstream)
- **Branch:** main
- **Dirty:** YES (1 uncommitted)
- **Supervisor:** Docker (16-container stack via docker-compose)
- **Ports:** 8080 (Caddy HTTP), 8443 (Caddy HTTPS), 7881 (LiveKit), 50000-50100 (LiveKit UDP)

## Docker Stack Containers
slimy-chat_caddy_1, slimy-chat_web_1, slimy-chat_smtp_1, slimy-chat_api_1, slimy-chat_pushd_1, slimy-chat_autumn_1, slimy-chat_events_1, slimy-chat_crond_1, slimy-chat_minio_1, slimy-chat_rabbit_1, slimy-chat_livekit_1, slimy-chat_database_1 (MongoDB), slimy-chat_proxy_1, slimy-chat_gifbox_1, slimy-chat_redis_1 (KeyDB), slimy-mysql (MySQL 8, port 3306)

## Missing from Wiki Article
- Full Docker container list
- Port mapping details
- LiveKit voice/video configuration
- MinIO S3-compatible storage
- Upstream fork relationship (stoatchat/self-hosted)

## Powered By
stoat-source (`/home/slimy/stoat-source`) — Rust backend for Revolt/Stoat platform