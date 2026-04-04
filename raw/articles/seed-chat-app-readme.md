# Slimy Chat

Self-hosted chat platform deployed at **chat.slimyai.xyz**

Based on [Stoat](https://github.com/stoatchat/self-hosted) (Revolt fork).

---

## Login & Registration Flow

### 1. Invite-Only Setup
- Registration is **invite-only** (`invite_only=true` in Revolt.toml)
- Invite codes: `slimy-001` through `slimy-005`

### 2. User Registration
1. Visit https://chat.slimyai.xyz
2. Click **Register**
3. Enter invite code, email, password, username
4. Submit → Verification email sent

### 3. Email Verification
- SMTP (Postfix) sends verification email
- User clicks link in email
- Account activated

### 4. Login
1. Visit https://chat.slimyai.xyz
2. Click **Login**
3. Enter email + password
4. JWT token issued (session stored in Redis)
5. WebSocket connection established for real-time

### 5. Password Reset
1. Login → **Forgot Password**
2. Enter email
3. Reset link sent via SMTP
4. User sets new password

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Database | MongoDB |
| Cache/Sessions | Redis (KeyDB) |
| Message Queue | RabbitMQ |
| File Storage | MinIO (S3-compatible) |
| Web Server | Caddy |
| Frontend | Stoat Web (Solid.js SPA) |
| Voice/Video | LiveKit (WebRTC) |
| Email | Postfix (SMTP relay) |

### Container Services (16 total)
- `database` - MongoDB
- `redis` - KeyDB
- `rabbit` - RabbitMQ
- `minio` - MinIO file storage
- `caddy` - Caddy web server
- `api` - Stoat API v0.11.1
- `events` - Real-time events
- `autumn` - File server
- `january` - Image proxy
- `gifbox` - Tenor GIF integration
- `crond` - Scheduled tasks
- `pushd` - Push notifications
- `voice-ingress` - Voice chat
- `livekit` - Voice/video (WebRTC)
- `web` - Frontend SPA
- `smtp` - Postfix email relay

---

## Deployment

### Quick Start
```bash
cd /home/slimy/slimy-chat
docker compose up -d
```

### Ports Exposed
| Port | Service |
|------|---------|
| 8080 | HTTP (internal Caddy) |
| 8443 | HTTPS (internal Caddy) |
| 7881 | LiveKit |
| 50000-50100 | Voice UDP |

### Environment
- Domain: chat.slimyai.xyz
- SSL: Let's Encrypt (via host Caddy)

---

## Admin

- **Admin account**: gurth@slimyai.xyz
- **Config**: `Revolt.toml`
- **Branding**: `custom/` directory

---

## Backups

- **Script**: `/home/slimy/backups/stoat-chat/backup.sh`
- **Schedule**: Daily 3:00 AM UTC
- **Retention**: 14 days

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/` | Web UI |
| `/api` | REST API |
| `/events` | WebSocket |
| `/autumn` | File server |
| `/livekit` | Voice/Video |

---

## Upstream

- **Upstream repo**: https://github.com/stoatchat/self-hosted
- **Pull updates**: `git fetch upstream && git merge upstream/main`

---

## License

AGPL-3.0 (inherited from Revolt/Stoat)
