# Bot Normalization Rules

**Sources:** `apps/bot/src/services/roster-ocr.ts`, `apps/bot/src/lib/club-vision.ts`, `apps/bot/src/lib/numparse.ts`

## Power Number Parsing (numparse.ts)

### OCR Normalization (pre-parse)

```
- Replace 'O'/'o' → '0'
- Replace 'l'/'I' → '1'
- Strip unicode spaces (\u00A0, \u2000-\u200B, \u202F, \u205F, \u3000)
- Replace Chinese comma '，' → ','
- Replace Chinese period '。' → '.'
```

### Suffix Notation Parsing

```
Pattern: /^([0-9]+(?:\.[0-9]+)?)\s*([KMB])$/i

Multipliers:
- K → 1,000
- M → 1,000,000
- B → 1,000,000,000

Example: "10.5M" → 10,500,000
```

### Grouped Number Parsing

```
- Remove all non-digit/non-dot/non-comma characters
- Remove commas
- Parse as float
```

## Club Vision Normalization (club-vision.ts)

### Name Canonicalization

- Uses `canonicalize()` from `club-store.ts`
- Deduplicates by canonical name
- Keeps highest value and highest confidence per canonical name

### Confidence Scoring

```
- Clamped to [0, 1] range
- Rounded to 3 decimal places
- Ensemble: modelA confidence × 0.7 (if only in A)
- Ensemble: modelB confidence × 0.9 (if only in B)
```

### Digit Reconciliation (Ensemble Mode)

```
- Pad both values to 12 digits with leading zeros
- Compare digit-by-digit
- Agreeing digits: keep
- Disagreeing digits: default to model B
- Track disagreement positions for review
```

## Roster OCR Normalization (roster-ocr.ts)

### JSON Parsing

```
1. Strip markdown code fences (```json...```)
2. Try JSON.parse() on cleaned text
3. If fails, try regex extract: /\[[\s\S]*\]/
4. If still fails, fall back to markdown parsing
```

### Markdown Fallback Parsing

Two patterns supported:

**Pattern A (labeled):**
```
**Name:** Stone
**Sim Power:** 14,321,191
**Status:** Online
```

**Pattern B (bold only):**
```
**Stone**
- Sim Power: 14,321,191
- Status: Online
```

### Power Coercion

```
- bigint → keep as-is
- number → Math.floor() then BigInt()
- string → remove all non-digits, then BigInt()
- null/undefined → skip row
```

### Name Disambiguation Heuristics

```
- Skip empty slots: "(Empty Slot)", "None", names containing "empty"
- Strip surrounding ** from markdown captures
- Levenshtein distance-1 fuzzy merge for model consensus
- Prefer longer name when models disagree by 1 character
```

## Hardcoded Field Names

### Power Metrics
- `sim_power` / `simPower`
- `total_power` / `totalPower`
- `power` (generic fallback)

### Status Fields
- `last_seen` / `lastSeen`
- `status` / `active` / `last_active`

### Member Fields
- `name` / `username`
