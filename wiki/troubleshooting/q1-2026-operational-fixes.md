# Q1 2026 Operational Fixes
> Category: troubleshooting
> Sources: raw/agent-learnings/seed-progress-history.md, raw/decisions/seed-server-state.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-16 19:36 UTC (git)
> Version: r4 / bc27293
KB METADATA -->

This article captures recurring failures and proven fixes from recent execution history.

## Database target mismatch in web env
Symptom:
- Snail API routes fail against wrong database name.
Cause:
- `DATABASE_URL` pointed to `slimyai_prod` instead of the active `slimy` schema.
Fix:
- Update `apps/web/.env` DB name and restart web service; verify build and route health checks.
Prevention:
- Validate DB target during startup checks and after repo sync.

## Bot OpenAI 401 failures
Symptom:
- `/chat`, `/dream`, or mention chat paths return 401-style API failures.
Cause:
- Invalid or stale `OPENAI_API_KEY` in bot env.
Fix:
- Rotate key in bot `.env`, restart PM2 process with env refresh, inspect fresh logs.
Prevention:
- Add key rotation checks to runbook and monitor startup logs for auth signatures.

## Tunnel-based MySQL access denied
Symptom:
- Club API data path fails through SSH tunnel with access denied from bridge IP.
Cause:
- MySQL grant missing for tunnel source host.
Fix:
- Apply host grant on NUC1 MySQL user for tunnel source IP/range.
Prevention:
- Include grant validation in tunnel bring-up checklist.

## Stats page missing server-rendered contract text
Symptom:
- Contract check via `curl` cannot find required leaderboard text in initial HTML.
Cause:
- Page rendered critical content only after client-side fetch.
Fix:
- Convert to server-rendered path for contract-visible content.
Prevention:
- Include raw-HTML assertions in acceptance criteria for SSR-required pages.

## See Also
- [Truth Gate](../concepts/truth-gate.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [NUC Topology and Services](../architecture/nuc-topology-and-services.md)
- [Cross-NUC Communication Matrix](../architecture/cross-nuc-communication-matrix.md)
