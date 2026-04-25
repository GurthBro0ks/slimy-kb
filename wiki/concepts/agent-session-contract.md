# Agent Session Contract
> Category: concepts
> Sources: raw/decisions/seed-agents-rules.md, raw/decisions/seed-slimy-monorepo-agents.md, raw/decisions/seed-pm_updown_bot_bundle-agents.md, raw/decisions/seed-app-agents.md
> Created: 2026-04-04
> Updated: 2026-04-04
> Status: draft

<!-- KB METADATA
> Last edited: 2026-04-25 00:33 UTC (git)
> Version: r40 / f9c7f6a
KB METADATA -->

This concept defines the non-negotiable working contract used across SlimyAI repos.

## Core Rules
- Run startup context first (progress, feature list, server state, repo-specific agent docs).
- Work one feature per session unless explicitly expanded.
- Keep changes scoped to the selected repo and follow local AGENTS.md before coding.
- Commit in the repo where work happened.

## Session Discipline
- Treat startup and shutdown checklists as required controls, not reminders.
- Preserve intentionally retired services and legacy boundaries exactly as documented.
- Prefer deterministic commands and explicit verification steps over ad-hoc manual checks.

## Why This Exists
The shared contract prevents cross-repo drift and keeps work auditable across multiple hosts and services.

## See Also
- [Source of Truth Ledgers](source-of-truth-ledgers.md)
- [Truth Gate](truth-gate.md)
- [Session Closeout Pattern](../patterns/session-closeout-pattern.md)
- [Auth and Retired Services](../architecture/auth-and-retired-services.md)
- [Harness Runtime Topology](../architecture/harness-runtime-topology.md)
