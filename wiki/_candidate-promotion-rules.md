# Harness Candidate Promotion Rules

> Category: concepts
> Updated: 2026-04-10T07:43:31Z
> Status: active

<!-- BEGIN MACHINE MANAGED — Do not edit manually -->

## Overview

Stage 1.86 adds **freshness-weighted promotion** to Stage 1.85's stricter criteria.
Recent evidence matters more than lifetime occurrence count.
Tasks can also enter `cooling_down` when recent evidence weakens.

## Promotion Statuses

| Status | Meaning |
|--------|---------|
| `not_candidate` | Default — tracked but does not yet qualify |
| `emerging` | Has some signals but not all criteria met |
| `candidate` | Meets all criteria — ready for harness dispatch consideration |
| `cooling_down` | Was candidate/emerging but recent evidence has weakened |
| `resolved` | No longer present in current queue |

## Freshness Bands

| Band | Meaning | Evidence Age |
|------|---------|--------------|
| `fresh` | Evidence seen or file modified < 24h ago | < 24h |
| `aging` | Evidence 1-3 days old | 24h–72h |
| `stale` | Evidence older than 3 days | >= 72h |

Evidence age is measured by file modification time of the primary evidence path.

## State Transitions

```
not_candidate → emerging → candidate → cooling_down → resolved
     ↑            ↑           ↑            ↓
     └─────────────┴───────────┴────────────┘  (demotion paths)
```

## Freshness-Weighted Promotion Criteria (Stage 1.86)

A task is promoted to `candidate` when **ALL** of the following are true:

### 1. Recent Occurrence Score
- Must have `recent_occurrence_count >= 3` within the last 5 runs
- Lifetime `occurrence_count` is tracked for audit only — it does NOT force candidate status

### 2. Evidence Quality + Recency
- Task must have at least one **real existing** `evidence_path`
- Evidence file must have been modified within `72h` (not stale)
- OR task must have `freshness_band = "fresh"` or `"aging"` AND evidence is real

### 3. Severity Floor
- Severity must be `medium` or `high`

### 4. No Hard Dispatch Blocker
- `dispatch_blocker` must be empty OR only `"advisory_only"`

### 5. Kind Allowlist
- Only `repo_drift`, `wiki_gap`, `doc_drift` are eligible

## Emerging

`emerging` when:
- `recent_occurrence_count >= 2` AND < `3`
- Evidence is real and freshness_band is `fresh` or `aging`
- Severity is `medium` or `high`

OR:
- Has real evidence, but `freshness_band = "stale"` with some recency signal

## Cooling Down

`cooling_down` when:
- Was previously `candidate` or `emerging`
- But `freshness_band = "stale"` OR evidence no longer exists
- Recent evidence has weakened even if lifetime count is high

## Not Candidate

`not_candidate` when:
- No real evidence path
- Evidence is stale AND no recent occurrences
- Kind is excluded
- Hard dispatch blocker present

## Stage 1.86 Boundary

Stage 1.86 does NOT dispatch harness jobs. Candidate status is advisory only.

<!-- END MACHINE MANAGED -->

## Human Notes

<!-- Add notes here -->
