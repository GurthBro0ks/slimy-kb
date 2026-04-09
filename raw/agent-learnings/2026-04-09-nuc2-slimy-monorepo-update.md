# NUC2 Slimy Monorepo Update — 2026-04-09

## NUC2 Runtime State (verified 2026-04-09)
- **Canonical path:** `/opt/slimy/slimy-monorepo`; `/home/slimy/slimy-monorepo` is a symlink to it
- **Branch:** main; HEAD `a910a9a` 2026-04-08 — "fix: /snail/club sort order"
- **Supervisor:** `systemd --user` (`slimy-web.service`) — NOT PM2
- **PM2:** obsidian-headless-sync only (kb tooling)
- **Port:** 3000 (Next.js standalone, pid 215978)
- **Classification:** ACTIVE | Confidence: HIGH

## Missing from wiki article slimy-monorepo.md

### Services (NUC2)
| Service | Type | Port | Status |
|---------|------|------|--------|
| slimy-web | systemd (slimy-web.service) | 3000 | active |
| slimy-mysql-tunnel | systemd | 3307 | active |
| postgres | systemd | 5432 | active |

### Truth Gate (NUC2)
```bash
# Standard truth gate
pnpm --filter web lint && pnpm --filter web build

# Specific API health
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/snail/club

# Systemd status
systemctl --user status slimy-web.service
```

### Dead Ports to Remove from Mental Model
- Port 3080 (admin-api) — DEAD since 2026-03-19, do not start
- Port 3081 (admin-ui) — DEAD since 2026-03-19, do not start
- `/api/* → 3080` rewrite — removed, Next.js API routes handle all

### Key Routes on NUC2
- `/owner/crypto` — crypto dashboard
- `/snail/club` — club power rankings
- `/snail/stats` — club movers (gainers/losers)
- `/trader/*` — trader dashboard with mock/http adapter

### Env Vars for Trader Adapter
- `NEXT_PUBLIC_TRADER_ADAPTER` — "mock" (default) or "http"
- `NEXT_PUBLIC_TRADER_API_BASE` — API base URL when using http adapter