# Auth and Retired Services
> Category: architecture
> Sources: raw/decisions/seed-agents-rules.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-25 00:33 UTC (git)
> Version: r41 / f9c7f6a
KB METADATA -->

The active auth model is email/password via `lib/slimy-auth` and MySQL-backed sessions.

## Current Auth Stack
- Argon2 password verification.
- Prisma session records in MySQL.
- httpOnly cookie session transport.
- Owner routes guarded by `requireAuth()`.

## Intentionally Retired Components
- `admin-api` on port 3080 is intentionally dead.
- `admin-ui` on port 3081 is intentionally dead.
- Discord OAuth is intentionally removed from login.
- Legacy `/api/* -> 3080` rewrite is intentionally removed.

## Safety Rule
If a retired component appears broken, that is expected. Do not restart or rebuild it unless explicitly directed.

## See Also
- [SlimyAI Login and Session Flow](slimyai-login-and-session-flow.md)
- [NUC Topology and Services](nuc-topology-and-services.md)
- [Cross-NUC Communication Matrix](cross-nuc-communication-matrix.md)
- [Agent Session Contract](../concepts/agent-session-contract.md)
