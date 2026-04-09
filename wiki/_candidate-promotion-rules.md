# Harness Candidate Promotion Rules

> Category: concepts
> Updated: 2026-04-09T17:45:04Z
> Status: active

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

## Overview

A task becomes a **harness candidate** when it meets explicit, bounded criteria. This page defines those criteria so promotion is deterministic and auditable.

## Promotion Statuses

| Status | Meaning |
|--------|---------|
| `not_candidate` | Default — task is tracked but does not yet qualify |
| `emerging` | Task has some signals but does not yet meet all criteria |
| `candidate` | Task meets all promotion criteria — ready for harness dispatch consideration |

## Bounded Promotion Criteria

A task is promoted to `candidate` when **ALL** of the following are true:

### 1. Persistence Threshold
- Task must have `occurrence_count >= 3` in the todo history
- Cross-NUC evidence adds a bonus of +2 to the effective occurrence count for this check

### 2. Evidence Quality
- Task must have at least one `evidence_path` in the todo record
- Evidence must reference a real file or directory in `raw/` or `wiki/`

### 3. Severity Floor
- Task severity must be `medium` or `high` (not `low`)
- OR task must be `persisting` with `occurrence_count >= 3 * 2`

### 4. No Active Dispatch Blocker
- `dispatch_blocker` must be empty OR only `"advisory_only"`
- advisory_only is a system-level blocker indicating Stage 1.x does not dispatch — this does not prevent candidate status

### 5. Kind Allowlist
- Only these kinds are eligible for promotion: `repo_drift`, `wiki_gap`, `doc_drift`
- `investigate` and `harness_candidate` kinds are excluded from promotion

## Promotion Reasons

When a task is promoted, `promotion_reason` is set to one of:

- `persistent_drift` — task is repo/wiki drift that has persisted >= 3 times
- `cross_nuc_conflict` — cross-NUC KB or repo conflict with >= 2 occurrences
- `repeated_gap` — wiki gap persisting >= 3 * 2 times

## Dispatch Blockers

Even candidate tasks may have dispatch blockers:

| Blocker | Meaning | Auto-clear? |
|---------|---------|-------------|
| _(empty)_ | No blocker — go ahead if severity warrants | N/A |
| `advisory_only` | Stage 1.x does not dispatch | Yes — cleared in Stage 2 |
| `needs_review` | Human review required before dispatch | No — manual clear |
| `cross_nuc_coordination` | Needs coordination with other NUC | No — manual clear |

## Stage 1.8 Boundary

Stage 1.8 does NOT dispatch harness jobs. Candidate status is recorded but dispatch is blocked by `advisory_only`. Stage 2 will handle actual dispatch.

<!-- END MACHINE MANAGED -->

## Human Notes

<!-- Add notes here -->
