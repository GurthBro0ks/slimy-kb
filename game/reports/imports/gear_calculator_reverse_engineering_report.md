# Gear Calculator Reverse Engineering Report

Source workbook: `Copy of Gear Calculator.xlsx`  
Generated: 2026-05-06T14:23:13Z

## Executive Summary

This workbook is a useful raw source for the Slimy Super Snail database, but it is not clean enough to promote directly into canonical records.

It contains three calculators/data systems:

1. **Gear stat calculator** — 29 gear items with equip toggles, enhancement levels, HP/ATK/DEF/RUSH contributions, and bonus effects.
2. **Combat calculator** — formulas for attack/rush base damage, crit damage, elemental damage, and boss defense mitigation.
3. **Gear cost calculator** — level-by-level material costs and difference calculation from current level to goal level.

Recommended handling for `slimy-kb`: import this as **staging source data**, not canonical truth. The extracted files from this reverse-engineering pass should land under something like:

```text
game/data/staging/gear_calculator/
game/reports/imports/
```

## Workbook Structure

- **Gear**: 157 formulas, 597 populated cells
- **GearMath**: 136 formulas, 520 populated cells
- **Combat**: 12 formulas, 104 populated cells
- **Copy of Combat**: 12 formulas, 105 populated cells
- **CombatMath**: 48 formulas, 96 populated cells
- **Cost**: 28 formulas, 60 populated cells
- **CostMath**: 400 formulas, 2223 populated cells

## Gear Data Model Found

The main gear model is split across `Gear` and `GearMath`.

- `Gear` is the user-facing sheet.
- `GearMath` is the helper/math sheet.
- `Gear!F<header_row>` is the equipped checkbox/boolean.
- `Gear!H<header_row>` is the level input.
- `GearMath!A<stat_row>` conditionally contributes a computed stat only if the gear is equipped.
- `GearMath!C2:C5` sum equipped HP, ATK, DEF, and RUSH.

### Extracted Gear Items

- **Realm** (4): Time Wanderer, The Great Scientist, The Great Collector, The Great Engineer
- **Form** (7): Serket Staff, Soul Reaper, Seraph's Light, Subspace Blade, Gaus M72, Fang of Tiamat, Excaladbolg
- **Instrument "Attack"** (9): Strength Master's Sword, Norris-chuck, Excalibur EX, Big Bounce, Power Spinach, Poseidon's Trident, Know-It-All Device, Golden Drazgul Fang, Incredible Key
- **Armor** (9): Ring of Paralysis, Dracula Cape, Fortress, Traveler Outfit, The Great Magician, Antimatter Shield, The Great Entertainer, Agamemnon Outfit, Libra Artifact

### Core Gear Formula Pattern

```text
effective_level_index = IF(level < 2, 0, level - 1)
stat_value = base_stat + per_level_stat * effective_level_index
effect_value = base_effect + per_level_effect * effective_level_index
equipped_contribution = IF(equipped, computed_stat, 0)
total_stat = SUM(all equipped_contributions for stat)
```

### Key Gear Formulas

- **Gear total HP** `GearMath!C2`: `=SUM(A12,A21,A47,A33,A27,A53,A59,A65,A71,A77,A84,A90,A96,A103,A109,A115,A121,A128,A134,A143,A150,A156,A162,A168,A174,A180,A187,A193,A41)`
- **Gear total ATK** `GearMath!C3`: `=SUM(A13,A22,A48,A42,A34,A28,A54,A60,A66,A72,A78,A85,A91,A97,A104,A110,A116,A122,A129,A135,A144,A151,A157,A163,A169,A175,A181,A188,A194)`
- **Equipped contribution pattern** `GearMath!A21`: `=if(Gear!F$20=True,Gear!C21,0)`
- **Enhancement index pattern** `GearMath!D20`: `=if(Gear!H20<2,0,Gear!H20-1)`
- **Gear stat scaling pattern** `Gear!C21`: `=GearMath!D21+(GearMath!E21*GearMath!$D$20)`
- **Gear effect scaling pattern** `Gear!E21`: `=GearMath!G21+(GearMath!D20*GearMath!H21)`
- **Combat mitigated boss defense** `CombatMath!B20`: `=$B$12*(1-$B$6)`
- **Combat attack base damage max** `CombatMath!H8`: `=IF(H3>H4,H3,H4)`
- **Combat rush base damage max** `CombatMath!H9`: `=IF(H5>H6,H5,H6)`
- **Combat elemental damage** `CombatMath!B21`: `=$E$9*$E$11`
- **Cost current lookup** `CostMath!B22`: `=VLOOKUP($D$20,$A$2:$AB$11,2,true)`
- **Cost goal lookup** `CostMath!B23`: `=VLOOKUP($F$20,$A$2:$AB$11,2,true)`
- **Cost diff** `CostMath!B24`: `=B23-B22`

## Combat Formula Model Found

The combat calculator is primarily implemented in `CombatMath`, with the visible `Combat` sheet pulling from it.

### Inputs

- Snail stats: HP, Attack, DEF, Rush
- Elemental stats: Fire, Water, Earth, Wind, Poison
- Crit Rate, Crit DMG, DMG Buff, Ignore Def
- Boss HP, Boss DEF, Crit DMG Red
- Turn and rush/crit toggles
- Per-round flat buffs: HP, ATK, DEF, RUSH

### Core Combat Formula Pattern

```text
snail_attack_after_buff = Combat!B3 + Combat!I11 * turn
snail_rush_after_buff   = Combat!B5 + Combat!I13 * turn

boss_def = IF(Combat!B15 = 0, 250000, Combat!B15)
ignore_def = Combat!B11
mitigated_def = boss_def * (1 - ignore_def)

attack_base = MAX(snail_attack_after_buff - mitigated_def, snail_attack_after_buff * 0.05)
rush_base   = MAX(snail_rush_after_buff - mitigated_def, snail_rush_after_buff * 0.05)

crit_damage = selected_base * ((0.5 + crit_dmg) * (1 - crit_dmg_reduction)) * (1 + dmg_buff)

elemental_attack_damage = total_elemental_damage * LOG(snail_attack_after_buff, 5)
elemental_rush_damage   = total_elemental_damage * LOG(snail_rush_after_buff, 5)
```

### Important Caveats

- **Copy of Combat is not an independent calculator.** Its damage output formulas reference `CombatMath`, and `CombatMath` references the original `Combat` sheet, not `Copy of Combat`. Changing inputs on the copy sheet will not fully flow through unless CombatMath is duplicated/parameterized.\n- **First-turn damage appears partially disconnected.** `CombatMath!B16` stores `Combat!I9` and `CombatMath!H20` computes a first-turn attack amount, but the visible Combat totals use `CombatMath!H8`, `CombatMath!J8`, and `CombatMath!B21`, not `H20` or total buff `B17`.\n- **Several right-side combat inputs are unused by formulas.** Lifesteal Rate/EFF, Dodge, Hit, DMG Reduc, and Crit DMG Reduc on `Combat!I16:I21` do not appear in formulas. Only per-round HP/ATK/DEF/RUSH buffs in `I10:I13` are used.\n

## Cost Formula Model Found

The cost calculator is mainly in `CostMath`.

- Rows `A2:AB11` are the normalized level cost table.
- `CostMath!D20` is the current level.
- `CostMath!F20` is the goal level.
- Rows 22 and 23 use `VLOOKUP` against the level table.
- Row 24 computes the difference.

### Level Cost Table

| Level | Glue Total | Btad Total | Reagent | Crystal | Eye | WingA | WingH |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 560 | 280000 | 0 | 1 | 1 | 1 | 1 |
| 2 | 1470 | 770000 | 100 | 2 | 3 | 3 | 3 |
| 3 | 2830 | 1700000 | 400 | 3 | 6 | 6 | 6 |
| 4 | 4750 | 3080000 | 1000 | 4 | 10 | 10 | 10 |
| 5 | 7350 | 5100000 | 2000 | 5 | 15 | 15 | 15 |
| 6 | 10760 | 7930000 | 3500 | 6 | 21 | 21 | 21 |
| 7 | 15170 | 11760000 | 5600 | 7 | 28 | 28 | 28 |
| 8 | 20940 | 16800000 | 8400 | 8 | 36 | 36 | 36 |
| 9 | 28330 | 23340000 | 12000 | 9 | 45 | 45 | 45 |


### Core Cost Formula Pattern

```text
current_cost = VLOOKUP(current_level, level_cost_table, material_column, TRUE)
goal_cost    = VLOOKUP(goal_level, level_cost_table, material_column, TRUE)
diff         = goal_cost - current_cost
```

Rows 135 onward contain pre-red / base-red material expansion formulas for specific named gear and placeholder gear slots. Those formulas are recipe-expansion math and should be treated as a second import category: `gear_crafting_recipe`.

## Findings / Risk List

- **Copy of Combat is not an independent calculator.** Its damage output formulas reference `CombatMath`, and `CombatMath` references the original `Combat` sheet, not `Copy of Combat`. Changing inputs on the copy sheet will not fully flow through unless CombatMath is duplicated/parameterized.\n- **First-turn damage appears partially disconnected.** `CombatMath!B16` stores `Combat!I9` and `CombatMath!H20` computes a first-turn attack amount, but the visible Combat totals use `CombatMath!H8`, `CombatMath!J8`, and `CombatMath!B21`, not `H20` or total buff `B17`.\n- **Several right-side combat inputs are unused by formulas.** Lifesteal Rate/EFF, Dodge, Hit, DMG Reduc, and Crit DMG Reduc on `Combat!I16:I21` do not appear in formulas. Only per-round HP/ATK/DEF/RUSH buffs in `I10:I13` are used.\n- **Some gear enhancement references look off-row.** Example: `Gear!D142 = IF(Gear!H141<2,0,Gear!H141-1)` even though Ring of Paralysis level is on row 142; `Gear!D149 = IF(Gear!H146<2,0,Gear!H146-1)` while Dracula Cape level is on row 149. These force enhancement index to 0 unless the referenced non-header cells happen to change.\n- **Spelling/normalization issues should be normalized before DB import.** Examples include `Equiped`, `Poisen`, `Excaladbolg`, `Dragon Ign Def`, `Mutant Ign Def`, and mixed labels like `IF Rush ATK` vs `If Rush DEF`.\n- **Gear data is valuable but not canonical-ready.** It should go into staging first, then be normalized into IDs, stat keys, effect keys, slot/category, base value, per-level value, source cell, and formula cell.\n

## Recommended Database Shape

### `gear_item`
```json
{
  "id": "the_great_scientist",
  "name": "The Great Scientist",
  "category": "Realm",
  "slot": null,
  "source_workbook": "Copy of Gear Calculator.xlsx",
  "source_sheet": "Gear",
  "source_row": 20
}
```

### `gear_stat_scaling`
```json
{
  "gear_id": "the_great_scientist",
  "stat": "hp",
  "base": 3000,
  "per_effective_level": 600,
  "formula": "base + per_effective_level * effective_level_index",
  "source_cell": "Gear!C21"
}
```

### `gear_effect_scaling`
```json
{
  "gear_id": "the_great_scientist",
  "effect": "time_chest",
  "base": 0.12,
  "per_effective_level": 0.02,
  "source_cell": "Gear!E21"
}
```

### `gear_cost_by_level`
```json
{
  "level": 8,
  "glue_total": 20940,
  "btad_total": 16800000,
  "reagent": 8400,
  "crystal": 8,
  "eye": 36
}
```

### `combat_formula`
Store formulas as versioned named formulas rather than hardcoding them into one table. This lets us improve/verify combat math without hiding changes.

```json
{
  "id": "attack_base_damage_v1",
  "formula": "max(snail_attack_after_buff - mitigated_def, snail_attack_after_buff * 0.05)",
  "source_cell": "CombatMath!H8",
  "status": "staging"
}
```

## Extracted Files

- `gear_items_extracted.json` — 29 parsed gear records with source rows, stats, effects, formulas, and raw rows.
- `cost_level_table.json` — normalized level 1 through 9 cost table.
- `formula_map.csv` — 793 formulas across all sheets.
- `formulas_extracted.json` — formula map in JSON form.
- `workbook_nonempty_cells.json` — raw non-empty cell archive.

## PM Recommendation

Next step should be a **staging import prompt**, not direct canonical promotion:

1. Copy extracted JSON/CSV into `game/data/staging/gear_calculator/`.
2. Create `gear_calculator_import_report.md`.
3. Normalize gear names/effects/stat keys.
4. Mark formula bugs as `known_issues`.
5. Only then promote clean records into canonical JSON.

