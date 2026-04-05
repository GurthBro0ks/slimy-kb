---
name: webhook-codex-yolo-normalization
description: Webhook category normalization and Codex --yolo flag on NUC2
type: agent-learning
---

# Webhook Normalization + Codex --yolo on NUC2

> Date: 2026-04-05 | Host: NUC2 | Source: agent session

## Changes Made

### 1. Webhook Category Variables
Replaced legacy `DISCORD_WEBHOOK_URL` with five category-specific variables:
- `DISCORD_WEBHOOK_RUNS` — agent run finish notifications
- `DISCORD_WEBHOOK_DAILY` — calendar sync, todo lists
- `DISCORD_WEBHOOK_RECOMMEND` — recommendations output
- `DISCORD_WEBHOOK_CHANGELOG` — changelog rollup, version scan
- `DISCORD_WEBHOOK_ALERTS` — failures: push failures, compile errors, KB conflicts

Webhook URLs are loaded from `~/.config/slimy/webhooks.env` via `source` when present.
All scripts skip cleanly when their category var is unset (no error, no URL printed).

### 2. Routing
| Script | Category |
|--------|----------|
| slimy-agent-finish.sh | RUNS (success) / ALERTS (failures) |
| kb-calendar-sync.sh | DAILY |
| kb-todo.sh | DAILY |
| kb-recommend.sh | RECOMMEND |
| kb-changelog-rollup.sh | CHANGELOG |
| kb-version-scan.sh | CHANGELOG |

### 3. Codex Wrapper --yolo Flag
`~/.npm-global/bin/codex` (user-facing wrapper) now passes `--yolo` before original args,
preserving recursion guard, exit code, and post-run finish hook.

### 4. Scripts Updated
- kb/tools/kb-calendar-sync.sh — migrated DISCORD_WEBHOOK_URL → DISCORD_WEBHOOK_DAILY, added webhooks.env sourcing
- kb/tools/kb-todo.sh — added webhook support (DAILY)
- kb/tools/kb-recommend.sh — added webhook support (RECOMMEND)
- kb/tools/kb-changelog-rollup.sh — added webhook support (CHANGELOG)
- kb/tools/kb-version-scan.sh — added webhook support (CHANGELOG)
- kb/tools/slimy-agent-finish.sh — added ALERTS webhook on failures, webhooks.env sourcing
- .npm-global/bin/codex — added --yolo flag

### 5. Security Notes
- Webhook URLs are never printed to stdout
- Scripts source webhooks.env only if present; skip cleanly if unset
- Codex recursion guard prevents double-wrap
