# NUC2 Slimyai Web (Legacy) Update — 2026-04-09

## Status: ARCHIVED
- **Path:** `/opt/slimy/web/slimyai-web`
- **Branch:** `fix/runtime-envs-check-2025-11-11-nuc2-snapshot`
- **Classification:** ARCHIVED — superseded by slimy-monorepo/apps/web

## What This Is
Standalone Next.js web app (legacy) with Admin API proxies, codes aggregator, MDX docs. Not the same as the current slimy-monorepo apps/web.

## Dead Ports (from old slimy-web.md)
- Port 3080 (admin-api) — DEAD since 2026-03-19, do not restart
- Port 3081 (admin-ui) — DEAD since 2026-03-19, do not restart

## Auth System Change
- Old: Discord OAuth (admin-api port 3080)
- Current: Email/password via slimy-auth (lib/slimy-auth/) in slimy-monorepo
- Database: MySQL via Prisma (SlimyUser, SlimySession, SlimyInvite, SlimyLoginAttempt)

## Current Web
- All web traffic now goes through `/opt/slimy/slimy-monorepo/apps/web` (port 3000)
- `/owner/*` routes protected by `requireAuth()` layout
- Login at slimyai.xyz/login