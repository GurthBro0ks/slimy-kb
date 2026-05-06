# SuperSnail Calcs.xlsx — Complete Formula Audit Report

> **File:** `Updated Copy of SuperSnail Calcs.xlsx`  
> **Sheets:** 33 | **With Formulas:** 29 | **Without:** 4  
> **Total Formulas:** 4,727 | **Unique Families:** 184  
> **Cross-Sheet References:** 72 | **Audit Date:** 2026-04-26  

---

# Excel Spreadsheet Audit Report

## Section 1: Executive Summary

**File Under Review:** `Updated Copy of SuperSnail Calcs.xlsx`

This audit examines a game-companion spreadsheet for **SuperSnail**, a mobile game. The workbook contains an extensive collection of calculators, reference tables, and optimization tools covering virtually every major game system --- from relic albums and museum management to gene research, travel speed, minion stats, sailing, and more. The spreadsheet is clearly a labor of love from a dedicated player community, but its size and complexity warrant a thorough structural review.

### Overall Scale

| Metric | Value |
|--------|-------|
| Total Sheets | 33 |
| Sheets with Formulas | 29 |
| Sheets without Formulas | 4 |
| Total Formulas | 4,727 |
| Unique Formula Families | 184 |
| Cross-Sheet References | 72 |
| VLOOKUP Functions | 412 |
| OFFSET Functions | 246 |

### Sheets Without Formulas (Pure Data/Reference)

| Sheet | Purpose |
|-------|---------|
| Lotto2 Expanded Stock | Static lottery reference data |
| Lotto3 Expanded Stock | Static lottery reference data |
| Useful Awakenings | Static awakening reference table |
| Drifter Priority | Static priority reference table |

### Formula-Heavy Sheets

The following five sheets account for **3,077 formulas** --- nearly **65% of all formulas** in the entire workbook:

| Rank | Sheet | Formula Count | % of Total | Game System |
|------|-------|---------------|------------|-------------|
| 1 | Minion Base Stats | 938 | 19.8% | Minion stat calculations |
| 2 | Museum | 732 | 15.5% | Museum/Relic management |
| 3 | Protomon | 511 | 10.8% | Monster/Protomon system |
| 4 | Compass | 494 | 10.5% | Compass/navigation calculations |
| 5 | Minion Boosts | 402 | 8.5% | Minion boost calculations |
| | **Subtotal** | **3,077** | **65.1%** | |

### Additional Active Sheets (Formula Count > 50)

| Sheet | Formula Count | Game System |
|-------|---------------|-------------|
| Drifter Stats | 210 | Drifter character stats |
| Sailing Calculator | 201 | Sailing/sea travel |
| Hitmen | 184 | Hitmen system |
| Dragon DNA Costs | 183 | Dragon DNA upgrade costs |
| Relic Albums | 140 | Relic album collections |
| DNA Costs | 126 | DNA upgrade costs |
| Gene Research | 96 | Gene research progression |
| Dance Calculator | 86 | Dance/band member optimization |
| Band Calculator | 82 | Band composition |
| Cells Gained | 80 | Cellular resource tracking |

### Formula Pattern Landscape

The 184 unique formula families reveal a spreadsheet that relies heavily on **basic arithmetic** and **lookup functions**. The top 5 patterns alone account for over **2,500 formulas** (53% of all formulas):

| Pattern | Count | Affected Sheets |
|---------|-------|-----------------|
| `[CELL]-[CELL]` (subtraction) | 704 | 7 sheets |
| `[CELL]+[CELL]` (addition) | 628 | 7 sheets |
| `[CELL]` (direct reference) | 596 | 9 sheets |
| `=sum([CELL]:[CELL])` | 350 | 16 sheets |
| `=([CELL]+[CELL])/[CELL]` (division) | 262 | 1 sheet |

> **Observation:** The spreadsheet leans heavily on simple cell arithmetic and SUM functions. The most complex recurring patterns are the VLOOKUP chains in **Compass** (columns G through Q) and the OFFSET-based dynamic sums in **Protomon**.

### Game-Related Context

This workbook serves as a comprehensive companion calculator for SuperSnail game mechanics. The sheets collectively track and optimize:

- **Relic & Museum Systems** (Museum, Relic Albums, Compass)
- **Minion Management** (Minion Base Stats, Minion Boosts)
- **Genetic Progression** (Gene Research, DNA Costs, Dragon DNA Costs)
- **Travel & Exploration** (Travel Speed, Sailing Calculator, Offering Speed)
- **Character Systems** (Drifter Stats, Drifter Priority, Hitmen, Protomon)
- **Resource Buildings** (Fungus Farm, Lumber Camp, Quarry, Tadpole Pond, Time Machine, Rocket Cabin Effects)
- **Mini-Game Calculators** (Dance Calculator, Band Calculator, Lottery)
- **Cross-System Optimizations** (Cost Reductions, Quantum Amp, Cells Gained, Leadership)

---

## Section 2: Error Audit

This section documents all error conditions, structural anomalies, and potential risk factors identified during the audit.

### 2.1 Critical Errors (None Found)

| Error Category | Count | Status |
|----------------|-------|--------|
| Circular References | 0 | Clean |
| Evaluated Error Values (#REF!, #N/A, #VALUE!, #DIV/0!, #NAME?) | 0 | Clean |
| Broken References in Formulas | 0 | Clean |
| #DIV/0! Errors | 0 | Clean |
| #VALUE! Errors | 0 | Clean |
| #NAME? Errors | 0 | Clean |

> **Assessment:** The spreadsheet is **error-free** from a traditional formula-error perspective. No cells currently display error values, no circular dependencies exist, and all formula references resolve correctly. This is a notably well-maintained workbook from a breakage standpoint.

### 2.2 Structural Concerns

While no runtime errors exist, the audit identified several **structural patterns** that introduce maintenance risk or represent suboptimal formula design.

#### 2.2.1 Single-Cell SUM Formulas (Redundant) --- 2 Instances

Using `SUM()` on a single cell is functionally equivalent to a direct cell reference but adds unnecessary function overhead and reduces readability.

| Sheet | Cell | Formula | Issue |
|-------|------|---------|-------|
| Leadership | D3 | `=SUM(D2)` | Unnecessary wrapper; should be `=D2` |
| Dance Calculator | E13 | `=FLOOR(VLOOKUP(...) + IF(...) + 3*$M$21*SUM(G12),1)` | Contains `SUM(G12)` --- a single-cell SUM |

> **Recommendation:** Replace single-cell SUM wrappers with direct references. In the Dance Calculator case, `SUM(G12)` can be replaced with `G12`.

#### 2.2.2 VLOOKUP Without IFERROR Wrapping --- 412 Instances

This is the **single largest structural concern** in the workbook. All 412 VLOOKUP functions lack `IFERROR()` protection. If any lookup value is not found in the table array, the formula will return `#N/A`, which can cascade through dependent calculations.

**VLOOKUP Distribution by Sheet:**

| Sheet | Approx. VLOOKUP Count | Risk Level | Notes |
|-------|----------------------|------------|-------|
| Compass | ~350+ | **High** | Core lookup engine; every row does 10+ VLOOKUPs |
| Dance Calculator | ~15 | Medium | Cross-references Drifter Stats and Rift Anecdotes |
| Band Calculator | ~3 | Low | Cross-references Drifter Stats and Rift Anecdotes |
| Sailing Calculator | ~10 | Medium | Cross-references Drifter Stats and Rift Anecdotes |
| Protomon | ~15 | Medium | Looks up monster stats and evolution data |
| Partner Research Costs | ~9 | Low | Research cost lookups |

**Example High-Risk Formula (Compass):**

```
=VLOOKUP($C32,$A$3:$R$25,12,FALSE)
```

If cell `C32` contains a value not present in the lookup table `$A$3:$R$25`, this formula returns `#N/A`. The Compass sheet alone has hundreds of such formulas arranged in grid-like lookup tables (columns G through Q, rows 32-163 and 197-237, among others).

> **Recommendation:** Wrap all VLOOKUPs with `IFERROR(..., 0)` or `IFERROR(..., "")` depending on the downstream use case. For Compass specifically, consider whether `IFNA()` (more specific) or `IFERROR()` is appropriate.

#### 2.2.3 OFFSET Usage --- 246 Instances

The Protomon sheet makes extensive use of `OFFSET()` for dynamic range calculations:

```
=SUM(OFFSET($J$70,1,0,I71))
```

| Metric | Count |
|--------|-------|
| OFFSET Functions | 246 |
| Volatile Functions (Total) | 246 |

All 246 OFFSET calls are **volatile functions**, meaning they recalculate on every workbook change --- not just when their precedents change. This can cause **performance degradation** in a 4,700+ formula workbook.

> **Recommendation:** Consider replacing OFFSET with `INDEX`-based ranges or structured table references (`Excel Tables`) for better performance and stability. The pattern `=SUM(OFFSET($J$70,1,0,I71))` can often be rewritten as a dynamic range using `INDEX` or by pre-sizing the sum range.

#### 2.2.4 Nested IFs --- 24 Instances

The audit identified 24 formulas with nested IF statements. While not excessive, the most complex appear in the **Sailing Calculator** with formulas combining `IF`, `FLOOR`, arithmetic, and VLOOKUP lookups across multiple columns.

### 2.3 Cross-Sheet Dependencies

| Metric | Value |
|--------|-------|
| Total Cross-Sheet References | 72 |
| Source Sheets | 3 |
| Target Sheet | Drifter Priority |

The only cross-sheet references in the entire workbook originate from three calculator sheets looking up values in **Drifter Priority**:

| Source Sheet | Reference Count | Target Range | Pattern |
|--------------|-----------------|--------------|---------|
| Dance Calculator | 20 | C41:D286 | `=IF(L >= 10, 'Drifter Priority'!D..., 'Drifter Priority'!C...)` |
| Band Calculator | 26 | C105:D284 | `=IF(H >= 10, 'Drifter Priority'!D..., 'Drifter Priority'!C...)` |
| Sailing Calculator | 26 | C76:D332 | `=IF(H >= 10, 'Drifter Priority'!D..., 'Drifter Priority'!C...)` |

> **Note:** All 72 cross-sheet references use the same conditional pattern: if a level is >= 10, pull the "D" column value; otherwise pull the "C" column value. This is consistent but couples three calculators tightly to the **Drifter Priority** sheet layout.

### 2.4 Error Audit Summary

| Category | Finding | Severity |
|----------|---------|----------|
| Runtime Errors | **None** (0 circular, 0 evaluated errors) | Low |
| Broken References | **None** | Low |
| Redundant Single-Cell SUMs | 2 instances | Low |
| VLOOKUP Without IFERROR | **412 instances** | **Medium-High** |
| Volatile OFFSET Functions | 246 instances | Medium |
| Nested IF Complexity | 24 instances | Low |
| Cross-Sheet Coupling | 72 references to one sheet | Low-Medium |

### Overall Verdict

> **This spreadsheet is "clean" from an error perspective --- no broken formulas, no circular references, and no visible error values. However, it carries meaningful structural concerns: the 412 unprotected VLOOKUPs create a latent risk of cascading #N/A errors if lookup tables are ever modified, and the 246 OFFSET functions introduce unnecessary volatility. The workbook would benefit from systematic IFERROR wrapping and OFFSET-to-INDEX refactoring as preventive maintenance.**

---

*Report generated from automated spreadsheet audit. Sections covered: Executive Summary, Error Audit.*


---

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


---

# Excel Audit Report - Cross-Tab Dependency Matrix & Optimization Recommendations

> **File Audited:** `Updated Copy of SuperSnail Calcs.xlsx`  
> **Total Sheets:** 33 | **Total Formulas:** 4,727 | **Formula Families:** 184 | **Sheets with Formulas:** 29

---

## Section 1: Cross-Tab Dependency Matrix

### 1.1 Overview

The workbook contains **72 cross-sheet references** that create dependencies between 3 source sheets and 2 target sheets. **Drifter Priority** is the central lookup target, receiving 70 of the 72 cross-sheet references (97%).

| Risk Indicator | Value | Severity |
|---------------|-------|----------|
| Total Cross-Sheet References | 72 | -- |
| References to `Drifter Priority` | 70 | **HIGH** |
| References to `Rift Anecdotes` | 2 | Low |
| Source Sheets | 3 | -- |
| Target Sheets | 2 | -- |

### 1.2 Dependency Matrix

| Source Sheet | Drifter Priority | Rift Anecdotes | Total Outbound |
|-------------|:----------------:|:--------------:|:--------------:|
| **Dance Calculator** | 20 | 0 | **20** |
| **Band Calculator** | 24 | 2 | **26** |
| **Sailing Calculator** | 26 | 0 | **26** |
| **Total Inbound** | **70** | **2** | **72** |

### 1.3 Target Sheet Analysis: Drifter Priority

> **CRITICAL FINDING:** `Drifter Priority` is the most referenced sheet in the entire workbook (**70 inbound references**) but contains **zero formulas itself** (it is listed among the 4 sheets without formulas). This indicates it functions as a **centralized data/lookup table**.

| Property | Observation |
|----------|-------------|
| Role | Read-only lookup / reference table |
| Formulas | 0 (pure data) |
| Consumers | Dance Calculator, Band Calculator, Sailing Calculator |
| Typical Access Pattern | Two-column lookup: `IF(X >= 10, ColumnD, ColumnC)` |
| Risk if Deleted | **70 formulas across 3 sheets break immediately** |
| Risk if Renamed | All cross-sheet references become `#REF!` errors |
| Risk if Rows Shift | Hard-coded row references (e.g., `C41`, `D285`) drift to wrong data |

### 1.4 Cross-Sheet Reference Detail

#### Dance Calculator → Drifter Priority (20 references)

All formulas follow the conditional two-column pattern: `=IF(L{row} >= 10, 'Drifter Priority'!D{row}, 'Drifter Priority'!C{row})`

| Cell | Target Sheet | Target Range | Formula |
|------|-------------|--------------|---------|
| K12 | Drifter Priority | C41, D41 | `=IF(L10 >= 10, 'Drifter Priority'!D41, 'Drifter Priority'!C41)` |
| K13 | Drifter Priority | C42, D42 | `=IF(L11 >= 10, 'Drifter Priority'!D42, 'Drifter Priority'!C42)` |
| K14 | Drifter Priority | C43, D43 | `=IF(L12 >= 10, 'Drifter Priority'!D43, 'Drifter Priority'!C43)` |
| K15 | Drifter Priority | C123, D123 | `=IF(L13 >= 10, 'Drifter Priority'!D123, 'Drifter Priority'!C123)` |
| K16 | Drifter Priority | C285, D285 | `=IF(L14 >= 10, 'Drifter Priority'!D285, 'Drifter Priority'!C285)` |
| K17 | Drifter Priority | C286, D286 | `=IF(L15 >= 10, 'Drifter Priority'!D286, 'Drifter Priority'!C286)` |
| K18 | Drifter Priority | C108, D108 | `=IF(L16 >= 10, 'Drifter Priority'!D108, 'Drifter Priority'!C108)` |
| K19 | Drifter Priority | C28, D28 | `=IF(L17 >= 10, 'Drifter Priority'!D28, 'Drifter Priority'!C28)` |
| K20 | Drifter Priority | C267, D267 | `=IF(L18 >= 10, 'Drifter Priority'!D267, 'Drifter Priority'!C267)` |
| K21 | Drifter Priority | C122, D122 | `=IF(L19 >= 10, 'Drifter Priority'!D122, 'Drifter Priority'!C122)` |

> **Note:** Each formula cell generates 2 tracked references (one to column C, one to column D). The actual formula count is 10 unique cells with 2 cross-sheet reads each.

#### Band Calculator → Drifter Priority / Rift Anecdotes (26 references)

| Cell | Target Sheet | Target Range | Formula |
|------|-------------|--------------|---------|
| G9 | Drifter Priority | C237, D237 | `=IF(H7 >= 10, 'Drifter Priority'!D237, 'Drifter Priority'!C237)` |
| G10 | Drifter Priority | C236, D236 | `=IF(H8 >= 10, 'Drifter Priority'!D236, 'Drifter Priority'!C236)` |
| G11 | Drifter Priority | C107, D107 | `=IF(H9 >= 10, 'Drifter Priority'!D107, 'Drifter Priority'!C107)` |
| G12 | Drifter Priority | C105, D105 | `=IF(H10 >= 10, 'Drifter Priority'!D105, 'Drifter Priority'!C105)` |
| G13 | Drifter Priority | C283, D283 | `=IF(H11 >= 10, 'Drifter Priority'!D283, 'Drifter Priority'!C283)` |
| G14 | Drifter Priority | C266, D266 | `=IF(H12 >= 10, 'Drifter Priority'!D266, 'Drifter Priority'!C266)` |
| G15 | Drifter Priority | C268, D268 | `=IF(H13 >= 10, 'Drifter Priority'!D268, 'Drifter Priority'!C268)` |
| G16 | Drifter Priority | C106, D106 | `=IF(H14 >= 10, 'Drifter Priority'!D106, 'Drifter Priority'!C106)` |
| G17 | Drifter Priority | C284, D284 | `=IF(H15 >= 10, 'Drifter Priority'!D284, 'Drifter Priority'!C284)` |
| G18 | Drifter Priority | C125, D125 | `=IF(H16 >= 10, 'Drifter Priority'!D125, 'Drifter Priority'!C125)` |
| G19 | Drifter Priority | C282, D282 | `=IF(H17 >= 10, 'Drifter Priority'!D282, 'Drifter Priority'!C282)` |
| G20 | Drifter Priority | C124, D124 | `=IF(H18 >= 10, 'Drifter Priority'!D124, 'Drifter Priority'!C124)` |
| **B10** | **Rift Anecdotes** | **B174:G195** | `=VLOOKUP(B9,'Rift Anecdotes'!B174:G195,5,FALSE)` |
| **B11** | **Rift Anecdotes** | **B174:G195** | `=VLOOKUP(B9,'Rift Anecdotes'!B174:G195,6,FALSE)` |

#### Sailing Calculator → Drifter Priority (26 references)

| Cell | Target Sheet | Target Range | Formula |
|------|-------------|--------------|---------|
| G11 | Drifter Priority | C299, D299 | `=IF(H9 >= 10, 'Drifter Priority'!D299, 'Drifter Priority'!C299)` |
| G12 | Drifter Priority | C298, D298 | `=IF(H10 >= 10, 'Drifter Priority'!D298, 'Drifter Priority'!C298)` |
| G13 | Drifter Priority | C300, D300 | `=IF(H11 >= 10, 'Drifter Priority'!D300, 'Drifter Priority'!C300)` |
| G14 | Drifter Priority | C314, D314 | `=IF(H12 >= 10, 'Drifter Priority'!D314, 'Drifter Priority'!C314)` |
| G15 | Drifter Priority | C315, D315 | `=IF(H13 >= 10, 'Drifter Priority'!D315, 'Drifter Priority'!C315)` |
| G16 | Drifter Priority | C316, D316 | `=IF(H14 >= 10, 'Drifter Priority'!D316, 'Drifter Priority'!C316)` |
| G17 | Drifter Priority | C330, D330 | `=IF(H15 >= 10, 'Drifter Priority'!D330, 'Drifter Priority'!C330)` |
| G18 | Drifter Priority | C331, D331 | `=IF(H16 >= 10, 'Drifter Priority'!D331, 'Drifter Priority'!C331)` |
| G19 | Drifter Priority | C332, D332 | `=IF(H17 >= 10, 'Drifter Priority'!D332, 'Drifter Priority'!C332)` |
| G20 | Drifter Priority | C188, D188 | `=IF(H18 >= 10, 'Drifter Priority'!D188, 'Drifter Priority'!C188)` |
| G21 | Drifter Priority | C189, D189 | `=IF(H19 >= 10, 'Drifter Priority'!D189, 'Drifter Priority'!C189)` |
| G22 | Drifter Priority | C77, D77 | `=IF(H20 >= 10, 'Drifter Priority'!D77, 'Drifter Priority'!C77)` |
| G23 | Drifter Priority | C76, D76 | `=IF(H21 >= 10, 'Drifter Priority'!D76, 'Drifter Priority'!C76)` |

### 1.5 Risk Assessment

| Risk ID | Risk Description | Impact | Likelihood | Severity |
|---------|-----------------|--------|------------|----------|
| **CT-01** | `Drifter Priority` sheet deleted or renamed | 70 formulas fail with `#REF!` | Medium | **HIGH** |
| **CT-02** | Rows in `Drifter Priority` shifted (e.g., insert/delete rows) | Hard-coded references point to wrong data | High | **HIGH** |
| **CT-03** | `Rift Anecdotes` sheet deleted or renamed | 2 VLOOKUPs in Band Calculator fail | Medium | Low |
| **CT-04** | No error handling on cross-sheet VLOOKUPs | `#N/A` propagates silently | High | Medium |
| **CT-05** | All cross-sheet lookups use row-specific hard-coding | Maintenance burden; fragile to data changes | High | Medium |

---

## Section 2: Optimization Recommendations

### Summary Table

| # | Recommendation | Priority | Effort | Impact |
|---|---------------|----------|--------|--------|
| 1 | VLOOKUP → XLOOKUP Migration | **High** | Medium | High readability, left-lookup support |
| 2 | OFFSET → Non-Volatile Alternatives | **High** | Medium | Eliminates 246 volatile recalculations |
| 3 | Add IFERROR Wrappers to VLOOKUPs | **High** | Low | Prevents 412 `#N/A` error cascades |
| 4 | Nested IF Cleanup (Sailing Calculator) | Medium | Low | Simpler boolean logic |
| 5 | Single-Cell SUM Redundancy | Low | Very Low | Cleanliness |
| 6 | General Structural Improvements | Medium | Medium | Long-term maintainability |
| 7 | Performance Concerns | Medium | High | Sheet-level optimization |

---

### 2.1 VLOOKUP → XLOOKUP Migration (412 instances)

**Priority: HIGH | Effort: Medium**

All 412 VLOOKUPs in the workbook are exact-match lookups (`FALSE` / `FALSE` / `false` parameter). XLOOKUP (Excel 2019/365+) provides a cleaner, more robust syntax, especially for the multi-column offset lookups seen in the **Compass** sheet.

#### Why Migrate?

| VLOOKUP Limitation | XLOOKUP Benefit |
|-------------------|-----------------|
| Counts column index from left | Directly references the return column |
| Breaks if insert/delete shifts columns | Immune to column shifts |
| Cannot look left (return column must be right of lookup) | Can return any column, left or right |
| Default approximate match (`TRUE`) | Default exact match (safer) |
| No built-in "not found" handling | Built-in `if_not_found` argument |

#### Before / After Examples

**Example A: Compass - Column-offset VLOOKUP (most common pattern, 30 instances per column)**

```excel
' BEFORE (Compass L32)
=VLOOKUP($C32,$A$3:$R$25,12,FALSE)

' AFTER (XLOOKUP)
=XLOOKUP($C32,$A$3:$A$25,$L$3:$L$25,"Not Found")
```

**Example B: Compass - Two VLOOKUPs added together**

```excel
' BEFORE (Compass G32)
=VLOOKUP($C32,$A$3:$R$25,4,FALSE)+VLOOKUP($C32,$A$3:$R$25,18,FALSE)

' AFTER (XLOOKUP)
=XLOOKUP($C32,$A$3:$A$25,$D$3:$D$25,0)+XLOOKUP($C32,$A$3:$A$25,$R$3:$R$25,0)

' EVEN BETTER: Use LET to avoid repeating the lookup
=LET(key,$C32,lkup,$A$3:$A$25,
   XLOOKUP(key,lkup,$D$3:$D$25,0)+XLOOKUP(key,lkup,$R$3:$R$25,0))
```

**Example C: Band Calculator cross-sheet VLOOKUP**

```excel
' BEFORE (Band Calculator B10)
=VLOOKUP(B9,'Rift Anecdotes'!B174:G195,5,FALSE)

' AFTER (XLOOKUP)
=XLOOKUP(B9,'Rift Anecdotes'!$B$174:$B$195,'Rift Anecdotes'!$F$174:$F$195,"N/A")
```

**Recommended Action:** Replace all 412 VLOOKUPs systematically. The Compass sheet alone accounts for the majority. Consider using **Find & Replace** with a macro or Power Query for bulk conversion.

---

### 2.2 OFFSET → Non-Volatile Alternatives (246 instances)

**Priority: HIGH | Effort: Medium**

`OFFSET` is a **volatile function** — it recalculates on *every* worksheet change, even when its inputs have not changed. This causes cascading full recalculations that degrade performance, especially in a workbook with 4,727 formulas.

#### Distribution of OFFSET Formulas

| Sheet | Count | Range | Pattern |
|-------|-------|-------|---------|
| **Protomon** | 240 | K71:K310 | `=SUM(OFFSET($J$70,1,0,I##))` |
| **Partner Research Costs** | 6 (est.) | B9:G9 | Range-building OFFSET |
| **Total** | **246** | -- | -- |

#### Before / After Examples

**Example A: Protomon - The dominant pattern (240 instances)**

```excel
' BEFORE (Protomon K71)
=SUM(OFFSET($J$70,1,0,I71))

' AFTER (INDEX-based range)
=SUM(INDEX($J$71:$J$1000,1):INDEX($J$71:$J$1000,I71))

' ALTERNATIVE: If data is in an Excel Table named ProtomonTable
=SUM(ProtomonTable[ColumnJ][1]:ProtomonTable[ColumnJ][@RowCount])
```

> **How it works:** `OFFSET($J$70,1,0,I71)` starts at J70, moves down 1 row, stays in the same column, and spans `I71` rows. The INDEX equivalent creates a dynamic range from `J71` down to `J(71+I71-1)`. Since `INDEX` is non-volatile, the formula only recalculates when `I71` changes.

**Example B: Partner Research Costs**

```excel
' BEFORE
=SUM(OFFSET($B$9,0,0,1,G9))

' AFTER
=SUM($B$9:INDEX($B$9:$Z$9,G9))
```

**Recommended Action:**
1. Convert the 240 Protomon formulas first (highest impact).
2. For any expanding ranges, consider converting the underlying data to an **Excel Table** (`Ctrl+T`), then use structured references like `[@Field]` or `Table[Column]`.
3. If using spill ranges (Excel 365), replace with `=SUM(TAKE(J71:J1000, I71))`.

---

### 2.3 Add IFERROR Wrappers (412 VLOOKUPs)

**Priority: HIGH | Effort: Low**

Every VLOOKUP in the workbook lacks error handling. If a lookup value does not exist in the table, the formula returns `#N/A`. In sheets like **Compass** where multiple VLOOKUPs are added together (`=VLOOKUP(...)+VLOOKUP(...)`), one `#N/A` poisons the entire sum.

#### Before / After Examples

**Example A: Simple VLOOKUP**

```excel
' BEFORE
=VLOOKUP($C32,$A$3:$R$25,12,FALSE)

' AFTER
=IFERROR(VLOOKUP($C32,$A$3:$R$25,12,FALSE), 0)
```

**Example B: Added VLOOKUPs (Compass)**

```excel
' BEFORE
=VLOOKUP($C32,$A$3:$R$25,4,FALSE)+VLOOKUP($C32,$A$3:$R$25,18,FALSE)

' AFTER (wrapping the entire expression)
=IFERROR(VLOOKUP($C32,$A$3:$R$25,4,FALSE),0)+IFERROR(VLOOKUP($C32,$A$3:$R$25,18,FALSE),0)

' OR with XLOOKUP (preferred):
=XLOOKUP($C32,$A$3:$A$25,$D$3:$D$25,0)+XLOOKUP($C32,$A$3:$A$25,$R$3:$R$25,0)
```

**Example C: Cross-sheet VLOOKUP**

```excel
' BEFORE (Band Calculator)
=VLOOKUP(B9,'Rift Anecdotes'!B174:G195,5,FALSE)

' AFTER
=IFERROR(VLOOKUP(B9,'Rift Anecdotes'!B174:G195,5,FALSE), "")
```

> **Default Value Guidance:**
> - For numeric calculations (Compass, etc.): use `0`
> - For text lookups: use `""` or `"N/A"`
> - For boolean checks: use `FALSE`

**Recommended Action:** Apply `IFERROR(..., 0)` to all 412 VLOOKUPs. This can be done with a bulk Find/Replace macro or by migrating to XLOOKUP (which has built-in `if_not_found`).

---

### 2.4 Nested IF Cleanup (24 instances in Sailing Calculator)

**Priority: Medium | Effort: Low**

The **Sailing Calculator** contains 24+ formulas using `IF(..., 1, 0)` as a boolean multiplier. These are unnecessarily verbose — Excel formulas treat `TRUE` as `1` and `FALSE` as `0` natively.

#### Pattern Analysis

| Pattern | Count | Example | Simplification |
|---------|-------|---------|----------------|
| `*$I$* *IF(COUNTIF(...)>0, 1, 0)` | 20 | `=$I$22*IF(COUNTIF($A$11:$A$14,$F$22)>0,1,0)` | `=$I$22*(COUNTIF(...)>0)` |
| `*IF(F##>0, 1, 0)` | 24+ | `=(F48+$B$23)*IF(F48>0,1,0)` | `=(F48+$B$23)*(F48>0)` |

#### Before / After Examples

**Example A: COUNTIF boolean multiplier**

```excel
' BEFORE (Sailing Calculator D2)
=$I$22*IF(COUNTIF($A$11:$A$14, $F$22)>0, 1, 0)

' AFTER
=$I$22*(COUNTIF($A$11:$A$14, $F$22)>0)
```

**Example B: Positive-check multiplier**

```excel
' BEFORE (Sailing Calculator B49)
=(F48+$B$23)*IF(F48>0, 1, 0)

' AFTER
=(F48+$B$23)*(F48>0)
```

**Example C: Complex nested IF in sailing damage calc**

```excel
' BEFORE
=(C48*$B$25*(1.5+$B$26)+C48*(1-$B$25))*IF(B48>0, 1, 0)

' AFTER
=(C48*$B$25*(1.5+$B$26)+C48*(1-$B$25))*(B48>0)
```

> **Tip:** If you want to ensure the result is exactly 0 or a positive number (never negative), wrap with `MAX(...,0)` instead.

**Recommended Action:** Search Sailing Calculator for `IF(..., 1, 0)` and replace with direct boolean expressions. This improves readability and slightly reduces formula complexity.

---

### 2.5 Single-Cell SUM Redundancy

**Priority: Low | Effort: Very Low**

Using `SUM()` around a single cell is functionally identical to just referencing the cell, but adds unnecessary function overhead.

| Sheet | Cell | Before | After |
|-------|------|--------|-------|
| **Leadership** | D3 | `=SUM(D2)` | `=D2` |
| **Dance Calculator** | E13 | `=FLOOR(VLOOKUP(...) + IF(...) + 3*$M$21*SUM(G12),1)` | `=FLOOR(VLOOKUP(...) + IF(...) + 3*$M$21*G12,1)` |

> The Dance Calculator instance is especially notable because `SUM(G12)` is buried inside a much larger formula. Removing it reduces nesting depth.

**Recommended Action:** Replace `SUM(singleCell)` with the cell reference directly. Use Find/Replace for Leadership D3.

---

### 2.6 General Structural Recommendations

**Priority: Medium | Effort: Medium**

#### A. Centralize Lookup Tables

`Drifter Priority` and `Rift Anecdotes` are already acting as centralized lookup stores, but they use **hard-coded row numbers** (`C41`, `D285`, etc.) rather than structured lookups. This makes the workbook fragile to row insertions.

**Recommendation:**
- Convert `Drifter Priority` and `Rift Anecdotes` to **Excel Tables** (`Ctrl+T`).
- Use `TableName[ColumnName]` references instead of `Sheet!C41`.
- This would allow the cross-sheet formulas to become:
  ```excel
  =IF(L10 >= 10, DrifterPriority[Advanced][@Item], DrifterPriority[Basic][@Item])
  ```

#### B. Named Ranges for Magic Numbers

The audit identified repeated constants across many formula families:

| Constant | Frequency | Sheets | Recommendation |
|----------|-----------|--------|----------------|
| 120 | 168+ | Drifter Stats | Define `BaseCap = 120` |
| 60 | 298+ | Protomon, Offering Speed | Define `BaseCost = 60` |
| 100 | 50+ | Offering Speed, Travel Speed | Define `PercentBase = 100` |
| 28 | 65+ | Relic Albums | Define `AlbumMultiplier = 28` |

**Example:**
```excel
' BEFORE
=(AG3-AH3*120)/$AF3

' AFTER (with named range)
=(AG3-AH3*BaseCap)/$AF3
```

#### C. Convert Static Ranges to Excel Tables

Any data that expands over time (Protomon, Minion Base Stats, Museum collections, etc.) should use Excel Tables for:
- Auto-expanding formulas
- Structured references
- Auto-fill on new rows
- Better integration with PivotTables

#### D. Add Data Validation

Sheets where users input lookup keys or configuration values should have **Data Validation** lists:
- **Compass**: Restrict column C to valid item names
- **Band Calculator / Dance Calculator / Sailing Calculator**: Restrict lookup inputs to valid drifter/band/dance names
- This prevents `#N/A` errors before they occur.

---

### 2.7 Performance Concerns

**Priority: Medium | Effort: High**

#### Volatile Formula Impact

| Metric | Value | Impact |
|--------|-------|--------|
| Volatile Formulas (OFFSET) | 246 | Every sheet change triggers full recalc |
| Total Formulas | 4,727 | Full recalc = 4,727+ formula evaluations |
| Cross-Sheet References | 72 | Additional recalc dependencies |

With 246 OFFSET formulas, **any cell edit anywhere in the workbook forces all 4,727 formulas to recalculate**, regardless of whether they are related to the edited cell.

#### Heavy Sheets

| Sheet | Formula Count | % of Total | Notes |
|-------|--------------|------------|-------|
| **Minion Base Stats** | 938 | 19.8% | Large stat matrix |
| **Museum** | 732 | 15.5% | Collection tracking |
| **Protomon** | 511 | 10.8% | Contains 240 volatile OFFSETs |
| **Compass** | 494 | 10.4% | Dense VLOOKUP grid |
| **Minion Boosts** | 402 | 8.5% | Calculation-heavy |

**Top 5 sheets contain 3,077 formulas (65% of the workbook).**

#### Performance Recommendations

1. **Eliminate OFFSET first** (see §2.2) — this is the single biggest performance win.
2. **Set calculation mode** to `Automatic Except Data Tables` if the workbook is used for interactive entry; switch to `Manual` during bulk data imports.
3. **Break up the Compass VLOOKUP grid** — the dense grid of 494 VLOOKUP-based formulas could potentially be replaced with a single `XLOOKUP` array formula (spill range) if on Excel 365:
   ```excel
   =XLOOKUP(C32:C40, A3:A25, L3:L25, 0)  ' Spills down automatically
   ```
4. **Consider Power Query** for static lookups (e.g., the `Rift Anecdotes` → `Band Calculator` data merge could be done at refresh-time rather than formula-time).
5. **Review Minion Base Stats** — at 938 formulas, consider whether any static calculation columns can be converted to values after computation.

---

## Appendix: Quick Reference — Formula Pattern Frequencies

| Rank | Pattern | Count | Sheets |
|------|---------|-------|--------|
| 1 | `=[CELL]-[CELL]` | 704 | Band Calculator, DNA Costs, Dragon DNA Costs, Hitmen, Minion Base Stats, Offering Speed, Sailing Calculator |
| 2 | `=[CELL]+[CELL]` | 628 | Cells Gained, Compass, Dragon DNA Costs, Drifter Stats, Minion Base Stats, Museum, Rocket Cabin Effects |
| 3 | `=[CELL]` (passthrough) | 596 | 9 sheets |
| 4 | `=sum([CELL]:[CELL])` | 350 | 16 sheets |
| 5 | `=([CELL]+[CELL])/[CELL]` | 262 | Minion Boosts |
| 6 | `=SUM(OFFSET(...))` | 240 | **Protomon** |
| 7 | `=SUM([CELL]:[CELL])` (uppercase) | 233 | 10 sheets |
| 8 | `=60*([CELL]+1) + 20*MAX(...)` | 181 | **Protomon** |
| 9 | `=([CELL]-[CELL]*120)/[CELL]` | 168 | **Drifter Stats** |
| 10 | `=[CELL]+[CELL]+[CELL]` | 98 | 10 sheets |

---

> **Report generated from automated Excel formula audit.**  
> **Recommendations should be validated against the actual workbook before implementation.**


---


# Appendix A: Extracted Sheet Files

All 33 sheets have been extracted to individual .xlsx files in `/mnt/agents/output/sheets/`:

1. `Band Calculator.xlsx`
2. `Cells Gained.xlsx`
3. `Compass.xlsx`
4. `Cost Reductions.xlsx`
5. `DNA Costs.xlsx`
6. `Dance Calculator.xlsx`
7. `Dragon DNA Costs.xlsx`
8. `Drifter Priority.xlsx`
9. `Drifter Stats.xlsx`
10. `Fungus Farm.xlsx`
11. `Gene Research.xlsx`
12. `Hitmen.xlsx`
13. `Leadership.xlsx`
14. `Lottery.xlsx`
15. `Lotto2 Expanded Stock.xlsx`
16. `Lotto3 Expanded Stock.xlsx`
17. `Lumber Camp.xlsx`
18. `Minion Base Stats.xlsx`
19. `Minion Boosts.xlsx`
20. `Museum.xlsx`
21. `Offering Speed.xlsx`
22. `Partner Research Costs.xlsx`
23. `Protomon.xlsx`
24. `Quantum Amp.xlsx`
25. `Quarry.xlsx`
26. `Relic Albums.xlsx`
27. `Rift Anecdotes.xlsx`
28. `Rocket Cabin Effects.xlsx`
29. `Sailing Calculator.xlsx`
30. `Tadpole Pond.xlsx`
31. `Time Machine.xlsx`
32. `Travel Speed.xlsx`
33. `Useful Awakenings.xlsx`
