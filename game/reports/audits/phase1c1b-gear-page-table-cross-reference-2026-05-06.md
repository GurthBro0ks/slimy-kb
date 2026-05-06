# Phase 1C.1B Gear Page Table Cross-Reference Audit

Generated UTC: 2026-05-06T15:56:50+00:00

## Scope

Parse Gear.wiki as an aggregate table page and compare spreadsheet calculator candidates to actual gear table rows.
No canonical data was modified.

## Counts

- Calculator candidates: 29
- Gear.wiki table row candidates parsed: 47
- Probable matches score >= 0.50: 1
- Unmatched: 28

## Classification Counts

- calculator_formula_row_needs_manual_mapping: 29

## Review Table

| Calculator Candidate | Best Gear.wiki Row | Score | Classification |
|---|---|---:|---|
| Time Wanderer | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| The Great Scientist | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| The Great Collector | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| The Cyber Snail | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Drifter's Power | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Drifter's Soul | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Adventurer's Soul | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Adventurer's Power | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Breakthrough Gene | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Tower of Qiankun | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Samsara | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Boundless Ocean | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Sea of Bitterness | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Life Evolution | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Mutation Direction | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Origin Seeker | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Biological Clock | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Bodhi Buddha | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Mysterious Aura | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Universal Truth | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Tai Chi | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Fortune Teller | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Fallen Angel | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Undead Reaper | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Dragon Ancestor | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Demon King | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Mutant Overlord | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Mecha Soldier | NONE | 0.0 | calculator_formula_row_needs_manual_mapping |
| Fortress | Fortress Ship | 0.6 | calculator_formula_row_needs_manual_mapping |

## PM Finding

The previous Phase 1C.1 page-filename matching was too literal.
The real Gear wiki source is an aggregate table, so Gear.wiki table rows should become the primary source for gear entity candidates.
Spreadsheet calculator rows should be treated as formula/modifier candidates unless they directly match a Gear.wiki row.

## Recommended Next Step

Run Phase 1C.2 to generate candidate gear entities from parsed Gear.wiki rows, with spreadsheet formula data linked only where names match.
