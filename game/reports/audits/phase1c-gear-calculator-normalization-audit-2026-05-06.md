# Phase 1C Gear Calculator Normalization Audit

Generated UTC: 2026-05-06T15:38:24+00:00

## Scope

Normalize Phase 1B.2 gear calculator staging files into candidate records only.
No canonical data was modified.

## Output Counts

- gear_items: 29
- gear_stat_scaling: 192
- gear_effect_scaling: 120
- gear_cost_by_level: 243
- combat_formulas: 793
- known_formula_issues: 8
- source_facts: 8

## Candidate Output Directory

- game/data/candidates/phase1c_gear_calculator

## Inputs

- game/data/staging/gear_calculator/gear_items_extracted.json
- game/data/staging/gear_calculator/cost_level_table.json
- game/data/staging/gear_calculator/formula_map_original_unpatched.csv
- game/data/staging/gear_calculator/workbook_nonempty_cells_original_unpatched.json
- game/data/staging/gear_calculator/formula_fixes_2026-05-06.json

## Formula Fixes Applied as Candidate Metadata

- gear_armor_level_formula_d142: Gear D142 — D142 was reading the wrong row. It must read its own level cell H142.
- gear_armor_level_formula_d149: Gear D149 — D149 was reading the wrong row. It must read its own level cell H149.
- combat_first_turn_attack_damage_c21: Combat C21 — Round 1 damage buff in I9 was calculated but not included in first-turn attack damage.
- combat_first_turn_attack_total_e21: Combat E21 — Round 1 damage buff in I9 was calculated but not included in first-turn attack total.
- combat_first_turn_rush_damage_c22: Combat C22 — Round 1 damage buff in I9 was calculated but not included in first-turn rush damage.
- combat_first_turn_rush_total_e22: Combat E22 — Round 1 damage buff in I9 was calculated but not included in first-turn rush total.
- combat_dead_inputs_i16_i21: Combat [I16, I17, I18, I19, I20, I21] — These inputs were visible but not referenced by any formulas.
- copy_of_combat_independence: [Copy of Combat, Copy of CombatMath] — Copy of Combat was secretly feeding through CombatMath back to the original Combat sheet.

## Shape Findings

- Raw gear record count: 29
- Formula row count: 793

## Review Rules For Next Phase

- Do not promote candidates directly.
- Compare candidate gear names against wiki.gg pages before canonical creation.
- Confirm slots and categories manually because spreadsheet categories may not match final schema slots.
- Prefer formula_fixes_2026-05-06.json over original unpatched formula_map rows.
- Combat formulas must remain candidate-only until tested against known in-game examples.

## Recommended Next Step

Run Phase 1C.1 to cross-reference candidate gear names against wiki.gg raw pages and generate a review matrix.
