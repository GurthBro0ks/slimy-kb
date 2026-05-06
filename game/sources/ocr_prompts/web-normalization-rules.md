# Web Normalization Rules

**Source:** `apps/web/app/api/snail/personal/ocr/route.ts`, `apps/web/app/api/snail/club/screenshots/route.ts`

## Number Parsing

### parseNumber() Function

```typescript
function parseNumber(val: unknown): number | null {
  if (val === null || val === undefined) return null;
  if (typeof val === "number") return Math.floor(val);
  if (typeof val === "string") {
    const cleaned = val.replace(/,/g, "").trim();
    // Handle K/M suffixes
    if (cleaned.match(/^(\d+(\.\d+)?)\s*[Kk]$/)) {
      const num = parseFloat(cleaned.replace(/[Kk]/, ""));
      return Math.floor(num * 1000);
    }
    if (cleaned.match(/^(\d+(\.\d+)?)\s*[Mm]$/)) {
      const num = parseFloat(cleaned.replace(/[Mm]/, ""));
      return Math.floor(num * 1000000);
    }
    const parsed = parseInt(cleaned, 10);
    return isNaN(parsed) ? null : parsed;
  }
  return null;
}
```

### Suffix Conversions

| Suffix | Multiplier | Example |
|--------|-----------|---------|
| K / k | ×1,000 | 60.2K → 60200 |
| M / m | ×1,000,000 | 3.05M → 3050000 |

## JSON Extraction

### stripCodeFence()

```typescript
function stripCodeFence(text: string): string {
  let cleaned = text.trim();
  if (cleaned.startsWith("```")) {
    cleaned = cleaned.replace(/^```[a-zA-Z]*\n?/, "").replace(/```$/, "");
  }
  return cleaned.trim();
}
```

### Fallback JSON Parsing

```typescript
// If JSON.parse fails, try regex extraction:
const objMatch = cleaned.match(/\{[\s\S]*\}/);
const arrayMatch = cleaned.match(/\[[\s\S]*\]/);
```

## Normalization Functions

### normalizeSnailResult()

```typescript
{
  hard_stats: {
    hp: parseNumber(hard.hp),
    atk: parseNumber(hard.atk),
    def: parseNumber(hard.def),
    rush: parseNumber(hard.rush),
  },
  affct_stats: {
    fame: parseNumber(affct.fame),
    art: parseNumber(affct.art),
    fth: parseNumber(affct.fth),
    civ: parseNumber(affct.civ),
    tech: parseNumber(affct.tech),
  },
  gear: gearRaw
    .filter(g => typeof g === "object" && g !== null)
    .map(g => ({
      slot_number: parseNumber(g.slot_number) || 0,
      enhancement: parseNumber(g.enhancement),
    })),
}
```

### normalizeTroopResult()

```typescript
{
  troop_stats: {
    troop_hp: parseNumber(troop.troop_hp),
    troop_atk: parseNumber(troop.troop_atk),
    troop_def: parseNumber(troop.troop_def),
    troop_rush: parseNumber(troop.troop_rush),
    leadership: parseNumber(troop.leadership),
    troop_power: parseNumber(troop.troop_power),
  },
  war_gear: warGearRaw
    .filter(g => typeof g === "object" && g !== null)
    .map(g => ({
      slot: parseNumber(g.slot) || 0,
      enhancement: parseNumber(g.enhancement),
    })),
}
```

### normalizeProfileResult()

```typescript
{
  username: typeof raw.username === "string" ? raw.username : null,
  power: parseNumber(raw.power),
  position: typeof raw.position === "string" ? raw.position : null,
  species: typeof raw.species === "string" ? raw.species : null,
  weekly_club_exp: parseNumber(raw.weekly_club_exp),
  total_club_exp: parseNumber(raw.total_club_exp),
  server: typeof raw.server === "string" ? raw.server : null,
  relic_points: parseNumber(raw.relic_points),
  dna_strength: parseNumber(raw.dna_strength),
  leadership: parseNumber(raw.leadership),
  gaming_time_days: parseNumber(raw.gaming_time_days),
}
```

## Club Screenshot Normalization (club/screenshots/route.ts)

### Member JSON Parsing

```typescript
function parseMemberJson(raw: string): ExtractedMember[] {
  // Strip code fences, try JSON.parse, fallback to regex array extraction
  // Coerce power fields:
  //   - sim_power: number → Math.floor, string → remove non-digits → parseInt
  //   - total_power: number → Math.floor, string → remove non-digits → parseInt
}
```

### Field Aliases

```typescript
const rawSimPower = obj.sim_power ?? obj.simPower ?? obj.power ?? 0;
const rawTotalPower = obj.total_power ?? obj.totalPower ?? 0;
```

## Hardcoded Field Names

### Snail Stats
- `hard_stats.hp`, `hard_stats.atk`, `hard_stats.def`, `hard_stats.rush`
- `affct_stats.fame`, `affct_stats.art`, `affct_stats.fth`, `affct_stats.civ`, `affct_stats.tech`
- `gear[].slot_number`, `gear[].enhancement`

### Troop Stats
- `troop_stats.troop_hp`, `troop_stats.troop_atk`, `troop_stats.troop_def`, `troop_stats.troop_rush`
- `troop_stats.leadership`, `troop_stats.troop_power`
- `war_gear[].slot`, `war_gear[].enhancement`

### Profile Card
- `username`, `power`, `position`, `species`
- `weekly_club_exp`, `total_club_exp`, `server`
- `relic_points`, `dna_strength`, `leadership`, `gaming_time_days`

### Club Members
- `name`, `sim_power`, `total_power`
