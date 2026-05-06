# Phase 1C.3 Gear Schema Validation Audit

Generated UTC: 2026-05-06T16:30:33.378728+00:00

## Scope

Validate Gear.wiki-derived candidate entities against the current gear.schema.json shape.
No canonical data was modified.

## Counts

- input_candidates: 313
- input_stat_rows: 1252
- input_source_facts: 313
- schema_ready_needs_manual_review: 74
- blocked_count: 239

## Readiness Counts

- blocked_missing_required: 239
- schema_shape_ready_needs_manual_review: 74

## Top Error Counts

- missing_or_uninferred:slot: 239
- missing_required:slot: 239

## Schema Observations

- Current gear.schema.json appears to require slot, but Gear.wiki aggregate rows do not always expose a direct slot.
- Current rarity enum is semantic, while Gear.wiki uses color/tier values. A formal color-to-rarity mapping needs PM approval before canonical promotion.
- Gear.wiki provides HP, ATK, DEF, and RUSH cleanly for most candidates.
- Effects and origin fields are raw text and need downstream normalization.

## Recommended Next Actions

- Review whether gear.schema.json should add gear_color or tier_color as a first-class field.
- Review whether slot should be optional/nullable or inferred from separate source data.
- Manually inspect schema_shape_ready_needs_manual_review records before promotion.
- Keep blocked records as candidates until schema gap is resolved.

## Decision

This phase produces a promotion readiness packet only. Promotion remains locked.
The likely next step is a schema review phase before any canonical gear import.

