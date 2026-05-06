# Per-Sheet Formula Catalog

**Source File:** `Updated Copy of SuperSnail Calcs.xlsx`  
**Total Sheets:** 33 | **Sheets with Formulas:** 29 | **Total Formulas:** 4,727  
**Formula Families:** 184 | **Cross-sheet References:** 72

---

## Sheet: Minion Base Stats
**Total Formulas:** 938
**Formula Families:** `=X-X` (704), `=X+X` (628), `=X` (596), `=(X-X)/4` (80), `=X/10+X+X+X` (30)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| H18 | `=A3` | Compound calculation *(Repeated 150x across sheet)* | A3 |
| I18 | `=B4` | Compound calculation | B4 |
| M18 | `=I18/10+J18+K18+L18` | Stat combination with tenth scaling *(Repeated 170x across sheet)* | I18, J18, K18, L18 |
| M19 | `=I19/10+J19+K19+L19` | Stat combination with tenth scaling | I19, J19, K19, L19 |
| B4 | `=(B13-B11)/4` | Quarter difference calculation *(Repeated 580x across sheet)* | B11, B13 |
| C4 | `=(C13-C11)/4` | Quarter difference calculation | C11, C13 |
| M5 | `=50*I5` | Scalar multiplication *(Repeated 22x across sheet)* | I5 |
| N5 | `=52.5*J5` | Scalar multiplication | J5 |
| B260 | `=B261/2` | Division/rate calculation *(Repeated 16x across sheet)* | B261 |
| C260 | `=C261/2` | Division/rate calculation | C261 |
| B324 | `=(B332-B331)/2` | Difference/subtraction *(Repeated 20x across sheet)* | B331, B332 |
| C324 | `=(C332-C331)/2` | Difference/subtraction | C331, C332 |
| B269 | `=B268+3*B260` | Additive combination *(Repeated 20x across sheet)* | B260, B268 |
| C269 | `=C268+3*C260` | Additive combination | C260, C268 |

#### Notable Patterns:
Computes minion stat scaling using differences, quartering, halving, and multiplication by constants (50, 52.5). Includes linear progression and tier-based calculations.

---

## Sheet: Museum
**Total Formulas:** 732
**Formula Families:** `=X+X` (628), `=X` (596), `=SUM(X:X)` (233), `=48+99+63+66+56` (1), `=106+62+49+69+76` (1)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| E32 | `=K13` | Compound calculation *(Repeated 229x across sheet)* | K13 |
| H32 | `=H13` | Compound calculation | H13 |
| E48 | `=SUM(E32:E47)` | Sum range of cells *(Repeated 32x across sheet)* | E32, E47 |
| F48 | `=SUM(F32:F47)` | Sum range of cells | F32, F47 |
| J4 | `=D4+I4` | Additive combination *(Repeated 471x across sheet)* | D4, I4 |
| K4 | `=E4+I4` | Additive combination | E4, I4 |

#### Notable Patterns:
Calculates museum artifact bonuses by combining base stats with synergy additions. Heavy use of simple additions and SUM ranges.

---

## Sheet: Protomon
**Total Formulas:** 511
**Formula Families:** `=SUM(OFFSET(X,1,0,X))` (240), `=60*(X+1) + 20*MAX(X-60, 0)` (181), `=60*(X+1)` (58), `=VLOOKUP(X,X:X,3,FALSE)` (10), `=VLOOKUP(X,X:X,2,FALSE)` (9)
**Cross-sheet References:** None
**Error Flags:** Contains VLOOKUPs without IFERROR wrapping; Uses volatile OFFSET functions (performance impact)

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B8 | `=MIN(VLOOKUP(B7,$N$61:$P$67,2,TRUE), VLOOKUP($B$4,$K$71:$L$310,2,TRUE))` | Capped lookup (MIN of two VLOOKUPs) *(Repeated 28x across sheet)* | B7 |
| A10 | `=VLOOKUP($B6,$B$45:$F$176,2,FALSE)` | Lookup value from table | B6 |
| K71 | `=SUM(OFFSET($J$70,1,0,I71))` | Volatile dynamic range sum *(Repeated 240x across sheet)* | I71 |
| K72 | `=SUM(OFFSET($J$70,1,0,I72))` | Volatile dynamic range sum | I72 |
| J130 | `=60*(I129+1) + 20*MAX(I130-60, 0)` | Breakpoint scaling (60 base + 20 overflow) *(Repeated 181x across sheet)* | I129, I130 |
| J131 | `=60*(I130+1) + 20*MAX(I131-60, 0)` | Breakpoint scaling (60 base + 20 overflow) | I130, I131 |
| F10 | `=E10+D10*B8` | Additive combination *(Repeated 62x across sheet)* | B8, D10, E10 |
| F16 | `=E16+D16*B14` | Additive combination | B14, D16, E16 |

#### Notable Patterns:
Pet/monster stat calculator with VLOOKUPs for base values, MIN functions for caps, and volatile OFFSET-based cumulative sums. Includes breakpoint calculations (60+ scaling).

---

## Sheet: Compass
**Total Formulas:** 494
**Formula Families:** `=X+X` (628), `=X` (596), `=sum(X:X)` (350), `=VLOOKUP(X,X:X,12,FALSE)` (30), `=VLOOKUP(X,X:X,13,FALSE)` (30)
**Cross-sheet References:** None
**Error Flags:** Contains VLOOKUPs without IFERROR wrapping

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| G32 | `=VLOOKUP($C32,$A$3:$R$25,4,FALSE)+VLOOKUP($C32,$A$3:$R$25,18,FALSE)` | Lookup value from table *(Repeated 23x across sheet)* | C32 |
| H32 | `=VLOOKUP($C32,$A$3:$R$25,8,FALSE)+VLOOKUP($G32,$Y$2:$AA$50,2)` | Lookup value from table | C32, G32 |
| I32 | `=VLOOKUP($C32,$A$3:$R$25,9,FALSE)+VLOOKUP($G32,$Y$2:$AA$50,2)` | Lookup value from table | C32, G32 |
| J32 | `=VLOOKUP($C32,$A$3:$R$25,10,FALSE)+VLOOKUP($G32,$Y$2:$AA$50,2)` | Lookup value from table | C32, G32 |
| K32 | `=VLOOKUP($C32,$A$3:$R$25,11,FALSE)+VLOOKUP($G32,$Y$2:$AA$50,2)` | Lookup value from table | C32, G32 |
| L32 | `=VLOOKUP($C32,$A$3:$R$25,12,FALSE)` | Lookup value from table *(Repeated 30x across sheet)* | C32 |
| M32 | `=VLOOKUP($C32,$A$3:$R$25,13,FALSE)` | Lookup value from table | C32 |
| N32 | `=VLOOKUP($C32,$A$3:$R$25,14,FALSE)` | Lookup value from table | C32 |
| O32 | `=VLOOKUP($C32,$A$3:$R$25,15,FALSE)` | Lookup value from table | C32 |
| P32 | `=VLOOKUP($C32,$A$3:$R$25,16,FALSE)` | Lookup value from table | C32 |
| Q32 | `=VLOOKUP($C32,$A$3:$R$25,17,FALSE)` | Lookup value from table | C32 |
| W33 | `=((V33-$Z$73)*(V35+P37/100)*((V36/100)*V37 + (1-V36/100)*1)) + LOG(V33,5)*Q37*(V35+P37/100)` | Logarithmic scaling factor *(Repeated 5x across sheet)* | V33, V35, V36, V37, P37, Q37 |
| V33 | `=$Z$66*(1+I37/100)` | Compound calculation *(Repeated 5x across sheet)* | I37 |
| G233 | `=IF(D233=F233, VLOOKUP($B233,$A$208:$S$226, 4,FALSE) + VLOOKUP($B233,$A$208:$S$226, 18,FALSE), VLOOKUP($B233,$A$208:$S$226, 19,FALSE))` | Conditional value selection | B233, D233, F233 |

#### Notable Patterns:
Multi-table VLOOKUP engine pulling data from lookup ranges across columns 4-18. Combines main table lookups with secondary lookups from Y:AA range.

---

## Sheet: Minion Boosts
**Total Formulas:** 402
**Formula Families:** `=X` (596), `=sum(X:X)` (350), `=(X+X)/X` (262)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| I3 | `=(D3+E3)/H3` | Percentage/average ratio *(Repeated 262x across sheet)* | D3, E3, H3 |
| I4 | `=(D4+E4)/H4` | Percentage/average ratio | D4, E4, H4 |
| O3 | `=I37` | Compound calculation *(Repeated 133x across sheet)* | I37 |
| P3 | `=F37` | Compound calculation | F37 |
| K3 | `=SUM(K4:K36)` | Sum range of cells *(Repeated 35x across sheet)* | K4, K36 |
| L3 | `=SUM(L4:L36)` | Sum range of cells | L4, L36 |

#### Notable Patterns:
Minion boost percentage calculator computing (boost1 + boost2) / divisor for each minion, plus cell-reference lookups across multiple boost columns.

---

## Sheet: Drifter Stats
**Total Formulas:** 210
**Formula Families:** `=X+X` (628), `=(X-X*120)/X` (168), `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B4 | `=(AG3-AH3*120)/$AF3` | Drifter stat regression formula *(Repeated 168x across sheet)* | AF3, AG3, AH3 |
| D4 | `=(AI3-AJ3*120)/$AF3` | Drifter stat regression formula | AF3, AI3, AJ3 |
| S4 | `=B4+D4+F4+H4+J4+L4+N4+P4` | Additive combination *(Repeated 42x across sheet)* | B4, D4, F4, H4, J4, L4, N4, P4 |
| T4 | `=F4+H4` | Additive combination *(Repeated 42x across sheet)* | F4, H4 |
| U4 | `=J4+L4` | Additive combination | J4, L4 |

#### Notable Patterns:
Drifter character stat analyzer using linear regression-style formulas: (stat - stat*120)/divisor. Aggregates across 8 stat columns and creates pairwise sums.

---

## Sheet: Sailing Calculator
**Total Formulas:** 201
**Formula Families:** `=X-X` (704), `=X` (596), `=sum(X:X)` (350), `=(X+X)*IF(X>0, 1, 0)` (38), `=IF(X >= 10, 'Drifter Priority'!X, 'Drifter Priority'!X)` (35)
**Cross-sheet References:** Drifter Priority
**Error Flags:** Contains VLOOKUPs without IFERROR wrapping

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| C2 | `=VLOOKUP(A2,'Drifter Stats'!$A$4:$Q$24,4,FALSE)` | Lookup value from table *(Repeated 22x across sheet)* | A2 |
| D2 | `=$I$22*IF(COUNTIF($A$11:$A$14, $F$22)>0, 1, 0)` | Conditional based on list membership *(Repeated 20x across sheet)* | A11, A14, F22, I22 |
| H2 | `=B2*C2*(1+D2)+E2+F2` | Compound calculation *(Repeated 22x across sheet)* | B2, C2, D2, E2, F2 |
| I2 | `=B2*C2*(1+D2)*10+G2` | Compound calculation *(Repeated 22x across sheet)* | B2, C2, D2, G2 |
| D48 | `=(C48*$B$25*(1.5+$B$26)+C48*(1-$B$25))*IF(B48>0, 1, 0)` | Compound calculation *(Repeated 20x across sheet)* | B25, B26, B48, C48 |
| F48 | `=MAX((B48-E48*(1-$B$22)), 0)` | Maximum of values *(Repeated 20x across sheet)* | B22, B48, E48 |
| C49 | `=($B$18+(A49-1)*$B$24+FLOOR((1-B49/$B$19)*10,1)*$B$27)*IF(B49>0, 1, 0)` | Round down to integer *(Repeated 19x across sheet)* | A49, B18, B19, B24, B27, B49 |
| B49 | `=(F48+$B$23)*IF(F48>0, 1, 0)` | Compound calculation *(Repeated 38x across sheet)* | B23, F48 |
| G11 | `=IF(H9 >= 10, 'Drifter Priority'!D299, 'Drifter Priority'!C299)` | Conditional value selection *(Repeated 26x across sheet)* | H9 |
| G12 | `=IF(H10 >= 10, 'Drifter Priority'!D298, 'Drifter Priority'!C298)` | Conditional value selection | H10 |

#### Notable Patterns:
Complex sailing expedition calculator with VLOOKUPs to Drifter Stats, nested IF+COUNTIF conditionals, multiplicative damage/speed formulas, and tiered reward calculations.

---

## Sheet: Hitmen
**Total Formulas:** 184
**Formula Families:** `=X-X` (704), `=X+X` (628)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B5 | `=B4-B$34` | Difference/subtraction *(Repeated 130x across sheet)* | B4, B34 |
| C5 | `=C4-C$34` | Difference/subtraction | C4, C34 |
| B20 | `=B13+B18-B15+B16-B17-B19-B14` | Additive combination *(Repeated 20x across sheet)* | B13, B14, B15, B16, B17, B18, B19 |
| B22 | `=B5-B20` | Difference/subtraction | B5, B20 |
| B24 | `=B22-B23` | Difference/subtraction | B22, B23 |

#### Notable Patterns:
Hitman progression calculator with differences and sums for combat stat tracking.

---

## Sheet: Dragon DNA Costs
**Total Formulas:** 183
**Formula Families:** `=X-X` (704), `=X+X` (628), `=sum(X:X)` (350), `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B5 | `=B4-B$45` | Difference/subtraction *(Repeated 130x across sheet)* | B4, B45 |
| C5 | `=C4-C$45` | Difference/subtraction | C4, C45 |
| B22 | `=B5-B20` | Difference/subtraction *(Repeated 20x across sheet)* | B5, B20 |
| B38 | `=B22+B36-B28+B30-B32-B34-B24+B26-B35` | Additive combination *(Repeated 20x across sheet)* | B22, B24, B26, B28, B30, B32, B34, B35, B36 |
| C98 | `=B98/24` | Convert to per-hour rate *(Repeated 14x across sheet)* | B98 |
| D98 | `=C98/24` | Convert to per-hour rate | C98 |
| B99 | `=D30+D33+D52+D80+D93+D97+D24+D36+D27+D39+D58+D84+D87+D90+D63+D69+D72+D75+D66+D78+D42+D45+D48+D54+D81+D94+D86+D89+D95+D96+D60+D46+D50+D56+D43+D47+D51+D53+D57+D82+D85+D88+D91+D40+D44+D49+D55+D59+D61+D64+D67+D70+D73+D76+D79+D83+D92` | Additive combination | D24, D27, D30, D33, D36, D39, D42, D43, D44, D45, D46, D47, D48, D49, D50, D51, D52, D53, D54, D55, D56, D57, D58, D59, D60, D61, D63, D64, D66, D67, D69, D70, D72, D73, D75, D76, D78, D79, D80, D81, D82, D83, D84, D85, D86, D87, D88, D89, D90, D91, D92, D93, D94, D95, D96, D97 |

#### Notable Patterns:
DNA cost calculator for dragon upgrades, using subtractions, divisions by 24, and summation of category costs.

---

## Sheet: Relic Albums
**Total Formulas:** 140
**Formula Families:** `=X*28` (65), `=X*8` (28), `=X*(280/2)` (14), `=CEILING(X*280/3,1)` (14), `=7*3*7*X` (11)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| C2 | `=A2*28` | Scalar multiplication *(Repeated 65x across sheet)* | A2 |
| C3 | `=A3*28` | Scalar multiplication | A3 |
| C168 | `=A168*8` | Scalar multiplication *(Repeated 28x across sheet)* | A168 |
| C169 | `=A169*8` | Scalar multiplication | A169 |
| C80 | `=A80*(280/2)` | Scalar multiplication *(Repeated 14x across sheet)* | A80 |
| C112 | `=CEILING(A112*280/3,1)` | Round up to integer *(Repeated 14x across sheet)* | A112 |
| C151 | `=7*3*7*A151` | Scalar multiplication *(Repeated 11x across sheet)* | A151 |

#### Notable Patterns:
Relic album completion calculator multiplying counts by constants (28, 8, 280, 280/2, 280/3) and applying CEILING/FLOOR for rounding.

---

## Sheet: DNA Costs
**Total Formulas:** 126
**Formula Families:** `=X-X` (704), `=sum(X:X)` (350), `=X+X+X` (98), `=SUM(X:X)` (233), `=X+X+X+X` (13)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B5 | `=B4-B$45` | Difference/subtraction *(Repeated 105x across sheet)* | B4, B45 |
| C5 | `=C4-C$45` | Difference/subtraction | C4, C45 |
| B22 | `=B5-B20` | Difference/subtraction *(Repeated 15x across sheet)* | B5, B20 |
| B38 | `=B22+B36-B28+B30-B32-B34-B24+B26-B35` | Additive combination *(Repeated 15x across sheet)* | B22, B24, B26, B28, B30, B32, B34, B35, B36 |
| C98 | `=B98/24` | Convert to per-hour rate *(Repeated 14x across sheet)* | B98 |
| D98 | `=C98/24` | Convert to per-hour rate | C98 |
| B99 | `=D24+D27+D52+D80+D30+D21+D33+D36` | Additive combination | D21, D24, D27, D30, D33, D36, D52, D80 |

#### Notable Patterns:
Standard DNA cost calculator with subtraction-based tier differences, division by 24 for time conversion, and grand totals.

---

## Sheet: Gene Research
**Total Formulas:** 96
**Formula Families:** `=sum(X:X)` (350), `=SUM(X:X)` (233), `=X+X+X` (98), `=X+X+X+X` (13), `=X+X+X+X+X` (10)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| D6 | `=sum(D3:E5)` | Sum range of cells *(Repeated 44x across sheet)* | D3, E5 |
| F6 | `=sum(F3:G5)` | Sum range of cells | F3, G5 |
| B56 | `=D6+D9+D14+D19+D35+D54+D29+D32+D26` | Additive combination *(Repeated 8x across sheet)* | D14, D19, D26, D29, D32, D35, D54, D6, D9 |
| B291 | `=B56+D73+D102` | Additive combination *(Repeated 7x across sheet)* | B56, D102, D73 |
| B293 | `=B58+H73+H102` | Additive combination *(Repeated 6x across sheet)* | B58, H102, H73 |
| B294 | `=B59+J73+J76+J102` | Additive combination *(Repeated 4x across sheet)* | B59, J102, J73, J76 |

#### Notable Patterns:
Gene research speed and cost calculator. Sums research times across gene categories and computes totals across 4 parallel research tracks.

---

## Sheet: Dance Calculator
**Total Formulas:** 86
**Formula Families:** `=X` (596), `=IF(X >= 10, 'Drifter Priority'!X, 'Drifter Priority'!X)` (35), `=X*FLOOR(10*(X*(1+SUM(X:X))*3)*(1+X),1)/10` (12), `=50*X` (10), `=VLOOKUP(X,'Drifter Stats'!X:X,12,FALSE)` (6)
**Cross-sheet References:** Drifter Priority, Drifter Stats
**Error Flags:** Contains VLOOKUPs without IFERROR wrapping; References 'Drifter Priority' which has no formulas

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| C2 | `=VLOOKUP(A2,'Drifter Stats'!$A$4:$Q$24,12,FALSE)` | Lookup value from table *(Repeated 10x across sheet)* | A2 |
| J2 | `=FLOOR(10*(C2*(1+SUM(D2:H2))*3)*(1+I2),1)/10` | Round down to integer *(Repeated 12x across sheet)* | C2, D2, H2, I2 |
| K2 | `=B2*FLOOR(10*(C2*(1+SUM(D2:G2))*3)*(1+I2),1)/10` | Scalar multiplication *(Repeated 12x across sheet)* | B2, C2, D2, G2, I2 |
| F12 | `=IF(AND(D12 = "Athena", C12 = "Male"), 0, (FLOOR(B12*(IF(D12="Amakusa", 1-$M$19, 1)) - 3*(IF(D12="Dracula",$M$18, 0)),1)))` | Multi-condition branch *(Repeated 5x across sheet)* | B12, C12, D12, M18, M19 |
| G12 | `=IF(E12 > F12, 1, 0)` | Conditional value selection *(Repeated 5x across sheet)* | E12, F12 |
| K12 | `=IF(L10 >= 10, 'Drifter Priority'!D41, 'Drifter Priority'!C41)` | Conditional value selection *(Repeated 20x across sheet)* | L10 |
| M12 | `=0.04*L12` | Scalar multiplication *(Repeated 6x across sheet)* | L12 |

#### Notable Patterns:
Dance performance calculator with VLOOKUPs to Drifter Stats and Drifter Priority, FLOOR-based score rounding, character-specific conditional logic (Athena/Amakusa/Dracula), and percentage multipliers.

---

## Sheet: Band Calculator
**Total Formulas:** 82
**Formula Families:** `=X-X` (704), `=X` (596), `=IF(X >= 10, 'Drifter Priority'!X, 'Drifter Priority'!X)` (35), `=0.04*X` (6), `=0.03*X` (6)
**Cross-sheet References:** Drifter Priority, Drifter Stats, Rift Anecdotes
**Error Flags:** Contains VLOOKUPs without IFERROR wrapping; References 'Drifter Priority' which has no formulas

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| C2 | `=VLOOKUP(A2,'Drifter Stats'!$A$4:$Q$24,2,FALSE)` | Lookup value from table *(Repeated 10x across sheet)* | A2 |
| J2 | `=$I$16*IF($B$10 = J1, 1, 0)` | Conditional value selection *(Repeated 11x across sheet)* | B10, I16, J1 |
| N2 | `=ROUND(10*C2*(SUM(D2:L2)+1)*(SUM(1+M2)),0)/10` | Round to precision *(Repeated 5x across sheet)* | C2, D2, L2, M2 |
| O2 | `=FLOOR(B2*N2,1)` | Round down to integer *(Repeated 5x across sheet)* | B2, N2 |
| B10 | `=VLOOKUP(B9,'Rift Anecdotes'!B174:G195,5,FALSE)` | Lookup value from table *(Repeated 2x across sheet)* | B9 |
| G9 | `=IF(H7 >= 10, 'Drifter Priority'!D237, 'Drifter Priority'!C237)` | Conditional value selection *(Repeated 24x across sheet)* | H7 |
| I12 | `=0.04*H12` | Scalar multiplication *(Repeated 6x across sheet)* | H12 |

#### Notable Patterns:
Band composition calculator with VLOOKUPs to Drifter Stats and Drifter Priority, ROUND/FLOOR-based stat calculations, instrument-specific multipliers, and anecdote lookups from Rift Anecdotes.

---

## Sheet: Cells Gained
**Total Formulas:** 80
**Formula Families:** `=X+X` (628), `=sum(X:X)` (350)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| D14 | `=sum(D2:E13)` | Sum range of cells *(Repeated 20x across sheet)* | D2, E13 |
| D22 | `=sum(D17:E21)` | Sum range of cells | D17, E21 |
| B57 | `=D14+D22+D31+D54` | Additive combination *(Repeated 5x across sheet)* | D14, D22, D31, D54 |
| B112 | `=$B$57+D64+D67` | Additive combination *(Repeated 30x across sheet)* | D64, D67 |
| B117 | `=$B$57+D108` | Additive combination *(Repeated 20x across sheet)* | D108 |

#### Notable Patterns:
Cell income calculator summing category gains and adding base values to compute total cells per stat type.

---

## Sheet: Rocket Cabin Effects
**Total Formulas:** 75
**Formula Families:** `=X+X` (628)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B31 | `=B4+B8+B12+B16+B20+B24+B28` | Additive combination *(Repeated 50x across sheet)* | B12, B16, B20, B24, B28, B4, B8 |
| C31 | `=C4+C8+C12+C16+C20+C24+C28` | Additive combination | C12, C16, C20, C24, C28, C4, C8 |
| B5 | `=B2+B3` | Additive combination *(Repeated 10x across sheet)* | B2, B3 |

#### Notable Patterns:
Rocket cabin buff calculator using additions and summations for cabin upgrade tracking.

---

## Sheet: Cost Reductions
**Total Formulas:** 18
**Formula Families:** `=sum(X:X)` (350)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B4 | `=SUM(B5:B24)` | Sum range of cells | B5, B24 |
| D4 | `=SUM(D5:D24)` | Sum range of cells | D5, D24 |
| F4 | `=SUM(F5:F24)` | Sum range of cells | F5, F24 |
| H4 | `=SUM(H5:H24)` | Sum range of cells | H5, H24 |
| J4 | `=SUM(J5:J24)` | Sum range of cells | J5, J24 |

#### Notable Patterns:
Cost reduction aggregator computing percentage-based discounts across upgrade categories.

---

## Sheet: Travel Speed
**Total Formulas:** 17
**Formula Families:** `=X-X` (704), `=SUM(X:X)` (233), `=X+X+X+X+X` (10)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| D10 | `=SUM(D3:F9)` | Sum range of cells | D3, F9 |
| D38 | `=MAX(SUM(D20:E21), SUM(D23:E25), SUM(D27:E28), SUM(D30:E31), SUM(D33:E34), SUM(D36:E37))` | Maximum of multiple sum ranges | D20, D23, D27, D30, D33, D36, E21, E25, E28, E31, E34, E37 |
| B64 | `=D10+D13+D38+D61+D16` | Additive combination | D10, D13, D16, D38, D61 |
| B66 | `=$B$65/(1+$B$64/100)` | Apply percentage divisor | B64, B65 |
| B72 | `=$B$64+SUM(D70:D71)` | Additive combination | D70, D71 |
| B73 | `=$B$65/(1+$B72/100)` | Apply percentage divisor | B72, B65 |

#### Notable Patterns:
Travel speed calculator using MAX of multiple SUM ranges, base speed division by (1 + bonus/100), and progressive speed summation.

---

## Sheet: Tadpole Pond
**Total Formulas:** 16
**Formula Families:** `=sum(X:X)` (350), `=SUM(X:X)` (233), `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B88 | `=F16+F19+F58+F84+F30+F24+F39+F36` | Additive combination | F16, F19, F24, F30, F36, F39, F58, F84 |
| B89 | `=H16+H58+H84+H19+H30+H39` | Additive combination | H16, H19, H30, H39, H58, H84 |

#### Notable Patterns:
Tadpole Pond building cost calculator adding up individual building costs into grand totals.

---

## Sheet: Fungus Farm
**Total Formulas:** 16
**Formula Families:** `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B83 | `=D16+D27+D52+D80+D21+D33+D24+D30` | Additive combination | D16, D21, D24, D27, D30, D33, D52, D80 |
| B84 | `=E16+E27+E52+E80+E21+E33+E24+E30` | Additive combination | E16, E21, E24, E27, E30, E33, E52, E80 |

#### Notable Patterns:
Fungus Farm building cost calculator with 8-term additions for total cost computation.

---

## Sheet: Time Machine
**Total Formulas:** 16
**Formula Families:** `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B104 | `=H18+H67+H99+H21+H24+H30+H39+H45` | Additive combination | H18, H21, H24, H30, H39, H45, H67, H99 |
| B105 | `=I18+I67+I99+I21+I24+I30+I39+I45` | Additive combination | I18, I21, I24, I30, I39, I45, I67, I99 |

#### Notable Patterns:
Time Machine building cost calculator adding component costs for total investment.

---

## Sheet: Quantum Amp
**Total Formulas:** 16
**Formula Families:** `=sum(X:X)` (350), `=X+X+X` (98), `=X+X+X+X+X` (10)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| D40 | `=D30+D32+D34+D36+D38` | Additive combination | D30, D32, D34, D36, D38 |
| F40 | `=F30+F32+F34+F36+F38` | Additive combination | F30, F32, F34, F36, F38 |

#### Notable Patterns:
Quantum Amp upgrade calculator summing category costs into grand totals.

---

## Sheet: Quarry
**Total Formulas:** 15
**Formula Families:** `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B83 | `=D16+D27+D52+D80+D21+D33+D24+D30` | Additive combination | D16, D21, D24, D27, D30, D33, D52, D80 |
| B84 | `=E16+E27+E52+E80+E21+E33+E24+E30` | Additive combination | E16, E21, E24, E27, E30, E33, E52, E80 |

#### Notable Patterns:
Quarry building cost calculator with multi-term additions for total cost tracking.

---

## Sheet: Partner Research Costs
**Total Formulas:** 14
**Formula Families:** `=IF(X<=X,0,SUM(OFFSET(X,X+1,0,X-X))*IF(X=X,0.5,1))` (6)
**Cross-sheet References:** None
**Error Flags:** Uses volatile OFFSET functions (performance impact)

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B9 | `=IF(B8<=B7,0,SUM(OFFSET($B$75,B7+1,0,B8-B7))*IF(B6=$B$4,0.5,1))` | Volatile dynamic range sum *(Repeated 6x across sheet)* | B4, B6, B7, B75, B8 |
| B7 | `=VLOOKUP($B$3,$A$23:$H$51,2,FALSE)` | Lookup value from table *(Repeated 9x across sheet)* | B3 |
| E7 | `=VLOOKUP($B$3,$A$23:$H$51,5,FALSE)` | Lookup value from table | B3 |

#### Notable Patterns:
Partner research cost calculator using VLOOKUPs for tier lookups and OFFSET-based conditional sums with IF-based range validation.

---

## Sheet: Lumber Camp
**Total Formulas:** 13
**Formula Families:** `=X+X+X` (98), `=X+X+X+X+X+X+X+X` (47)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B83 | `=D16+D27+D52+D80+D21+D33+D24+D30` | Additive combination | D16, D21, D24, D27, D30, D33, D52, D80 |
| B84 | `=E16+E27+E52+E80+E21+E33+E24+E30` | Additive combination | E16, E21, E24, E27, E30, E33, E52, E80 |

#### Notable Patterns:
Lumber Camp building cost calculator summing individual building costs.

---

## Sheet: Leadership
**Total Formulas:** 12
**Formula Families:** `=sum(X:X)` (350)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B3 | `=sum(B5:B12)` | Sum range of cells | B12, B5 |
| B4 | `=sum(B13:B20)` | Sum range of cells | B13, B20 |
| D3 | `=sum(D5:D12)` | Sum range of cells | D12, D5 |
| D4 | `=sum(D13:D20)` | Sum range of cells | D13, D20 |

#### Notable Patterns:
Leadership stat aggregator computing totals from multiple sub-categories.

---

## Sheet: Lottery
**Total Formulas:** 12
**Formula Families:** `=sum(X:X)` (350), `=X+X+X` (98), `=X+X+X+X+X` (10)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B24 | `=sum(B14:B23)` | Sum range of cells | B14, B23 |
| B28 | `=B24+B25+B26+B27` | Additive combination | B24, B25, B26, B27 |

#### Notable Patterns:
Lottery reward calculator summing reward values across categories.

---

## Sheet: Offering Speed
**Total Formulas:** 11
**Formula Families:** `=X-X` (704), `=SUM(X:X)` (233), `=X/(1+X/100)` (11), `=X/24` (14)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| D9 | `=SUM(D2:E8)` | Sum range of cells | D2, E8 |
| D37 | `=SUM(D24:E36)` | Sum range of cells | D24, E36 |
| B40 | `=D9+D12+D37+D21+D15+D18` | Additive combination | D12, D15, D18, D21, D37, D9 |
| B47 | `=48*4 + 8*4` | Compound calculation | None |
| B48 | `=B46-B47` | Difference/subtraction | B46, B47 |
| C43 | `=$B43/(1+$B$40/100)` | Apply percentage divisor | B40, B43 |
| B49 | `=B48/24` | Convert to per-hour rate | B48 |

#### Notable Patterns:
Offering speed calculator computing base speed, applying (1 + bonus/100) divisors, and converting to per-second rates.

---

## Sheet: Rift Anecdotes
**Total Formulas:** 11
**Formula Families:** `=X` (596)
**Cross-sheet References:** None
**Error Flags:** None identified

#### Representative Formulas:

| Cell | Formula | Description | Dependencies |
|------|---------|-------------|--------------|
| B31 | `=B12+B22+B26+B27` | Additive combination | B12, B22, B26, B27 |
| B42 | `=B35+B36+B37+B38+B39+B40+B41` | Additive combination | B35, B36, B37, B38, B39, B40, B41 |
| B54 | `=B43+B45+B46+B47+B48+B50+B49+B51+B53+B44+B52` | Additive combination | B43, B44, B45, B46, B47, B48, B49, B50, B51, B52, B53 |

#### Notable Patterns:
Rift anecdote data sheet with lookup formulas referencing story content ranges.

---

## Sheets Without Formulas

The following sheets contain no formulas and are used purely as data/lookup tables:

- **Lotto2 Expanded Stock** — Static reference data sheet
- **Lotto3 Expanded Stock** — Static reference data sheet
- **Useful Awakenings** — Static reference data sheet
- **Drifter Priority** — Static reference data sheet

---

## Audit Summary

- **VLOOKUPs without IFERROR:** 412
- **Volatile OFFSET formulas:** 246
- **Nested IFs:** 24
- **Single-cell SUMs:** 2
- **Circular References:** 0
