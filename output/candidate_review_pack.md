# Candidate Review Pack — 2026-05-30T06:14:28Z

> Stage: 1.86
> Generated: 2026-05-30T06:14:28Z
> Purpose: Human review digest for future harness dispatch

**This file does NOT dispatch. It is a review aid.**

## Summary

- **Candidates:** 7
- **Emerging:** 0
- **Cooling down:** 0
- **Not candidate:** 2
- **Total in queue:** 9

## Freshness Bands
- **fresh** (< 24h): 9
- **aging** (24-72h): 0
- **stale** (> 72h): 0

## Candidates — Ready for Harness Dispatch Review

These tasks meet all Stage 1.86 promotion criteria:
recent evidence (3+ in last 5 runs), fresh/aging evidence, medium+ severity.

### [todo-2026-05-30-001] NUC1 repo has uncommitted changes: mailbox_outbox

| Field | Value |
|-------|-------|
| Project | mailbox_outbox |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 71x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |
| Related wiki page | mailbox-outbox.md |

**Why it matters:** Repo 'mailbox_outbox' on NUC1 has uncommitted changes (dirty=true). Risk of work loss or drift.

**Recommended action:** Review mailbox_outbox on NUC1, commit or stash uncommitted work, push if appropriate.

### [todo-2026-05-30-002] NUC1 repo diverged from remote: Slimefun4

| Field | Value |
|-------|-------|
| Project | Slimefun4 |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 93x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |

**Why it matters:** Repo 'Slimefun4' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review Slimefun4 on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-05-30-003] NUC1 repo diverged from remote: slimy-monorepo

| Field | Value |
|-------|-------|
| Project | slimy-monorepo |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 93x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |
| Related wiki page | slimy-monorepo.md |

**Why it matters:** Repo 'slimy-monorepo' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review slimy-monorepo on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-05-30-005] Review orphaned page: log.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 5x recent / 96x lifetime |
| Freshness | fresh |
| Evidence | wiki/log.md |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | slimy-nuc2 (nuc2) |
| Related wiki page | kb-bridge-gear-donation.md |

**Why it matters:** Page 'log.md' has no inbound links.

**Recommended action:** Check if log.md should be linked from related articles or removed.

### [todo-2026-05-30-006] Review orphaned page: projects/actionbook.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 5x recent / 29x lifetime |
| Freshness | fresh |
| Evidence | wiki/projects/actionbook.md |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | slimy-nuc2 (nuc2) |
| Related wiki page | kb-bridge-gear-donation.md |

**Why it matters:** Page 'projects/actionbook.md' has no inbound links.

**Recommended action:** Check if projects/actionbook.md should be linked from related articles or removed.

### [todo-2026-05-30-007] Review orphaned page: projects/agents-backup-full.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 5x recent / 96x lifetime |
| Freshness | fresh |
| Evidence | wiki/projects/agents-backup-full.md |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | slimy-nuc2 (nuc2) |
| Related wiki page | kb-bridge-gear-donation.md |

**Why it matters:** Page 'projects/agents-backup-full.md' has no inbound links.

**Recommended action:** Check if projects/agents-backup-full.md should be linked from related articles or removed.

### [todo-2026-05-30-009] Review orphaned page: projects/mailbox-outbox.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 5x recent / 68x lifetime |
| Freshness | fresh |
| Evidence | wiki/projects/mailbox-outbox.md |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | slimy-nuc2 (nuc2) |
| Related wiki page | kb-bridge-gear-donation.md |

**Why it matters:** Page 'projects/mailbox-outbox.md' has no inbound links.

**Recommended action:** Check if projects/mailbox-outbox.md should be linked from related articles or removed.

## Not Candidate (2 tasks)

These tasks are tracked but lack sufficient recent evidence, have stale evidence,
or are excluded kinds. Lifetime history is preserved for audit.

- **[todo-2026-05-30-004]** Resolve 22 orphaned wiki pages — insufficient_recency (fresh)
- **[todo-2026-05-30-008]** Review orphaned page: projects/kb-bridge-gear-donation.md — insufficient_recency (fresh)

---
_Stage 1.86 — advisory only. Candidate status is advisory only, dispatch blocked by `advisory_only`._