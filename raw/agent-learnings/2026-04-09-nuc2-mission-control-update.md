# NUC2 Mission Control Update — 2026-04-09

## Verified Runtime (2026-04-09)
- **Path:** `/home/slimy/mission-control`
- **Branch:** main; HEAD `8d33bd3` 2026-04-08
- **Supervisor:** `systemd --user` (`mission-control.service`)
- **Listening:** 0.0.0.0:3838 (next-server pid 1731)
- **Classification:** ACTIVE | Confidence: HIGH

## Truth Gate
```bash
# Health check
curl http://localhost:3838/api/health

# Systemd status
systemctl --user status mission-control.service
```

## API Endpoints
- `GET /api/health` — health check
- `GET /api/tasks` — list all tasks
- `GET /api/tasks/:id` — single task
- `POST /api/tasks` — create task
- `GET /api/agents` — list agents
- `GET /api/calendar?month=YYYY-MM` — calendar events
- `GET /api/comms?limit=N` — messages
- `POST /api/comms` — send message
- `GET /api/memory` — list memory files