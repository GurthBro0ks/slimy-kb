# Truth Gate
> Category: concepts
> Sources: raw/decisions/seed-app-agents.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/agent-learnings/seed-progress-history.md
> Created: 2026-04-04
> Updated: 2026-04-16
> Status: reviewed

<!-- KB METADATA
> Last edited: 2026-04-19 00:25 UTC (git)
> Version: r16 / 2b8f6a1
KB METADATA -->

A truth gate is the required verification set that proves a change is actually done.

## Harness Truth Gate

For the slimy-harness repo itself, the truth gate is:

```bash
bash /home/slimy/slimy-harness/scripts/validate-harness.sh
```

Current criteria (as of 2026-04-10): **53 passed | 0 warnings | 0 failures**

The validation checks: shell syntax on all scripts, dry-run zero-write, docs vs installer consistency, required files present, AGENTS.md host-neutrality, per-repo harness completeness, ambiguous repo fail-closed, init.sh ↔ server-install.sh skip policy sync, real paths in server-state template, and sync hygiene vs origin/main (Check 9).

## Doc-Sync Verification

The doc-sync subsystem (`kb/tools/kb-project-doc-sync.sh`) has its own verification layer:

- **Allowlist gate:** only repos in `kb/config/doc-sync-allowlist.txt` are processed. Non-listed repos are skipped with a log message.
- **Content-diff gate:** VERSION.md is only rewritten if content differs (md5 comparison excluding timestamp). Prevents spurious noise commits.
- **Dirty-tree gate:** repos with non-doc dirty files are skipped entirely.
- **Push-or-revert:** if push fails after auto-sync commit, the commit is reverted (no local-only accumulation).
- **Daily dedupe:** if HEAD is already today's auto-sync and no doc files are dirty, skip.

These guards run automatically on every session finish. No manual verification needed — they are structural, not procedural.

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
