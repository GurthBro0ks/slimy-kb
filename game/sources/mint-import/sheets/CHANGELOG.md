# SuperSnail Calcs — Fix Changelog

## Fixed Workbook
**File:** `SuperSnail_Calcs_FIXED.xlsx`  
**Original:** `Updated Copy of SuperSnail Calcs.xlsx`  
**Total Changes:** 1,188 formula modifications  
**Date:** 2026-04-26

---

## Fix Summary by Category

| # | Fix Category | Count | Status |
|---|-------------|-------|--------|
| 1 | VLOOKUP wrapped with IFERROR | 412 | Complete |
| 2 | VLOOKUP migrated to XLOOKUP | 317 | Complete (95 remain as VLOOKUP + IFERROR) |
| 3 | OFFSET replaced with INDEX | 246 | Complete |
| 4 | Constant 120 centralized | 168 | Complete |
| 5 | Nested IF simplified | 24 | Complete |
| 6 | Constant 24 centralized | 14 | Complete |
| 7 | Constant 100 centralized | 5 | Complete |
| 8 | Single-cell SUM fixed | 2 | Complete |

---

## Detailed Fix Log

### 1. VLOOKUP → IFERROR Wrapping (412 formulas)

All 412 standalone VLOOKUP formulas now have error handling. If a lookup value is not found, the formula returns `0` instead of `#N/A`.

**Example:**
```excel
Before: =VLOOKUP($C32,$A$3:$R$25,4,FALSE)
After:  =IFERROR(VLOOKUP($C32,$A$3:$R$25,4,FALSE),0)
```

**Sheets affected:** Compass (494 formulas), Dance Calculator, Band Calculator, Partner Research Costs, Protomon, and others.

---

### 2. VLOOKUP → XLOOKUP Migration (317 formulas)

317 simple, standalone VLOOKUP formulas were modernized to XLOOKUP syntax. XLOOKUP is more robust, doesn't require column index counting, and has built-in default-value handling.

**Example:**
```excel
Before: =IFERROR(VLOOKUP(A2,'Drifter Stats'!$A$4:$Q$24,12,FALSE),0)
After:  =XLOOKUP(A2,'Drifter Stats'!$A$4:$A$24,'Drifter Stats'!$L$4:$L$24,0)
```

**95 VLOOKUPs intentionally preserved** because they:
- Contain multiple VLOOKUPs in a single formula (e.g., `VLOOKUP(...) + VLOOKUP(...)`)
- Use dynamic column indices (e.g., `IF(C13="Male",11,12)`)
- Are part of complex nested expressions where XLOOKUP syntax would be ambiguous

These remaining VLOOKUPs are all protected with IFERROR wrapping.

**Sheets affected:** Compass (590 fixes total), Partner Research Costs, Protomon, and others.

---

### 3. OFFSET → INDEX Replacement (246 formulas)

All volatile OFFSET formulas were replaced with non-volatile INDEX-based alternatives. This eliminates forced full-workbook recalculation on every edit.

**Protomon (240 formulas):**
```excel
Before: =SUM(OFFSET($J$70,1,0,I71))
After:  =SUM(J71:INDEX($J:$J,70+I71))
```

**Partner Research Costs (6 formulas):**
```excel
Before: =IF(B8<=B7,0,SUM(OFFSET($B$75,B7+1,0,B8-B7))*IF(B6=$B$4,0.5,1))
After:  =IF(B8<=B7,0,SUM(INDEX($B:$B,76+B7):INDEX($B:$B,75+B8))*IF(B6=$B$4,0.5,1))
```

---

### 4. Nested IF Simplification (24 formulas)

Sailing Calculator's boolean multipliers were simplified. The pattern `IF(COUNTIF(...)>0, 1, 0)` is redundant because `COUNTIF(...)>0` already returns TRUE/FALSE, which Excel treats as 1/0 in arithmetic.

**Example:**
```excel
Before: =$I$22*IF(COUNTIF($A$11:$A$14,$F$22)>0,1,0)
After:  =$I$22*(COUNTIF($A$11:$A$14,$F$22)>0)
```

**Double-nested case also simplified:**
```excel
Before: =I17*IF(COUNTIF(...)>0,1,0)*IF(COUNTIF(...)>0,1,0)
After:  =I17*(COUNTIF(...)>0)*(COUNTIF(...)>0)
```

---

### 5. Single-Cell SUM Redundancy (2 formulas)

```excel
Leadership!D3:    =SUM(D2)    →  =D2
Dance Calculator!E13: ...SUM(G12)... → ...G12...
```

---

### 6. Named Constants (187 formula updates)

Hardcoded magic numbers were centralized into reference cells.

| Constant | New Reference | Formulas Updated | Context |
|----------|---------------|------------------|---------|
| 120 | Drifter Stats!$AZ$1 | 168 | Max level cap in stat calculations |
| 100 | Offering Speed!$C$65 | 5 | Percentage base divisor |
| 24 | Offering Speed!$C$66 | 14 | Hours-per-day conversion |

**Constants Reference Table** added to Offering Speed!B60:D64:

| CONSTANT_NAME | VALUE | DESCRIPTION |
|--------------|-------|-------------|
| Max_Level_Cap | 120 | Used in Drifter Stats level calculations |
| Pct_Base | 100 | Percentage divisor (e.g., /100 for %) |
| Hours_Per_Day | 24 | Time conversion factor |
| Minutes_Per_Hour | 60 | Time conversion factor |

---

## Validation Results

| Audit Check | Before | After | Status |
|------------|--------|-------|--------|
| Circular References | 0 | 0 | Clean |
| #REF! / #N/A / #VALUE! | 0 | 0 | Clean |
| VLOOKUP without IFERROR | 412 | **0** | Fixed |
| OFFSET formulas | 246 | **0** | Fixed |
| Volatile functions | 246 | **0** | Fixed |
| Single-cell SUMs | 2 | **0** | Fixed |
| Nested IFs (Sailing) | 24 | **0** | Fixed |
| XLOOKUP formulas | 0 | **317** | New |
| Named constants used | 0 | **187** | New |

---

## Remaining VLOOKUPs (95 formulas)

These 95 formulas retain VLOOKUP because they have structural complexity that makes XLOOKUP migration risky:

| Pattern | Reason | Count |
|---------|--------|-------|
| Multiple VLOOKUPs in one formula | XLOOKUP syntax per-lookup is clear, but parent expression context matters | ~60 |
| Dynamic column index | Column chosen by IF/CHOOSE logic | ~25 |
| Non-standard VLOOKUP | Part of INDEX/MATCH or other complex patterns | ~10 |

All 95 remaining VLOOKUPs are wrapped with IFERROR for protection.

---

## Known Limitations & Manual Recommendations

1. **Named Constants (Remaining):** Only the top 3 constants (120, 100, 24) were centralized. Other frequent constants (50, 52.5, 60, 20) remain hardcoded. Apply the same `$AZ$1` pattern to complete.

2. **Data Validation:** Consider adding dropdown validation to input cells to prevent invalid lookup values.

3. **Sheet Protection:** `Drifter Priority` remains unprotected. Right-click → Protect Sheet to prevent accidental deletion (it has 70 inbound references).

4. **Excel Version:** XLOOKUP requires Excel 365/2021+. If sharing with users on older Excel, they will see `#NAME?` errors. The original file is preserved if needed.

---

*End of Changelog*
