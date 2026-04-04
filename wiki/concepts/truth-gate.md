# Truth Gate
> Category: concepts
> Sources: raw/decisions/seed-app-agents.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/agent-learnings/seed-progress-history.md, raw/decisions/nuc1-seed-proofs-agents.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

A truth gate is the required verification set that proves a change is actually done.

## Typical Gate Components
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

## Fail-Closed Variant
- Some repos define a strict fail-closed truth gate where success cannot be claimed unless one explicit command exits cleanly (for example `./scripts/run_tests.sh`).
- This variant usually pairs with forbidden zones and no-auto-commit rules to prevent accidental drift while debugging.
- Operationally, it is a tighter specialization of the same core concept: evidence first, claims second.

## See Also
- [Agent Session Contract](agent-session-contract.md)
- [Q1 2026 Operational Fixes](../troubleshooting/q1-2026-operational-fixes.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
