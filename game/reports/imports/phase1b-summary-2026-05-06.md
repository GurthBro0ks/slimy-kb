# Phase 1B Import Summary

**Date:** 2026-05-06
**Project:** kb-game
**Scope:** Mint import inventory, OCR prompt extraction, source categorization

---

## Total Files Inventoried

| Source | Files | Size |
|--------|-------|------|
| mint-import (total) | 17,720 | 2.1 GB |
| mint-import (meaningful, excl. artifacts) | ~15,124 | ~1.8 GB |

### Top-Level Breakdown

| Directory | Files | Size | Description |
|-----------|-------|------|-------------|
| sheets/ | 50 | 4.5 MB | Calculation spreadsheets, formulas, audits |
| slimy_snail/ | 2,929 | 26 MB | Reverse engineering project |
| gnome_game/ | 14,735 | 104 MB | Unity game source + wiki exports |
| test photos/ | 0 | 4 KB | Empty |

---

## Files Staged by Category

### game/data/staging/ (51 files)

| Subdirectory | Files | Description |
|-------------|-------|-------------|
| formulas/ | 34 | Calculators, cost sheets, formula metadata, audit reports |
| forms/ | 2 | DNA Costs, Dragon DNA Costs |
| research/ | 2 | Gene Research, Partner Research Costs |
| relics/ | 2 | Museum, Relic Albums |
| unsorted/ | 1 | Rift Anecdotes (mixed content) |
| gear/ | 0 | No gear-specific spreadsheets found in mint-import |
| codes/ | 0 | No code-specific spreadsheets found |

### game/sources/ (4,196 files)

| Subdirectory | Files | Description |
|-------------|-------|-------------|
| ocr_prompts/ | 6 | Bot + Web OCR prompts and normalization rules |
| reverse_engineering/ | 72 | Scripts, docs, decoded data, captures, reports from slimy_snail |
| wiki_gg/ | 4,124 | Scraped wiki.gg page exports (4,124 .wiki files) |

### game/guides/ (2 files)

| File | Description |
|------|-------------|
| beginner/existing-web-beginners-guide.md | Extracted from /snail/wiki page.tsx |
| existing-web-docs-overview.md | Extracted from /snail/docs page.tsx |

---

## OCR Prompts Extracted (6 files)

| File | Source | Models |
|------|--------|--------|
| bot-roster-ocr-prompt.md | apps/bot/src/services/roster-ocr.ts | Gemini 2.5 Flash + Pro |
| bot-normalization-rules.md | apps/bot/src/lib/club-vision.ts, numparse.ts | N/A |
| web-profile-ocr-prompt.md | apps/web/app/api/snail/personal/ocr/route.ts | Gemini 2.5 Flash + GPT-4o |
| web-snailstats-ocr-prompt.md | apps/web/app/api/snail/personal/ocr/route.ts | Gemini 2.5 Flash + GPT-4o |
| web-troopstats-ocr-prompt.md | apps/web/app/api/snail/personal/ocr/route.ts | Gemini 2.5 Flash + GPT-4o |
| web-normalization-rules.md | apps/web/app/api/snail/personal/ocr/route.ts, club/screenshots/route.ts | N/A |

---

## Wiki/Guide Content Extracted

| File | Source | Content Type |
|------|--------|-------------|
| existing-web-beginners-guide.md | apps/web/app/snail/wiki/page.tsx | Beginner guide (What is SS, Joining Cormys, Power leveling, Club mgmt, Codes, Bot commands, Links) |
| existing-web-docs-overview.md | apps/web/app/snail/docs/page.tsx | Ops manual (Club dashboard, Screenshot OCR, Codes, Stats, Access model, Data trust rules) |

---

## Files Left in mint-import/ Not Yet Categorized

The following remain in mint-import/ and were NOT copied:

1. **gnome_game/** — 14,735 files
   - Unity project source code (C# scripts, assets, scenes)
   - Unity Library artifacts (excluded from inventory as build artifacts)
   - Wiki exports (4,124 .wiki files) — copied to wiki_gg/
   - Root-level APKs and manifest.json

2. **slimy_snail/** — 2,929 files
   - Complete reverse engineering workspace
   - Git repository (2,000+ objects in .git/)
   - Evidence hashes and harness proofs (excluded as generated artifacts)
   - Captures/ — network traffic captures, Frida logs, mitmdump logs
   - Core files copied to reverse_engineering/

3. **sheets/** — 50 files
   - All structured data files copied to staging/
   - Audit reports and changelogs copied to staging/formulas/

4. **Root-level binaries**
   - config.arm64_v8a.apk — Game config APK
   - install_asset_pack_na.apk — Asset pack APK
   - manifest.json — Game asset manifest

---

## Recommended Next Actions

### Priority 1: Canonical Records First

1. **Formula/Calculation Data** — The 34 files in `staging/formulas/` should become canonical first:
   - These are player-created calculators with hardcoded formulas
   - They represent the most structured game knowledge available
   - Action: Parse XLSX files into JSON schema records

2. **OCR Prompts** — The 6 prompt files are already canonical references:
   - Should be kept in sync with actual monorepo code
   - Action: Add CI check or monorepo hook to sync prompt changes

3. **Wiki Exports** — 4,124 wiki.gg pages:
   - These are raw wikitext dumps
   - Action: Parse and normalize into structured markdown articles
   - Cross-reference with existing schemas (gear, relics, forms)

### Priority 2: Data Quality

4. **Schema Validation** — The 15 JSON schemas created in Phase 1A should be applied to:
   - Staged XLSX data (after conversion)
   - Wiki export content (after parsing)
   - OCR normalization rules (as field definitions)

5. **Missing Categories** — No gear-specific or code-specific structured data was found:
   - Gear data may be embedded in the wiki exports or Unity source
   - Codes data is already in the monorepo (apps/web/app/api/snail/codes/)

### Priority 3: RE Data

6. **Protocol Analysis** — The slimy_snail RE project contains:
   - Decoded protocol messages
   - Substitution tables for game protocol cipher
   - Frida scripts for SSL unpinning and API hooking
   - Action: Extract protocol field definitions for API documentation

---

## Verification Commands

```bash
# Inventory report
cat game/reports/imports/mint-inventory-2026-05-06.md | head -50

# OCR prompts
ls game/sources/ocr_prompts/

# Staged data
ls game/data/staging/

# Summary report
wc -l game/reports/imports/phase1b-summary-2026-05-06.md
```

---

*Report generated: 2026-05-06*
