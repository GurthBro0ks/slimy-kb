# Phase 1C.4 Gear Schema v2 Proposal

Generated UTC: 2026-05-06T16:43:07.995337+00:00

## PM Finding

The current gear.schema.json is too strict for the actual Gear.wiki source shape.
Gear.wiki provides item identity, tier/color, HP, ATK, DEF, RUSH, effect, and origin.
It does not reliably provide weapon/armor/accessory slot classification.

## Proposed Schema Decisions

- Add `tier_color` as required first-class field.
- Make `slot` optional nullable.
- Preserve raw `effect` and `origin` as strings for later normalization.
- Preserve `source` object with wiki URL and local source file.
- Do not force semantic rarity during import.

## Validation Results

- Total candidates: 313
- v2 ready but needs manual review: 313
- v2 blocked: 0

## Tier Color Counts

- blue: 33
- gray: 25
- green: 36
- orange: 91
- purple: 48
- red: 80

## v2 Error Counts


## Decision Needed

Approve or reject gear.schema.v2.proposal.json before canonical import.
Recommended: approve v2 direction, then run Phase 1C.5 to prepare a no-write canonical import dry run.

