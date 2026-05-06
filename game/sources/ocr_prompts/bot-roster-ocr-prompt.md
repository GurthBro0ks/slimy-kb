# Bot Roster OCR Prompt

**Source:** `apps/bot/src/services/roster-ocr.ts`
**Models:** Gemini 2.5 Flash (primary), Gemini 2.5 Pro (tiebreaker)

## System Prompt

```
Extract visible member rows from this Super Snail Manage Members screenshot.
SKIP any row where the power number is cut off or not fully visible.
last_seen is a string like '5h ago' or 'Online'.
Do NOT include any text outside the JSON array.

IMPORTANT — Character disambiguation:
The game font makes certain characters very hard to distinguish. Be especially careful with short names (1-4 characters):
- Lowercase "l" (L) vs uppercase "I" (i) vs digit "1": these look nearly identical. Prefer "l" (lowercase L) for names.
- Uppercure "O" vs digit "0": prefer the letter "O" for names.
- If a name could be read multiple ways, choose the reading that looks most like a player name (e.g., "lil" not "ill" or "1i1").
Examine each character of short names extra carefully before committing to a reading.
```

## Metric-Specific Prompt (Sim Power)

```
The screenshots show the "Sim Power" view of the Manage Members list.
The power value is labeled either "Sim Power" (when sim toggle is active) or "Power" (when total toggle is active).
Return ONLY a JSON array. Each row: {name, power, last_seen}.
power must be an integer with no commas.
```

## Metric-Specific Prompt (Total Power)

```
The screenshots show the "Power" view of the Manage Members list.
The power value is labeled either "Sim Power" (when sim toggle is active) or "Power" (when total toggle is active).
Return ONLY a JSON array. Each row: {name, power, last_seen}.
power must be an integer with no commas.
```

## Fields Extracted

- `name` (string): Player display name
- `power` (bigint): Power value (Sim or Total depending on metric)
- `last_seen` (string): Activity status like "5h ago" or "Online"

## Notes

- Images are resized to max 1568px / JPEG q85 before sending to VLMs
- Dual-model ensemble: Gemini Flash + Gemini Pro run in parallel
- Diff results per row to flag low-confidence entries
- Supports both JSON array and markdown fallback parsing
