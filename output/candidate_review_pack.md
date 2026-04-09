# Candidate Review Pack — 2026-04-09T19:37:03Z

> Stage: 1.85
> Generated: 2026-04-09T19:37:03Z
> Purpose: Human review digest for future harness dispatch

**This file does NOT dispatch. It is a review aid.**

## Summary

- **Candidates:** 12
- **Emerging:** 0
- **Not candidate:** 0
- **Total in queue:** 12

## Candidates — Ready for Harness Dispatch Review

These tasks meet all Stage 1.85 promotion criteria. They are the most
urgent but still require human confirmation before actual dispatch.

### [todo-2026-04-09-001] NUC1 repo has uncommitted changes: kb

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (repo_drift) |
| Persistence | 18x |
| Promotion reason | cross_nuc_conflict |
| Evidence | raw/inbox-nuc1/ |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | nuc1 (cross_nuc) |
| Notes | Dirty repo detected via NUC1 digest. |

**Why it matters:** Repo 'kb' on NUC1 has uncommitted changes (dirty=true). Risk of work loss or drift.

**Recommended action:** Review kb on NUC1, commit or stash uncommitted work, push if appropriate.

### [todo-2026-04-09-002] NUC1 repo has uncommitted changes: ned-autonomous

| Field | Value |
|-------|-------|
| Project | ned-autonomous |
| Severity | HIGH (repo_drift) |
| Persistence | 18x |
| Promotion reason | cross_nuc_conflict |
| Evidence | raw/inbox-nuc1/ |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | nuc1 (cross_nuc) |
| Related wiki page | ned-autonomous.md |
| Notes | Dirty repo detected via NUC1 digest. |

**Why it matters:** Repo 'ned-autonomous' on NUC1 has uncommitted changes (dirty=true). Risk of work loss or drift.

**Recommended action:** Review ned-autonomous on NUC1, commit or stash uncommitted work, push if appropriate.

### [todo-2026-04-09-003] NUC1 repo diverged from remote: Slimefun4

| Field | Value |
|-------|-------|
| Project | Slimefun4 |
| Severity | HIGH (repo_drift) |
| Persistence | 18x |
| Promotion reason | cross_nuc_conflict |
| Evidence | raw/inbox-nuc1/ |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | nuc1 (cross_nuc) |
| Notes | Diverged repo detected via NUC1 digest. |

**Why it matters:** Repo 'Slimefun4' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review Slimefun4 on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-04-09-004] NUC1 repo diverged from remote: clawd

| Field | Value |
|-------|-------|
| Project | clawd |
| Severity | HIGH (repo_drift) |
| Persistence | 18x |
| Promotion reason | cross_nuc_conflict |
| Evidence | raw/inbox-nuc1/ |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | nuc1 (cross_nuc) |
| Related wiki page | clawd-agent-rules.md |
| Notes | Diverged repo detected via NUC1 digest. |

**Why it matters:** Repo 'clawd' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review clawd on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-04-09-005] NUC1 repo diverged from remote: slimy-monorepo

| Field | Value |
|-------|-------|
| Project | slimy-monorepo |
| Severity | HIGH (repo_drift) |
| Persistence | 18x |
| Promotion reason | cross_nuc_conflict |
| Evidence | raw/inbox-nuc1/ |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | nuc1 (cross_nuc) |
| Related wiki page | slimy-monorepo.md |
| Notes | Diverged repo detected via NUC1 digest. |

**Why it matters:** Repo 'slimy-monorepo' on NUC1 is both ahead and behind remote — unmerged commits present.

**Recommended action:** Review slimy-monorepo on NUC1, merge or rebase remote changes, resolve any conflicts.

### [todo-2026-04-09-006] Resolve 28 orphaned wiki pages

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 18x |
| Promotion reason | repeated_gap |
| Evidence | wiki/_orphans.md |
| Suggested prompt mode | plan-build-qa |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Orphaned pages have 0 inbound links and are effectively hidden from navigation.

**Recommended action:** Review each orphan: add links from related pages, merge into existing articles, or delete if redundant.

### [todo-2026-04-09-007] Review orphaned page: architecture/nuc2-server-state.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 18x |
| Promotion reason | repeated_gap |
| Evidence | wiki/architecture/nuc2-server-state.md |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Page 'architecture/nuc2-server-state.md' has no inbound links.

**Recommended action:** Check if architecture/nuc2-server-state.md should be linked from related articles or removed.

### [todo-2026-04-09-008] Review orphaned page: log.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 18x |
| Promotion reason | repeated_gap |
| Evidence | wiki/log.md |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Page 'log.md' has no inbound links.

**Recommended action:** Check if log.md should be linked from related articles or removed.

### [todo-2026-04-09-009] Review orphaned page: projects/actionbook.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 18x |
| Promotion reason | repeated_gap |
| Evidence | wiki/projects/actionbook.md |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Page 'projects/actionbook.md' has no inbound links.

**Recommended action:** Check if projects/actionbook.md should be linked from related articles or removed.

### [todo-2026-04-09-010] Review orphaned page: projects/agents-backup-full.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 18x |
| Promotion reason | repeated_gap |
| Evidence | wiki/projects/agents-backup-full.md |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Page 'projects/agents-backup-full.md' has no inbound links.

**Recommended action:** Check if projects/agents-backup-full.md should be linked from related articles or removed.

### [todo-2026-04-09-011] Review orphaned page: projects/apify-market-scanner.md

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (wiki_gap) |
| Persistence | 18x |
| Promotion reason | repeated_gap |
| Evidence | wiki/projects/apify-market-scanner.md |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | slimy-nuc2 (nuc2) |

**Why it matters:** Page 'projects/apify-market-scanner.md' has no inbound links.

**Recommended action:** Check if projects/apify-market-scanner.md should be linked from related articles or removed.

### [todo-2026-04-09-012] NUC1 KB has uncommitted changes

| Field | Value |
|-------|-------|
| Project | kb |
| Severity | HIGH (repo_drift) |
| Persistence | 18x |
| Promotion reason | cross_nuc_conflict |
| Evidence | raw/inbox-nuc1/ |
| Suggested prompt mode | manual |
| Dispatch blocker | advisory_only |
| Actionability | review_required |
| Source | nuc1 (cross_nuc) |
| Notes | Cross-NUC KB drift signal — NUC1 has uncommitted work in shared KB. |

**Why it matters:** The kb repo on NUC1 is dirty — there are uncommitted changes that may need to be merged.

**Recommended action:** Coordinate with NUC1 to push or transfer the uncommitted KB changes, then reconcile.

---
_Stage 1.85 — advisory only. Candidate status is recorded but dispatch is blocked by `advisory_only`._