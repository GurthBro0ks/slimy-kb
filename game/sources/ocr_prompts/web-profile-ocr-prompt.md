# Web Profile Card OCR Prompt

**Source:** `apps/web/app/api/snail/personal/ocr/route.ts`
**Models:** Gemini 2.5 Flash (primary), GPT-4o (fallback)

## System Prompt

```
Extract all data from this Super Snail player profile card screenshot.
Return ONLY a JSON object with these exact keys, no other text:

{
  "username": "<string - the large player name at top>",
  "power": <number - the power value shown, convert M to millions, K to thousands>,
  "position": "<string - Member/Leader/etc>",
  "species": "<string - Snail/Bird/Cyclops>",
  "weekly_club_exp": <number>,
  "total_club_exp": <number>,
  "server": "<string - server name>",
  "relic_points": <number - convert M/K suffixes>,
  "dna_strength": <number - convert M/K suffixes>,
  "leadership": <number>,
  "gaming_time_days": <number - the number before 'd'>
}

Convert all abbreviated numbers: 188M = 188000000, 9.36M = 9360000,
541K = 541000. Return ONLY valid JSON.
```

## Fields Extracted

| Field | Type | Description |
|-------|------|-------------|
| username | string | Large player name at top of card |
| power | number | Power value (M→millions, K→thousands) |
| position | string | Member/Leader/etc |
| species | string | Snail/Bird/Cyclops |
| weekly_club_exp | number | Weekly club experience |
| total_club_exp | number | Total club experience |
| server | string | Server name |
| relic_points | number | Relic points (M/K converted) |
| dna_strength | number | DNA strength (M/K converted) |
| leadership | number | Leadership value |
| gaming_time_days | number | Number before 'd' suffix |

## Hardcoded Values

### Species Options
- "Snail"
- "Bird"
- "Cyclops"

### Position Options
- "Member"
- "Leader"
- (other rank strings as shown)

### Number Suffix Conversions
- `M` → ×1,000,000
- `K` → ×1,000

Examples:
- `188M` → `188000000`
- `9.36M` → `9360000`
- `541K` → `541000`
