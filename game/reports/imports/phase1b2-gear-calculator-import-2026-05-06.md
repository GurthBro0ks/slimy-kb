# Phase 1B.2 Gear Calculator Import

Generated UTC: 2026-05-06 15:21:00 UTC

## Purpose

Stage reverse-engineered spreadsheet data from Copy of Gear Calculator.xlsx.
Record reviewed formula fixes before Phase 1C normalization.
This data is source and staging only. It is not canonical yet.

## Source Bundle

- game/sources/spreadsheets/gear_calc_reverse_engineering_bundle.zip

## Extracted Source Directory

- game/sources/spreadsheets/gear_calc_reverse_engineering

## Staging Directory

- game/data/staging/gear_calculator

## Staged Files

- game/data/staging/gear_calculator/cost_level_table.json
- game/data/staging/gear_calculator/formula_fixes_2026-05-06.json
- game/data/staging/gear_calculator/formula_map_original_unpatched.csv
- game/data/staging/gear_calculator/gear_items_extracted.json
- game/data/staging/gear_calculator/workbook_nonempty_cells_original_unpatched.json

## Formula Fix Files

- game/data/staging/gear_calculator/formula_fixes_2026-05-06.json
- game/reports/imports/gear_calculator_formula_fixes_2026-05-06.md
- Patched workbook not created because openpyxl was unavailable (externally-managed Python environment).

## Known Findings

- Gear calculator data includes gear item rows (29 items), stat formulas, level scaling, equipped flags, and cost tables.
- Original formula extraction is preserved as unpatched evidence.
- Corrected formulas are recorded in formula_fixes_2026-05-06.json and should be preferred during normalization.
- Combat calculator formulas require separate Phase 1C review before canonical use.

## Recommended Next Step

Run Phase 1C to normalize staged records into review tables:
- gear_item
- gear_stat_scaling
- gear_effect_scaling
- gear_cost_by_level
- combat_formula
- known_formula_issue
