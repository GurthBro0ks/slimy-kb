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
