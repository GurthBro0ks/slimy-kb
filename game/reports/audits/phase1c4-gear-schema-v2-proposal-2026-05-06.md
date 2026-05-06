# Phase 1C.4 Gear Schema v2 Proposal Audit

Generated UTC: 2026-05-06T16:43:41.284722+00:00

## Scope

Create a proposed gear schema v2 based on real Gear.wiki candidate shape.
No canonical data was modified. The active gear.schema.json was not replaced.

## Results

- Candidate count: 313
- v1 ready but needs manual review: 74
- v1 blocked: 239
- v2 ready but needs manual review: 313
- v2 blocked: 0

## Tier Color Counts

- blue: 33
- gray: 25
- green: 36
- orange: 91
- purple: 48
- red: 80

## Recommended PM Decisions

- canonical_promotion: still locked until manual review packet is approved
- effect_origin: keep raw text now; normalize in later effect/origin pipelines
- rarity: do not force semantic rarity during import; derive later if needed
- slot: make optional nullable; do not require weapon/armor/accessory for Gear.wiki-derived records
- tier_color: add as required first-class field

## Schema Comparison

- v1 required: ['id', 'name', 'slot']
- v2 required: ['id', 'name', 'tier_color', 'base_stats', 'source']

## Decision

Review and approve the schema v2 proposal before any canonical import.
The v2 schema aligns better with actual Gear.wiki data by making slot optional
and adding tier_color as a required first-class field.

