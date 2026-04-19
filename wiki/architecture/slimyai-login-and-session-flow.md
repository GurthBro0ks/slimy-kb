# SlimyAI Login and Session Flow
> Category: architecture
> Sources: /home/slimy/kb/wiki/architecture/auth-and-retired-services.md, /home/slimy/kb/wiki/projects/slimy-web.md, /home/slimy/kb/wiki/architecture/nuc-topology-and-services.md, /opt/slimy/slimy-monorepo/apps/web/app/login/page.tsx, /opt/slimy/slimy-monorepo/apps/web/app/api/session/login/route.ts, /opt/slimy/slimy-monorepo/apps/web/app/api/session/logout/route.ts, /opt/slimy/slimy-monorepo/apps/web/app/api/session/me/route.ts, /opt/slimy/slimy-monorepo/apps/web/app/api/session/register/route.ts, /opt/slimy/slimy-monorepo/apps/web/app/api/session/verify/route.ts, /opt/slimy/slimy-monorepo/apps/web/app/api/session/forgot-password/route.ts, /opt/slimy/slimy-monorepo/apps/web/app/api/session/reset-password/route.ts, /opt/slimy/slimy-monorepo/apps/web/lib/slimy-auth/session.ts, /opt/slimy/slimy-monorepo/apps/web/lib/slimy-auth/rate-limit.ts, /opt/slimy/slimy-monorepo/apps/web/lib/slimy-auth/invite.ts, /opt/slimy/slimy-monorepo/apps/web/lib/auth/server.ts, /opt/slimy/slimy-monorepo/apps/web/lib/auth/owner.ts, /opt/slimy/slimy-monorepo/apps/web/prisma/schema.prisma, /opt/slimy/slimy-monorepo/apps/web/middleware.ts
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-18 12:25 UTC (git)
> Version: r13 / ff55646
KB METADATA -->

This article documents the active SlimyAI web login/session architecture and explicitly separates canonical behavior from legacy or unclear paths.

## Current Login Stack
Canonical stack in `apps/web`:
- Credential auth: email (or username) + password via `/api/session/login`.
- Password hashing: argon2 (`verifyPassword` / `hashPassword`).
- Session storage: DB-backed `SlimySession` rows keyed by SHA-256 `tokenHash`.
- Transport: `slimy_session` httpOnly cookie.
- Authorization: `requireAuth()` for authenticated access, `requireOwner()` for owner-only APIs/pages.

Core Prisma models:
- `SlimyUser`
- `SlimySession`
- `SlimyInvite`
- `SlimyEmailVerification`
- `SlimyPasswordReset`
- `SlimyLoginAttempt`

## Login Route and Post-Login Flow
Primary user flow:
1. User opens `/login`.
2. Client posts credentials to `POST /api/session/login`.
3. API checks rate limit, user existence, `disabled`, `emailVerified`, and password validity.
4. On success, server creates `SlimySession`, sets `slimy_session` cookie, returns success payload.
5. Client hard-redirects to `returnTo` or `/dashboard`.

Route middleware behavior:
- Unauthenticated requests to protected paths redirect to `/login?returnTo=...`.
- Public paths include `/`, `/login`, `/auth/*`, `/snail/*`, and `/api/session/*`.

## Session Persistence and Cookie Lifecycle
Session lifecycle:
- Create: `createSession()` generates random token, stores only SHA-256 hash in DB.
- TTL: 30 days (`SESSION_TTL_SECONDS`).
- Validate: `validateSession()` rejects missing, invalid, revoked, expired, or disabled-account sessions.
- Logout: `POST /api/session/logout` revokes DB session (`revokedAt`) and clears cookie.

Cookie settings:
- Name: `slimy_session`
- `httpOnly: true`
- `sameSite: "lax"`
- `path: "/"`
- `maxAge: 30 days`
- `secure`: determined at set-time from `x-forwarded-proto === "https"` (login/verify); logout path always clears with `secure: true` in normal path.

## Invite and Role Assignment Behavior
Registration is invite-only:
- `POST /api/session/register` requires `invite_code`, email, username, password.
- Invite is validated against `SlimyInvite` (`revokedAt`, `expiresAt`, `maxUses/useCount` enforced).
- Invite role is copied to new `SlimyUser.role`.
- Invite use count increments on successful registration.
- New users start with `emailVerified: false` and must verify before login.

Owner gating:
- Owner routes use `requireOwner()`.
- Access requires either `user.role === "owner"` or `user.id === OWNER_USER_ID` env override.

Allowlist status:
- An `OwnerAllowlist` concept exists in schema/tests, but canonical runtime owner checks in `requireOwner()` do not consult email allowlist directly.
- Treat allowlist as ancillary/legacy unless runtime call sites are reintroduced.

## Verification, Reset, Recovery, and Lockout
Email verification:
- `POST /api/session/register` creates verification token (`SlimyEmailVerification`) and emails link.
- `GET /api/session/verify?token=...` marks email verified and auto-creates login session.

Known route mismatch to track:
- Register email currently points to `/auth/verify?token=...` while implemented handler is `/api/session/verify?token=...`.
- No `app/auth/verify/page.tsx` route is present in this repo snapshot.
- Result: final verification URL handling is not fully proven from code alone and should be treated as a documentation/runtime check item.

Password recovery:
- `POST /api/session/forgot-password` always returns generic success (prevents email enumeration).
- Creates one-hour reset token (`SlimyPasswordReset`) for valid active users.
- `POST /api/session/reset-password` validates token + password policy, rotates password hash, marks token used, revokes all active sessions for the user.

Login rate limiting / lockout:
- Failed attempts tracked in `SlimyLoginAttempt`.
- Window: 15 minutes.
- Threshold: 5 failures by identifier or IP.
- Lockout duration: 15 minutes (returns HTTP 429 and `lockoutUntil`).

## Retired and Non-Canonical Auth Paths
Must remain retired:
- Discord OAuth login integration (retired).
- `admin-api` auth surface on port 3080 (retired).
- `admin-ui` auth panel on port 3081 (retired).

Non-canonical/testing path present in codebase:
- `/api/local-auth/*` endpoints still exist and use base64 token payloads with inline comments stating they are not secure and for testing.
- These are not the canonical production session model.

## See Also
- [Auth and Retired Services](auth-and-retired-services.md)
- [NUC Topology and Services](nuc-topology-and-services.md)
- [Slimy Web](../projects/slimy-web.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
