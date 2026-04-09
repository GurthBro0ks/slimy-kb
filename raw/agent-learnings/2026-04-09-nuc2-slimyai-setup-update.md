# NUC2 Slimyai Setup Update — 2026-04-09

## Verified Runtime (2026-04-09)
- **Path:** `/opt/slimy/app` (Discord bot super-snail)
- **Branch:** main; HEAD `c1fbf1b` 2026-04-05
- **Supervisor:** PM2 (ecosystem.config.js) or direct node
- **Classification:** ACTIVE | Confidence: HIGH

## Current Work (NUC2)
- Bot is the **super-snail Discord bot** with club analytics, GPT-4 Vision OCR, DALL-E image gen, Google Sheets sync
- Primary commands: `/club analyze`, `/club stats`, `/club-admin`
- MySQL via SSH tunnel (port 3307 to NUC1)
- Google Sheets API for club member tracking

## Key Scripts
```bash
# Ingest club screenshots (dry run)
node scripts/ingest-club-screenshots.js \
  --guild "$GUILD_ID" \
  --dir "/opt/slimy/app/screenshots/test" \
  --type both --dry --debug

# Commit with corrections sync
node scripts/ingest-club-screenshots.js \
  --guild "$GUILD_ID" \
  --dir "/opt/slimy/app/screenshots" \
  --type both
```

## Truth Gate
```bash
# Smoke test
node -e "require('./index.js')"

# Or check PM2 status
pm2 list | grep slimy
```

## Services
- slimy-mysql-tunnel.service (port 3307) — SSH tunnel to NUC1 MySQL
- slimy-web-health.service — FAILED (non-critical, from old setup)

## Key Files
- `index.js` — main bot entry
- `snail.js` — Super Snail command handlers
- `sheets.js` — Google Sheets integration
- `ecosystem.config.js` — PM2 config