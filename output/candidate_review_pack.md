# Candidate Review Pack — 2026-04-15T17:25:51Z

> Stage: 1.86
> Generated: 2026-04-15T17:25:51Z
> Purpose: Human review digest for future harness dispatch

**This file does NOT dispatch. It is a review aid.**

## Summary

- **Candidates:** 6
- **Emerging:** 0
- **Cooling down:** 4
- **Not candidate:** 10
- **Total in queue:** 20

## Freshness Bands
- **fresh** (< 24h): 16
- **aging** (24-72h): 0
- **stale** (> 72h): 4

## Candidates — Ready for Harness Dispatch Review

These tasks meet all Stage 1.86 promotion criteria:
recent evidence (3+ in last 5 runs), fresh/aging evidence, medium+ severity.

### [todo-2026-04-15-006] NUC1 repo has uncommitted changes: ned-autonomous

| Field | Value |
|-------|-------|
| Project | ned-autonomous |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 23x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |
| Related wiki page | ned-autonomous.md |

**Why it matters:** Repo 'ned-autonomous' on NUC1 has uncommitted changes (dirty=true). Risk of work loss or drift.

**Recommended action:** Review ned-autonomous on NUC1, commit or stash uncommitted work, push if appropriate.

### [todo-2026-04-15-012] NUC1 repo diverged from remote: Slimefun4

| Field | Value |
|-------|-------|
| Project | Slimefun4 |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 23x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |

**Why it matters:** Repo 'Slimefun4' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review Slimefun4 on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-04-15-013] NUC1 repo diverged from remote: clawd

| Field | Value |
|-------|-------|
| Project | clawd |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 23x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |
| Related wiki page | clawd-agent-rules.md |

**Why it matters:** Repo 'clawd' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review clawd on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-04-15-014] NUC1 repo diverged from remote: slimy-monorepo

| Field | Value |
|-------|-------|
| Project | slimy-monorepo |
| Severity | HIGH (repo_drift) |
| Persistence | 5x recent / 23x lifetime |
| Freshness | fresh |
| Evidence | raw/inbox-nuc1/ |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | nuc1 (cross_nuc) |
| Related wiki page | slimy-monorepo.md |

**Why it matters:** Repo 'slimy-monorepo' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review slimy-monorepo on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-04-15-015] Resolve 30 orphaned wiki pages

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 5x recent / 5x lifetime |
| Freshness | fresh |
| Evidence | wiki/_orphans.md |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Orphaned pages have 0 inbound links and are effectively hidden from navigation.

**Recommended action:** Review each orphan: add links from related pages, merge into existing articles, or delete if redundant.

### [todo-2026-04-15-017] Review orphaned page: log.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 5x recent / 26x lifetime |
| Freshness | fresh |
| Evidence | wiki/log.md |
| Dispatch blocker | advisory_only |
| Actionability | actionable |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Page 'log.md' has no inbound links.

**Recommended action:** Check if log.md should be linked from related articles or removed.

## Cooling Down (4 tasks)

These tasks were previously candidate/emerging but recent evidence has weakened.
They are tracked but require fresh evidence before they can be restored to candidate.

- **[todo-2026-04-15-016]** Review orphaned page: architecture/nuc2-server-state.md — HIGH (stale) — evidence_stale_cooling
- **[todo-2026-04-15-018]** Review orphaned page: projects/actionbook.md — HIGH (stale) — evidence_stale_cooling
- **[todo-2026-04-15-019]** Review orphaned page: projects/agents-backup-full.md — HIGH (stale) — evidence_stale_cooling
- **[todo-2026-04-15-020]** Review orphaned page: projects/apify-market-scanner.md — HIGH (stale) — evidence_stale_cooling

## Not Candidate (10 tasks)

These tasks are tracked but lack sufficient recent evidence, have stale evidence,
or are excluded kinds. Lifetime history is preserved for audit.

- **[todo-2026-04-15-001]** NUC1 repo has uncommitted changes: Slimefun4 — insufficient_recency (fresh)
- **[todo-2026-04-15-002]** NUC1 repo has uncommitted changes: PrivateStorage — insufficient_recency (fresh)
- **[todo-2026-04-15-003]** NUC1 repo has uncommitted changes: DynaTech — insufficient_recency (fresh)
- **[todo-2026-04-15-004]** NUC1 repo has uncommitted changes: mission-control — insufficient_recency (fresh)
- **[todo-2026-04-15-005]** NUC1 repo has uncommitted changes: slimy-harness — insufficient_recency (fresh)
- **[todo-2026-04-15-007]** NUC1 repo has uncommitted changes: stoat-source — insufficient_recency (fresh)
- **[todo-2026-04-15-008]** NUC1 repo has uncommitted changes: mailbox_outbox — insufficient_recency (fresh)
- **[todo-2026-04-15-009]** NUC1 repo has uncommitted changes: slimy-chat — insufficient_recency (fresh)
- _...and 2 more_

---
_Stage 1.86 — advisory only. Candidate status is advisory only, dispatch blocked by `advisory_only`._