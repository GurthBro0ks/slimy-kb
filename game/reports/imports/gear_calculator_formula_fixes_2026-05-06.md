# Gear Calculator Formula Fixes — Reviewed

## Status

These fixes are accepted as spreadsheet-source corrections and should be treated as staging metadata.

Do not promote spreadsheet-derived data to canonical until Phase 1C normalization review is complete.

## Fix 1: Armor Level Formulas

Sheet: Gear

| Cell | Correct Formula |
|---|---|
| D142 | `=if(Gear!H142<2,0,Gear!H142-1)` |
| D149 | `=if(Gear!H149<2,0,Gear!H149-1)` |

Reason: both formulas were off-row and reading the wrong level cells.

## Fix 2: First-Turn Damage

Sheet: Combat

| Cell | Correct Formula |
|---|---|
| C21 | `=(1+B10+I9)*(CombatMath!H8)` |
| E21 | `=(1+B10+I9)*CombatMath!B21` |
| C22 | `=if(E16=TRUE,(1+B10+I9)*CombatMath!H9,0)` |
| E22 | `=if(E16=TRUE,(1+B10+I9)*CombatMath!B22,0)` |

Reason: Round 1 DMG buff in I9 was calculated but disconnected from first-turn damage outputs.

## Fix 3: Dead Inputs

Sheet: Combat

Clear values in I16 through I21.

Update labels:

| Cell | Label |
|---|---|
| H16 | Lifesteal Rate (unused) |
| H17 | Lifesteal EFF (unused) |
| H18 | Dodge (unused) |
| H19 | Hit (unused) |
| H20 | DMG Reduc (unused) |
| H21 | Crit DMG Reduc (unused) |

Reason: these inputs were visible but unused.

## Fix 4: Copy of Combat Independence

Create Copy of CombatMath from CombatMath.

In Copy of CombatMath, replace formula references from `Combat!` to `'Copy of Combat'!`.

In Copy of Combat, replace formula references from `CombatMath!` to `'Copy of CombatMath'!`.

Then apply the same first-turn damage and dead-input fixes to Copy of Combat using Copy of CombatMath references.

## Import Rule

The original extraction files remain preserved as unpatched source evidence.

The normalized candidate data must prefer the patched formulas recorded here.
