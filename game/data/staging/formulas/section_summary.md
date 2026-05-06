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
