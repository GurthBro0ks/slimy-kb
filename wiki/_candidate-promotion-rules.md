# Harness Candidate Promotion Rules

> Category: concepts
> Updated: 2026-04-09T19:37:03Z
> Status: active

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

## Overview

Stage 1.85 introduces stricter promotion criteria to end over-promotion. Tasks must now demonstrate **both persistence AND quality signals** before becoming a harness candidate. Tasks can also move downward (demotion) as well as upward.

## Promotion Statuses

| Status | Meaning |
|--------|---------|
| `not_candidate` | Default — tracked but does not yet qualify |
| `emerging` | Has some signals but not all criteria met |
| `candidate` | Meets all criteria — ready for harness dispatch consideration |
| `cooling_down` | Was candidate but evidence has weakened |
| `resolved` | No longer present in current queue |

## State Transitions

```
not_candidate → emerging → candidate → cooling_down → resolved
     ↑            ↑           ↑            ↓
     └─────────────┴───────────┴────────────┘  (demotion paths)
```

A task can be demoted if its evidence degrades (e.g., occurrence_count drops below threshold,
evidence path becomes stale, severity drops).

## Bounded Promotion Criteria (Stage 1.85 — Stricter)

A task is promoted to `candidate` when **ALL** of the following are true:

### 1. Hard Persistence Floor
- `occurrence_count >= 5` (with cross-NUC bonus of +2 applied: so 3 base occurrences + 2 cross-NUC bonus = 5)
- OR `occurrence_count >= 5` without bonus for local NUC2 tasks
- Tasks at exactly 3-4 occurrences (or 3+2=5 with bonus) land in `emerging`

### 2. Evidence Quality
- Task must have at least one `evidence_path` pointing to a **real existing file or directory**
- Evidence paths are verified at promotion time

### 3. Severity Floor
- Severity must be `medium` or `high`
- Tasks with `low` severity can only reach `emerging` at best

### 4. No Hard Dispatch Blocker
- `dispatch_blocker` must be empty OR only `"advisory_only"`
- Any other blocker (e.g., `needs_review`, `cross_nuc_coordination`) prevents promotion

### 5. Kind Allowlist
- Only `repo_drift`, `wiki_gap`, `doc_drift` are eligible
- `investigate` and `harness_candidate` kinds are permanently excluded

## Promotion Reasons

- `cross_nuc_conflict` — cross-NUC evidence, persistent (>=5 eff. occurrences)
- `persistent_drift` — repo drift with high severity, >=5 occurrences
- `repeated_gap` — wiki gap persisting >=5 times with medium+ severity

## Demotion Signals

A task is demoted when:
- `occurrence_count` drops (if previously candidate but now resolved)
- Evidence path becomes stale or unavailable
- Severity drops below `medium`
- A hard dispatch blocker is added

## Dispatch Blockers

| Blocker | Blocks promotion? | Auto-clear? |
|--------|------------------|-------------|
| _(empty)_ | No | N/A |
| `advisory_only` | No (stage gate only) | Yes — cleared in Stage 2 |
| `needs_review` | Yes | No — manual clear |
| `cross_nuc_coordination` | Yes | No — manual clear |

## Stage 1.85 Boundary

Stage 1.85 does NOT dispatch harness jobs. Candidate status is advisory only, dispatch blocked by `advisory_only`.

<!-- END MACHINE MANAGED -->

## Human Notes

<!-- Add notes here -->
