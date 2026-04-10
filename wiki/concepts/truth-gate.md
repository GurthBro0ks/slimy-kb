# Truth Gate
> Category: concepts
> Sources: raw/decisions/seed-app-agents.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

A truth gate is the required verification set that proves a change is actually done.

## Harness Truth Gate

For the slimy-harness repo itself, the truth gate is:

```bash
bash /home/slimy/slimy-harness/scripts/validate-harness.sh
```

Current criteria (as of 2026-04-10): **53 passed | 0 warnings | 0 failures**

The validation checks: shell syntax on all scripts, dry-run zero-write, docs vs installer consistency, required files present, AGENTS.md host-neutrality, per-repo harness completeness, ambiguous repo fail-closed, init.sh ↔ server-install.sh skip policy sync, real paths in server-state template, and sync hygiene vs origin/main (Check 9).

## Practical Pattern
- Lint and build success for touched repos.
- Tests or smoke checks relevant to changed behavior.
- Runtime checks for user-facing endpoints or services.
- Explicit pass/fail recording in the feature ledger.

## Practical Pattern
- Define pass criteria before implementation.
- Run commands that map directly to those criteria.
- Mark fail when any contractual criterion misses threshold.

## Anti-Patterns
- Reporting pass from local assumptions without command evidence.
- Skipping regression checks after targeted fixes.
- Treating warnings as pass when contract requires zero errors.

## See Also
- [Agent Session Contract](agent-session-contract.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
